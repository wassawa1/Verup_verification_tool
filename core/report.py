#!/usr/bin/env python3
"""
レポート生成機能を提供するモジュール
"""
import os
import csv
import datetime
from utils.parser import parse_content_for_structured_data


class Report:
    """レポート生成クラス
    
    実行結果のCSVとHTML形式のレポートを生成します。
    """
    
    # 検証項目の定義（観点と項目のマッピング）
    DEFAULT_VERIFICATION_ITEMS = [
        {'phase': '動作', 'item': '起動・実行確認', 'success_memo': '正常終了', 'failed_memo': '異常終了', 'link_type': 'log'},
        {'phase': '成果物', 'item': '出力フォーマット検証', 'success_memo': '差異なし', 'failed_memo': 'フォーマット変更あり', 'link_type': 'new_artifact'},
        {'phase': '成果物', 'item': '計算結果精度検証', 'success_memo': '期待通り', 'failed_memo': '精度低下', 'link_type': 'compare_artifacts'},
        {'phase': '成果物', 'item': 'パフォーマンス検証', 'success_memo': '5%向上', 'failed_memo': '性能低下', 'link_type': 'log'},
        {'phase': '成果物', 'item': 'サマリー情報検証', 'success_memo': '問題なし', 'failed_memo': '不整合あり', 'link_type': 'new_artifact'},
        {'phase': 'ログ', 'item': '警告・エラー解析', 'success_memo': 'エラーなし', 'failed_memo': '警告メッセージあり', 'link_type': 'log'},
        {'phase': '総括', 'item': 'バージョン互換性評価', 'success_memo': '安全に移行可', 'failed_memo': '要対応事項あり', 'link_type': 'report'}
    ]
    
    # 各ツールの検証項目をカスタマイズできる設定
    TOOL_SPECIFIC_ITEMS = {
        'sampletool': [
            {'phase': '動作', 'item': '起動・実行確認', 'success_memo': '正常終了', 'failed_memo': '異常終了', 'link_type': 'log'},
            {'phase': '成果物', 'item': '出力フォーマット検証', 'success_memo': '差異なし', 'failed_memo': 'フォーマット変更あり', 'link_type': 'new_artifact'},
            {'phase': '成果物', 'item': '計算結果精度検証', 'success_memo': '期待通り', 'failed_memo': '精度低下', 'link_type': 'compare_artifacts'},
            {'phase': '成果物', 'item': 'パフォーマンス検証', 'success_memo': '5%向上', 'failed_memo': '性能低下', 'link_type': 'log'},
            {'phase': '成果物', 'item': 'サマリー情報検証', 'success_memo': '問題なし', 'failed_memo': '不整合あり', 'link_type': 'new_artifact'},
            {'phase': 'ログ', 'item': '警告・エラー解析', 'success_memo': 'エラーなし', 'failed_memo': '警告メッセージあり', 'link_type': 'log'},
            {'phase': '総括', 'item': 'バージョン互換性評価', 'success_memo': '安全に移行可', 'failed_memo': '要対応事項あり', 'link_type': 'report'}
        ],
        'icc2_smoke': [
            {'phase': '動作', 'item': '起動・実行確認', 'success_memo': '正常終了', 'failed_memo': '異常終了', 'link_type': 'log'},
            {'phase': '成果物', 'item': '出力フォーマット検証', 'success_memo': '差異なし', 'failed_memo': 'フォーマット変更あり', 'link_type': 'new_artifact'},
            {'phase': '成果物', 'item': '計算結果精度検証', 'success_memo': '期待通り', 'failed_memo': '精度低下', 'link_type': 'compare_artifacts'},
            {'phase': '成果物', 'item': 'メモリ使用量検証', 'success_memo': '改善', 'failed_memo': '悪化', 'link_type': 'log'}, # ICC2固有の項目
            {'phase': '成果物', 'item': 'サマリー情報検証', 'success_memo': '問題なし', 'failed_memo': '不整合あり', 'link_type': 'new_artifact'},
            {'phase': 'ログ', 'item': '警告・エラー解析', 'success_memo': 'エラーなし', 'failed_memo': '警告メッセージあり', 'link_type': 'log'},
            {'phase': '総括', 'item': 'バージョン互換性評価', 'success_memo': '安全に移行可', 'failed_memo': '要対応事項あり', 'link_type': 'report'}
        ]
        # 他のツール用の検証項目も追加可能
    }
    
    def __init__(self, results=None, verification_items=None):
        """
        Parameters:
            results (list, optional): 比較結果のリスト
            verification_items (list, optional): カスタム検証項目リスト
        """
        self.results = results if results else []
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.verification_items = verification_items if verification_items else self.DEFAULT_VERIFICATION_ITEMS
    
    def add_result(self, result):
        """
        結果を追加する
        
        Parameters:
            result (dict): 比較結果
        """
        self.results.append(result)
    
    def generate_csv(self, filename='report.csv'):
        """
        CSV形式のレポートを生成する
        
        Parameters:
            filename (str, optional): 出力ファイル名
            
        Returns:
            str: 出力ファイルのパス
        """
        with open(filename, 'w', newline='', encoding='cp932') as csvfile:
            fieldnames = ['Timestamp', 'Tool', 'Version_old', 'Version_new', '観点', '判定', '判定メモ', '項目', '評価指標', 'リンク']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            default_timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
            
            for result in self.results:
                tool_name = result.get('tool_name', '')
                old_version = result.get('old_version', '')
                new_version = result.get('new_version', '')
                status = result.get('status', 'Error')
                detail = result.get('detail', '')
                
                # 各項目ごとのタイムスタンプがなければ、デフォルトタイムスタンプを使用
                result_timestamp = result.get('timestamp', default_timestamp)
                
                # 実際のファイルが存在するかチェック
                artifact_old = f"artifacts/{tool_name}_{old_version}.txt"
                artifact_new = f"artifacts/{tool_name}_{new_version}.txt"
                
                # 最新のログファイルを探す
                log_pattern = f"{tool_name}_{old_version}_{new_version}_"
                log_files = [f for f in os.listdir('logs') if f.startswith(log_pattern)]
                latest_log = f"logs/{log_files[-1]}" if log_files else ""
                
                # ツール固有のカスタム検証項目があれば使用
                if tool_name.lower() in self.TOOL_SPECIFIC_ITEMS:
                    verification_items = self.TOOL_SPECIFIC_ITEMS[tool_name.lower()]
                else:
                    verification_items = result.get('verification_items', self.verification_items)
                
                # 項目ごとの判定結果を解析
                structured_data = parse_content_for_structured_data(result.get('detail', ''))
                
                # 各検証項目ごとにレコードを生成
                for item in verification_items:
                    phase = item['phase']  # 観点
                    item_name = item['item']  # 項目名
                    success_memo = item['success_memo']
                    failed_memo = item['failed_memo']
                    link_type = item['link_type']
                    
                    # 項目ごとの判定を取得（項目固有の判定がなければツール全体のステータスを使用）
                    item_status = result.get(f'status_{item_name}', status)
                    item_timestamp = result.get(f'timestamp_{item_name}', result_timestamp)
                    
                    # N/A（評価対象外）のものは表示しない
                    if item_status == 'N/A':
                        continue
                    
                    # 判定メモを設定
                    if item_status == 'Success':
                        judgment_memo = success_memo
                    elif item_status == 'Failed':
                        judgment_memo = failed_memo
                    elif item_status == 'N/A':
                        judgment_memo = '評価対象外'
                    else:
                        judgment_memo = 'エラー'
                    
                    # リンクの有効性を確認
                    has_valid_link = False
                    
                    # リンクを設定
                    link_text = ''
                    link_url = ''
                    if link_type == 'log':
                        if latest_log and os.path.exists(latest_log):
                            has_valid_link = True
                            link_text = '実行ログ'
                            link_url = latest_log
                    elif link_type == 'new_artifact':
                        if artifact_new and os.path.exists(artifact_new):
                            has_valid_link = True
                            link_text = f'成果物({new_version})'
                            link_url = artifact_new
                    elif link_type == 'compare_artifacts':
                        if os.path.exists(artifact_old) and os.path.exists(artifact_new):
                            has_valid_link = True
                            link_text = '成果物比較'
                            link_url = f"{artifact_old})→({artifact_new}"
                    elif link_type == 'report':
                        # レポートは常に存在すると仮定
                        has_valid_link = True
                        link_text = 'レポート'
                        link_url = 'report.html'
                    
                    # 総括項目は常に表示（リンクがなくても）
                    if phase == '総括':
                        has_valid_link = True
                    
                    # リンクを生成
                    link = ''
                    if link_url and os.path.exists(link_url):
                        link = f'[{link_text}]({link_url})'
                    elif link_type == 'report':  # レポートは常に存在すると仮定
                        link = f'[{link_text}]({link_url})'
                    elif link_type == 'compare_artifacts' and os.path.exists(artifact_old) and os.path.exists(artifact_new):
                        link = f'[成果物比較]({artifact_old})→({artifact_new})'
                    else:
                        link = '[成果物なし]()'
                    
                    # 評価結果を表示するかどうか判断
                    # 総括項目は常に表示、それ以外はリンクが有効な場合のみ表示
                    if phase == '総括' or has_valid_link:
                        # 評価指標を取得（なければ空文字列）
                        criteria = result.get(f'criteria_{item_name}', '')
                        
                        # レコード書き込み
                        writer.writerow({
                            'Timestamp': item_timestamp,
                            'Tool': tool_name,
                            'Version_old': old_version,
                            'Version_new': new_version,
                            '観点': phase,
                            '判定': item_status,  # 全体判定ではなく項目ごとの判定を使用
                            '判定メモ': judgment_memo,
                            '項目': item_name,
                            '評価指標': criteria,
                            'リンク': link
                        })
        
        return os.path.abspath(filename)
    
    def generate_html(self, filename='report.html'):
        """
        HTML形式のレポートを生成する
        
        Parameters:
            filename (str, optional): 出力ファイル名
            
        Returns:
            str: 出力ファイルのパス
        """
        html_content = self._generate_html_content()
        
        # UTF-8で保存
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return os.path.abspath(filename)
    
    def _generate_html_content(self):
        """
        HTMLコンテンツを生成する
        READMEに記載されたCSVレポートと同等の内容をHTML形式で表示する
        
        Returns:
            str: HTMLコンテンツ
        """
        timestamp_now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>バージョンアップ検証結果</title>
    <style>
