# アップデートツール動作検証システム

このシステムは、ツールの異なるバージョン間での動作の違いを検証するためのフレームワークです。ツールの実行、成果物の比較、レポートの生成を自動化し、バージョンアップに伴う変更点を可視化します。

## 概要

指定したツールのバージョンアップ後の動作を自動で検証し、成果物／ログの比較結果をレポートとして出力します。入力ファイル群を処理し、各バージョンでの出力結果の違いを明確にすることができます。

本システムは、複数の検証項目（観点）ごとに検証結果を記録し、それぞれの項目を個別の行としてレポートに出力します。これにより、各検証項目ごとの結果（ステータス、タイムスタンプ、評価指標）を詳細に確認することができます。各ツールごとに独自の検証項目を定義することも可能です。

## 想定ユーザー

このシステムは以下の3つの役割を想定しています：

### 1. 一般ユーザー

- **想定スキル**: コマンドライン/シェルの基本操作
- **必要な知識**: Pythonの知識は不要
- **主な作業**:
  - 既存ツールの検証実行
  - レポートの閲覧
  - 結果の確認

- **操作例**:

```bash
python run_update_tool## コアモジュール** (`core/`):
  - `comparator.py`: 比較機能の基底クラスと比較ロジック（設定ベースコンパレータ含む）
  - `report.py`: レポート生成機能（CSV/HTML）
  - `tool_runner.py`: ツール実行と結果収集
  - `parser.py`: コマンドライン引数のパースampleTool 1.0.0 2.0.0
```

### 2. カスタマイザー

- **想定スキル**: YAML/JSON設定ファイルの編集 (基本的なPythonプログラミングは不要)
- **必要な知識**: 設定ファイルの編集
- **主な作業**:
  - 新しいツールの検証項目設定
  - 既存の比較ロジックの調整
  - カスタム検証項目の追加

- **カスタマイズ例**:
  - 設定ファイルによる比較ロジックの定義 (`comparators/configs/ツール名.yaml`)
  - `core/report.py` の `TOOL_SPECIFIC_ITEMS` の編集
  - 必要に応じて新しいコンパレータの実装（上級者向け）

### 3. 開発者

- **想定スキル**: Pythonプログラミング、ソフトウェア設計
- **必要な知識**: システムアーキテクチャ、モジュール設計
- **主な作業**:
  - システム全体の保守と拡張
  - 新機能の追加
  - バグ修正
  - パフォーマンス最適化

## 構成・前提

- 各ツールは `Apps/<tool名>/<バージョン>/` ディレクトリごとに実行ファイル（例: SampleTool.py, .exe, .bat など）を配置してください。
  - 例: `Apps/SampleTool/1.0.0/SampleTool.py`, `Apps/SampleTool/2.0.0/SampleTool.py`
- Pythonスクリプトの場合は `python` コマンド経由で自動実行されます。
- 成果物は各ツール自身が `artifacts/` ディレクトリに出力してください。
- 入力ファイルは `inputs/` ディレクトリに配置してください。

## 検証観点（フェーズ）

システムは以下の主要な観点で検証を行います：

1. **動作検証**：各バージョンのツールを順に実行し、正常に動作するか確認
   - 起動・実行確認：ツールが正常に起動し、処理を完了できるか
   
2. **成果物検証**：各バージョン実行後の成果物を比較し、差異や問題を検出
   - 出力フォーマット検証：出力ファイルのフォーマットに変更がないか
   - 計算結果精度検証：計算結果の精度が維持・向上しているか
   - パフォーマンス検証：実行速度やメモリ使用量などに問題がないか
   - サマリー情報検証：結果サマリーが正確に生成されているか
   
3. **ログ検証**：各バージョン実行時のログを比較し、問題がないか確認
   - 警告・エラー解析：新たな警告やエラーが発生していないか
   - ログdiff分析：新旧バージョン間のログ差分を視覚的に比較検証
   
4. **総括**：すべての検証結果をまとめ、全体的な評価を行う
   - バージョン互換性評価：新バージョンが旧バージョンと互換性を保っているか

