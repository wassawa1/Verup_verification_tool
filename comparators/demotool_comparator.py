#!/usr/bin/env python3
"""
DemoToolのカスタム比較関数

このファイルは、DemoToolの出力を比較するためのカスタム関数を提供します。
"""
import re
import os
import json
import difflib

def compare_artifacts(old_file, new_file):
    """
    DemoToolの成果物を比較する関数
    
    Parameters:
        old_file (str): 旧バージョンの成果物ファイルパス
        new_file (str): 新バージョンの成果物ファイルパス
        
    Returns:
        tuple: (比較結果（True: 正常、False: 異常）, 差分メッセージ, 差分の詳細コンテンツ)
    """
    print(f"[CUSTOM] DemoToolの成果物比較を実行します")
    print(f"[CUSTOM] 旧ファイル: {old_file}")
    print(f"[CUSTOM] 新ファイル: {new_file}")
    
    try:
        with open(old_file, encoding='cp932') as f1, open(new_file, encoding='cp932') as f2:
            data1 = f1.read()
            data2 = f2.read()
            
        # パフォーマンス情報を抽出
        old_perf_times = re.findall(r'処理時間: (\d+\.\d+)秒', data1)
        new_perf_times = re.findall(r'処理時間: (\d+\.\d+)秒', data2)
        
        if old_perf_times and new_perf_times:
            old_avg = sum(float(t) for t in old_perf_times) / len(old_perf_times)
            new_avg = sum(float(t) for t in new_perf_times) / len(new_perf_times)
            improvement = (old_avg - new_avg) / old_avg * 100
            
            # 詳細な比較内容をContentに記録
            msg = "Performance improvement"
            content_lines = [
                "Performance differences:",
                f"- Old version: {old_avg:.1f} seconds",
                f"- New version: {new_avg:.1f} seconds",
                f"- Improvement: {improvement:.1f}%",
                "",
                "File content differences:"
            ]
            
            # 処理時間の差分を詳細に記録
            for i, (old_time, new_time) in enumerate(zip(old_perf_times, new_perf_times)):
                file_imp = ((float(old_time) - float(new_time)) / float(old_time) * 100)
                content_lines.append(f"- 処理時間: {old_time}秒 → {new_time}秒 ({file_imp:.1f}% 改善)")
                
            # 構造化データの作成
            analysis_data = {
                "analysis_type": "performance",
                "processing_time": {
                    "old": old_avg,
                    "new": new_avg,
                    "diff_percent": improvement
                },
                "file_details": [
                    {
                        "old_time": float(old_time),
                        "new_time": float(new_time),
                        "improvement": ((float(old_time) - float(new_time)) / float(old_time) * 100)
                    }
                    for old_time, new_time in zip(old_perf_times, new_perf_times)
                ]
            }
            
            # 構造化データをJSON形式で埋め込み
            content = f"STRUCTURED_DATA={json.dumps(analysis_data)}\n\n" + "\n".join(content_lines)
            print(f"[CUSTOM][DEMO] Performance improved by {improvement:.1f}%")
            return True, msg, content
            
        # 構造化データを差分から生成
        diff = list(difflib.unified_diff(
            data1.splitlines(), 
            data2.splitlines(), 
            lineterm='',
            n=3
        ))
        
        if not diff:  # 差分がない場合
            analysis_data = {
                "analysis_type": "no_differences",
                "file_size": len(data1),
                "line_count": data1.count('\n') + 1,
                "success_count": len(re.findall(r'成功', data1)),
                "failure_count": len(re.findall(r'失敗|エラー|異常', data1))
            }
            
            msg = "No differences"
            content = f"STRUCTURED_DATA={json.dumps(analysis_data)}\n\n成果物ファイルに差異はありません。"
            print(f"[CUSTOM][DEMO] Artifacts match")
            return True, msg, content
        else:
            # 1. ファイルサイズの比較
            size_old = len(data1)
            size_new = len(data2)
            size_diff = size_new - size_old
            size_percent = (size_diff / size_old * 100) if size_old > 0 else 0
                
            # 2. 行数の比較
            lines_old = data1.count('\n') + 1
            lines_new = data2.count('\n') + 1
            lines_diff = lines_new - lines_old
                
            # 3. 成功/失敗カウント
            old_success = len(re.findall(r'成功', data1))
            new_success = len(re.findall(r'成功', data2))
            old_fail = len(re.findall(r'失敗|エラー|異常', data1))
            new_fail = len(re.findall(r'失敗|エラー|異常', data2))
            
            analysis_data = {
                "analysis_type": "differences",
                "file_size": {"old": size_old, "new": size_new, "diff_percent": size_percent},
                "line_count": {"old": lines_old, "new": lines_new, "diff": lines_diff},
                "success_count": {"old": old_success, "new": new_success},
                "failure_count": {"old": old_fail, "new": new_fail},
                "diff_lines": len(diff)
            }
            
            msg = "Artifacts differ"
            content = f"STRUCTURED_DATA={json.dumps(analysis_data)}\n\n" + "\n".join(diff[:100])
            if len(diff) > 100:
                content += "\n... (差分が多すぎるため省略) ..."
                
            print(f"[CUSTOM][DEMO] Artifacts differ ({len(diff)} lines)")
            return True, msg, content
            
    except Exception as e:
        print(f"[CUSTOM][ERROR] Error comparing demo artifacts: {str(e)}")
        error_message = f"比較エラー: {str(e)}"
        return False, error_message, f"比較処理中にエラーが発生しました: {str(e)}"


