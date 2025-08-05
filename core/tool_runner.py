#!/usr/bin/env python3
"""
ツールの実行と比較を管理するクラス
"""
import os
import sys
import subprocess
import datetime
import glob
from utils.file_utils import get_exec_cmd, setup_logging, get_log_files, Tee
from core.comparator import load_comparator_class, get_available_comparators


class ToolRunner:
    """
    ツールの実行と比較を管理するクラス
    """

    def __init__(self, args):
        """
        Parameters:
            args (Namespace): コマンドライン引数
        """
        self.tool_name = args.tool_name
        self.old_version = args.old_version
        self.new_version = args.new_version
        self.input_dir = args.input_dir
        self.output_dir = args.output_dir
        self.comparator = args.comparator
        self.debug = args.debug
        self.silent = args.silent
        self.log_dir = args.log_dir
        self.log_file = None
        self.results = []

    def setup(self):
        """
        実行の準備を行います。
        """
        # ログディレクトリの作成
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # ログファイルのセットアップ
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # ツール固有のログディレクトリの処理
        if self.tool_name and self.tool_name in ["ICC2_smoke"]:
            # ICC2_smokeはApps/ICC2_smoke/logsディレクトリにログを保存
            app_log_dir = os.path.join("Apps", self.tool_name, "logs")
            os.makedirs(app_log_dir, exist_ok=True)
            
            if self.old_version and self.new_version:
                log_filename = f"{self.tool_name}_{self.old_version}_{self.new_version}_{timestamp}.log"
            else:
                log_filename = f"{self.tool_name}_{timestamp}.log"
                
            self.log_file = os.path.join(app_log_dir, log_filename)
        else:
            # 本ツールのログは通常のlogsディレクトリに保存
            if self.tool_name and self.old_version and self.new_version:
                log_filename = f"{self.tool_name}_{self.old_version}_{self.new_version}_{timestamp}.log"
            else:
                log_filename = f"verup_verification_{timestamp}.log"
                
            self.log_file = os.path.join(self.log_dir, log_filename)
        
        # 標準出力のリダイレクトをセットアップ
        if not self.silent:
            self.stdout_redirector = Tee(self.log_file, 'w')
            self.stdout_redirector.start_redirect()

    def run(self):
        """
        指定されたツールの実行と比較を行います。
        
        Returns:
            list: 比較結果のリスト
        """
        self.setup()
        
        try:
            if self.tool_name:
                # 単一ツールの実行
                result = self._run_single_tool()
                self.results = [result]
            else:
                # すべての利用可能なツールを実行
                self.results = self._run_all_tools()
        
        finally:
            # 標準出力のリダイレクトを終了
            if not self.silent and hasattr(self, 'stdout_redirector'):
                self.stdout_redirector.stop_redirect()
        
        return self.results

    def _run_single_tool(self):
        """
        単一ツールの実行と比較を行います。
        
        Returns:
            dict: 比較結果
        """
        comparator_name = self.comparator or self._get_default_comparator()
        
        try:
            # 比較ツールクラスの動的ロード
            comparator_class = load_comparator_class(comparator_name)
            
            # 比較ツールのインスタンス化と実行
            comparator = comparator_class(
                self.tool_name,
                self.old_version,
                self.new_version,
                self.input_dir,
                self.output_dir
            )
            
            # ログファイルパスを抽出してコンパレータに渡す
            log_file_basename = os.path.basename(self.log_file) if self.log_file else None
            
            # 比較の実行
            result = comparator.run(log_file_basename)
            
            # 成果物のパスを追加
            old_artifact_path, new_artifact_path = comparator.get_output_files()
            result['old_artifact_path'] = old_artifact_path
            result['new_artifact_path'] = new_artifact_path
            
            # 成果物の内容を読み込む
            if old_artifact_path and os.path.exists(old_artifact_path):
                with open(old_artifact_path, 'r', encoding='utf-8', errors='replace') as f:
                    result['old_content'] = f.read()
            
            if new_artifact_path and os.path.exists(new_artifact_path):
                with open(new_artifact_path, 'r', encoding='utf-8', errors='replace') as f:
                    result['new_content'] = f.read()
            
            print(f"[INFO] {self.tool_name} comparison: {result['status']}")
            return result
            
        except Exception as e:
            print(f"[ERROR] Failed to compare {self.tool_name}: {str(e)}")
            if self.debug:
                import traceback
                traceback.print_exc()
            
            # エラーの場合も結果を返す
            return {
                'tool_name': self.tool_name,
                'old_version': self.old_version,
                'new_version': self.new_version,
                'status': 'Error',
                'detail': f"比較処理でエラーが発生しました: {str(e)}"
            }

    def _run_all_tools(self):
        """
        全ての利用可能なツールの実行と比較を行います。
        
        Returns:
            list: 比較結果のリスト
        """
        results = []
        available_tools = self._get_available_tools()
        
        # ツール名のリストを取得
        tool_names = [tool_info.get('name') for tool_info in available_tools]
        print(f"[INFO] Running all available tools: {', '.join(tool_names)}")
        
        for tool_info in available_tools:
            tool_name = tool_info.get('name')
            old_version = tool_info.get('old_version', self.old_version)
            new_version = tool_info.get('new_version', self.new_version)
            
            # ツールランナーの一時的な設定を更新
            self.tool_name = tool_name
            self.old_version = old_version
            self.new_version = new_version
            
            # ツールの実行
            result = self._run_single_tool()
            results.append(result)
        
        return results

    def _get_default_comparator(self):
        """
        デフォルトの比較ツール名を取得します。
        
        ツール名から適切な比較ツールを推測します。
        
        Returns:
            str: 比較ツール名
        """
        if not self.tool_name:
            return "sampletool_comparator"  # デフォルト
        
        # ツール名からコンパレータ名を推測
        comparator_name = self.tool_name.lower().replace('-', '_') + "_comparator"
        
        # 存在する場合は使用、しない場合はデフォルト
        comparators_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "comparators")
        comparator_file = os.path.join(comparators_dir, f"{comparator_name}.py")
        
        if os.path.exists(comparator_file):
            return comparator_name
        else:
            print(f"[WARNING] No specific comparator found for {self.tool_name}, using default")
            return "sampletool_comparator"

    def _get_available_tools(self):
        """
        利用可能なツールの一覧を取得します。
        
        Returns:
            list: 利用可能なツール情報のリスト
        """
        tools = []
        
        # 利用可能なコンパレータの取得
        comparators = get_available_comparators()
        
        for comparator_name in comparators:
            if comparator_name.endswith('_comparator'):
                tool_name = comparator_name.replace('_comparator', '')
                
                tools.append({
                    'name': tool_name,
                    'comparator': comparator_name,
                    'old_version': self.old_version or '1.0.0',
                    'new_version': self.new_version or '2.0.0'
                })
        
        return tools