各観点の検証結果は、個別の行としてレポートに記録されます。各検証項目ごとに実行時刻（タイムスタンプ）と評価指標が記録されるため、実行順序や判定基準を明確に確認できます。検証項目はツールの種類や目的に応じてカスタマイズ可能です。

### 評価指標

各検証項目には、判定の基準となる評価指標が定義されており、レポートに表示されます。これにより、どのような基準で判定が行われたかを明確に把握できます。例：

- 出力フォーマット検証：「許容変更: なし」
- 計算結果精度検証：「許容誤差: 1%」
- パフォーマンス検証：「許容遅延: 10%」
- サマリー情報検証：「確認キーワード: キーワード1, キーワード2, ...」

## ステータス

検証結果は以下のいずれかのステータスで表されます：

|ステータス|説明|
|---|---|
|Success|正常に動作している - 検証項目をパスした状態|
|Failed|異常が発生している - 検証項目で問題が検出された状態|
|Error|ツールの実行に失敗している - 検証自体ができなかった状態|
|N/A|評価対象外 - 成果物がない場合など、検証自体が不要または不可能な状態|

## ディレクトリ構成

```plaintext
Verup_verification_tool/
├── run_update_tool.py    # メインスクリプト
├── core/                 # コア機能モジュール
│   ├── comparator.py     # 比較機能の基底クラス
│   ├── config_comparator.py # 設定ベース比較システム
│   ├── report.py         # レポート生成機能
│   └── tool_runner.py    # ツール実行機能
├── utils/                # ユーティリティ機能
│   ├── file_utils.py     # ファイル操作ユーティリティ
│   └── parser.py         # パース機能ユーティリティ
├── Apps/                 # ツール本体を配置するディレクトリ
│   ├── SampleTool/       # サンプルツール
│   │   ├── 1.0.0/        # バージョン1.0.0
│   │   │   └── SampleTool.py
│   │   └── 2.0.0/        # バージョン2.0.0
│   │       └── SampleTool.py
│   └── ICC2_smoke.py     # 他のサンプルツール
├── comparators/          # カスタム比較関数モジュール
│   ├── __init__.py
│   ├── sampletool_comparator.py
│   ├── icc2_smoke_comparator.py
│   └── configs/          # YAML/JSON設定ファイル（カスタマイザー向け）
│       └── sampletool.yaml
├── inputs/               # 入力ファイル配置ディレクトリ
│   ├── sample1.txt
│   └── sample2.txt
├── artifacts/            # 成果物出力ディレクトリ（自動生成）
│   ├── SampleTool_1.0.0.txt
│   └── SampleTool_2.0.0.txt
├── logs/                 # ログディレクトリ（自動生成）
│   └── ToolName_OldVersion_NewVersion_YYYYMMDD_HHMMSS.log
├── Apps/                 
│   └── ICC2_smoke/       # ツール固有のディレクトリ
│       ├── logs/         # ツール固有のログディレクトリ
│       │   └── diffs/    # ログ比較diff HTMLファイル
├── docs/                 # ドキュメント
│   └── config_comparator_guide.md # 設定ベースコンパレータガイド
├── report.csv            # CSVレポート
└── report.html           # HTMLレポート
```

## 一般ユーザーガイド

このセクションは、Pythonの知識がなくても本システムを使用できる「一般ユーザー」向けのガイドです。

### 基本的な使用方法

バージョン間の比較は以下のように簡単に実行できます：

```bash
# 例: SampleTool の 1.0.0 → 2.0.0 を比較
python run_update_tool.py SampleTool 1.0.0 2.0.0

# 入力ファイルを指定して実行
python run_update_tool.py SampleTool 1.0.0 2.0.0 --input "inputs/sample1.txt" --input "inputs/sample2.txt"

# 入力ファイルをパターンで指定
python run_update_tool.py SampleTool 1.0.0 2.0.0 --input-pattern "inputs/*.txt"

# デモモード（全ての利用可能なツールをサンプル入力で実行）
python run_update_tool.py --demo

# レポートをクリアしてから実行
python run_update_tool.py --clean SampleTool 1.0.0 2.0.0
```

### 利用可能なツールの確認

システムに登録されているツールを確認するには：

