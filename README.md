# Face Mosaic Tool v2.0

YuNet専用高精度顔モザイク処理ツール - リファクタリング版

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5.4%2B-green.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 概要

Face Mosaic Tool v2.0は、OpenCV YuNetを使用した高精度な顔検出とモザイク処理を提供するPythonアプリケーションです。

### 主な特徴

- 🎯 **高精度検出**: OpenCV YuNetによる最新の顔検出技術
- 🏗️ **モジュラー設計**: SOLID原則に基づく保守性の高いアーキテクチャ
- ⚙️ **柔軟な設定**: 実行時設定変更とカスタマイズ可能な処理パラメータ
- 📊 **詳細統計**: 包括的な処理結果と時間推定機能
- 🖥️ **デュアルインターフェース**: CLI版とGUI版の両方を提供
- 🧪 **テスト対応**: 単体テスト可能な設計
- 🦾 **物体検出拡張**: PyTorch FasterRCNNによる物体検出・任意ラベルへのモザイク対応（`--object-detect`, `--object-labels`）

## 📋 システム要件

- **Python**: 3.8以上
- **OS**: Windows, macOS, Linux

## 🚀 インストール

### 1. リポジトリのクローン

```bash
git clone https://github.com/RyoWakabayashi/face_mosaic_tool.git
cd face_mosaic_tool
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. システム要件の確認

```bash
python3 cli.py --info
```

## 📖 使用方法

### CLI版

#### 基本的な使用方法

```bash
# ディレクトリ処理
python3 cli.py -i input_dir -o output_dir

# 単一ファイル処理
python3 cli.py -i image.jpg -o processed_image.jpg

# モザイク比率を指定
python3 cli.py -i input_dir -o output_dir -r 0.05

# ブラーモザイクを使用
python3 cli.py -i input_dir -o output_dir --blur
```

#### 高度なオプション

```bash
# 処理時間推定
python3 cli.py -i input_dir -o output_dir --estimate

# ドライラン（対象ファイル確認）
python3 cli.py -i input_dir -o output_dir --dry-run

# 確認プロンプトをスキップ
python3 cli.py -i input_dir -o output_dir --no-confirm

# 信頼度閾値を調整
python3 cli.py -i input_dir -o output_dir -c 0.8

# システム情報表示
python3 cli.py --info
```

### GUI版

```bash
python3 gui.py
```

GUI版では以下の機能が利用できます：

- 📁 **ファイル選択**: ドラッグ&ドロップまたはブラウザで選択
- ⚙️ **リアルタイム設定**: スライダーによる設定変更
- 📊 **進捗表示**: リアルタイム進捗バーと統計情報
- 📝 **ログ表示**: 詳細な処理ログ
- ⏱️ **時間推定**: 処理前の時間予測

## 🏗️ アーキテクチャ

### ディレクトリ構造

```
face_mosaic_tool/
├── src/face_mosaic/           # メインパッケージ
│   ├── __init__.py           # パッケージ初期化
│   ├── core/                 # コア機能
│   │   ├── application.py    # メインアプリケーション
│   │   ├── face_detector.py  # 顔検出エンジン
│   │   ├── image_processor.py # 画像処理エンジン
│   │   ├── batch_processor.py # バッチ処理エンジン
│   │   ├── model_manager.py  # モデル管理
│   │   └── exceptions.py     # カスタム例外
│   ├── config/               # 設定管理
│   │   └── settings.py       # 設定クラス
│   ├── utils/                # ユーティリティ
│   │   ├── system_info.py    # システム情報
│   │   └── file_utils.py     # ファイル操作
│   ├── cli/                  # CLI版
│   │   └── main.py           # CLIメイン
│   └── gui/                  # GUI版
│       └── main.py           # GUIメイン
├── tests/                    # テスト
├── examples/                 # 使用例
├── docs/                     # ドキュメント
├── cli.py                    # CLI エントリーポイント
├── gui.py                    # GUI エントリーポイント
└── requirements.txt          # 依存関係
```

### 主要コンポーネント

#### FaceMosaicApplication
メインアプリケーションクラス。全体の処理を統合管理。

```python
from face_mosaic import FaceMosaicApplication

