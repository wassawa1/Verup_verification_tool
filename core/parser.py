#!/usr/bin/env python3
"""
コマンドライン引数の解析モジュール
"""
import argparse
import sys
import os


def parse_arguments():
    """
    コマンドライン引数を解析する
    
    Returns:
        argparse.Namespace: 解析された引数
    """
    parser = argparse.ArgumentParser(
        description='バージョンアップの検証ツール',
        formatter_class=argparse.RawTextHelpFormatter)
    
    # 基本的なオプション
    parser.add_argument('-t', '--tool-name',
                      help='検証対象ツールの名前')
    parser.add_argument('-o', '--old-version',
                      help='旧バージョン')
    parser.add_argument('-n', '--new-version',
                      help='新バージョン')
    
    # 入出力ディレクトリオプション
    parser.add_argument('-i', '--input-dir',
                      default='inputs',
                      help='入力ファイルのディレクトリ (デフォルト: inputs)')
    parser.add_argument('-a', '--output-dir',
                      default='artifacts',
                      help='成果物出力のディレクトリ (デフォルト: artifacts)')
    
    # 比較ツールオプション
    parser.add_argument('-c', '--comparator',
                      help='使用する比較ツール')
    
    # リスト表示オプション
    parser.add_argument('-l', '--list',
                      action='store_true',
                      help='利用可能なツール一覧を表示')
    
    # デモモード
    parser.add_argument('-d', '--demo',
                      action='store_true',
                      help='デモモード (サンプル成果物を生成)')
    
    # 詳細設定
    parser.add_argument('--debug',
                      action='store_true',
                      help='デバッグモード')
    parser.add_argument('-s', '--silent',
                      action='store_true',
                      help='サイレントモード (標準出力への出力を抑制)')
    parser.add_argument('--log-dir',
                      default='logs',
                      help='ログ出力のディレクトリ (デフォルト: logs)')
    
    # レポート設定
    parser.add_argument('--csv-report',
                      default='report.csv',
                      help='CSVレポートのファイル名 (デフォルト: report.csv)')
    parser.add_argument('--html-report',
                      default='report.html',
                      help='HTMLレポートのファイル名 (デフォルト: report.html)')
    parser.add_argument('--no-report',
                      action='store_true',
                      help='レポート生成を無効化')
    
    # カレントディレクトリをデフォルトにする
    parser.add_argument('--tools-dir',
                      default=os.getcwd(),
                      help='ツールのインストールディレクトリ')
    
    args = parser.parse_args()
    
    # ディレクトリパスを絶対パスに変換
    args.input_dir = os.path.abspath(args.input_dir)
    args.output_dir = os.path.abspath(args.output_dir)
    args.log_dir = os.path.abspath(args.log_dir)
    args.tools_dir = os.path.abspath(args.tools_dir)
    
    return args