```bash
python run_update_tool.py --list
```

### 実行結果の確認

実行が完了すると、以下のファイルが生成されます：

1. **CSVレポート**: `report.csv` - 各検証項目ごとの結果を行単位で記録
   - Windows環境: エクセルまたはメモ帳で開くことができます
   - 日本語文字化けの問題はcp932エンコーディングにより回避されています
   - 各検証項目ごとに個別のタイムスタンプと評価指標が記録されます

2. **HTMLレポート**: `report.html` - CSVと同じ内容をブラウザで見やすく表示
   - 一般的なブラウザ（Chrome、Edge、Firefox）で開くことができます
   - 項目ごとに色分けされ、成功/失敗が一目でわかります
   - 成果物やログファイルへのリンクを含みます
   - 各検証項目に対する評価指標が表示されます

3. **ログファイル**: `logs/` ディレクトリ内に各実行のログを保存
   - 各実行の詳細なログが日時付きで保存されます
   - `Apps/<ツール名>/logs/diffs/` ディレクトリには新旧バージョンのログ差分を視覚的に表示するHTMLファイルが生成されます
   - レポートの「ログ検証」項目からこのdiffファイルにリンクされています

4. **成果物**: `artifacts/` ディレクトリ内に各ツールの出力結果を保存
   - 各バージョンごとの出力ファイルが保存されます

### トラブルシューティング

よくある問題と解決方法：

1. **ツールが見つからない**
   - `Apps/<ツール名>/<バージョン>/` ディレクトリにツールが正しく配置されているか確認してください
   
2. **レポートに項目が表示されない**
   - 検証項目の設定が正しいか確認してください（カスタマイザー向け）
   
3. **実行エラー**
   - ログディレクト���（`logs/`）内の最新のログファイルを確認してください

### コマンドラインオプション

| オプション | 説明 |
|------------|------|
| `--tools-dir` | ツール実行ファイルが置かれたディレクトリを指定（デフォルト: 'Apps'） |
| `--inputs-dir` | 入力ファイルが置かれたディレクトリを指定（デフォルト: 'inputs'） |
| `--input`, `-i` | 処理する入力ファイルを指定（複数指定可能） |
| `--input-pattern` | 入力ファイルをパターンで指定（例: "*.txt"） |
| `--clean` | 既存のレポート（CSV/HTML）をクリアして開始 |
| `--demo` | デモモードで動作（既定値を使用） |
| `--no-report` | レポート生成を無効化 |
| `--csv-report` | CSVレポートのファイル名を指定（デフォルト: 'report.csv'） |
| `--html-report` | HTMLレポートのファイル名を指定（デフォルト: 'report.html'） |
| `--list` | 利用可能なツールの一覧を表示 |

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

検証結果は以下の2つの形式で出力されます：

### CSV レポート (`report.csv`)

各検証観点の各項目ごとに1行を使用して記録します。一つのツールの検証に対して複数行のレコードが生成されます。

以下のカラムを含みます:

| Timestamp           | Tool       | Version_old | Version_new | 観点     | 判定     | 判定メモ   | 項目                 | リンク                                |
|---------------------|------------|-------------|-------------|----------|----------|------------|--------------------|--------------------------------------|
| 2025/08/04 12:00:00 | SampleTool | 1.0.0       | 2.0.0       | 動作     | Success  | 正常終了    | 起動・実行確認        | [artifact](artifact.html)            |
| 2025/08/04 12:00:00 | SampleTool | 1.0.0       | 2.0.0       | 成果物   | Success  | 差異なし    | 出力フォーマット検証   | [report.html](report.html)           |
| 2025/08/04 12:00:00 | SampleTool | 1.0.0       | 2.0.0       | 成果物   | Success  | 期待通り    | 計算結果精度検証      | [report.limit.csv](report.limit.csv) |
| 2025/08/04 12:00:00 | SampleTool | 1.0.0       | 2.0.0       | 成果物   | Success  | 5%向上     | パフォーマンス検証    | [timing.log](timing.log)             |
| 2025/08/04 12:00:00 | SampleTool | 1.0.0       | 2.0.0       | 成果物   | Success  | 問題なし    | サマリー情報検証      | [summary.txt](summary.txt)           |
| 2025/08/04 12:00:00 | SampleTool | 1.0.0       | 2.0.0       | ログ     | Success  | エラーなし   | 警告・エラー解析      | [logfile.txt](logfile.txt)           |
| 2025/08/04 12:00:00 | SampleTool | 1.0.0       | 2.0.0       | ログ     | Success  | 差分確認済   | ログ検証            | [log_diff.html](log_diff.html)        |
| 2025/08/04 12:00:00 | SampleTool | 1.0.0       | 2.0.0       | 総括     | Success  | 安全に移行可 | バージョン互換性評価   | [overview.html](overview.html)       |

