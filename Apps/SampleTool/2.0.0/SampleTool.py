#!/usr/bin/env python3
import sys
import os
import re

def process_file(input_file, output_file):
    """入力ファイルを処理して結果をファイルに出力する（v2.0.0）"""
    try:
        print(f"[SampleTool v2.0.0] Processing {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f_in:
            content = f_in.read()
            
        # バージョン2.0.0の処理（1.0.0より高度な処理を行う）
        lines = content.splitlines()
        char_count = len(content)
        word_count = len(content.split())
        
        # 2.0.0での追加機能: 単語頻度分析
        word_freq = {}
        words = re.findall(r'\b\w+\b', content.lower())
        for word in words:
            if len(word) > 2:  # 3文字以上の単語のみ
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 頻出上位5単語
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Windows環境ではcp932（Shift-JIS）を使用
        with open(output_file, 'a', encoding='cp932') as f_out:
            f_out.write(f"=== {os.path.basename(input_file)} の処理結果 ===\n")
            f_out.write(f"行数: {len(lines)}\n")
            f_out.write(f"文字数: {char_count}\n")
            f_out.write(f"単語数: {word_count}\n")
            f_out.write(f"平均行長: {char_count / len(lines) if lines else 0:.2f} 文字\n")
            
            # 頻出単語表示（2.0.0の新機能）
            f_out.write(f"\n頻出単語トップ5:\n")
            for word, count in top_words:
                f_out.write(f"- {word}: {count}回\n")
            
            f_out.write(f"\n先頭10行:\n")
            for i, line in enumerate(lines[:10]):
                f_out.write(f"{i+1}: {line}\n")
            f_out.write("\n")
        
        return True
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

def main():
    print("[SampleTool v2.0.0] Hello from version 2.0.0!")
    # 絶対パスでartifactsディレクトリを作成
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    artifacts_dir = os.path.join(root_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    
    # 成果物出力ファイル
    output_file = os.path.join(artifacts_dir, "SampleTool_2.0.0.txt")
    
    # 基本情報を出力
    with open(output_file, "w", encoding="cp932") as f:
        f.write("SampleTool 2.0.0 実行結果\n")
        f.write("=======================\n\n")
        f.write("※ バージョン2.0.0では単語頻度解析機能が追加されました\n\n")
    
    # 入力ファイルがコマンドライン引数として与えられている場合は処理
    input_files = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if input_files:
        for input_file in input_files:
            process_file(input_file, output_file)
        print(f"[INFO] {len(input_files)}個のファイルを処理しました")
    else:
        with open(output_file, "a", encoding="cp932") as f:
            f.write("入力ファイルはありません。\n")
        print("[INFO] 入力ファイルはありません")
    
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()