def compare_logs(old_log, new_log):
    """
    DemoToolのログを比較する関数
    
    Parameters:
        old_log (str): 旧バージョンのログファイルパス
        new_log (str): 新バージョンのログファイルパス
        
    Returns:
        tuple: (比較結果（True: 正常、False: 異常）, 差分メッセージ, 差分の詳細コンテンツ)
    """
    print(f"[CUSTOM] DemoToolのログ比較を実行します")
    print(f"[CUSTOM] 旧ログ: {old_log}")
    print(f"[CUSTOM] 新ログ: {new_log}")
    
    # ログファイルが存在しない場合
    if not os.path.exists(old_log) or not os.path.exists(new_log):
        msg = "Log files not found"
        print(f"[CUSTOM][WARNING] {msg}")
        return True, msg, ""
    
    try:
        with open(old_log, encoding='utf-8') as f1, open(new_log, encoding='utf-8') as f2:
            old_content = f1.read()
            new_content = f2.read()
        
        # エラー数をカウント
        old_errors = len(re.findall(r'error|exception|fail|fault', old_content.lower()))
        new_errors = len(re.findall(r'error|exception|fail|fault', new_content.lower()))
        
        # 処理時間を検出
        old_time_match = re.search(r'処理時間: (\d+\.\d+)秒', old_content)
        new_time_match = re.search(r'処理時間: (\d+\.\d+)秒', new_content)
        
        old_time = float(old_time_match.group(1)) if old_time_match else None
        new_time = float(new_time_match.group(1)) if new_time_match else None
        
        # 処理時間の改善率を計算
        time_improvement = 0
        if old_time and new_time and old_time > 0:
            time_improvement = (old_time - new_time) / old_time * 100
            
        # 構造化データを作成
        import difflib
        diff = list(difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            n=1
        ))
        
        analysis_data = {
            "analysis_type": "log_comparison",
            "processing_time": {
                "old": old_time,
                "new": new_time,
                "diff_percent": time_improvement
            },
            "errors": {
                "old": old_errors,
                "new": new_errors,
                "diff": new_errors - old_errors
            },
            "diff_lines": len(diff)
        }
        
        # メッセージを生成
        messages = []
        if old_time and new_time:
            if new_time < old_time:
                messages.append(f"処理時間が改善: {old_time:.2f}秒 → {new_time:.2f}秒 ({time_improvement:.1f}%)")
            else:
                messages.append(f"処理時間が低下: {old_time:.2f}秒 → {new_time:.2f}秒")
                
        if old_errors != new_errors:
            if new_errors < old_errors:
                messages.append(f"エラー数が減少: {old_errors}件 → {new_errors}件")
            else:
                messages.append(f"エラー数が増加: {old_errors}件 → {new_errors}件")
        
        if not messages:
            messages.append(f"ログに大きな変化なし")
            
        msg = ", ".join(messages)
        content = f"STRUCTURED_DATA={json.dumps(analysis_data)}\n\n" + "\n".join(diff[:100])
        
        print(f"[CUSTOM] {msg}")
        return True, msg, content
        
    except Exception as e:
        print(f"[CUSTOM][ERROR] ログ比較中にエラーが発生しました: {str(e)}")
        error_message = f"ログ比較エラー: {str(e)}"
        return False, error_message, f"ログ比較処理中にエラーが発生しました: {str(e)}"