**重要**: 各検証観点（動作、成果物、ログ、総括）と各項目の組み合わせで1行のレコードが生成されます。同じツールの検証であっても、複数の行に分かれて記録されます。検証項目はツールの種類や目的によってカスタマイズ可能です。システムはデフォルトの検証項目を備えていますが、ツール固有の検証項目も定義できます（例：ICC2_smokeツールには「メモリ使用量検証」という特有の検証項目があります）。

各検証項目には、判定に使用された「評価指標」も記録されるため、判定の根拠が明確になります。タイムスタンプ欄には各検証が実際に実行された時刻が記録され、処理の流れを時系列で追跡できます。成果物やログの有無に関わらず、総括項目のようにシステムにとって必要な検証は常に実行されます。

### HTMLレポート (`report.html`)

CSVレポートと同じ内容を視覚的に見やすく表示するHTMLビューです：

- CSVと同様に、各検証観点と項目ごとに1行を使用
- ブラウザで閲覧可能（Chrome/Edge/Firefoxなどの一般的なブラウザを推奨）
- サマリー情報（成功・失敗・エラー件数）を表示
- 検証結果に応じた色分け表示（Success: 緑、Failed: 赤、Error: 黄）
- 各成果物やログファイルへのリンクを含む
- ログ検証項目からは新旧バージョンのログdiffを色分け表示するHTMLファイルへリンク
- 詳細分析セクションで各検証項目の詳細情報を確認可能

## カスタマイザーガイド

このセクションは「カスタマイザー」役割のユーザー向けに、新しいツールを追加する方法や検証項目をカスタマイズする方法について説明します。

### カスタム比較機能とツール固有の検証項目

このシステムはモジュール化されており、各ツールごとにカスタム比較ロジックを実装することができます。また、ツールごとに異なる検証項目を定義することで、ツールの特性に合わせた検証レポートを生成できます。

カスタマイザーには **2つの方法** でツール固有の比較ロジックを実装できます：

1. **設定ファイルベース（推奨・簡単）**: YAMLまたはJSONファイルで設定するだけ
2. **Pythonクラスベース（高度）**: 完全なカスタマイズが必要な場合

### 方法1: 設定ファイルによる比較ロジックの定義（推奨）

1. `comparators/configs` ディレクトリに新しいYAMLまたはJSONファイルを作成します:
   - ファイル名: `<ツール名小文字>.yaml` または `<ツール名小文字>.json`
   - 例: `sampletool.yaml`
   - 詳細なガイドは [設定ベースコンパレータガイド](docs/config_comparator_guide.md) を参照

2. 以下のような設定ファイルを作成します。評価指標も設定できます:

```yaml
# ツール実行設定
execute_command: "python {tool_path} {input_file} {parameters}"
old_artifact_pattern: "MyTool_{old_version}.txt"
new_artifact_pattern: "MyTool_{new_version}.txt"
input_files: 
  - "sample*.txt"  # グロブパターン使用可能
parameters:
  - "-o"
  - "{output_file}"

# 比較方法の設定
comparison_methods:
  # ファイル形式やサイズの大きな変化をチェック
  format_check: true
  
  # 出力ファイルの行数をチェック
  line_count: true
  
  # 出力内容の差分をチェック
  content_diff: true
  
  # 特定のキーワードの出現回数をチェック
  keyword_check:
    - "Total lines"
    - "Total characters"
    - "Total words"

# 評価指標の設定
verification_criteria:
  # フォーマット検証の評価指標
  format:
    allowed_changes: false  # フォーマット変更を許容するか
  
  # 精度検証の評価指標
  precision:
    tolerance_percent: 1.0  # 許容誤差率
  
  # パフォーマンス検証の評価指標
  performance:
    tolerance_percent: 10.0  # 許容遅延率
    - "重要な単語1"
    - "重要な単語2"
    
  # 正規表現パターンによるチェック
  custom_patterns:
    # 数値データを抽出して比較
    - name: "重要な数値"
      pattern: "重要な値:\\s*(\\d+\\.\\d+)"
```

