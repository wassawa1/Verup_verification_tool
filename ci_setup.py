#!/usr/bin/env python3
"""
GitHub Actionsなど、CI環境でのセットアップを行うスクリプト
"""
import os
import glob
import stat
import sys

def ensure_execute_permission():
    """
    Appsディレクトリ内の全てのPythonスクリプトに実行権限を付与する
    Linux環境でのCI実行時に必要
    """
    # Appsディレクトリ内の全てのPythonスクリプト
    python_files = glob.glob("Apps/**/*.py", recursive=True)
    
    # 各ファイルに実行権限を付与
    for py_file in python_files:
        if os.path.isfile(py_file):
            current_mode = os.stat(py_file).st_mode
            execute_mode = current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            os.chmod(py_file, execute_mode)
            print(f"[INFO] 実行権限を付与しました: {py_file}")

if __name__ == "__main__":
    # CI環境が検出された場合のみ実行
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        print("[INFO] CI環境を検出しました。セットアップを開始します...")
        ensure_execute_permission()
        print("[INFO] セットアップが完了しました。")
    else:
        print("[INFO] ローカル環境で実行中です。CI環境セットアップはスキップします。")
