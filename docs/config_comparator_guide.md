# 設定ベースコンパレータガイド

このガイドでは、YAML/JSON設定ファイルを使用してカスタム比較ロジックを簡単に実装する方法について説明します。設定ファイルベースのコンパレータを使うと、Pythonプログラミングの知識がなくても、ツール固有の比較ロジックを実装することができます。

## 設定ファイルの基本構造

設定ファイルはYAMLまたはJSON形式で記述し、以下のセクションから構成されます：

1. **実行設定** - ツールの実行方法を定義
2. **比較方法** - 成果物の比較方法を定義
3. **検証基準** - 合格/不合格の判定基準を定義

## 設定ファイルの配置

設定ファイルは以下のディレクトリに配置します：

```plaintext
comparators/configs/<ツール名小文字>.yaml
```

または

```plaintext
comparators/configs/<ツール名小文字>.json
```

例：`sampletool.yaml`

## 設定項目の詳細

### 1. 実行設定

| 設定キー | 説明 | 例 |
|---------|------|-----|
| `execute_command` | ツール実行コマンドのテンプレート | `"python {tool_path} {input_file} {parameters}"` |
| `old_artifact_pattern` | 旧バージョン成果物のファイル名パターン | `"Tool_{old_version}.txt"` |
| `new_artifact_pattern` | 新バージョン成果物のファイル名パターン | `"Tool_{new_version}.txt"` |
| `input_files` | 入力ファイルのリスト（グロブパターン可） | `["sample.txt", "test*.txt"]` |
| `parameters` | コマンドラインパラメータのリスト | `["-o", "{output_file}"]` |

### 2. 比較方法

| 設定キー | 説明 | 例 |
|---------|------|-----|
| `format_check` | ファイル形式やサイズの変化をチェック | `true` or `false` |
| `line_count` | 出力ファイルの行数をチェック | `true` or `false` |
| `content_diff` | 出力内容の差分をチェック | `true` or `false` |
| `keyword_check` | 特定キーワードの出現回数チェック | `["重要な単語", "エラー"]` |
| `custom_patterns` | 正規表現パターンによるチェック | 個別に定義（下記参照） |

#### カスタムパターン

```yaml
custom_patterns:
  - name: "精度値"
    pattern: "accuracy:\\s*(\\d+\\.\\d+)"
  - name: "メモリ使用量"
    pattern: "memory usage:\\s*(\\d+)\\s*MB"
```

### 3. 検証基準

```yaml
verification_criteria:
  performance:
    tolerance_percent: 10  # 許容するパフォーマンス低下（%）
  format:
    allowed_changes: false  # 出力フォーマットの変更を許可するか
  precision:
    tolerance_percent: 1  # 許容する精度の変動（%）
```

## 完全な設定例

```yaml
# MyTool用の設定ファイル例
execute_command: "python {tool_path} {input_file} {parameters}"
old_artifact_pattern: "MyTool_{old_version}_result.json"
new_artifact_pattern: "MyTool_{new_version}_result.json"
input_files: 
  - "sample_data.txt"
  - "test_*.txt"
parameters:
  - "-o"
  - "{output_file}"
  - "--verbose"

# 比較方法の設定
comparison_methods:
  format_check: true
  line_count: true
  content_diff: true
  keyword_check:
    - "Total"
    - "Average"
    - "Error"
  custom_patterns:
    - name: "精度値"
      pattern: "Accuracy:\\s*(\\d+\\.\\d+)"
    - name: "処理時間"
      pattern: "Processing time:\\s*(\\d+\\.\\d+)\\s*sec"
    - name: "メモリ使用量"
      pattern: "Memory usage:\\s*(\\d+)\\s*MB"

# 検証基準
verification_criteria:
  performance:
    tolerance_percent: 10
  format:
    allowed_changes: false
  precision:
    tolerance_percent: 1
```

## 利用可能な変数

設定ファイル内で使用できる変数は以下の通りです：

- `{tool_path}` - ツールの実行ファイルパス
- `{input_file}` - 入力ファイルパス
- `{output_file}` - 出力ファイルパス
- `{old_version}` - 旧バージョン番号
- `{new_version}` - 新バージョン番号
- `{parameters}` - パラメータ文字列

## トラブルシューティング

1. **比較が実行されない**
   - 設定ファイルの名前が `<ツール名小文字>.yaml` または `<ツール名小文字>.json` になっていることを確認
   - 設定ファイルの構文が正しいことを確認

2. **実行エラー**
   - コンソール出力を確認して詳細なエラーメッセージを確認
   - `execute_command` の形式が正しいことを確認

3. **誤検出が多い**
   - `custom_patterns` を調整して、より正確なパターンを定義
   - `verification_criteria` で許容値を調整
