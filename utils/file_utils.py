#!/usr/bin/env python3
"""
ファイル操作に関するユーティリティ関数
"""
import os
import glob
import stat
import sys
import datetime
import platform

class Tee:
    """
    標準出力と標準エラー出力を複数の出力先にリダイレクトするためのクラス
    """
    def __init__(self, filename, mode='a'):
        self.file = open(filename, mode, encoding='utf-8')
        self.stdout = sys.stdout
        self.stderr = sys.stderr
    
    def start_redirect(self):
        """リダイレクト開始"""
        sys.stdout = self
        sys.stderr = self
    
    def stop_redirect(self):
        """リダイレクト停止"""
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        self.file.close()
    
    def write(self, obj):
        self.file.write(obj)
        self.stdout.write(obj)
        self.file.flush()
    
    def flush(self):
        self.file.flush()
        self.stdout.flush()


def normalize_path(path):
    """
    プラットフォーム間でのパスを正規化する
    
    Parameters:
        path (str): 正規化するパス
        
    Returns:
        str: 正規化されたパス
    """
    return os.path.normpath(path)


def get_platform_info():
    """
    実行プラットフォームの情報を取得
    
    Returns:
        dict: プラットフォーム情報
    """
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'python': platform.python_version()
    }


def get_exec_cmd(tool, tools_dir):
    """
    実行ファイルを検索する関数
    
    Parameters:
        tool (str): ツール名
        tools_dir (str): ツールが配置されているディレクトリ
        
    Returns:
        function: 実行ファイルを検索する関数
    """
    def find_exec(name, version):
        """特定のバージョンの実行ファイルを探す"""
        # Windowsの場合
        exec_patterns = ['*.exe', '*.bat', '*.cmd', '*.py']
        tool_path = os.path.join(tools_dir, name, version)
        
        if not os.path.exists(tool_path):
            return None
        
        for pattern in exec_patterns:
            execs = glob.glob(os.path.join(tool_path, pattern))
            if execs:
                return execs[0]  # 最初に見つかった実行ファイルを返す
        
        return None  # 実行ファイルが見つからない場合
    
    return find_exec


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


def setup_logging(tool, old_version, new_version):
    """
    ログファイルの設定とTeeの設定を行う
    
    Parameters:
        tool (str): ツール名
        old_version (str): 旧バージョン
        new_version (str): 新バージョン
        
    Returns:
        tuple: (log_file_path, log_file_obj, tee_obj)
    """
    # ログディレクトリを作成
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # タイムスタンプとログファイル名を生成
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # 安全なファイル名を作成（無効な文字をエスケープ）
    safe_tool_name = "".join([c if c.isalnum() or c in ['_', '-'] else '_' for c in tool])
    log_file_path = os.path.join(log_dir, f"{safe_tool_name}_{old_version}_{new_version}_{timestamp_str}.log")
    
    # Teeオブジェクトを作成
    tee = Tee(log_file_path, 'w')
    
    return log_file_path, tee


def generate_demo_artifacts(tool, old_version, new_version):
    """
    デモ用の成果物ファイルを生成する関数
    
    Parameters:
        tool (str): ツール名
        old_version (str): 旧バージョン
        new_version (str): 新バージョン
        
    Returns:
        tuple: (old_file_path, new_file_path)
    """
    # デモ用ディレクトリの作成
    artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    
    # ファイルパスのみを返す (実際のファイル生成はカスタムコンパレータで行う)
    old_file = os.path.join(artifacts_dir, f"{tool}_{old_version}.txt")
    new_file = os.path.join(artifacts_dir, f"{tool}_{new_version}.txt")
    
    return old_file, new_file
