#!/usr/bin/env python3
"""
SampleToolのカスタム比較関数

このファイルは、SampleToolの出力を比較するためのカスタム関数を提供します。
"""
import os
import json
import difflib
import re
from core.comparator import BaseComparator


class SampletoolComparator(BaseComparator):
    """SampleToolの比較クラス"""
    
    def setup_tool_configs(self):
        """ツール固有の設定"""
        self.config = {
            'execute_command': 'python SampleTool.py',
            'old_artifact_pattern': f'SampleTool_{self.old_version}.txt',
            'new_artifact_pattern': f'SampleTool_{self.new_version}.txt',
            'input_files': ['sample.txt'],
            'parameters': ['-o', '{output_file}']
        }
    
    def _setup(self):
        """実行前のセットアップ"""
        # 成果物ディレクトリの作成
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 旧バージョン用の成果物ファイル名
        self.old_artifact = os.path.join(self.output_dir, f"SampleTool_{self.old_version}.txt")
        
        # 新バージョン用の成果物ファイル名
        self.new_artifact = os.path.join(self.output_dir, f"SampleTool_{self.new_version}.txt")
    
    def _run_old_version(self):
        """旧バージョンのツール実行"""
        old_tool_path = os.path.join('Apps', 'SampleTool', self.old_version, 'SampleTool.py')
        input_file = os.path.join(self.input_dir, 'sample.txt')
        
        if not os.path.exists(old_tool_path):
            print(f"[ERROR] 旧バージョンのツールが見つかりません: {old_tool_path}")
            return None
        
        if not os.path.exists(input_file):
            print(f"[ERROR] 入力ファイルが見つかりません: {input_file}")
            return None
        
        # コマンド実行
        command = f'python "{old_tool_path}" "{input_file}" -o "{self.old_artifact}"'
        print(f"[INFO] 旧バージョン実行コマンド: {command}")
        
        import subprocess
        proc = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate()
        
        if proc.returncode != 0:
            print(f"[ERROR] 旧バージョンの実行に失敗しました")
            print(f"[ERROR] 標準出力: {stdout}")
            print(f"[ERROR] 標準エラー: {stderr}")
            return None
        
        return stdout
    
    def _run_new_version(self):
        """新バージョンのツール実行"""
        new_tool_path = os.path.join('Apps', 'SampleTool', self.new_version, 'SampleTool.py')
        input_file = os.path.join(self.input_dir, 'sample.txt')
        
        if not os.path.exists(new_tool_path):
            print(f"[ERROR] 新バージョンのツールが見つかりません: {new_tool_path}")
            return None
        
        if not os.path.exists(input_file):
            print(f"[ERROR] 入力ファイルが見つかりません: {input_file}")
            return None
        
        # コマンド実行
        command = f'python "{new_tool_path}" "{input_file}" -o "{self.new_artifact}"'
        print(f"[INFO] 新バージョン実行コマンド: {command}")
        
        import subprocess
        proc = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate()
        
        if proc.returncode != 0:
            print(f"[ERROR] 新バージョンの実行に失敗しました")
            print(f"[ERROR] 標準出力: {stdout}")
            print(f"[ERROR] 標準エラー: {stderr}")
            return None
        
        return stdout
    
    def _compare(self, old_result, new_result):
        """
        比較処理
        
        Parameters:
            old_result (str): 旧バージョンの標準出力
            new_result (str): 新バージョンの標準出力
            
        Returns:
            dict: 比較結果
        """
        result = {
            'tool_name': self.tool_name,
            'old_version': self.old_version,
            'new_version': self.new_version,
            'status': 'Error',
            'detail': '',
        }
        
        # 標準出力の確認
        if old_result is None or new_result is None:
            result['detail'] = 'いずれかのバージョンの実行に失敗しました'
            return result
        
        # 成果物の確認
        if not os.path.exists(self.old_artifact):
            result['detail'] = f'旧バージョンの成果物が作成されていません: {self.old_artifact}'
            return result
        
        if not os.path.exists(self.new_artifact):
            result['detail'] = f'新バージョンの成果物が作成されていません: {self.new_artifact}'
            return result
        
        # 成果物の内容を読み込み
        try:
            with open(self.old_artifact, 'r', encoding='cp932', errors='replace') as f:
                old_content = f.read()
            
            with open(self.new_artifact, 'r', encoding='cp932', errors='replace') as f:
                new_content = f.read()
                
            # SampleToolの処理結果を解析
            old_stats = self._parse_sampletool_output(old_content)
            new_stats = self._parse_sampletool_output(new_content)
            
            # 行数のカウント
            old_lines = old_content.count('\n') + 1 if old_content else 0
            new_lines = new_content.count('\n') + 1 if new_content else 0
            
            # ファイルサイズの比較
            old_size = os.path.getsize(self.old_artifact)
            new_size = os.path.getsize(self.new_artifact)
            
            # 成果物のサイズが小さい場合は同一か簡単に比較
            if old_size < 1000 and new_size < 1000 and old_content == new_content:
                result['status'] = 'Success'
                result['detail'] = '旧バージョンと新バージョンの成果物は完全に一致しています'
                return result
            
            # 比較結果を作成
            # ファイルサイズの変化率計算
            size_change = ((new_size - old_size) / old_size * 100) if old_size > 0 else float('inf')
            
            # 差分行数を計算
            diff = list(difflib.unified_diff(
                old_content.splitlines(),
                new_content.splitlines(),
                n=1  # コンテキスト行数
            ))
            diff_lines = len(diff)
            
            # 成功/失敗カウント
            old_success = old_stats.get('file_count', 0)
            new_success = new_stats.get('file_count', 0)
            
            # 構造化データとして埋め込み
            structured_data = {
                'analysis_type': 'differences' if old_content != new_content else 'no_differences',
                'file_size': {
                    'old': old_size,
                    'new': new_size,
                    'diff': new_size - old_size,
                    'diff_percent': size_change
                },
                'line_count': {
                    'old': old_lines,
                    'new': new_lines,
                    'diff': new_lines - old_lines
                },
                'success_count': {
                    'old': old_success,
                    'new': new_success
                },
                'failure_count': {
                    'old': 0,
                    'new': 0
                },
                'diff_lines': diff_lines
            }
            
            # 成功判定
            if new_success >= old_success:
                result['status'] = 'Success'
            else:
                result['status'] = 'Failed'
            
            # 詳細メッセージを構築
            detail_parts = []
            detail_parts.append(f"STRUCTURED_DATA={structured_data}")
            detail_parts.append(f"ファイルサイズ: 旧={old_size} バイト, 新={new_size} バイト ({size_change:.1f}% 変化)")
            detail_parts.append(f"行数: 旧={old_lines} 行, 新={new_lines} 行 ({new_lines - old_lines:+d} 行)")
            detail_parts.append(f"処理ファイル数: 旧={old_success} 件, 新={new_success} 件")
            detail_parts.append(f"差分行数: {diff_lines} 行")
            
            result['detail'] = '\n'.join(detail_parts)
            return result
            
        except Exception as e:
            print(f"[ERROR] 比較中にエラーが発生しました: {str(e)}")
            result['detail'] = f"比較処理中にエラーが発生しました: {str(e)}"
            return result
    
    def _parse_sampletool_output(self, content):
        """SampleToolの出力から統計情報を抽出する"""
        stats = {
            'file_count': 0,
            'line_count': 0,
            'char_count': 0,
            'word_count': 0
        }
        
        # 処理されたファイル数をカウント
        file_matches = content.count("の処理結果")
        stats['file_count'] = file_matches
        
        # 行数、文字数、単語数を抽出
        line_matches = re.findall(r'行数: (\d+)', content)
        char_matches = re.findall(r'文字数: (\d+)', content)
        word_matches = re.findall(r'単語数: (\d+)', content)
        
        if line_matches:
            stats['line_count'] = sum(map(int, line_matches))
        if char_matches:
            stats['char_count'] = sum(map(int, char_matches))
        if word_matches:
            stats['word_count'] = sum(map(int, word_matches))
            
        return stats


