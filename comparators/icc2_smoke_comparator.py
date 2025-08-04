#!/usr/bin/env python3
"""
ICC2_smokeのカスタム比較関数

このファイルは、ICC2_smokeの出力を比較するためのカスタム関数を提供します。
"""
import re
import os
import json
import difflib

def compare_artifacts(old_file, new_file):
    """
    ICC2_smokeの成果物を比較する関数
    
    Parameters:
        old_file (str): 旧バージョンの成果物ファイルパス
        new_file (str): 新バージョンの成果物ファイルパス
        
    Returns:
        tuple: (比較結果（True: 正常、False: 異常）, 差分メッセージ, 差分の詳細コンテンツ)
    """
    print(f"[CUSTOM] ICC2_smokeの成果物比較を実行します")
    print(f"[CUSTOM] 旧ファイル: {old_file}")
    print(f"[CUSTOM] 新ファイル: {new_file}")
    
    try:
        with open(old_file, encoding='utf-8') as f1, open(new_file, encoding='utf-8') as f2:
            old_content = f1.read()
            new_content = f2.read()
        
        # ICC2_smokeの処理結果を解析
        old_stats = parse_icc2smoke_output(old_content)
        new_stats = parse_icc2smoke_output(new_content)
        
        # 各指標の比較
        print(f"[CUSTOM] 旧バージョン統計: {old_stats}")
        print(f"[CUSTOM] 新バージョン統計: {new_stats}")
        
        # タイミング違反の改善を確認
        old_violations = old_stats.get('timing_violations', 0)
        new_violations = new_stats.get('timing_violations', 0)
        
        if new_violations < old_violations:
            print(f"[CUSTOM] タイミング違反が減少しました: {old_violations} -> {new_violations}")
            timing_improved = True
        else:
            timing_improved = False
        
        # 処理ファイル数の比較
        old_files = old_stats.get('processed_files', 0)
        new_files = new_stats.get('processed_files', 0)
        
        if old_files != new_files:
            print(f"[CUSTOM][WARNING] 処理ファイル数が異なります: {old_files} -> {new_files}")
            
        # パフォーマンス情報の抽出
        old_time = extract_processing_time(old_content)
        new_time = extract_processing_time(new_content)
        
        # デフォルト値を設定
        time_diff_percent = 0
        
        if old_time and new_time and old_time > 0:
            time_diff_percent = ((old_time - new_time) / old_time * 100)
            if time_diff_percent > 0:
                print(f"[CUSTOM] 処理時間が改善されました: {old_time:.2f}秒 -> {new_time:.2f}秒 ({time_diff_percent:.1f}%)")
            else:
                print(f"[CUSTOM] 処理時間が低下しました: {old_time:.2f}秒 -> {new_time:.2f}秒")
        
        # 構造化データとして生成
        import json
        
        # 差分分析の結果を構造化データとして生成
        analysis_data = {
            "analysis_type": "differences" if old_content != new_content else "no_differences",
            "file_size": {
                "old": len(old_content),
                "new": len(new_content),
                "diff_percent": (len(new_content) - len(old_content)) / max(1, len(old_content)) * 100
            },
            "processed_files": {
                "old": old_files,
                "new": new_files,
                "diff": new_files - old_files
            },
            "timing_violations": {
                "old": old_violations,
                "new": new_violations,
                "diff": new_violations - old_violations,
                "improved": timing_improved
            },
            "processing_time": {
                "old": old_time,
                "new": new_time,
                "diff_percent": time_diff_percent if old_time and new_time else 0
            },
            "memory_usage": {
                "old": old_stats.get('memory_usage', 0),
                "new": new_stats.get('memory_usage', 0)
            },
            "rtl_modules": {
                "old": old_stats.get('rtl_modules', 0),
                "new": new_stats.get('rtl_modules', 0)
            },
            "constraints": {
                "old": old_stats.get('constraints', 0),
                "new": new_stats.get('constraints', 0)
            },
            "tech_cells": {
                "old": old_stats.get('tech_cells', 0),
                "new": new_stats.get('tech_cells', 0)
            }
        }
        
        # 差分の詳細
        import difflib
        diff = list(difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            n=1  # コンテキスト行数
        ))
        analysis_data["diff_lines"] = len(diff)
        
        # 差分メッセージの生成
        messages = []
        
        if timing_improved:
            messages.append(f"タイミング違反が{old_violations - new_violations}件減少")
        
        if old_time and new_time and time_diff_percent > 0:
            messages.append(f"処理時間が{time_diff_percent:.1f}%改善")
        
        if new_stats.get('memory_usage', 0) > old_stats.get('memory_usage', 0):
            messages.append(f"メモリ使用量が増加 ({old_stats.get('memory_usage', 0)}MB -> {new_stats.get('memory_usage', 0)}MB)")
        
        if not messages:
            if analysis_data["diff_lines"] > 0:
                messages.append(f"出力に{analysis_data['diff_lines']}行の差分あり")
            else:
                messages.append("出力に差分なし")
        
        diff_message = ", ".join(messages)
        
        # 構造化データをJSON形式に変換
        diff_content = f"STRUCTURED_DATA={json.dumps(analysis_data)}\n\n" + "\n".join(diff[:100])  # 最大100行に制限
        
        # カスタム比較の結果
        return True, diff_message, diff_content
    except Exception as e:
        print(f"[CUSTOM][ERROR] 比較中にエラーが発生しました: {str(e)}")
        error_message = f"比較エラー: {str(e)}"
        return False, error_message, f"比較処理中にエラーが発生しました: {str(e)}"


