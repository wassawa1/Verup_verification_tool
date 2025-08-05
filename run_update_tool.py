#!/usr/bin/env python3
"""
バージョンアップ検証ツール メインスクリプト
このツールは、旧バージョンと新バージョンのツールの動作を比較し、
その結果をレポートとして出力するためのものです。
"""
import os
import sys
import datetime
from core.parser import parse_arguments
from core.tool_runner import ToolRunner
from core.report import Report
from core.comparator import get_available_comparators


def list_available_tools():
    """
    利用可能なツールの一覧を表示する
    """
    comparators = get_available_comparators()
    
    print("利用可能なツール:")
    tool_names = set()
    for comparator in comparators:
        if comparator.endswith('_comparator'):
            tool_name = comparator.replace('_comparator', '')
            tool_names.add(tool_name)
    
    # ソートして表示
    for tool_name in sorted(tool_names):
        print(f"  - {tool_name}")
    
    print("\n比較ツール:")
    for comparator in sorted(comparators):
        print(f"  - {comparator}")


def create_output_directories(args):
    """
    出力ディレクトリを作成する
    
    Parameters:
        args (Namespace): コマンドライン引数
    """
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.log_dir, exist_ok=True)


def main():
    """
    メイン処理
    """
    from utils.file_utils import get_platform_info
    
    args = parse_arguments()
    
    # プラットフォーム情報をログ出力（CI環境での診断用）
    platform_info = get_platform_info()
    print(f"[INFO] 実行環境: {platform_info['system']} {platform_info['release']} ({platform_info['machine']})")
    print(f"[INFO] Python バージョン: {platform_info['python']}")
    
    # 利用可能なツールの一覧表示
    if args.list:
        list_available_tools()
        sys.exit(0)
    
    # 出力ディレクトリの作成
    create_output_directories(args)
    
    # ツールの実行と比較
    runner = ToolRunner(args)
    results = runner.run()
    
    # レポート生成
    if not args.no_report:
        report = Report(results)
        csv_path = report.generate_csv(args.csv_report)
        html_path = report.generate_html(args.html_report)
        
        print(f"\n[INFO] CSVレポートを生成しました: {csv_path}")
        print(f"[INFO] HTMLレポートを生成しました: {html_path}")
    
    # 成功・失敗の集計
    success_count = sum(1 for result in results if result.get('status') == 'Success')
    failed_count = sum(1 for result in results if result.get('status') == 'Failed')
    error_count = sum(1 for result in results if result.get('status') == 'Error')
    total_count = len(results)
    
    # 結果の表示
    print(f"\n[サマリー] 合計: {total_count}, 成功: {success_count}, 失敗: {failed_count}, エラー: {error_count}")
    
    # レポート表示方法の案内（レポートが生成されている場合のみ）
    if not args.no_report:
        print("\n[レポート表示方法]")
        print(f"CSVレポート: メモ帳やExcelで開いてください")
        print(f"HTMLレポート: ウェブブラウザ(Chrome/Edge/Firefox)で開いてください")
    
    # 終了コードの設定
    if failed_count > 0 or error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