設定ファイルベースのコンパレータは、ファイルの差分を自動的に検出し、設定された項目に基づいて検証結果を生成します。

### 方法2: Pythonクラスによる比較ロジックの実装（高度）

より複雑な比較ロジックが必要な場合は、Pythonクラスを実装します:

1. `comparators` ディレクトリに新しいファイルを作成します:
   - ファイル名: `<ツール名小文字>_comparator.py`
   - 例: `sampletool_comparator.py`

2. 以下のようなクラスを実装します:

```python
from core.comparator import BaseComparator

class SampletoolComparator(BaseComparator):
    """SampleTool用のカスタム比較クラス"""
    
    def compare_artifacts(self, old_file, new_file):
        """
        成果物を比較する関数
        
        Parameters:
            old_file (str): 旧バージョンの成果物ファイルパス
            new_file (str): 新バージョンの成果物ファイルパス
            
        Returns:
            dict: 比較結果 {'status': 'Success'/'Failed'/'Error', 'detail': '詳細情報'}
        """
        # 比較ロジック
        status = 'Success'  # または 'Failed', 'Error'
        detail = '検証成功'  # 詳細情報
        
        return {
            'status': status,
            'detail': detail
        }
    
    def compare_logs(self, old_log, new_log):
        """
        ログを比較する関数
        
        Parameters:
            old_log (str): 旧バージョンのログファイルパス
            new_log (str): 新バージョンのログファイルパス
            
        Returns:
            dict: 比較結果 {'status': 'Success'/'Failed'/'Error', 'detail': '詳細情報', 'log_diff': 'ログdiffへのパス'}
        """
        # 比較ロジック
        status = 'Success'
        detail = 'ログ検証成功'
        
        # ログdiffの生成
        diff_file = self._generate_log_diff(old_log, new_log)
        
        return {
            'status': status,
            'detail': detail,
            'log_diff': diff_file  # ログdiffへのパス
        }
        
    def _generate_log_diff(self, old_log, new_log):
        """
        新旧ログのdiffを比較するHTMLファイルを生成する
        
        Returns:
            str: 生成したHTMLファイルへのパス
        """
        # diff生成ロジック
        # ...
        
        return "logs/diffs/log_diff.html"  # 生成したdiffファイルへのパス
```

カスタムコンパレータが見つからない場合や、エラーが発生した場合は、標準の比較ロジックが使用されます。

### ツール固有の検証項目の定義

各ツールには独自の検証項目を設定することができます。これは `core/report.py` の `TOOL_SPECIFIC_ITEMS` ディクショナリで定義します：

```python
# 各ツールの検証項目をカスタマイズできる設定
TOOL_SPECIFIC_ITEMS = {
    'sampletool': [
        {'phase': '動作', 'item': '起動・実行確認', 'success_memo': '正常終了', 'failed_memo': '異常終了', 'link_type': 'log'},
        {'phase': 'ログ', 'item': 'ログ検証', 'success_memo': '差分確認済', 'failed_memo': '差分に問題あり', 'link_type': 'log_diff'},
        # 他の検証項目...
    ],
    'icc2_smoke': [
        {'phase': '動作', 'item': '起動・実行確認', 'success_memo': '正常終了', 'failed_memo': '異常終了', 'link_type': 'log'},
        # icc2_smoke固有の検証項目
        {'phase': '成果物', 'item': 'メモリ使用量検証', 'success_memo': '改善', 'failed_memo': '悪化', 'link_type': 'log'},
        {'phase': 'ログ', 'item': 'ログ検証', 'success_memo': '差分確認済', 'failed_memo': '差分に問題あり', 'link_type': 'log_diff'},
        # 他の検証項目...
}
```