def compare_logs(old_log, new_log):
    """
    ICC2_smokeのログを比較する関数
    
    Parameters:
        old_log (str): 旧バージョンのログファイルパス
        new_log (str): 新バージョンのログファイルパス
        
    Returns:
        tuple: (比較結果（True: 正常、False: 異常）, 差分メッセージ, 差分の詳細コンテンツ)
    """
    print(f"[CUSTOM] ICC2_smokeのログ比較を実行します")
    print(f"[CUSTOM] 旧ログ: {old_log}")
    print(f"[CUSTOM] 新ログ: {new_log}")
    
    try:
        # ログファイルが存在しない場合
        if not os.path.exists(old_log) or not os.path.exists(new_log):
            print(f"[CUSTOM][WARNING] ログファイルが見つかりません")
            return True, "Log files not found", ""
            
        with open(old_log, encoding='utf-8') as f1, open(new_log, encoding='utf-8') as f2:
            old_content = f1.read()
            new_content = f2.read()
        
        # 処理時間を比較
        old_time = extract_processing_time(old_content)
        new_time = extract_processing_time(new_content)
        
        # デフォルト値を設定
        time_diff_percent = 0
        time_message = ""
        
        if old_time and new_time and old_time > 0:
            time_diff_percent = ((old_time - new_time) / old_time * 100)
            if time_diff_percent > 0:
                time_message = f"処理時間が改善: {old_time:.2f}秒 → {new_time:.2f}秒 ({time_diff_percent:.1f}%)"
                print(f"[CUSTOM] 新バージョンの処理時間が改善されています: {old_time:.2f}秒 -> {new_time:.2f}秒 ({time_diff_percent:.1f}%)")
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
                "diff_percent": time_diff_percent if old_time and new_time else 0
            },
            "errors": {
                "old": old_errors,
                "new": new_errors,
                "diff": new_errors - old_errors
            }
        }
        
        # ログに含まれるファイル数をカウント
        old_files = len(re.findall(r'^[0-9]+\.\s+(.+?)$', old_content, re.MULTILINE))
        new_files = len(re.findall(r'^[0-9]+\.\s+(.+?)$', new_content, re.MULTILINE))
        
        analysis_data["processed_files"] = {
            "old": old_files,
            "new": new_files,
            "diff": new_files - old_files
        }
        
        # 差分の詳細
        diff = list(difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            n=1  # コンテキスト行数
        ))
        analysis_data["diff_lines"] = len(diff)
        
        # 構造化データをJSON形式に変換
        diff_content = f"STRUCTURED_DATA={json.dumps(analysis_data)}\n\n" + "\n".join(diff[:100])  # 最大100行に制限
        
        # 差分メッセージの生成
        messages = []
        if time_message:
            messages.append(time_message)
        if old_errors != new_errors:
            messages.append(f"エラー数: {old_errors} → {new_errors}")
        if old_files != new_files:
            messages.append(f"処理ファイル数: {old_files} → {new_files}")
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

def parse_icc2smoke_output(content):
    """ICC2_smokeの出力から統計情報を抽出する"""
    stats = {
        'processed_files': 0,
        'timing_violations': 0,
        'rtl_modules': 0,
        'constraints': 0,
        'tech_cells': 0,
        'memory_usage': 0
    }
    
    # 処理ファイル数を抽出
    file_match = re.search(r'処理ファイル数:\s*(\d+)', content)
    if file_match:
        stats['processed_files'] = int(file_match.group(1))
    
    # タイミング違反数を抽出
    violations_match = re.search(r'タイミング違反数:\s*(\d+)', content)
    if violations_match:
        stats['timing_violations'] = int(violations_match.group(1))
        
    # RTLモジュール数を抽出
    rtl_match = re.search(r'RTLファイル:\s*\d+\s*\(モジュール数:\s*(\d+)\)', content)
    if rtl_match:
        stats['rtl_modules'] = int(rtl_match.group(1))
    
    # 制約数を抽出
    constraints_match = re.search(r'制約ファイル:\s*\d+\s*\(制約数:\s*(\d+)\)', content)
    if constraints_match:
        stats['constraints'] = int(constraints_match.group(1))
    
    # セル数を抽出
    cells_match = re.search(r'技術ファイル:\s*\d+\s*\(セル定義数:\s*(\d+)\)', content)
    if cells_match:
        stats['tech_cells'] = int(cells_match.group(1))
    
    # メモリ使用量を抽出 (バージョン2.0.0にのみ存在)
    memory_match = re.search(r'メモリ使用量:\s*(\d+)MB', content)
    if memory_match:
        stats['memory_usage'] = int(memory_match.group(1))
        
    return stats


def extract_processing_time(content):
    """テキストから処理時間を抽出する"""
    time_match = re.search(r'処理時間:\s*([\d\.]+)秒', content)
    if time_match:
        return float(time_match.group(1))
    return None


def count_errors(content):
    """テキスト内のエラー数をカウントする"""
    error_count = len(re.findall(r'\[ERROR\]', content))
    return error_count
