# クイックスタートガイド

Face Mosaic Tool v2.0を素早く始めるためのガイドです。

## 🚀 5分で始める

### 1. システム要件の確認

```bash
python3 --version  # Python 3.8以上が必要
```

### 2. インストール

```bash
git clone https://github.com/your-username/face-mosaic-tool.git
cd face-mosaic-tool
pip install -r requirements.txt
```

### 3. 動作確認

```bash
python3 cli.py --info
```

以下のような出力が表示されれば正常です：

```
=== システム情報 ===
platform: Darwin
opencv_version: 4.11.0
yunet_supported: True

=== 要件チェック ===
✓ opencv_version_ok: True
✓ system_supported: True

✓ OpenCV YuNet (推奨)
```

### 4. 最初の処理

#### CLI版で単一画像を処理

```bash
# テスト画像をダウンロード（例）
curl -o test.jpg https://example.com/sample-image.jpg

# 処理実行
python3 cli.py -i test.jpg -o test_processed.jpg
```

#### GUI版を起動

```bash
python3 gui.py
```

## 📁 サンプルデータでテスト

### サンプル画像の準備

```bash
mkdir sample_images
# お手持ちの画像ファイルをsample_imagesに配置
```

### バッチ処理の実行

```bash
python3 cli.py -i sample_images -o processed_images
```

## ⚙️ 基本設定

### モザイク比率の調整

```bash
# 細かいモザイク
python3 cli.py -i input -o output -r 0.05

# 粗いモザイク
python3 cli.py -i input -o output -r 0.3
```

### ブラーモザイクの使用

```bash
python3 cli.py -i input -o output --blur
```

### 信頼度閾値の調整

```bash
# 高い信頼度（誤検出を減らす）
python3 cli.py -i input -o output -c 0.8

# 低い信頼度（検出漏れを減らす）
python3 cli.py -i input -o output -c 0.4
```

## 🔧 よくある問題と解決方法

### OpenCVバージョンエラー

```
エラー: YuNetにはOpenCV 4.5.4以上が必要です
```

**解決方法:**
```bash
pip install --upgrade opencv-python
```

### モデルダウンロードエラー

```
エラー: モデルのダウンロードに失敗しました
```

**解決方法:**
1. インターネット接続を確認
2. ファイアウォール設定を確認
3. 再実行

### メモリ不足

```
エラー: メモリが不足しています
```

**解決方法:**
1. 大きな画像は自動的にリサイズされます
2. 一度に処理するファイル数を減らす
3. システムメモリを増やす

## 📊 処理結果の確認

### 成功例

```
=== 処理結果 ===
対象ファイル数: 10
成功: 10 ファイル
失敗: 0 ファイル
検出された顔: 25 個
処理時間: 2.5 秒
平均処理時間: 0.25 秒/ファイル

全ての処理が正常に完了しました
```

### 統計情報の見方

- **対象ファイル数**: 処理対象の画像ファイル数
- **成功/失敗**: 処理に成功/失敗したファイル数
- **検出された顔**: 全体で検出された顔の総数
- **処理時間**: 実際にかかった時間
- **平均処理時間**: 1ファイルあたりの平均時間

## 🎯 次のステップ

### 高度な機能を試す

1. **処理時間推定**
   ```bash
   python3 cli.py -i large_directory -o output --estimate
   ```

2. **ドライラン**
   ```bash
   python3 cli.py -i input -o output --dry-run
   ```

3. **カスタム設定**
   ```python
   from face_mosaic import AppConfig, FaceMosaicApplication
   
   config = AppConfig()
   config.mosaic.ratio = 0.05
   app = FaceMosaicApplication(config)
   ```

### GUI版の活用

1. **リアルタイム設定変更**: スライダーで設定を調整
2. **進捗監視**: リアルタイムで処理状況を確認
3. **ログ確認**: 詳細な処理ログを表示

### API使用

```python
from face_mosaic import FaceMosaicApplication

app = FaceMosaicApplication()
result = app.process_single_image("input.jpg", "output.jpg")
print(f"検出された顔: {result['faces_detected']} 個")
```

## 📚 さらに詳しく

- [README.md](../README.md) - 完全なドキュメント
- [examples/](../examples/) - 使用例
- [docs/](.) - 詳細ドキュメント

## 🆘 サポート

問題が発生した場合：

1. `python3 cli.py --info` でシステム情報を確認
2. [GitHub Issues](https://github.com/your-username/face-mosaic-tool/issues) で報告
3. [examples/basic_usage.py](../examples/basic_usage.py) を参考にする

---

**Face Mosaic Tool v2.0** で高精度な顔モザイク処理を始めましょう！