body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f5f5f5;
}}
        h1, h2, h3 {{
            color: #444;
        }}
        h1 {{
            border-bottom: 2px solid #ddd;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f8f8;
            font-weight: 600;
            border-bottom: 2px solid #ddd;
            color: #555;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #e9f3ff;
        }}
        .Success {{
            background-color: #dff0d8;
            color: #3c763d;
            font-weight: bold;
        }}
        .Failed {{
            background-color: #f2dede;
            color: #a94442;
            font-weight: bold;
        }}
        .Error {{
            background-color: #fcf8e3;
            color: #8a6d3b;
            font-weight: bold;
        }}
        .N\\/A {{
            background-color: #f5f5f5;
            color: #777;
            font-style: italic;
        }}
        .detail-section {{
            background-color: white;
            border: 1px solid #ddd;
            padding: 15px;
            margin-top: 10px;
            border-radius: 5px;
        }}
        .detail-title {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .criteria-item {{
            margin-bottom: 8px;
            padding: 8px;
            border-radius: 4px;
        }}
        .criteria-item.Success {{
            background-color: #dff0d8;
        }}
        .criteria-item.Failed {{
            background-color: #f2dede;
        }}
        .criteria-item.Error {{
            background-color: #fcf8e3;
        }}
        .summary-box {{
            margin: 20px 0;
            padding: 15px;
            border-radius: 5px;
            border-left: 5px solid #ddd;
        }}
        .summary-success {{
            border-left-color: #3c763d;
            background-color: #dff0d8;
        }}
        .summary-failed {{
            border-left-color: #a94442;
            background-color: #f2dede;
        }}
        .value-item {{
            margin-bottom: 5px;
            padding: 5px;
            border-bottom: 1px solid #eee;
        }}
        .timestamp {{
            text-align: right;
            color: #777;
            font-style: italic;
            margin-top: 20px;
        }}
        details {{
            margin-bottom: 10px;
            padding: 10px;
            background-color: white;
            border-radius: 5px;
            border: 1px solid #ddd;
        }}
        summary {{
            font-weight: bold;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <h1>バージョンアップ検証結果</h1>
    <div class="timestamp">レポート生成日時: {timestamp}</div>
    
    {summary}
    
    <h2>詳細結果</h2>
    <table>
        <thead>
            <tr>
                <th>タイムスタンプ</th>
                <th>ツール</th>
                <th>旧バージョン</th>
                <th>新バージョン</th>
                <th>観点</th>
                <th>判定</th>
                <th>判定メモ</th>
                <th>項目</th>
                <th>評価指標</th>
                <th>リンク</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    
    <h2>詳細分析</h2>
    {detail_sections}
</body>
</html>
'''
        
        # テーブル行の生成
        table_rows = []
        
        for result in self.results:
            tool_name = result.get('tool_name', '')
            old_version = result.get('old_version', '')
            new_version = result.get('new_version', '')
            status = result.get('status', 'Error')
            detail = result.get('detail', '')
            
            # 実際のファイルが存在するかチェック
            artifact_old = f"artifacts/{tool_name}_{old_version}.txt"
            artifact_new = f"artifacts/{tool_name}_{new_version}.txt"
            
            # 最新のログファイルを探す
            log_pattern = f"{tool_name}_{old_version}_{new_version}_"
            log_files = [f for f in os.listdir('logs') if f.startswith(log_pattern)]
            latest_log = f"logs/{log_files[-1]}" if log_files else ""
            
            # デフォルトのタイムスタンプを設定
            result_timestamp = result.get('timestamp', timestamp_now)
            
            # ツール固有のカスタム検証項目があれば使用
            if tool_name.lower() in self.TOOL_SPECIFIC_ITEMS:
                verification_items = self.TOOL_SPECIFIC_ITEMS[tool_name.lower()]
            else:
                verification_items = result.get('verification_items', self.verification_items)
            
            # 各検証項目ごとにレコードを生成
            for item in verification_items:
                phase = item['phase']  # 観点
                item_name = item['item']  # 項目名
                success_memo = item['success_memo']
                failed_memo = item['failed_memo']
                link_type = item['link_type']
                
                # 項目ごとの判定を取得（項目固有の判定がなければツール全体のステータスを使用）
                item_status = result.get(f'status_{item_name}', status)
                item_timestamp = result.get(f'timestamp_{item_name}', result_timestamp)
                
                # N/A（評価対象外）のものは表示しない
                if item_status == 'N/A':
                    continue
                
                # 判定メモを設定
                if item_status == 'Success':
                    judgment_memo = success_memo
                elif item_status == 'Failed':
                    judgment_memo = failed_memo
                elif item_status == 'N/A':
                    judgment_memo = '評価対象外'
                else:
                    judgment_memo = 'エラー'
                
                # リンクの有効性を確認
                has_valid_link = False
                
                # リンクを設定
                link_html = ''
                if link_type == 'log':
                    if latest_log and os.path.exists(latest_log):
                        has_valid_link = True
                        link_html = f'<a href="{latest_log}">実行ログ</a>'
                    else:
                        link_html = 'ログなし'
                elif link_type == 'new_artifact':
                    if artifact_new and os.path.exists(artifact_new):
                        has_valid_link = True
                        link_html = f'<a href="{artifact_new}">成果物({new_version})</a>'
                    else:
                        link_html = '成果物なし'
                elif link_type == 'compare_artifacts':
                    if os.path.exists(artifact_old) and os.path.exists(artifact_new):
                        has_valid_link = True
                        link_html = f'<a href="{artifact_old}">旧</a>→<a href="{artifact_new}">新</a>'
                    else:
                        link_html = '成果物なし'
                elif link_type == 'report':
                    # レポートは常に存在すると仮定
                    has_valid_link = True
                    link_html = '<a href="report.html">レポート</a>'
                
                # 総括項目は常に表示
                if phase == '総括':
                    has_valid_link = True
                
                # 行を生成（初期値を空文字列にしておく）
                row = ''
                
                # 評価結果を表示するかどうか判断
                # 総括項目は常に表示、それ以外はリンクが有効な場合のみ表示
                if phase == '総括' or has_valid_link:
                    # 評価指標を取得（なければ空文字列）
                    criteria = result.get(f'criteria_{item_name}', '')
                    
                    # 行を生成
                    row = f'''
                    <tr>
                        <td>{item_timestamp}</td>
                        <td>{tool_name}</td>
                        <td>{old_version}</td>
                        <td>{new_version}</td>
                        <td>{phase}</td>
                        <td class="{item_status}">{item_status}</td>
                        <td>{judgment_memo}</td>
                        <td>{item_name}</td>
                        <td>{criteria}</td>
                        <td>{link_html}</td>
                    </tr>'''
                # 行が生成された場合のみ追加
                if row:
                    table_rows.append(row)
            
            # 重複している部分を削除（すでに上部のループで処理されています）
        
        table_rows_html = '\n'.join(table_rows)
        
        # サマリーの生成
        success_count = sum(1 for result in self.results if result.get('status') == 'Success')
        failed_count = sum(1 for result in self.results if result.get('status') == 'Failed')
        error_count = sum(1 for result in self.results if result.get('status') == 'Error')
        total_count = len(self.results)
        
        summary_class = 'summary-success' if failed_count == 0 and error_count == 0 else 'summary-failed'
        
        summary = f'''
        <div class="summary-box {summary_class}">
            <h3>サマリー</h3>
            <p>合計テスト数: {total_count}</p>
            <p>成功: {success_count}</p>
            <p>失敗: {failed_count}</p>
            <p>エラー: {error_count}</p>
        </div>'''
        
        # 詳細セクションの生成
        detail_sections = []
        
        for result in self.results:
            tool_name = result.get('tool_name', '')
            old_version = result.get('old_version', '')
            new_version = result.get('new_version', '')
            status = result.get('status', 'Error')
            detail = result.get('detail', '')
            
            # 成果物のパスを取得
            old_artifact_path = result.get('old_artifact_path', '')
            new_artifact_path = result.get('new_artifact_path', '')
            
            # 成果物の内容を解析して構造化データを抽出
            old_content = result.get('old_content', '')
            new_content = result.get('new_content', '')
            structured_data = None
            
            if new_content:
                structured_data = parse_content_for_structured_data(new_content)
            
            # 詳細セクションの作成
            detail_section = f'''
            <details>
                <summary>【{status}】{tool_name} ({old_version} → {new_version})</summary>
                <div class="detail-section">
                    <div class="detail-title">基本情報:</div>
                    <p>ツール: {tool_name}</p>
                    <p>旧バージョン: {old_version}</p>
                    <p>新バージョン: {new_version}</p>
                    <p>ステータス: <span class="{status}">{status}</span></p>
                    
                    <div class="detail-title">詳細:</div>
                    <p>{detail}</p>
            '''
            
            # 構造化データがある場合、検証項目を表示
            if structured_data and structured_data.get('criteria'):
                detail_section += '''
                    <div class="detail-title">検証項目:</div>
                '''
                
                for criteria in structured_data.get('criteria', []):
                    criteria_status = criteria.get('status', 'Success')
                    criteria_name = criteria.get('name', '')
                    criteria_desc = criteria.get('description', '')
                    
                    detail_section += f'''
                    <div class="criteria-item {criteria_status}">
                        <strong>{criteria_name}:</strong> {criteria_desc}
                    </div>
                    '''
            
            # 値のデータがある場合、表示
            if structured_data and structured_data.get('values'):
                detail_section += '''
                    <div class="detail-title">測定値:</div>
                '''
                
                for value in structured_data.get('values', []):
                    value_name = value.get('name', '')
                    value_val = value.get('value', '')
                    value_unit = value.get('unit', '')
                    
                    detail_section += f'''
                    <div class="value-item">
                        <strong>{value_name}:</strong> {value_val} {value_unit}
                    </div>
                    '''
            
            # 成果物パスを表示
            if old_artifact_path or new_artifact_path:
                detail_section += '''
                    <div class="detail-title">成果物:</div>
                '''
                
                if old_artifact_path:
                    detail_section += f'<p>旧バージョン: {old_artifact_path}</p>'
                
                if new_artifact_path:
                    detail_section += f'<p>新バージョン: {new_artifact_path}</p>'
            
            detail_section += '''
                </div>
            </details>
            '''
            
            detail_sections.append(detail_section)
        
        detail_sections_html = '\n'.join(detail_sections)
        
        # HTMLテンプレートに値を埋め込む
        html_content = html.format(
            timestamp=self.timestamp,
            summary=summary,
            table_rows=table_rows_html,
            detail_sections=detail_sections_html
        )
        
        return html_content