# 従来の関数インターフェースとの互換性を維持
def compare_artifacts(old_file, new_file):
    """
    SampleToolの成果物を比較する関数
    
    Parameters:
        old_file (str): 旧バージョンの成果物ファイルパス
        new_file (str): 新バージョンの成果物ファイルパス
        
    Returns:
        tuple: (比較結果（True: 正常、False: 異常）, 差分メッセージ, 差分の詳細コンテンツ)
    """
    print(f"[CUSTOM] SampleToolの成果物比較を実行します")
    print(f"[CUSTOM] 旧ファイル: {old_file}")
    print(f"[CUSTOM] 新ファイル: {new_file}")
    
    try:
        with open(old_file, encoding='cp932') as f1, open(new_file, encoding='cp932') as f2:
            old_content = f1.read()
            new_content = f2.read()
        
        # SampleToolの処理結果を解析
        old_stats = parse_sampletool_output(old_content)
        new_stats = parse_sampletool_output(new_content)
        
        # 各指標の比較
        print(f"[CUSTOM] 旧バージョン統計: {old_stats}")
        print(f"[CUSTOM] 新バージョン統計: {new_stats}")
        
        # 新バージョンでは単語頻度解析が追加されているか確認
        has_word_freq = "単語頻度" in new_content
        if has_word_freq:
            print(f"[CUSTOM] 新バージョンで単語頻度解析機能が確認できました")
        
        # すべてのファイルが処理されているか確認
        if old_stats.get('file_count', 0) != new_stats.get('file_count', 0):
            print(f"[CUSTOM][WARNING] 処理ファイル数が異なります: {old_stats.get('file_count', 0)} -> {new_stats.get('file_count', 0)}")
        
        # 標準の比較関数を呼び出す
        # 注意: モジュールインポートを避けるため、オーバーライドした関数からはグローバルの比較関数を直接呼び出せません
        # そのため、ここでは元のカスタム比較ロジックを使用し、結果を構造化データとして返します
        import json
        
        # 差分分析の結果を構造化データとして生成
        analysis_data = {
            "analysis_type": "differences" if old_content != new_content else "no_differences",
            "file_size": {
                "old": len(old_content),
                "new": len(new_content),
                "diff_percent": (len(new_content) - len(old_content)) / max(1, len(old_content)) * 100
            },
            "line_count": {
                "old": old_stats.get('line_count', 0),
                "new": new_stats.get('line_count', 0),
                "diff": new_stats.get('line_count', 0) - old_stats.get('line_count', 0)
            },
            "success_count": {
                "old": old_stats.get('file_count', 0),
                "new": new_stats.get('file_count', 0)
            },
            "failure_count": {
                "old": 0,
                "new": 0
            },
            "diff_lines": 0
        }
        
        # 差分の詳細
        import difflib
        diff = list(difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            n=1  # コンテキスト行数
        ))
        analysis_data["diff_lines"] = len(diff)
        
        diff_content = f"STRUCTURED_DATA={json.dumps(analysis_data)}\n\n" + "\n".join(diff[:100])  # 最大100行に制限
        diff_message = f"SampleTool成果物比較: " + (
            f"差分あり ({analysis_data['diff_lines']}行)" if analysis_data["diff_lines"] > 0
            else "完全一致"
        )
        
        # カスタム比較の結果
        return True, diff_message, diff_content
    except Exception as e:
        print(f"[CUSTOM][ERROR] 比較中にエラーが発生しました: {str(e)}")
        error_message = f"比較エラー: {str(e)}"
        return False, error_message, f"比較処理中にエラーが発生しました: {str(e)}"