各検証項目は以下の要素で定義します：

- `phase`: 検証観点（動作、成果物、ログ、総括など）
- `item`: 検証項目名
- `success_memo`: 成功時のメモ
- `failed_memo`: 失敗時のメモ
- `link_type`: リンクタイプ（log, new_artifact, compare_artifacts, report）

### 新しいツールの追加手順

カスタマイザーが新しいツールをシステムに追加する基本的な手順は以下の通りです：

1. **ツールの配置**
   - `Apps/<新ツール名>/<バージョン>/` にツール実行ファイルを配置します

2. **カスタム比較ロジックの作成**（オプション）
   - **簡単な方法（推奨）**: `comparators/configs/<新ツール名小文字>.yaml` を作成
   - **高度な方法**: `comparators/<新ツール名小文字>_comparator.py` を作成

3. **検証項目の定義**
   - `core/report.py` の `TOOL_SPECIFIC_ITEMS` ディクショナリに新しいツール用の検証項目を追加します

4. **テスト実行**
   - `python run_update_tool.py <新ツール名> <旧バージョン> <新バージョン> --demo` で動作確認します

### カスタマイズの実例: 新ツール追加手順（簡易版）

以下は、新しいツール「MyAnalyzer」を追加する簡単な手順です：

1. ツール実行ファイルを配置:

   ```plaintext
   Apps/MyAnalyzer/1.0.0/MyAnalyzer.py
   Apps/MyAnalyzer/2.0.0/MyAnalyzer.py
   ```

2. 設定ファイルを作成:
   `comparators/configs/myanalyzer.yaml`

   ```yaml
   # 実行設定
   execute_command: "python {tool_path} {input_file} -f {output_file}"
   old_artifact_pattern: "MyAnalyzer_{old_version}_result.json"
   new_artifact_pattern: "MyAnalyzer_{new_version}_result.json"
   input_files: 
     - "sample_data.txt"
   
   # 比較方法
   comparison_methods:
     format_check: true
     content_diff: true
     keyword_check:
       - "accuracy"
       - "precision"
       - "recall"
     custom_patterns:
       - name: "精度値"
         pattern: "accuracy:\\s*(\\d+\\.\\d+)"
       - name: "実行時間"
         pattern: "execution time:\\s*(\\d+\\.\\d+)\\s*sec"
   ```

3. 検証項目の定義（オプション）:
   `core/report.py` に以下を追加

   ```python
   TOOL_SPECIFIC_ITEMS = {
       # 既存のエントリ...
       'myanalyzer': [
           {'phase': '動作', 'item': '起動・実行確認', 'success_memo': '正常終了', 'failed_memo': '異常終了', 'link_type': 'log'},
           {'phase': '成果物', 'item': '精度検証', 'success_memo': '精度維持/向上', 'failed_memo': '精度低下', 'link_type': 'compare_artifacts'},
           {'phase': '成果物', 'item': '実行時間検証', 'success_memo': '実行時間短縮', 'failed_memo': '実行時間増加', 'link_type': 'log'},
       ]
   }
   ```

4. 実行:

   ```bash
   python run_update_tool.py MyAnalyzer 1.0.0 2.0.0 --input "inputs/sample_data.txt"
   ```

以上の手順で、プログラミングをほとんど必要とせずに新しいツールの比較ロジックを追加できます。

### 検証項目のカスタマイズ例

典型的なカスタマイズシナリオを以下に示します：

#### 1. 特定の処理時間を検証項目に追加

```python
# core/report.py に追加
TOOL_SPECIFIC_ITEMS = {
    'mynewtool': [
        {'phase': '動作', 'item': '起動・実行確認', 'success_memo': '正常終了', 'failed_memo': '異常終了', 'link_type': 'log'},
        {'phase': '成果物', 'item': '出力フォーマット検証', 'success_memo': '差異なし', 'failed_memo': 'フォーマット変更あり', 'link_type': 'new_artifact'},
        {'phase': '成果物', 'item': '実行時間検証', 'success_memo': '50%高速化', 'failed_memo': '遅延あり', 'link_type': 'log'},
        # 他の項目...
    ]
}
```

