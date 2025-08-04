#!/usr/bin/env python3
import os
import sys
import csv
import glob
import shutil
import argparse
import datetime
import subprocess
import importlib.util
import inspect
import re
import stat


# グローバル定数
TOOLS_DIR = 'Apps'  # ツールが配置されているディレクトリ
INPUTS_DIR = 'inputs'  # 入力ファイルが配置されているディレクトリ

class Tee:
    """
    標準出力と標準エラー出力を複数の出力先にリダイレクトするためのクラス
    """
    def __init__(self, *files):
        self.files = files
    
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    
    def flush(self):
        for f in self.files:
            f.flush()


def get_exec_cmd(tool):
    """
    実行ファイルを検索する関数
    
    Parameters:
        tool (str): ツール名
        
    Returns:
        str or None: 実行ファイルのパス、見つからない場合はNone
    """
    def find_exec(name, version):
        """特定のバージョンの実行ファイルを探す"""
        # Windowsの場合
        exec_patterns = ['*.exe', '*.bat', '*.cmd', '*.py']
        tool_path = os.path.join(TOOLS_DIR, name, version)
        
        if not os.path.exists(tool_path):
            return None
        
        for pattern in exec_patterns:
            execs = glob.glob(os.path.join(tool_path, pattern))
            if execs:
                return execs[0]  # 最初に見つかった実行ファイルを返す
        
        return None  # 実行ファイルが見つからない場合
    
    return find_exec