def compare_logs(old_log, new_log):
    """
    SampleToolのログを比較する関数
    
    Parameters:
        old_log (str): 旧バージョンのログファイルパス
        new_log (str): 新バージョンのログファイルパス
        
    Returns:
        tuple: (比較結果（True: 正常、False: 異常）, 差分メッセージ, 差分の詳細コンテンツ)
    """
    print(f"[CUSTOM] SampleToolのログ比較を実行します")
    print(f"[CUSTOM] 旧ログ: {old_log}")
    print(f"[CUSTOM] 新ログ: {new_log}")
    
    try:
        with open(old_log, encoding='utf-8') as f1, open(new_log, encoding='utf-8') as f2:
            old_content = f1.read()
            new_content = f2.read()
        
        # 処理時間を比較
        old_time = extract_processing_time(old_content)
        new_time = extract_processing_time(new_content)
        
        time_message = ""
        if old_time and new_time:
            if new_time < old_time:
                time_message = f"処理時間が改善: {old_time:.2f}秒 → {new_time:.2f}秒"
                print(f"[CUSTOM] 新バージョンの処理時間が改善されています: {old_time:.2f}秒 -> {new_time:.2f}秒")
            else:
                time_message = f"処理時間が低下: {old_time:.2f}秒 → {new_time:.2f}秒"
                print(f"[CUSTOM] 新バージョンの処理時間が低下しています: {old_time:.2f}秒 -> {new_time:.2f}秒")
        
        # エラーの検出
        old_errors = count_errors(old_content)
        new_errors = count_errors(new_content)
        
        print(f"[CUSTOM] エラー数: {old_errors} -> {new_errors}")
        
        # 構造化データの生成
        import json
        import difflib
        
        # ログ分析の結果を構造化データとして生成
        analysis_data = {
            "analysis_type": "log_comparison",
            "processing_time": {
                "old": old_time,
                "new": new_time,
                "diff_percent": ((old_time - new_time) / old_time * 100) if old_time and new_time and old_time > 0 else 0
            },
            "errors": {
                "old": old_errors,
                "new": new_errors,
                "diff": new_errors - old_errors
            }
        }
        
        # 差分の詳細
        diff = list(difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            n=1  # コンテキスト行数
        ))
        analysis_data["diff_lines"] = len(diff)
        
        diff_content = f"STRUCTURED_DATA={json.dumps(analysis_data)}\n\n" + "\n".join(diff[:100])  # 最大100行に制限
        
        # 差分メッセージの生成
        messages = []
        if time_message:
            messages.append(time_message)
        if old_errors != new_errors:
            messages.append(f"エラー数: {old_errors} → {new_errors}")
        if not messages:
            messages.append(f"ログ比較: {analysis_data['diff_lines']}行の差分あり")
            
        diff_message = ", ".join(messages)
        
        # 結果を返す
        return True, diff_message, diff_content
    except Exception as e:
        print(f"[CUSTOM][ERROR] ログ比較中にエラーが発生しました: {str(e)}")
        error_message = f"ログ比較エラー: {str(e)}"
        return False, error_message, f"ログ比較処理中にエラーが発生しました: {str(e)}"


# ヘルパー関数

def parse_sampletool_output(content):
    """SampleToolの出力から統計情報を抽出する"""
    stats = {
        'file_count': 0,
        'line_count': 0,
        'char_count': 0,
        'word_count': 0
    }
    
    # 処理されたファイル数をカウント
    file_matches = content.count("の処理結果")
    stats['file_count'] = file_matches
    
    # 行数、文字数、単語数を抽出
    import re
    line_matches = re.findall(r'行数: (\d+)', content)
    char_matches = re.findall(r'文字数: (\d+)', content)
    word_matches = re.findall(r'単語数: (\d+)', content)
    
    if line_matches:
        stats['line_count'] = sum(map(int, line_matches))
    if char_matches:
        stats['char_count'] = sum(map(int, char_matches))
    if word_matches:
        stats['word_count'] = sum(map(int, word_matches))
        
    return stats


def extract_processing_time(log_content):
    """ログから処理時間を抽出する"""
    import re
    time_matches = re.findall(r'処理時間: ([\d\.]+)秒', log_content)
    if time_matches:
        return float(time_matches[0])
    return None


def count_errors(log_content):
    """ログ内のエラー数を数える"""
    import re
    error_count = len(re.findall(r'\[ERROR\]', log_content))
    return error_count
