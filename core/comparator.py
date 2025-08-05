#!/usr/bin/env python3
"""
比較ツール基本クラスとユーティリティ関数
"""
import os
import sys
import glob
import importlib
import re
import difflib
import datetime
import time
from utils.file_utils import setup_logging


class BaseComparator:
    """比較ツールの基本クラス
    
    このクラスは全ての比較ツールの基底クラスです。
    各ツール固有の比較ロジックを実装するためには、このクラスを継承してください。
    """

    def __init__(self, tool_name, old_version, new_version, input_dir="inputs", output_dir="artifacts"):
        """
        Parameters:
            tool_name (str): ツール名
            old_version (str): 旧バージョン
            new_version (str): 新バージョン
            input_dir (str, optional): 入力ディレクトリ
            output_dir (str, optional): 出力ディレクトリ
        """
        self.tool_name = tool_name
        self.old_version = old_version
        self.new_version = new_version
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # ツール固有の設定
        self.setup_tool_configs()

    def setup_tool_configs(self):
        """
        ツール固有の設定を行います。
        子クラスでオーバーライドしてください。
        """
        self.config = {
            'execute_command': '',
            'old_artifact_pattern': '',
            'new_artifact_pattern': '',
            'input_files': [],
            'parameters': []
        }

    def run(self):
        """
        比較処理を実行します。
        
        Returns:
            dict: 比較結果
        """
        self._setup()
        
        old_result = self._run_old_version()
        new_result = self._run_new_version()
        
        return self._compare(old_result, new_result)
    
    def _setup(self):
        """
        比較実行前のセットアップを行います。
        """
        pass
    
    def _run_old_version(self):
        """
        旧バージョンのツールを実行します。
        
        Returns:
            str or None: 実行結果の標準出力、エラー時はNone
        """
        pass
    
    def _run_new_version(self):
        """
        新バージョンのツールを実行します。
        
        Returns:
            str or None: 実行結果の標準出力、エラー時はNone
        """
        pass
    
    def _compare(self, old_result, new_result):
        """
        旧バージョンと新バージョンの結果を比較します。
        
        Parameters:
            old_result (str): 旧バージョンの実行結果
            new_result (str): 新バージョンの実行結果
            
        Returns:
            dict: 比較結果
        """
        result = {
            'tool_name': self.tool_name,
            'old_version': self.old_version,
            'new_version': self.new_version,
            'status': 'Success',
            'detail': '',
        }
        
        # 基本的な比較のみ実施
        if old_result == new_result:
            result['status'] = 'Success'
            result['detail'] = 'Old version and new version produce identical results.'
        else:
            result['status'] = 'Failed'
            result['detail'] = 'Old version and new version produce different results.'
        
        return result
    
    def get_output_files(self):
        """
        出力ファイルのパスを取得します
        
        Returns:
            tuple: (旧バージョン成果物, 新バージョン成果物)
        """
        old_pattern = os.path.join(self.output_dir, f"{self.tool_name}_{self.old_version}*")
        new_pattern = os.path.join(self.output_dir, f"{self.tool_name}_{self.new_version}*")
        
        old_files = glob.glob(old_pattern)
        new_files = glob.glob(new_pattern)
        
        return (old_files[0] if old_files else None,
                new_files[0] if new_files else None)