#### 2. 検証ロジックのカスタマイズ

```python
# comparators/mynewtool_comparator.py
from core.comparator import BaseComparator

class MynewtoolComparator(BaseComparator):
    """カスタム比較クラス"""
    
    def _compare(self, old_result, new_result):
        # 基本的な比較
        result = super()._compare(old_result, new_result)
        
        # カスタム検証ロジック
        # 例: 実行時間の測定と比較
        old_runtime = self._extract_runtime(old_result)
        new_runtime = self._extract_runtime(new_result)
        
        if new_runtime < old_runtime * 0.8:  # 20%以上の改善
            result['runtime_improved'] = True
            result['runtime_detail'] = f"実行時間が改善: {old_runtime:.2f}秒 → {new_runtime:.2f}秒"
        
        return result
    
    def _extract_runtime(self, result):
        # 実行時間を抽出するロジック
        # ...
        return runtime
```

## 開発者ガイド

このセクションは、システム全体を保守・拡張する「開発者」向けの情報を提供します。

### システムアーキテクチャ

本システムは以下のモジュール構成で設計されています：

- **コアモジュール** (`core/`):
  - `comparator.py`: 比較機能の基底クラスと比較ロジック
  - `report.py`: レポート生成機能（CSV/HTML）
  - `tool_runner.py`: ツール実行と結果収集
  - `parser.py`: コマンドライン引数のパース

- **ユーティリティ** (`utils/`):
  - `file_utils.py`: ファイル操作関連の機能
  - `parser.py`: 特殊形式のパース機能

- **コンパレータ** (`comparators/`):
  - 各ツール固有のカスタム比較機能を実装

- **実行スクリプト**:
  - `run_update_tool.py`: メインエントリーポイント

### 拡張・修正のガイドライン

1. **新機能追加**
   - 関連するモジュールに追加するか、新規モジュールを作成
   - 既存インターフェースとの互換性を維持

2. **コード修正**
   - 各モジュールの責務を明確に分離
   - ユニットテストでの動作確認を推奨

3. **インターフェース変更**
   - API変更時は下位互換性に配慮
   - ドキュメント（README）の更新が必須


## システム実装の特徴

- **モジュール化**: コア機能、ユーティリティ、コンパレータなどが分離され、拡張性が高い設計
- **柔軟な検証観点**: 各ツールに対して複数の観点から詳細な検証が可能
- **詳細なレポート**: 各検証項目ごとに個別の行を使用して詳細に結果を記録
- **カスタマイズ可能**: 各ツールに特化したカスタム比較ロジックを実装可能
- **役割分担**: 一般ユーザー、カスタマイザー、開発者の役割に応じた使い方が可能

## 注意事項

- **文字コード**:
  - CSVレポートはWindowsの日本語表示に最適化するためcp932（Shift-JIS）で保存
  - HTMLレポートはUTF-8で保存（一般的なブラウザで正しく表示）
  - 入力ファイルはUTF-8を推奨

- **実行環境**:
  - Windows環境での実行を想定
  - Linux環境（GitHub Actions含む）でも動作
  - Python 3.6以上が必要

- **ステータス**:
  - 検証結果は「Success」「Failed」「Error」の3種類に統一

- **パス指定**:
  - ディレクトリパスの最後にスラッシュは不要
  - 絶対パスよりも相対パスの使用を推奨

## 継続的インテグレーション

このプロジェクトには、GitHub Actionsによる継続的インテグレーション（CI）設定が含まれています。

### GitHub Actions

プッシュやプルリクエストが行われた際に、自動的に以下の処理が実行されます：

1. Pythonのセットアップ
2. 依存パッケージのインストール
3. デモモードでの検証ツール実行
4. 生成されたレポートのアーティファクト保存

手動でワークフローを実行することも可能です（GitHub リポジトリのActions タブから）。

生成されたレポートやログファイルは、GitHub Actionsのアーティファクトとして保存され、ダウンロードして確認することができます。



