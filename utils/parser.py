#!/usr/bin/env python3
"""
データ解析に関するユーティリティ関数
"""
import re
import json


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
                    status = "Success"
                    if diff_percent < -10:  # サイズが10%以上削減
                        status = "Success"
                    elif diff_percent > 20:  # サイズが20%以上増加
                        status = "Failed"
                        
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
                        "status": "Success",
                        "description": f"旧:{old_lines} 行 → 新:{new_lines} 行 ({diff_lines:+d} 行)"
                    })
                
                # 成功数の変化
                success_data = structured_data.get("success_count", {})
                if isinstance(success_data, dict) and "old" in success_data and "new" in success_data:
                    old_success = success_data["old"]
                    new_success = success_data["new"]
                    
                    status = "Success"
                    if new_success > old_success:
                        status = "Success"
                    elif new_success < old_success:
                        status = "Failed"
                        
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
                    
                    status = "Success"
                    if new_fail < old_fail:
                        status = "Success"
                    elif new_fail > old_fail:
                        status = "Failed"
                    
                    if old_fail > 0 and new_fail == 0:
                        status = "Success"
                        
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
                        "status": "Success",
                        "description": f"{diff_lines} 行の差分あり"
                    })
                    
            # 成果物に差分がない場合
            elif structured_data.get("analysis_type") == "no_differences":
                result["type"] = "artifact_identical"
                
                result["criteria"].append({
                    "name": "成果物一致", 
                    "status": "Success",
                    "description": "旧バージョンと新バージョンの成果物が完全に一致しています"
                })
                
                # 成功/エラー数の報告
                success_count = structured_data.get("success_count", 0)
                failure_count = structured_data.get("failure_count", 0)
                
                if success_count > 0:
                    result["criteria"].append({
                        "name": "成功件数", 
                        "status": "Success",
                        "description": f"成功: {success_count} 件"
                    })
                
                if failure_count == 0:
                    result["criteria"].append({
                        "name": "エラー/失敗数", 
                        "status": "Success",
                        "description": "エラーや失敗はありません"
                    })
                elif failure_count > 0:
                    result["criteria"].append({
                        "name": "エラー/失敗数", 
                        "status": "Failed",
                        "description": f"エラー/失敗: {failure_count} 件"
                    })
                    
            return result
        except Exception as e:
            # JSONデータの解析に失敗した場合は通常の処理を続行
            print(f"[WARNING] JSONデータ解析エラー: {e}")
    
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
                "status": "Success" if new_version < old_version else "Failed",
                "description": f"旧:{old_version:.1f}秒 → 新:{new_version:.1f}秒" + 
                              (f" ({improvement:.1f}%改善)" if improvement and improvement > 0 else "")
            })
            
            # パフォーマンス改善率の検証項目
            if improvement:
                if improvement > 20:
                    result["criteria"].append({
                        "name": "パフォーマンス改善率",
                        "status": "Success",
                        "description": f"改善率: {improvement:.1f}% (20%超の大幅改善)"
                    })
                elif improvement > 10:
                    result["criteria"].append({
                        "name": "パフォーマンス改善率",
                        "status": "Success",
                        "description": f"改善率: {improvement:.1f}% (10%超の改善)"
                    })
                elif improvement > 0:
                    result["criteria"].append({
                        "name": "パフォーマンス改善率",
                        "status": "Success",
                        "description": f"改善率: {improvement:.1f}% (10%未満の改善)"
                    })
                else:
                    result["criteria"].append({
                        "name": "パフォーマンス改善率",
                        "status": "Failed",
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
            "status": "Success" if new_count <= old_count else "Failed",
            "description": f"旧バージョン: {old_count}件 → 新バージョン: {new_count}件"
        })
        
        if old_count > 0 and new_count > 0:
            if old_count > new_count:
                improvement = ((old_count - new_count) / old_count * 100)
                result["criteria"].append({
                    "name": "エラー数改善率",
                    "status": "Success",
                    "description": f"エラー数が{improvement:.1f}%減少"
                })
            elif old_count < new_count:
                increase = ((new_count - old_count) / old_count * 100)
                result["criteria"].append({
                    "name": "エラー数増加率",
                    "status": "Failed",
                    "description": f"エラー数が{increase:.1f}%増加"
                })
        
        if new_count == 0:
            result["criteria"].append({
                "name": "エラー解消",
                "status": "Success",
                "description": "新バージョンでエラーが完全に解消されました"
            })
    
    # ログ比較情報の抽出
    if "Log comparison:" in content_str:
        result["type"] = "log_comparison"
        
        old_log_lines = 0
        new_log_lines = 0
        diff_count = 0
        log_errors_old = 0
        log_errors_new = 0
        
        # ログ情報を抽出
        for line in lines:
            if "Old log lines:" in line:
                match = re.search(r'Old log lines:\s*(\d+)', line)
                if match:
                    old_log_lines = int(match.group(1))
            elif "New log lines:" in line:
                match = re.search(r'New log lines:\s*(\d+)', line)
                if match:
                    new_log_lines = int(match.group(1))
            elif "Different lines:" in line:
                match = re.search(r'Different lines:\s*(\d+)', line)
                if match:
                    diff_count = int(match.group(1))
            elif "Errors in old log:" in line:
                match = re.search(r'Errors in old log:\s*(\d+)', line)
                if match:
                    log_errors_old = int(match.group(1))
            elif "Errors in new log:" in line:
                match = re.search(r'Errors in new log:\s*(\d+)', line)
                if match:
                    log_errors_new = int(match.group(1))
        
        # ログサイズの検証項目
        result["criteria"].append({
            "name": "ログサイズの変化",
            "status": "Success",
            "description": f"旧ログ: {old_log_lines}行 → 新ログ: {new_log_lines}行"
        })
        
        # 差分行数の検証項目
        if diff_count > 0:
            diff_percent = (diff_count / old_log_lines * 100) if old_log_lines > 0 else 0
            status = "Success"
            if diff_percent > 50:
                status = "Failed"
                desc = f"ログ内容に大きな変化があります: {diff_count}行の差分 ({diff_percent:.1f}%)"
            else:
                desc = f"ログ内容の差分: {diff_count}行 ({diff_percent:.1f}%)"
                
            result["criteria"].append({
                "name": "ログ内容の差分",
                "status": status,
                "description": desc
            })
        else:
            result["criteria"].append({
                "name": "ログ内容の一致",
                "status": "Success",
                "description": "ログ内容が完全に一致しています"
            })
        
        # エラー数の検証項目
        if log_errors_old > 0 or log_errors_new > 0:
            status = "Success"
            if log_errors_new > log_errors_old:
                status = "Failed"
                desc = f"ログ内のエラー数が増加: {log_errors_old}件 → {log_errors_new}件"
            elif log_errors_new < log_errors_old:
                desc = f"ログ内のエラー数が減少: {log_errors_old}件 → {log_errors_new}件"
            else:
                desc = f"ログ内のエラー数が変化なし: {log_errors_old}件"
                
            result["criteria"].append({
                "name": "ログ内のエラー数",
                "status": status,
                "description": desc
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
            
    # 複数の処理時間がある場合、まとめて検証項目を追加（平均改善率を計算）
    if file_times:
        # 個別ファイル処理の平均改善率
        total_improvement = sum(item["improvement"] for item in file_times)
        avg_improvement = total_improvement / len(file_times) if file_times else 0
        
        status = "Success"
        if avg_improvement > 20:
            status = "Success"
        elif avg_improvement > 10:
            status = "Success"
        elif avg_improvement <= 0:
            status = "Failed"
            
        result["criteria"].append({
            "name": "個別ファイル処理時間",
            "status": status,
            "description": f"平均改善率: {avg_improvement:.1f}% ({len(file_times)}ファイル)"
        })
    
    return result


def format_values(values):
    """
    値データをフォーマットする
    
    Parameters:
        values (list): 値データリスト
        
    Returns:
        str: フォーマットされた値データ文字列
    """
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


def format_criteria(criteria):
    """
    判定基準データをフォーマットする
    
    Parameters:
        criteria (list): 判定基準データリスト
        
    Returns:
        str: フォーマットされた判定基準データ文字列
    """
    if not criteria:
        return ""
        
    criteria_items = []
    for item in criteria:
        criteria_items.append(f"{item['name']}: {item['status']} - {item['description']}")
    return "\n".join(criteria_items)