app = FaceMosaicApplication()
result = app.process_single_image(input_path, output_path)
```

#### 設定管理
型安全な設定クラスによる一元管理。

```python
from face_mosaic import AppConfig

config = AppConfig()
config.mosaic.ratio = 0.2
config.detection.confidence_threshold = 0.8
app = FaceMosaicApplication(config)
```

#### カスタム例外
適切なエラーハンドリング。

```python
from face_mosaic import ModelError, DetectionError

try:
    app.process_directory(input_dir, output_dir)
except ModelError as e:
    print(f"モデルエラー: {e}")
except DetectionError as e:
    print(f"検出エラー: {e}")
```

## ⚙️ 設定オプション

### 顔検出設定

| パラメータ | デフォルト | 説明 |
|-----------|-----------|------|
| `confidence_threshold` | 0.6 | 顔検出の信頼度閾値 |
| `nms_threshold` | 0.3 | Non-Maximum Suppression閾値 |
| `input_size` | (320, 320) | 検出器の入力サイズ |

### モザイク設定

| パラメータ | デフォルト | 説明 |
|-----------|-----------|------|
| `ratio` | 0.1 | モザイクの粗さ（0.01-1.0） |
| `pixelate` | True | ピクセル化モザイク使用 |
| `blur_strength` | 15 | ブラー強度 |
| `margin_ratio` | 0.1 | 顔領域のマージン比率 |

### 処理設定

| パラメータ | デフォルト | 説明 |
|-----------|-----------|------|
| `supported_formats` | jpg, png, bmp等 | サポートする画像形式 |
| `max_image_size` | 4096 | 最大画像サイズ |
| `quality` | 95 | JPEG品質 |

## 🆕 物体検出によるモザイク（オプション）

PyTorch FasterRCNNを用いた物体検出で、任意のCOCOラベル（例: person, car, dog など）にもモザイクをかけられます。

- 有効化: `--object-detect`
- 対象ラベル指定: `--object-labels person,car,dog`

例:
```
python main.py -i sample_inputs -o sample_outputs --object-detect --object-labels car
```

顔検出と物体検出は併用可能です。

### デフォルトのCOCOラベル

デフォルトでは YOLOv8 の COCOラベルが使用されます。

指定できるラベルの一覧は以下の URL を参照してください。

<https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml>

### カスタムモデル

独自の学習済みモデルを使用する場合は、 `--object-model` オプションでモデルファイルを指定できます。

## 📊 パフォーマンス

### 処理速度

| 画像サイズ | 処理時間（目安） | メモリ使用量 |
|-----------|----------------|-------------|
| 1920x1080 | 0.1-0.3秒 | ~50MB |
| 3840x2160 | 0.3-0.8秒 | ~100MB |
| 大量バッチ | 0.1秒/ファイル | ~100MB |

### 検出精度

- **高精度**: YuNetによる最新の検出技術
- **多角度対応**: 様々な角度の顔を検出
- **複数顔対応**: 1枚の画像で複数の顔を同時処理
- **誤検出抑制**: 調整可能な信頼度閾値

## 🧪 開発・テスト

### 開発環境のセットアップ

```bash
# 開発用依存関係のインストール
pip install -r requirements.txt
pip install black flake8 pytest pytest-cov

# コード整形
python3 -m black src/

# テスト実行
pytest tests/
```

### API使用例

#### 基本的な使用方法

```python
from face_mosaic import FaceMosaicApplication
from pathlib import Path

# アプリケーション初期化
app = FaceMosaicApplication()

# 単一画像処理
result = app.process_single_image(
    Path("input.jpg"), 
    Path("output.jpg")
)
print(f"検出された顔: {result['faces_detected']} 個")

# ディレクトリ処理
stats = app.process_directory(
    Path("input_dir"), 
    Path("output_dir")
)
print(f"成功: {stats['success']}, 失敗: {stats['failed']}")
```

#### カスタム設定

```python
from face_mosaic import AppConfig, FaceMosaicApplication

# カスタム設定
config = AppConfig()
config.mosaic.ratio = 0.05  # 細かいモザイク
config.detection.confidence_threshold = 0.8  # 高い信頼度
config.mosaic.pixelate = False  # ブラーモザイク

