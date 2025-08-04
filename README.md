# アップデートツール動作検証システム

このシステムは、ツールの異なるバージョン間での動作の違いを検証するためのフレームワークです。ツールの実行、成果物の比較、レポートの生成を自動化し、バージョンアップに伴う変更点を可視化します。

## 概要

指定したツールのバージョンアップ後の動作を自動で検証し、成果物／ログの比較結果をレポートとして出力します。入力ファイル群を処理し、各バージョンでの出力結果の違いを明確にすることができます。

## 構成・前提

- 各ツールは `Apps/<tool名>/<バージョン>/` ディレクトリごとに実行ファイル（例: SampleTool.py, .exe, .bat など）を配置してください。
    - 例: `Apps/SampleTool/1.0.0/SampleTool.py`, `Apps/SampleTool/2.0.0/SampleTool.py`
- Pythonスクリプトの場合は `python` コマンド経由で自動実行されます。
- 成果物は各ツール自身が `artifacts/` ディレクトリに出力してください。
- 入力ファイルは `inputs/` ディレクトリに配置してください。

## 検証フェーズ

1. 動作：各バージョンのツールを順に実行
2. 成果物：各バージョン実行後の成果物を比較
3. ログ：各バージョン実行時のログを比較
4. 総括：各フェーズの結果をまとめる

## ステータス

|ステータス|説明|
|---|---|
|Success|正常に動作している|
|Failure|異常が発生している|
|Error|ツールの実行に失敗している|

## ディレクトリ構成

```plaintext
update_tools/
├── run_update_tool.py    # メインスクリプト
├── Apps/                 # ツール本体を配置するディレクトリ
│   └── SampleTool/       # サンプルツール
│       ├── 1.0.0/        # バージョン1.0.0
│       │   └── SampleTool.py
│       └── 2.0.0/        # バージョン2.0.0
│           └── SampleTool.py
├── inputs/               # 入力ファイル配置ディレクトリ
│   ├── sample1.txt
│   └── sample2.txt
├── artifacts/            # 成果物出力ディレクトリ（自動生成）
│   ├── SampleTool_1.0.0.txt
│   └── SampleTool_2.0.0.txt
├── logs/                 # ログディレクトリ（自動生成）
├── report.csv            # CSVレポート
└── report.html           # HTMLレポート
```

## 使い方

### 基本的な使用方法

```bash
# 例: SampleTool の 1.0.0 → 2.0.0 を比較
python run_update_tool.py SampleTool 1.0.0 2.0.0

# 入力ファイルを指定して実行
python run_update_tool.py SampleTool 1.0.0 2.0.0 --input "inputs/sample1.txt" --input "inputs/sample2.txt"

# 入力ファイルをパターンで指定
python run_update_tool.py SampleTool 1.0.0 2.0.0 --input-pattern "inputs/*.txt"

# デモモード（ダミーデータで動作）
python run_update_tool.py --demo

# レポートをクリアしてから実行
python run_update_tool.py --clean SampleTool 1.0.0 2.0.0
```

## オプション

| オプション | 説明 |
|------------|------|
| `--tools-dir` | ツール実行ファイルが置かれたディレクトリを指定（デフォルト: 'Apps'） |
| `--inputs-dir` | 入力ファイルが置かれたディレクトリを指定（デフォルト: 'inputs'） |
| `--input`, `-i` | 処理する入力ファイルを指定（複数指定可能） |
| `--input-pattern` | 入力ファイルをパターンで指定（例: "*.txt"） |
| `--clean` | 既存のレポート（CSV/HTML）をクリアして開始 |
| `--demo` | デモモードで動作（既定値を使用） |

## SampleToolの仕様

### バージョン1.0.0 の機能

- テキストファイルの基本統計情報を生成
  - 行数のカウント
  - 文字数のカウント
  - 単語数のカウント
  - 先頭10行の表示

### バージョン2.0.0 の機能

- バージョン1.0.0の全機能を含む
- 追加機能:
  - 平均行長の計算
  - 単語頻度解析（頻出上位5単語の表示）

## レポート形式

### CSV レポート (`report.csv`)

|Timestamp|Tool|Version_old|Version_new|Stage|Status|Message|Content|
|---|---|---|---|---|---|---|---|
|2025/08/04 12:00:00|SampleTool|1.0.0|2.0.0|動作|Success||項目1|
|2025/08/04 12:00:00|SampleTool|1.0.0|2.0.0|成果物|Success||項目2|
|2025/08/04 12:00:00|SampleTool|1.0.0|2.0.0|成果物|Success||項目3|
|2025/08/04 12:00:00|SampleTool|1.0.0|2.0.0|成果物|Success||項目4|
|2025/08/04 12:00:00|SampleTool|1.0.0|2.0.0|成果物|Success|||  
|2025/08/04 12:00:00|SampleTool|1.0.0|2.0.0|ログ|Success|||  
|2025/08/04 12:00:00|SampleTool|1.0.0|2.0.0|総括|Success|||  

各Stageの1検証項目につき、1行のレコードが生成されます。

### HTMLレポート (`report.html`)

- CSVレポートを整形したHTMLビュー
- ブラウザで閲覧可能
- HTML形式のテーブルでCSVと同等の内容を表示
- ログファイルへのリンクを含む

## カスタム比較関数の作成方法

このシステムでは、各ツールごとに成果物比較やログ比較をカスタマイズすることができます。カスタム関数は `comparators` ディレクトリに配置します。

### カスタム比較関数の命名規則

ファイル名: `<ツール名小文字>_comparator.py`

例: `sampletool_comparator.py`

### カスタム比較関数の実装

各モジュールには以下の関数を実装します:

### 成果物比較関数

```python
def compare_artifacts(old_file, new_file):
    """
    成果物を比較する関数
    
    Parameters:
        old_file (str): 旧バージョンの成果物ファイルパス
        new_file (str): 新バージョンの成果物ファイルパス
        
    Returns:
        bool: 比較結果（True: 正常、False: 異常）
    """
    # 比較ロジック
    return True  # 成功の場合
```

### ログ比較関数

```python
def compare_logs(old_log, new_log):
    """
    ログを比較する関数
    
    Parameters:
        old_log (str): 旧バージョンのログファイルパス
        new_log (str): 新バージョンのログファイルパス
        
    Returns:
        bool: 比較結果（True: 正常、False: 異常）
    """
    # 比較ロジック
    return True  # 成功の場合
```

カスタム比較関数が見つからない場合は、デフォルトの比較ロジックが使用されます。

## 注意事項

- 文字コードは日本語表示のため `cp932`（Windows向けShift-JIS）を使用
- 入力ファイルは `utf-8` エンコードを想定
- Windows環境で実行することを想定しています
- カスタム比較関数でエラーが発生した場合は、標準の比較ロジックが使用されます
- ヘルプ機能は今は一切不要です。