def write_html_report(csv_file, html_file):
    """
    CSVレポートからHTMLレポートを生成する関数
    
    Parameters:
        csv_file (str): 入力CSVファイルのパス
        html_file (str): 出力HTMLファイルのパス
    """
    # CSVファイルを読み込む
    rows = []
    header = None
    
    try:
        # ファイルが存在しない場合、処理をスキップ
        if not os.path.exists(csv_file):
            print(f"[WARNING] CSV file not found: {csv_file}")
            return
            
        # Windows環境での権限問題対策
        if os.path.exists(html_file):
            try:
                os.chmod(html_file, stat.S_IWRITE)
            except:
                pass  # 権限変更に失敗しても続行
                
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # ヘッダー行を読み込む
            for row in reader:
                rows.append(row)
    except Exception as e:
        print(f"[ERROR] Failed to read CSV: {str(e)}")
        return
    
    # HTMLの生成
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Update Tool Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                color: #333;
            }
            h1 {
                color: #333;
                border-bottom: 2px solid #4CAF50;
                padding-bottom: 10px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            th {
                background-color: #4CAF50;
                color: white;
                position: sticky;
                top: 0;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f2f2f2;
            }
            .success, .good, .excellent {
                background-color: #dff0d8;
                color: #3c763d;
            }
            .failure, .warning {
                background-color: #f2dede;
                color: #a94442;
            }
            .error {
                background-color: #fcf8e3;
                color: #8a6d3b;
            }
            .normal {
                background-color: #e8f4f8;
                color: #31708f;
            }
            .excellent-text {
                color: #2e7d32;
                font-weight: bold;
            }
            .good-text {
                color: #388e3c;
                font-weight: bold;
            }
            .normal-text {
                color: #0277bd;
            }
            .warning-text {
                color: #ff9800;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <h1>Update Tool Report</h1>
        <table>
            <tr>
    """
    
    # ヘッダーの追加
    for col in header:
        html_content += f"<th>{col}</th>"
    
    html_content += "</tr>"
    
    # データ行の追加
    for row in rows:
        # 結果列のインデックスを取得
        result_col_idx = header.index("結果") if "結果" in header else -1
        
        # 結果に基づいて行のスタイルを設定
        row_class = ""
        if result_col_idx >= 0 and len(row) > result_col_idx:
            result = row[result_col_idx].lower()
            if result == "success":
                row_class = "success"
            elif result == "failure":
                row_class = "failure"
            elif result == "error":
                row_class = "error"
            elif result == "excellent":
                row_class = "excellent"
            elif result == "good":
                row_class = "good"
            elif result == "normal":
                row_class = "normal"
            elif result == "warning":
                row_class = "warning"
        
        html_content += f'<tr class="{row_class}">'
        
        # 各セルのフォーマット
        for i, cell in enumerate(row):
            cell_class = ""
            cell_content = cell
            
            # 特定の列の場合、スタイルを変更
            col_name = header[i] if i < len(header) else ""
            
            # 結果列の特別なフォーマット
            if col_name == "結果":
                if cell.lower() == "excellent":
                    cell_class = "excellent-text"
                elif cell.lower() == "good":
                    cell_class = "good-text"
                elif cell.lower() == "normal":
                    cell_class = "normal-text"
                elif cell.lower() == "warning":
                    cell_class = "warning-text"
            
            # 詳細列
            elif col_name == "詳細" and len(cell) > 300:
                preview = cell[:300] + "..."
                full_content = cell.replace('"', '&quot;')
                cell_content = f"""<details>
                               <summary>詳細を表示/非表示</summary>
                               <div style="white-space: pre-wrap;">{full_content}</div>
                             </details>"""
            else:
                cell_content = f'<div style="white-space: pre-wrap;">{cell}</div>'
            
            html_content += f'<td class="{cell_class}">{cell_content}</td>'
        
        html_content += "</tr>"
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    try:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML report created: {html_file}")
    except PermissionError:
        print(f"[ERROR] Permission denied while writing HTML report. Please close any program that might be using {html_file}")
    except Exception as e:
        print(f"[ERROR] Failed to write HTML report: {str(e)}")


def load_custom_comparator(tool, comparator_type):
    """
    カスタム比較関数をロードする
    
    Parameters:
        tool (str): ツール名
        comparator_type (str): 比較関数のタイプ ("artifacts" or "logs")
        
    Returns:
        function or None: カスタム比較関数またはNone
    """
    try:
        # 比較関数のファイル名を生成
        comparator_dir = "comparators"
        comparator_file = os.path.join(comparator_dir, f"{tool.lower()}_comparator.py")
        
        # ファイルが存在しなければNoneを返す
        if not os.path.exists(comparator_file):
            return None
            
        # モジュールの名前を設定
        module_name = f"{tool.lower()}_comparator"
        
        # モジュールをロード
        spec = importlib.util.spec_from_file_location(module_name, comparator_file)
        if not spec or not spec.loader:
            print(f"Failed to create spec for {comparator_file}")
            return None
            
        module = importlib.util.module_from_spec(spec)
        
        if not hasattr(spec.loader, 'exec_module'):
            print(f"Loader for {comparator_file} does not support exec_module")
            return None
            
        spec.loader.exec_module(module)
        
        # 比較関数を取得
        function_name = f"compare_{comparator_type}"
        if hasattr(module, function_name):
            return getattr(module, function_name)
        else:
            return None
    except Exception as e:
        print(f"[ERROR] Error loading custom comparator: {str(e)}")
        return None


def get_log_files(tool, version):
    """
    ログファイルのパスを取得する関数
    
    Parameters:
        tool (str): ツール名
        version (str): バージョン
        
    Returns:
        str or None: 最新のログファイルパスまたはNone
    """
    log_dir = "logs"
    log_pattern = os.path.join(log_dir, f"{tool}_{version}_*.log")
    logs = glob.glob(log_pattern)
    
    if not logs:
        # 古いログパターンもチェック
        old_pattern = os.path.join(log_dir, f"{tool}_{version}.log")
        if os.path.exists(old_pattern):
            return old_pattern
        return None
        
    # タイムスタンプで降順ソートし、最新のログを返す
    logs.sort(reverse=True)
    return logs[0]


def generate_demo_artifacts(tool, old_version, new_version):
    """
    デモ用の成果物ファイルを生成する
    ※この機能はデモ用のために残していますが、すべてカスタムコンパレータを使用する設計のため、
    実際にはDemoToolのカスタムコンパレータが使用されます。
    
    Parameters:
        tool (str): ツール名
        old_version (str): 旧バージョン
        new_version (str): 新バージョン
        
    Returns:
        tuple: (old_file_path, new_file_path)
    """
    # デモ用ディレクトリの作成
    artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    
    # ファイルパスのみを返す (実際のファイル生成はカスタムコンパレータで行う)
    old_file = os.path.join(artifacts_dir, f"{tool}_{old_version}.txt")
    new_file = os.path.join(artifacts_dir, f"{tool}_{new_version}.txt")
    
    return old_file, new_file
        
    return None, None


def run_tool(tool, old, new, input_files=[]):
    """
    ツールの旧バージョンと新バージョンを実行する
    
    Parameters:
        tool (str): ツール名
        old (str): 旧バージョン
        new (str): 新バージョン
        input_files (list): 入力ファイル一覧
        
    Returns:
        bool: 実行結果（True: 成功、False: 失敗）
    """
    print(f"[STEP1] Running {tool} versions {old} and {new}")
    
    if input_files:
        print(f"[STEP1] Using input files: {', '.join(os.path.basename(f) for f in input_files)}")
    else:
        print("[STEP1] No input files specified")
    
    # DemoTool の場合はデモ用成果物を生成
    if tool == 'DemoTool':
        print(f"[STEP1][DEMO] Simulating execution of DemoTool {old} -> {new}")
        
        # バージョン比較用に十分な差をつける
        old_time = 3.5
        new_time = 2.6
        print(f"[STEP1][DEMO] DemoTool {old} executed in {old_time:.1f} seconds")
        print(f"[STEP1][DEMO] DemoTool {new} executed in {new_time:.1f} seconds")
        print(f"[STEP1][DEMO] Performance improved by {(old_time - new_time) / old_time * 100:.1f}%")
        
        # デモ用ディレクトリの作成
        artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
        os.makedirs(artifacts_dir, exist_ok=True)
        
        # デモ用成果物を生成
        for version, ver_time in [(old, old_time), (new, new_time)]:
            output_file = os.path.join(artifacts_dir, f"{tool}_{version}.txt")
            
            # 共通の出力内容
            content = f"""{tool} {version}
===================
処理結果サマリー
-------------------
合計処理ファイル数: 3
成功: 3
失敗: 0
警告: 0
"""

            # バージョン固有の内容を追加
            if version == old:
                content += f"""
詳細:
- ファイル1: 正常処理 (処理時間: 1.2秒)
- ファイル2: 正常処理 (処理時間: 0.8秒)
- ファイル3: 正常処理 (処理時間: 1.5秒)
"""
            else:
                content += f"""
詳細:
- ファイル1: 正常処理 (処理時間: 0.9秒)
- ファイル2: 正常処理 (処理時間: 0.6秒)
- ファイル3: 正常処理 (処理時間: 1.1秒)
"""
            
            # ファイルに書き込み
            with open(output_file, "w", encoding="cp932") as f:
                f.write(content)
                
                # 入力ファイルごとの処理結果を追加
                input_files = glob.glob(os.path.join(INPUTS_DIR, "*.*"))
                if input_files:
                    for input_file in input_files:
                        f.write(f"=== {os.path.basename(input_file)} の処理結果 ===\n")
                        if version == old:
                            f.write("処理パラメータ: 標準設定\n")
                        else:
                            f.write("処理パラメータ: 最適化設定\n")
                        f.write("\n")
        
        # ログファイル生成
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # タイムスタンプ生成
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(logs_dir, f"{tool}_{old}_{new}_{timestamp}.log")
        
        # ログファイル内容
        log_content = f"""[{tool}] バージョン {old} → {new} 実行ログ
実行日時: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
入力ファイル: {', '.join(os.path.basename(f) for f in input_files) if input_files else 'なし'}
処理時間: {old_time}秒 → {new_time}秒 ({(old_time - new_time) / old_time * 100:.1f}% 改善)
実行結果: 正常終了
"""
        
        # ログファイル書き込み
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write(log_content)
            
        return True
    
    try:
        find_exec = get_exec_cmd(tool)
        
        # 旧バージョン実行
        exec_old = find_exec(tool, old)
        if not exec_old:
            print(f"[ERROR] {tool} {old} 実行ファイルが見つかりません")
            return False
        if exec_old.lower().endswith('.py'):
            cmd_old = [sys.executable, exec_old]
        else:
            cmd_old = [exec_old]
        print(f"[STEP1] Running {tool} {old} ...")
        result_old = subprocess.run(cmd_old, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result_old.stdout)
        # 新バージョン実行
        exec_new = find_exec(tool, new)
        if not exec_new:
            print(f"[ERROR] {tool} {new} 実行ファイルが見つかりません")
            return False
        if exec_new.lower().endswith('.py'):
            cmd_new = [sys.executable, exec_new]
        else:
            cmd_new = [exec_new]
        print(f"[STEP1] Running {tool} {new} ...")
        result_new = subprocess.run(cmd_new, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result_new.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"[ERROR] Tool '{tool}' not found")
        return False


def compare_artifacts(tool, old, new):
    """
    成果物の比較を行う関数
    カスタムコンパレータのみを使用する設計
    
    Parameters:
        tool (str): ツール名
        old (str): 旧バージョン
        new (str): 新バージョン
        
    Returns:
        tuple: (bool, str, str) - (成功/失敗, メッセージ, 詳細内容)
    """
    print(f"[STEP2] Comparing artifacts for {tool} {old} -> {new}...")
    
    # カスタム比較関数をロード
    custom_comparator = load_custom_comparator(tool, "artifacts")
    
    # カスタム比較関数が必須
    if not custom_comparator:
        msg = f"カスタムコンパレータが見つかりません。{tool}用のカスタム比較関数を実装してください。"
        print(f"[STEP2][ERROR] {msg}")
        return False, msg, f"ツール {tool} 用のカスタムコンパレータを以下に作成してください:\n" \
                          f"comparators/{tool.lower()}_comparator.py\n\n" \
                          f"def compare_artifacts(old_file, new_file):\n" \
                          f"    # 実装が必要です\n" \
                          f"    return True, 'カスタム比較メッセージ', 'カスタム比較の詳細内容'"
    
    # カスタム比較関数を実行
    print(f"[STEP2] Using custom artifacts comparator for {tool}")
    try:
        # カスタム関数のシグネチャを取得
        sig = inspect.signature(custom_comparator)
        params = list(sig.parameters.keys())
        
        # パラメータが一致するか確認
        if len(params) < 2:  # 最低限old_fileとnew_fileが必要
            msg = f"カスタムコンパレータのシグネチャが不正です: {params}"
            print(f"[STEP2][ERROR] {msg}")
            return False, msg, ""
            
        # 成果物ファイルパスを構築
        artifact_dir = "artifacts"
        old_file = os.path.join(artifact_dir, f"{tool}_{old}.txt")
        new_file = os.path.join(artifact_dir, f"{tool}_{new}.txt")
        
        # ファイルの存在チェック
        if not os.path.exists(old_file) or not os.path.exists(new_file):
            msg = f"Artifact files not found: {old_file} or {new_file}"
            print(f"[STEP2][ERROR] {msg}")
            return False, msg, ""
            
        # カスタム関数呼び出し
        result = custom_comparator(old_file, new_file)
        if isinstance(result, tuple) and len(result) >= 3:
            # 戻り値が3要素以上のタプルの場合は(ok, msg, content)と解釈
            ok, msg, content = result
            print(f"[STEP2] Custom comparison {'succeeded' if ok else 'failed'}: {msg}")
            return ok, msg, content
        elif isinstance(result, bool):
            # 戻り値がブール値の場合は(ok, "", "")と解釈
            msg = "Custom comparison " + ("succeeded" if result else "failed")
            print(f"[STEP2] {msg}")
            return result, msg, ""
        else:
            msg = f"Invalid return type from custom comparator: {type(result)}"
            print(f"[STEP2][ERROR] {msg}")
            return False, msg, ""
    except Exception as e:
        msg = f"Error in custom comparator: {str(e)}"
        print(f"[STEP2][ERROR] {msg}")
        return False, msg, ""


def compare_logs(tool, old, new):
    """
    ログファイルの比較を行う関数
    カスタム比較関数のみを使用する設計
    
    Parameters:
        tool (str): ツール名
        old (str): 旧バージョン
        new (str): 新バージョン
        
    Returns:
        tuple: (bool, str, str) - (成功/失敗, メッセージ, 詳細内容)
    """
    print(f"[STEP3] Comparing logs for {tool} {old} -> {new}...")
    
    # カスタム比較関数をロード
    custom_comparator = load_custom_comparator(tool, "logs")
    
    # カスタム比較関数が必須
    if not custom_comparator:
        # ログファイルがなくてもエラーとはしないため、カスタム比較器がない場合はスキップと表示
        msg = f"カスタムログ比較器が見つかりません。{tool}用のカスタム比較関数を実装してください。"
        print(f"[STEP3][WARNING] {msg}")
        return True, msg, f"ツール {tool} 用のカスタムログコンパレータを以下に作成してください:\n" \
                          f"comparators/{tool.lower()}_comparator.py\n\n" \
                          f"def compare_logs(old_log, new_log):\n" \
                          f"    # 実装が必要です\n" \
                          f"    return True, 'カスタム比較メッセージ', 'カスタム比較の詳細内容'"
    
    # カスタム比較関数を実行
    print(f"[STEP3] Using custom logs comparator for {tool}")
    try:
        # カスタム関数のシグネチャを取得
        sig = inspect.signature(custom_comparator)
        params = list(sig.parameters.keys())
        
        # パラメータが一致するか確認
        if len(params) < 2:  # 最低限old_logとnew_logが必要
            msg = f"カスタムログ比較器のシグネチャが不正です: {params}"
            print(f"[STEP3][ERROR] {msg}")
            return False, msg, ""
            
        # 最新のログファイルを取得
        old_log = get_log_files(tool, old)
        new_log = get_log_files(tool, new)
        
        if not old_log or not new_log:
            msg = "Log files not found"
            print(f"[STEP3][WARNING] {msg}")
            # ログファイルがなくてもエラーとはしない
            return True, msg, ""
            
        # カスタム関数呼び出し
        result = custom_comparator(old_log, new_log)
        if isinstance(result, tuple) and len(result) >= 3:
            # 戻り値が3要素以上のタプルの場合は(ok, msg, content)と解釈
            ok, msg, content = result
            print(f"[STEP3] Custom log comparison {'succeeded' if ok else 'failed'}: {msg}")
            return ok, msg, content
        elif isinstance(result, bool):
            # 戻り値がブール値の場合は(ok, "", "")と解釈
            msg = "Custom log comparison " + ("succeeded" if result else "failed")
            print(f"[STEP3] {msg}")
            return result, msg, ""
        else:
            msg = f"Invalid return type from custom log comparator: {type(result)}"
            print(f"[STEP3][ERROR] {msg}")
            return False, msg, ""
    except Exception as e:
        msg = f"Error in custom log comparator: {str(e)}"
        print(f"[STEP3][ERROR] {msg}")
        return False, msg, ""


def parse_content_for_structured_data(content_str):
    """
    Content文字列から構造化データを抽出する
    検証項目とその判定結果を検出し、レポート用にフォーマットする
    
    Parameters:
        content_str (str): コンテンツ文字列
        
    Returns:
        dict: 構造化データ（キーと値のペア）
    """
    if not content_str:
        return {}
        
    result = {"values": [], "criteria": [], "type": ""}
    lines = content_str.split('\n')
    
    # 構造化データがJSON形式で埋め込まれている場合、抽出して処理
    structured_data_match = re.search(r'STRUCTURED_DATA=(\{.*\})', content_str)
    if structured_data_match:
        try:
            import json
            structured_data = json.loads(structured_data_match.group(1))
            
            # 成果物の差分分析データ
            if structured_data.get("analysis_type") == "differences":
                result["type"] = "artifact_differences"
                
                # ファイルサイズの変化
                size_data = structured_data.get("file_size", {})
                if isinstance(size_data, dict) and "old" in size_data and "new" in size_data:
                    old_size = size_data["old"]
                    new_size = size_data["new"]
                    diff_percent = size_data.get("diff_percent", 0)
                    
                    # ファイルサイズの検証項目
                    status = "normal"
                    if diff_percent < -10:  # サイズが10%以上削減
                        status = "good"
                    elif diff_percent > 20:  # サイズが20%以上増加
                        status = "warning"
                        
                    result["criteria"].append({
                        "name": "ファイルサイズの変化", 
                        "status": status,
                        "description": f"旧:{old_size} バイト → 新:{new_size} バイト ({diff_percent:.1f}% 変化)"
                    })
                    
                # 行数の変化
                line_data = structured_data.get("line_count", {})
                if isinstance(line_data, dict) and "old" in line_data and "new" in line_data:
                    old_lines = line_data["old"]
                    new_lines = line_data["new"]
                    diff_lines = line_data.get("diff", 0)
                    
                    result["criteria"].append({
                        "name": "行数の変化", 
                        "status": "normal",
                        "description": f"旧:{old_lines} 行 → 新:{new_lines} 行 ({diff_lines:+d} 行)"
                    })
                
                # 成功数の変化
                success_data = structured_data.get("success_count", {})
                if isinstance(success_data, dict) and "old" in success_data and "new" in success_data:
                    old_success = success_data["old"]
                    new_success = success_data["new"]
                    
                    status = "normal"
                    if new_success > old_success:
                        status = "good"
                    elif new_success < old_success:
                        status = "warning"
                        
                    result["criteria"].append({
                        "name": "成功数の変化", 
                        "status": status,
                        "description": f"旧:{old_success} 件 → 新:{new_success} 件"
                    })
                
                # 失敗/エラー数の変化
                failure_data = structured_data.get("failure_count", {})
                if isinstance(failure_data, dict) and "old" in failure_data and "new" in failure_data:
                    old_fail = failure_data["old"]
                    new_fail = failure_data["new"]
                    
                    status = "normal"
                    if new_fail < old_fail:
                        status = "good"
                    elif new_fail > old_fail:
                        status = "warning"
                    
                    if old_fail > 0 and new_fail == 0:
                        status = "excellent"
                        
                    result["criteria"].append({
                        "name": "エラー/失敗数の変化", 
                        "status": status,
                        "description": f"旧:{old_fail} 件 → 新:{new_fail} 件"
                    })
                    
                # 差分行数
                diff_lines = structured_data.get("diff_lines", 0)
                if diff_lines > 0:
                    result["criteria"].append({
                        "name": "差分行数", 
                        "status": "normal",
                        "description": f"{diff_lines} 行の差分あり"
                    })
                    
            # 成果物に差分がない場合
            elif structured_data.get("analysis_type") == "no_differences":
                result["type"] = "artifact_identical"
                
                result["criteria"].append({
                    "name": "成果物一致", 
                    "status": "good",
                    "description": "旧バージョンと新バージョンの成果物が完全に一致しています"
                })
                
                # 成功/エラー数の報告
                success_count = structured_data.get("success_count", 0)
                failure_count = structured_data.get("failure_count", 0)
                
                if success_count > 0:
                    result["criteria"].append({
                        "name": "成功件数", 
                        "status": "normal",
                        "description": f"成功: {success_count} 件"
                    })
                
                if failure_count == 0:
                    result["criteria"].append({
                        "name": "エラー/失敗数", 
                        "status": "excellent",
                        "description": "エラーや失敗はありません"
                    })
                elif failure_count > 0:
                    result["criteria"].append({
                        "name": "エラー/失敗数", 
                        "status": "warning",
                        "description": f"エラー/失敗: {failure_count} 件"
                    })
                    
            return result
        except Exception as e:
            # JSONデータの解析に失敗した場合は通常の処理を続行
            pass
    
    # パフォーマンス比較情報の抽出
    if "Performance differences:" in content_str:
        result["type"] = "performance_comparison"
        
        # パフォーマンス値を抽出
        old_version = None
        new_version = None
        improvement = None
        
        for line in lines:
            if "Old version:" in line:
                val = re.search(r'Old version:\s*([\d\.]+)', line)
                if val:
                    old_version = float(val.group(1))
                    result["values"].append({"name": "処理時間（旧バージョン）", "value": old_version, "unit": "seconds"})
            elif "New version:" in line:
                val = re.search(r'New version:\s*([\d\.]+)', line)
                if val:
                    new_version = float(val.group(1))
                    result["values"].append({"name": "処理時間（新バージョン）", "value": new_version, "unit": "seconds"})
            elif "Improvement:" in line:
                val = re.search(r'Improvement:\s*([\d\.]+)', line)
                if val:
                    improvement = float(val.group(1))
                    result["values"].append({"name": "改善率", "value": improvement, "unit": "%"})
        
        # 検証項目として追加
        if old_version is not None and new_version is not None:
            # 処理時間の検証項目
            result["criteria"].append({
                "name": "処理時間", 
                "status": "good" if new_version < old_version else "warning",
                "description": f"旧:{old_version:.1f}秒 → 新:{new_version:.1f}秒" + 
                              (f" ({improvement:.1f}%改善)" if improvement and improvement > 0 else "")
            })
            
            # パフォーマンス改善率の検証項目
            if improvement:
                if improvement > 20:
                    result["criteria"].append({
                        "name": "パフォーマンス改善率",
                        "status": "excellent",
                        "description": f"改善率: {improvement:.1f}% (20%超の大幅改善)"
                    })
                elif improvement > 10:
                    result["criteria"].append({
                        "name": "パフォーマンス改善率",
                        "status": "good",
                        "description": f"改善率: {improvement:.1f}% (10%超の改善)"
                    })
                elif improvement > 0:
                    result["criteria"].append({
                        "name": "パフォーマンス改善率",
                        "status": "normal",
                        "description": f"改善率: {improvement:.1f}% (10%未満の改善)"
                    })
                else:
                    result["criteria"].append({
                        "name": "パフォーマンス改善率",
                        "status": "warning",
                        "description": f"改善率: {improvement:.1f}% (パフォーマンス低下)"
                    })
    
    # エラー情報の抽出
    if "errors:" in content_str:
        result["type"] = "error_analysis"
        old_errors = []
        new_errors = []
        collecting_old = False
        collecting_new = False
        
        for line in lines:
            if "Old errors:" in line:
                collecting_old, collecting_new = True, False
            elif "New errors:" in line:
                collecting_old, collecting_new = False, True
            elif collecting_old and line.strip():
                old_errors.append(line.strip())
            elif collecting_new and line.strip():
                new_errors.append(line.strip())
        
        old_count = len(old_errors)
        new_count = len(new_errors)
        
        # 検証項目として追加
        result["criteria"].append({
            "name": "エラー数の変化",
            "status": "good" if new_count <= old_count else "warning",
            "description": f"旧バージョン: {old_count}件 → 新バージョン: {new_count}件"
        })
        
        if old_count > 0 and new_count > 0:
            if old_count > new_count:
                improvement = ((old_count - new_count) / old_count * 100)
                result["criteria"].append({
                    "name": "エラー数改善率",
                    "status": "good",
                    "description": f"エラー数が{improvement:.1f}%減少"
                })
            elif old_count < new_count:
                increase = ((new_count - old_count) / old_count * 100)
                result["criteria"].append({
                    "name": "エラー数増加率",
                    "status": "warning",
                    "description": f"エラー数が{increase:.1f}%増加"
                })
        
        if new_count == 0:
            result["criteria"].append({
                "name": "エラー解消",
                "status": "excellent",
                "description": "新バージョンでエラーが完全に解消されました"
            })
    
    # 処理時間などの抽出（個別ファイルの処理時間など）
    file_times = []
    for line in lines:
        # 処理時間パターンの抽出
        time_match = re.search(r'(.*処理時間.*?):\s*(\d+\.\d+)秒\s*→\s*(\d+\.\d+)秒', line)
        if time_match:
            key = time_match.group(1)
            old_time = float(time_match.group(2))
            new_time = float(time_match.group(3))
            improvement = ((old_time - new_time) / old_time * 100) if old_time > 0 else 0
            
            file_times.append({
                "name": key,
                "old_time": old_time,
                "new_time": new_time,
                "improvement": improvement
            })
            
    # 複数の処理時間がある場合、まとめて検証項目を追加
    if file_times:
        # 個別ファイル処理の平均改善率
        total_improvement = sum(item["improvement"] for item in file_times)
        avg_improvement = total_improvement / len(file_times) if file_times else 0
        
        status = "normal"
        if avg_improvement > 20:
            status = "excellent"
        elif avg_improvement > 10:
            status = "good"
        elif avg_improvement <= 0:
            status = "warning"
            
        result["criteria"].append({
            "name": "個別ファイル処理時間",
            "status": status,
            "description": f"平均改善率: {avg_improvement:.1f}% ({len(file_times)}ファイル)"
        })
    
    return result

def _format_values(values):
    """値データをフォーマットする"""
    if not values:
        return ""
        
    value_items = []
    for item in values:
        if "old_value" in item and "new_value" in item:
            value_items.append(f"{item['name']}: {item['old_value']} → {item['new_value']} ({item['improvement']:.1f}%)")
        elif "value" in item and "unit" in item:
            value_items.append(f"{item['name']}: {item['value']} {item['unit']}")
        elif "value" in item:
            value_items.append(f"{item['name']}: {item['value']}")
    return "\n".join(value_items)

def _format_criteria(criteria):
    """判定基準データをフォーマットする"""
    if not criteria:
        return ""
        
    criteria_items = []
    for item in criteria:
        criteria_items.append(f"{item['name']}: {item['status']} - {item['description']}")
    return "\n".join(criteria_items)


def write_full_report(tool, old, new, ok1, ok2, msg2, content2, ok3, msg3, content3, overall_status, overall_msg):
    """
    ツール実行結果をレポートとして出力する関数
    各ステージの検証項目ごとに1行ずつレポートに記録する
    """
    # レポートファイル名とヘッダー
    timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    filename = "report.csv"
    header = ["DD/HH:MM:SS","Tool","Version_old","Version_new","Stage","検証項目","結果","詳細"]
    write_header = (not os.path.exists(filename)) or os.path.getsize(filename) == 0
    
    # 値データの抽出と整形
    artifact_data = parse_content_for_structured_data(content2)
    log_data = parse_content_for_structured_data(content3)
    
    # レポート行を作成
    rows = []
    
    # 動作ステージ
    rows.append((timestamp, tool, old, new, "動作", "実行完了", "Success" if ok1 else "Failure", ""))
    
    # 成果物ステージの検証項目をレポート行に追加
    if artifact_data and "criteria" in artifact_data:
        for item in artifact_data["criteria"]:
            item_name = item["name"]
            status = item["status"]
            description = item["description"]
            
            rows.append((
                timestamp, tool, old, new, 
                "成果物", 
                item_name,  # 検証項目
                status,     # 結果
                description # 詳細
            ))
    else:
        # 成果物ステージの基本情報
        rows.append((timestamp, tool, old, new, "成果物", "比較結果", "Success" if ok2 else "Failure", msg2))
        
    # ログステージの検証項目をレポート行に追加
    if log_data and "criteria" in log_data:
        for item in log_data["criteria"]:
            item_name = item["name"]
            status = item["status"]
            description = item["description"]
            
            rows.append((
                timestamp, tool, old, new, 
                "ログ", 
                item_name,  # 検証項目
                status,     # 結果
                description # 詳細
            ))
    else:
        # ログステージの基本情報
        rows.append((timestamp, tool, old, new, "ログ", "比較結果", "Success" if ok3 else "Failure", msg3))
    
    # 総括情報
    rows.append((timestamp, tool, old, new, "総括", "全体結果", overall_status, overall_msg))
    
    # CSVファイルに書き込み
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(header)
            for row in rows:
                writer.writerow(row)
        print(f"[STEP4] CSV report updated: {filename}")
        
        # HTMLレポート生成
        html_file = "report.html"
        write_html_report(filename, html_file)
        print(f"[STEP5] HTML report updated: {html_file}")
    except Exception as e:
        print(f"[ERROR] Failed to write report: {str(e)}")


def main():
    # メインパーサーの設定
    parser = argparse.ArgumentParser(description="アップデートツール動作確認スクリプト")
    
    # 基本オプション
    parser.add_argument('--tools-dir', default='Apps', help='ツール実行ファイルが置かれたディレクトリ（例: ICC2, Primetime など）')
    parser.add_argument('--inputs-dir', default='inputs', help='入力ファイルが置かれたディレクトリ')
    parser.add_argument('--input', '-i', action='append', help='入力ファイルを指定（複数指定可能）')
    parser.add_argument('--input-pattern', help='入力ファイルをパターンで指定（例: "*.txt"）')
    parser.add_argument('--demo', action='store_true', help='デモモードで動作（既定値使用）')
    parser.add_argument('--clean', action='store_true', help='既存のレポート（CSV/HTML）をクリアして開始')
    parser.add_argument('tool_name', nargs='?', help='ツール名を指定')
    parser.add_argument('version_old', nargs='?', help='旧バージョンを指定')
    parser.add_argument('version_new', nargs='?', help='新バージョンを指定')
    args = parser.parse_args()
    

    # レポートクリアオプション
    if args.clean:
        for f in ('report.csv', 'report.html'):
            if os.path.exists(f):
                os.remove(f)
                print(f"[CLEAN] Removed {f}")
    # ツール配置ディレクトリをグローバルに設定
    global TOOLS_DIR, INPUTS_DIR
    TOOLS_DIR = args.tools_dir
    INPUTS_DIR = args.inputs_dir

    # 入力ファイル一覧を準備
    input_files = []
    if args.input:
        input_files.extend(args.input)
    
    if args.input_pattern:
        pattern_path = os.path.join(INPUTS_DIR, args.input_pattern)
        matched_files = glob.glob(pattern_path)
        if not matched_files:
            print(f"[WARNING] No files matched pattern: {args.input_pattern}")
        input_files.extend(matched_files)
    
    # 指定したinputs_dirにファイルがない場合はディレクトリを作成
    if not os.path.exists(INPUTS_DIR):
        os.makedirs(INPUTS_DIR)
        print(f"[INFO] Created inputs directory: {INPUTS_DIR}")
    
    # デモモード設定
    if args.demo:
        args.tool_name = 'DemoTool'
        args.version_old = '1.0.0'
        args.version_new = '2.0.0'
        
        # デモ用入力ファイルがない場合はサンプル作成
        if not input_files:
            demo_input = os.path.join(INPUTS_DIR, "sample.txt")
            with open(demo_input, "w", encoding="utf-8") as f:
                f.write("これはサンプル入力ファイルです。\n各バージョンのツールで処理されます。\n")
            input_files.append(demo_input)
            print(f"[DEMO] Created sample input file: {demo_input}")
        
        print(f'[DEMO] DemoTool 1.0.0 -> 2.0.0 with {len(input_files)} input file(s)')
    else:
        # 必須引数チェック
        if not (args.tool_name and args.version_old and args.version_new):
            parser.print_usage()
            sys.exit(1)

    # ログ出力用ファイルとTeeをセットアップ
    now = datetime.datetime.now()
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{args.tool_name}_{args.version_old}_{args.version_new}_{timestamp_str}.log")
    f_log = open(log_file, 'w', encoding='utf-8')
    tee = Tee(sys.stdout, f_log)
    sys.stdout = tee
    sys.stderr = tee
    
    # 各ステージ結果を初期化
    ok1 = False
    artifact_ok = False
    artifact_msg = ""
    artifact_content = ""
    log_ok = False
    log_msg = ""
    log_content = ""
    
    try:
        # 入力ファイルの情報を表示
        if input_files:
            print(f"[INFO] Processing {len(input_files)} input file(s):")
            for i, f in enumerate(input_files, 1):
                print(f"  {i}. {os.path.basename(f)}")
        else:
            print("[INFO] No input files specified")
            
        ok1 = run_tool(args.tool_name, args.version_old, args.version_new, input_files)
        artifact_ok, artifact_msg, artifact_content = compare_artifacts(args.tool_name, args.version_old, args.version_new)
        log_ok, log_msg, log_content = compare_logs(args.tool_name, args.version_old, args.version_new)
        
        if ok1 and artifact_ok and log_ok:
            status = "Success"
            message = ""
        else:
            status = "Failure"
            message = "比較に失敗しました"
    except Exception as e:
        status = "Error"
        message = str(e)
        import traceback
        traceback.print_exc(file=sys.stderr)

    write_full_report(
        args.tool_name,
        args.version_old,
        args.version_new,
        ok1,
        artifact_ok,
        artifact_msg,
        artifact_content,
        log_ok,
        log_msg,
        log_content,
        status,
        message
    )
    
    # ログファイルをクローズ
    f_log.close()
    
    if status != "Success":
        sys.exit(1)

if __name__ == "__main__":
    main()