# アプリケーション作成
app = FaceMosaicApplication(config)

# 処理実行
result = app.process_single_image("input.jpg", "output.jpg")
```

#### 処理時間推定

```python
# 処理時間推定
estimation = app.estimate_processing_time(Path("large_directory"))
print(f"推定時間: {estimation['estimated_time']:.1f} 秒")
print(f"対象ファイル: {estimation['total_files']} 個")
```

## 🔧 トラブルシューティング

### よくある問題

#### OpenCVバージョンエラー
```
エラー: YuNetにはOpenCV 4.5.4以上が必要です
```
**解決方法**: OpenCVを最新版にアップデート
```bash
pip install --upgrade opencv-python
```

#### モデルダウンロードエラー
```
エラー: モデルのダウンロードに失敗しました
```
**解決方法**: ネットワーク接続を確認し、再実行

#### メモリ不足エラー
```
エラー: メモリが不足しています
```
**解決方法**:
- 画像サイズを小さくする
- バッチサイズを減らす
- システムメモリを増やす

### ログレベルの調整

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### システム情報の確認

```bash
python3 cli.py --info
```

## 🗂️ モデルファイルの配置について

PyTorch FasterRCNNの独自学習済みモデルを利用する場合は、
`models/` ディレクトリを作成し、以下のようにファイルを配置してください。

- `models/custom_fasterrcnn.pt` : トレーニング済みモデル本体
- `models/labels.json` : ラベル名リスト（COCO形式、例: ["person", "car", ...]）

`labels.json` が存在しない場合は、COCOデフォルトラベルが自動で使用されます。

> 例: models ディレクトリ構成
> ```
> models/
> ├── custom_fasterrcnn.pt
> └── labels.json
> ```

`models/` 配下に .pth/.pt ファイルが複数ある場合は最初に見つかったものが自動で読み込まれます。

## 📝 更新履歴

### v2.0.0 (2024-06-20)
- 🏗️ **大規模リファクタリング**: モジュラー設計への移行
- ⚙️ **設定管理改善**: 型安全な設定クラス
- 🧪 **テスト対応**: 単体テスト可能な設計
- 📊 **機能追加**: 処理時間推定、詳細統計
- 🎨 **UI改善**: 新しいGUIデザイン
- 🚀 **パフォーマンス向上**: 最適化されたアルゴリズム

### v1.x (以前のバージョン)
- 基本的な顔検出とモザイク処理機能

## 🤝 コントリビューション

プロジェクトへの貢献を歓迎します！

### 貢献方法

1. **Fork** このリポジトリ
2. **Feature branch** を作成 (`git checkout -b feature/amazing-feature`)
3. **Commit** 変更 (`git commit -m 'Add amazing feature'`)
4. **Push** ブランチ (`git push origin feature/amazing-feature`)
5. **Pull Request** を作成

### 開発ガイドライン

- **コードスタイル**: Black による自動整形
- **テスト**: 新機能には単体テストを追加
- **ドキュメント**: 変更に応じてドキュメントを更新
- **コミット**: 明確なコミットメッセージ

## ライセンスとサードパーティー表記

本ソフトウェアはMITライセンスですが、物体検出機能で利用している「ultralytics/ultralytics (YOLOv8)」は GNU Affero General Public License v3 (AGPL-3.0) で配布されています。

- YOLOv8 (ultralytics): https://github.com/ultralytics/ultralytics
- ライセンス: GNU Affero General Public License v3 (AGPL-3.0)

本リポジトリを公開・配布する場合は、AGPL-3.0の条件に従い、
- サードパーティーライセンス（AGPL-3.0）を明記
- 利用者がultralytics/ultralyticsのソースコードを取得できるよう案内
- 本リポジトリのMITライセンスと併記
が必要です。

### 参考: YOLOv8 (ultralytics) ライセンス抜粋

> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU Affero General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> (at your option) any later version.

> This program is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
> GNU Affero General Public License for more details.

> You should have received a copy of the GNU Affero General Public License
> along with this program.  If not, see <https://www.gnu.org/licenses/>.

---

**Face Mosaic Tool v2.0** - YuNet専用高精度顔モザイク処理ツール