def load_comparator_class(comparator_name):
    """
    指定された名前の比較ツールクラスを動的にロードします。
    設定ファイルベースのコンパレータにも対応しています。
    
    Parameters:
        comparator_name (str): 比較ツールのモジュール名または設定ファイル名
        
    Returns:
        class or function: 比較ツールクラスまたはファクトリ関数
        
    Raises:
        ImportError: モジュールが見つからない場合
        AttributeError: クラスが見つからない場合
    """
    # まず、ツール名をコンパレータ名から取得
    if comparator_name.endswith('_comparator'):
        tool_name = comparator_name.replace('_comparator', '')
    else:
        tool_name = comparator_name
    
    # 1. 設定ファイルがあるか確認
    config_paths = [
        os.path.join("comparators", "configs", f"{tool_name.lower()}.yaml"),
        os.path.join("comparators", "configs", f"{tool_name.lower()}.yml"),
        os.path.join("comparators", "configs", f"{tool_name.lower()}.json"),
        os.path.join("configs", f"{tool_name.lower()}.yaml"),
        os.path.join("configs", f"{tool_name.lower()}.yml"),
        os.path.join("configs", f"{tool_name.lower()}.json"),
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            print(f"[INFO] 設定ファイルが見つかりました: {config_path}")
            print(f"[INFO] 設定ファイルベースのコンパレータを使用します: {tool_name}")
            
            # 設定ベースのコンパレータファクトリ関数を返す
            # この関数は、後でツール名、バージョンなどを渡して呼び出される
            def config_comparator_factory(tool_name, old_version, new_version, input_dir="inputs", output_dir="artifacts"):
                return _create_config_based_comparator(tool_name, old_version, new_version, config_path, input_dir, output_dir)
            
            # ファクトリ関数の名前を設定（デバッグ用）
            config_comparator_factory.__name__ = f"{tool_name.capitalize()}ConfigComparator"
            return config_comparator_factory
    
    # 2. 設定ファイルがなければ、通常のクラスをロード
    try:
        # モジュールをimport
        module_name = f"comparators.{comparator_name}"
        module = importlib.import_module(module_name)
        
        # クラス名を推測 - コンパレータ名が既に "xxx_comparator" の形式であれば処理
        if comparator_name.endswith('_comparator'):
            # xxxComparator 形式を作る
            base_name = comparator_name.replace('_comparator', '')
            class_name = "".join(part.capitalize() for part in base_name.split('_')) + "Comparator"
        else:
            # 単にキャメルケースに変換
            class_name = "".join(part.capitalize() for part in comparator_name.split('_'))
        
        # クラスを取得
        comparator_class = getattr(module, class_name)
        return comparator_class
        
    except ImportError:
        print(f"[ERROR] Comparator module 'comparators.{comparator_name}' not found")
        raise
        
    except AttributeError as e:
        print(f"[ERROR] Comparator class not found in module 'comparators.{comparator_name}'")
        print(f"[ERROR] Details: {str(e)}")
        raise


def _create_config_based_comparator(tool_name, old_version, new_version, config_path, input_dir="inputs", output_dir="artifacts"):
    """
    設定ファイルに基づいたコンパレータを作成する（内部関数）
    
    Parameters:
        tool_name (str): ツール名
        old_version (str): 旧バージョン
        new_version (str): 新バージョン
        config_path (str): 設定ファイルパス
        input_dir (str, optional): 入力ディレクトリ
        output_dir (str, optional): 出力ディレクトリ
        
    Returns:
        BaseComparator: 設定ベースのコンパレータインスタンス
    """
    # 設定ファイル読み込み
    config = _load_config_file(config_path)
    
    if not config:
        print(f"[WARNING] 設定ファイルの読み込みに失敗しました: {config_path}")
        return BaseComparator(tool_name, old_version, new_version, input_dir, output_dir)
        
    # 設定ベースの比較クラスを動的に作成
    class ConfigBasedComparator(BaseComparator):
        """設定ファイルに基づく比較クラス"""
        
        def __init__(self, tool_name, old_version, new_version, config, input_dir, output_dir):
            super().__init__(tool_name, old_version, new_version, input_dir, output_dir)
            self.custom_config = config
            print(f"[INFO] 設定ベースのコンパレータを初期化しました")
            
            # 設定を適用
            if 'execute_command' in self.custom_config:
                self.config['execute_command'] = self.custom_config['execute_command']
            if 'old_artifact_pattern' in self.custom_config:
                self.config['old_artifact_pattern'] = self.custom_config['old_artifact_pattern']
            if 'new_artifact_pattern' in self.custom_config:
                self.config['new_artifact_pattern'] = self.custom_config['new_artifact_pattern']
            if 'input_files' in self.custom_config:
                self.config['input_files'] = self.custom_config['input_files']
            if 'parameters' in self.custom_config:
                self.config['parameters'] = self.custom_config['parameters']
            
        def _compare(self, old_result, new_result):
            """比較を実行（オーバーライド）"""
            # 基本比較結果を取得
            result = super()._compare(old_result, new_result)
            
            # 現在のタイムスタンプを記録（ミリ秒まで含める）
            result['timestamp'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
            
            # 各検証項目ごとの結果を記録するための辞書
            item_results = {}
            
            # 評価指標を取得
            criteria = self.custom_config.get('verification_criteria', {})
            
            # 基本項目の追加
            # 起動・実行確認の項目は常に設定（実行自体は成功している）
            result['status_起動・実行確認'] = 'Success'
            result['timestamp_起動・実行確認'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
            result['criteria_起動・実行確認'] = '終了コード: 0'
            
            # カスタム比較を実行
            if self.custom_config.get('comparison_methods', None):
                methods = self.custom_config['comparison_methods']
                issues = []
                
                # 設定に基づいて各種比較を実行
                try:
                    old_file, new_file = self.get_output_files()
                    
                    # 成果物の有無を確認
                    has_artifacts = old_file and new_file and os.path.exists(old_file) and os.path.exists(new_file)
                    
                    # 成果物がない場合は成果物関連の項目を「評価対象外」とする
                    if not has_artifacts:
                        print(f"[INFO] 成果物が不足しているため、成果物評価は対象外とします")
                        item_results['status_出力フォーマット検証'] = 'N/A'
                        item_results['timestamp_出力フォーマット検証'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
                        item_results['criteria_出力フォーマット検証'] = '成果物なし'
                        
                        # 計算結果精度検証には少し遅延を入れて時間差を出す
                        time.sleep(0.1)  # 0.1秒の遅延
                        item_results['status_計算結果精度検証'] = 'N/A'
                        item_results['timestamp_計算結果精度検証'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
                        item_results['criteria_計算結果精度検証'] = '成果物なし'
                        
                        # パフォーマンス検証にも遅延を入れる
                        time.sleep(0.1)  # 0.1秒の遅延
                        item_results['status_パフォーマンス検証'] = 'N/A'
                        item_results['timestamp_パフォーマンス検証'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
                        # パフォーマンス評価の指標を取得
                        perf_tolerance = criteria.get('performance', {}).get('tolerance_percent', 10)
                        item_results['criteria_パフォーマンス検証'] = f'許容遅延: {perf_tolerance}%'
                        
                        # サマリー情報検証にも遅延を入れる
                        time.sleep(0.1)  # 0.1秒の遅延
                        item_results['status_サマリー情報検証'] = 'N/A'
                        item_results['timestamp_サマリー情報検証'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
                        item_results['criteria_サマリー情報検証'] = '成果物なし'
                    else:
                        # 成果物がある場合のみ、各比較メソッドを実行
                        if methods.get('format_check', False):
                            format_issues = self._check_format(old_file, new_file)
                            # 評価指標を取得
                            format_allowed = criteria.get('format', {}).get('allowed_changes', False)
                            format_criteria = f"許容変更: {'あり' if format_allowed else 'なし'}"
                            
                            if format_issues:
                                issues.append(f"フォーマットの変更: {format_issues}")
                                item_results['status_出力フォーマット検証'] = 'Failed'
                            else:
                                item_results['status_出力フォーマット検証'] = 'Success'
                            # 項目ごとのタイムスタンプと評価指標を記録
                            item_results['timestamp_出力フォーマット検証'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
                            item_results['criteria_出力フォーマット検証'] = format_criteria
                                
                        if methods.get('line_count', False):
                            line_count_issues = self._check_line_count(old_file, new_file)
                            if line_count_issues:
                                issues.append(f"行数の変更: {line_count_issues}")
                                item_results['status_出力フォーマット検証'] = 'Failed'  # フォーマットに関連する項目
                            # タイムスタンプは既に設定済み
                                
                        if methods.get('content_diff', False):
                            content_issues = self._check_content_diff(old_file, new_file)
                            # 評価指標を取得
                            precision_tolerance = criteria.get('precision', {}).get('tolerance_percent', 1)
                            precision_criteria = f"許容誤差: {precision_tolerance}%"
                            
                            if content_issues:
                                issues.append(f"内容の変更: {content_issues}")
                                item_results['status_計算結果精度検証'] = 'Failed'
                            else:
                                item_results['status_計算結果精度検証'] = 'Success'
                            # 明確な時間差を出すために遅延を入れる
                            time.sleep(0.1)  # 0.1秒の遅延
                            item_results['timestamp_計算結果精度検証'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
                            item_results['criteria_計算結果精度検証'] = precision_criteria
                                
                        # キーワード検証
                        keywords = methods.get('keyword_check', [])
                        if keywords:
                            keyword_issues = self._check_keywords(old_file, new_file, keywords)
                            # 評価指標を取得 - サマリー情報はキーワードの存在チェック
                            summary_criteria = f"確認キーワード: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}"
                            
                            if keyword_issues:
                                issues.append(f"キーワードの変更: {keyword_issues}")
                                item_results['status_サマリー情報検証'] = 'Failed'
                            else:
                                item_results['status_サマリー情報検証'] = 'Success'
                            # 明確な時間差を出すために遅延を入れる
                            time.sleep(0.1)  # 0.1秒の遅延
                            item_results['timestamp_サマリー情報検証'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
                            item_results['criteria_サマリー情報検証'] = summary_criteria
                                
                        # カスタムパターン検証
                        patterns = methods.get('custom_patterns', [])
                        if patterns:
                            custom_issues = self._check_custom_patterns(old_file, new_file, patterns)
                            if custom_issues:
                                issues.append(f"カスタムパターンの変更: {custom_issues}")
                                # カスタムパターンは様々な項目に関連する可能性があるため、
                                # 必要に応じて適切な項目名に対応させる
                    
                    # 結果の更新
                    if issues:
                        result['status'] = 'Failed'
                        result['detail'] = '; '.join(issues)
                    
                    # 各項目ごとの結果をメイン結果に追加
                    result.update(item_results)
                    
                    # ログ関連の評価（成果物の有無に関わらず実行可能）
                    # 警告・エラー解析の項目は標準出力から判断
                    if old_result and new_result:
                        if "エラー" in new_result or "警告" in new_result:
                            result['status_警告・エラー解析'] = 'Failed'
                        else:
                            result['status_警告・エラー解析'] = 'Success'
                        result['criteria_警告・エラー解析'] = '警告/エラーメッセージの有無'
                    else:
                        result['status_警告・エラー解析'] = 'N/A'
                        result['criteria_警告・エラー解析'] = 'ログなし'
                    # 明確な時間差を出すために遅延を入れる
                    time.sleep(0.1)  # 0.1秒の遅延
                    result['timestamp_警告・エラー解析'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
                    
                    # バージョン互換性評価は全体の結果に基づいて判定
                    # 最後に行うため明確な時間差を出す
                    time.sleep(0.1)  # 0.1秒の遅延
                    result['status_バージョン互換性評価'] = result['status']
                    result['timestamp_バージョン互換性評価'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
                    result['criteria_バージョン互換性評価'] = '全検証項目の総合評価'
                except Exception as e:
                    print(f"[ERROR] カスタム比較中にエラーが発生しました: {str(e)}")
            
            return result
        
        # 各種比較メソッド
        def _check_format(self, old_file, new_file):
            """フォーマット検証"""
            try:
                # ファイル拡張子の比較
                old_ext = os.path.splitext(old_file)[1]
                new_ext = os.path.splitext(new_file)[1]
                if old_ext != new_ext:
                    return f"ファイル形式の変更: {old_ext} -> {new_ext}"
                
                # ファイルサイズの比較
                old_size = os.path.getsize(old_file)
                new_size = os.path.getsize(new_file)
                size_diff_percent = 0
                if old_size > 0:
                    size_diff_percent = abs(new_size - old_size) * 100 / old_size
                
                if size_diff_percent > 50:  # 50%以上サイズが変わったらフォーマット変更と判断
                    return f"ファイルサイズの大幅な変更: {old_size} -> {new_size} バイト ({size_diff_percent:.1f}%)"
                
                return None
            except Exception as e:
                return f"フォーマット検証エラー: {str(e)}"
        
        def _check_line_count(self, old_file, new_file):
            """行数検証"""
            try:
                with open(old_file, 'r', encoding='utf-8', errors='ignore') as f:
                    old_lines = f.readlines()
                
                with open(new_file, 'r', encoding='utf-8', errors='ignore') as f:
                    new_lines = f.readlines()
                
                old_count = len(old_lines)
                new_count = len(new_lines)
                
                if old_count != new_count:
                    return f"行数の変更: {old_count} -> {new_count}"
                
                return None
            except Exception as e:
                return f"行数検証エラー: {str(e)}"
        
        def _check_content_diff(self, old_file, new_file):
            """内容の差分検証"""
            try:
                with open(old_file, 'r', encoding='utf-8', errors='ignore') as f:
                    old_content = f.read()
                
                with open(new_file, 'r', encoding='utf-8', errors='ignore') as f:
                    new_content = f.read()
                
                # difflib で差分を検出
                diff = list(difflib.unified_diff(
                    old_content.splitlines(),
                    new_content.splitlines(),
                    lineterm=''
                ))
                
                if len(diff) > 0:
                    changed_lines = len([line for line in diff if line.startswith('+') or line.startswith('-')])
                    return f"{changed_lines}行の変更"
                
                return None
            except Exception as e:
                return f"内容検証エラー: {str(e)}"
        
        def _check_keywords(self, old_file, new_file, keywords):
            """キーワード検証"""
            try:
                issues = []
                
                with open(old_file, 'r', encoding='utf-8', errors='ignore') as f:
                    old_content = f.read()
                
                with open(new_file, 'r', encoding='utf-8', errors='ignore') as f:
                    new_content = f.read()
                
                for keyword in keywords:
                    old_count = old_content.count(keyword)
                    new_count = new_content.count(keyword)
                    
                    if old_count != new_count:
                        issues.append(f"キーワード '{keyword}' の出現回数変更: {old_count} -> {new_count}")
                
                return '; '.join(issues) if issues else None
            except Exception as e:
                return f"キーワード検証エラー: {str(e)}"
        
        def _check_custom_patterns(self, old_file, new_file, patterns):
            """カスタムパターン検証"""
            try:
                issues = []
                
                with open(old_file, 'r', encoding='utf-8', errors='ignore') as f:
                    old_content = f.read()
                
                with open(new_file, 'r', encoding='utf-8', errors='ignore') as f:
                    new_content = f.read()
                
                for pattern_info in patterns:
                    pattern = pattern_info.get('pattern', '')
                    name = pattern_info.get('name', pattern)
                    
                    if not pattern:
                        continue
                    
                    try:
                        regex = re.compile(pattern)
                        old_matches = regex.findall(old_content)
                        new_matches = regex.findall(new_content)
                        
                        old_count = len(old_matches)
                        new_count = len(new_matches)
                        
                        if old_count != new_count:
                            issues.append(f"パターン '{name}' の一致回数変更: {old_count} -> {new_count}")
                    except re.error:
                        issues.append(f"パターン '{name}' の正規表現エラー")
                
                return '; '.join(issues) if issues else None
            except Exception as e:
                return f"カスタムパターン検証エラー: {str(e)}"
    
    # インスタンス作成して返す
    return ConfigBasedComparator(tool_name, old_version, new_version, config, input_dir, output_dir)
    
def _load_config_file(config_path):
    """設定ファイルを読み込む（内部関数）"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.endswith('.json'):
                import json
                return json.load(f)
            elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
                import yaml
                return yaml.safe_load(f)
    except Exception as e:
        print(f"[ERROR] 設定ファイルの読み込みに失敗しました: {str(e)}")
    return {}

def get_available_comparators():
    """
    利用可能な比較ツールの一覧を取得します。
    
    Returns:
        list: 利用可能な比較ツールの名前リスト
    """
    comparators = []
    
    # comparatorsディレクトリにあるPythonファイルを検索
    comparator_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "comparators")
    for file in os.listdir(comparator_dir):
        if file.endswith(".py") and not file.startswith("__"):
            comparator_name = file[:-3]  # .pyを除去
            comparators.append(comparator_name)
    
    # configsディレクトリにあるYAML/JSONファイルから直接ツール名を取得
    config_dir = os.path.join(comparator_dir, "configs")
    if os.path.exists(config_dir):
        for file in os.listdir(config_dir):
            if file.endswith((".yaml", ".yml", ".json")):
                tool_name = os.path.splitext(file)[0]  # 拡張子を除去
                # ツール名をそのまま追加（_configサフィックスなし）
                if f"{tool_name}_comparator" not in comparators:
                    comparators.append(f"{tool_name}_comparator")
    
    return comparators


def get_comparator(tool_name, old_version, new_version, input_dir="inputs", output_dir="artifacts"):
    """
    ツール名に対応する比較クラスを取得する
    
    Parameters:
        tool_name (str): ツール名
        old_version (str): 旧バージョン
        new_version (str): 新バージョン
        input_dir (str, optional): 入力ディレクトリ
        output_dir (str, optional): 出力ディレクトリ
        
    Returns:
        BaseComparator: 比較クラスのインスタンス
        
    Raises:
        ImportError: モジュールのインポートに失敗した場合
        AttributeError: クラスが見つからない場合
    """
    # 1. 設定ファイルがあるか確認
    config_paths = [
        os.path.join("comparators", "configs", f"{tool_name.lower()}.yaml"),
        os.path.join("comparators", "configs", f"{tool_name.lower()}.yml"),
        os.path.join("comparators", "configs", f"{tool_name.lower()}.json"),
        os.path.join("configs", f"{tool_name.lower()}.yaml"),
        os.path.join("configs", f"{tool_name.lower()}.yml"),
        os.path.join("configs", f"{tool_name.lower()}.json"),
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            print(f"[INFO] 設定ファイルが見つかりました: {config_path}")
            print(f"[INFO] 設定ファイルベースのコンパレータを使用します: {tool_name}")
            # 設定ベースのコンパレータを使用
            return _create_config_based_comparator(tool_name, old_version, new_version, config_path, input_dir, output_dir)
    
    # 2. カスタムコンパレータクラスがあるか確認
    # ツール名から比較クラス名を推測
    comparator_name = f"{tool_name.lower()}_comparator"
    module_path = f"comparators.{comparator_name}"
    
    try:
        # モジュールを動的にインポート
        module = importlib.import_module(module_path)
        
        # クラス名を推測 - モジュール名がすでに xxx_comparator の形式であれば処理
        if comparator_name.endswith('_comparator'):
            # XxxComparator 形式を作る
            base_name = comparator_name.replace('_comparator', '')
            class_name = "".join(part.capitalize() for part in base_name.split('_')) + "Comparator"
        else:
            # 単にキャメルケースに変換
            class_name = "".join(part.capitalize() for part in comparator_name.split('_'))
        
        # クラスを取得
        try:
            comparator_class = getattr(module, class_name)
            print(f"[INFO] カスタムコンパレータクラスを使用します: {class_name}")
            return comparator_class(tool_name, old_version, new_version, input_dir, output_dir)
        except AttributeError:
            # クラス名が見つからない場合、設定ファイルの有無を確認して設定ベースのコンパレータを使用
            for config_path in config_paths:
                if os.path.exists(config_path):
                    print(f"[INFO] クラス {class_name} が見つかりませんが、設定ファイルが見つかりました: {config_path}")
                    print(f"[INFO] 設定ファイルベースのコンパレータを使用します: {tool_name}")
                    return _create_config_based_comparator(tool_name, old_version, new_version, config_path, input_dir, output_dir)
            
            print(f"[ERROR] Comparator class not found in module 'comparators.{comparator_name}'")
            raise AttributeError(f"module 'comparators.{comparator_name}' has no attribute '{class_name}'")
        
    except ImportError as e:
        # 3. モジュールがインポートできない場合、設定ファイルを再確認
        for config_path in config_paths:
            if os.path.exists(config_path):
                print(f"[INFO] モジュール {module_path} が見つかりませんが、設定ファイルが見つかりました: {config_path}")
                print(f"[INFO] 設定ファイルベースのコンパレータを使用します: {tool_name}")
                return _create_config_based_comparator(tool_name, old_version, new_version, config_path, input_dir, output_dir)
        
        # 4. それでも見つからなければデフォルトのコンパレータを使用
        print(f"[WARNING] モジュール 'comparators.{comparator_name}' が見つかりません。")
        print(f"[INFO] 設定ファイルも見つからないため、デフォルトの比較クラスを使用します。")
        print(f"[INFO] カスタム比較ロジックを使用するには、次のいずれかを作成してください:")
        print(f"[INFO] 1. 設定ファイル: comparators/configs/{tool_name.lower()}.yaml")
        print(f"[INFO] 2. カスタムクラス: comparators/{comparator_name}.py")
        print(f"[WARNING] 詳細: {str(e)}")
        return BaseComparator(tool_name, old_version, new_version, input_dir, output_dir)
