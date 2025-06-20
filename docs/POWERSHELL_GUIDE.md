# PowerShell インストールガイド

Windows PowerShellを使用したインストール方法を説明します。

## 🚀 クイックスタート

### 方法1: 自動起動スクリプト（推奨）

```cmd
install_powershell.bat
```

このスクリプトが以下の選択肢を提供します：
1. PowerShell で直接実行
2. 実行ポリシーを一時的に変更して実行
3. コマンドプロンプト版を使用

### 方法2: PowerShell で直接実行

```powershell
# 実行ポリシーを設定（初回のみ）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# インストールスクリプト実行
.\install.ps1
```

### 方法3: 実行ポリシーをバイパス

```powershell
# 一時的に実行ポリシーをバイパス
powershell.exe -ExecutionPolicy Bypass -File "install.ps1"
```

## 📋 PowerShell版の特徴

### ✅ 高度な機能
- **カラー出力**: 見やすい色分け表示
- **詳細な進捗表示**: インストール状況をリアルタイム表示
- **エラーハンドリング**: より詳細なエラー情報
- **パラメータ対応**: コマンドラインオプション

### 🎛️ コマンドラインオプション

```powershell
# 基本実行
.\install.ps1

# 強制実行（確認をスキップ）
.\install.ps1 -Force

# バージョンチェックをスキップ
.\install.ps1 -SkipVersionCheck

# 両方のオプションを使用
.\install.ps1 -Force -SkipVersionCheck
```

## 🔧 トラブルシューティング

### 実行ポリシーエラー

**エラー**: `このシステムではスクリプトの実行が無効になっているため...`

**解決方法**:
```powershell
# 現在の実行ポリシーを確認
Get-ExecutionPolicy

# 実行ポリシーを変更（推奨）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# または一時的にバイパス
powershell.exe -ExecutionPolicy Bypass -File "install.ps1"
```

### PowerShellバージョンが古い

**要件**: PowerShell 5.1以上

**確認方法**:
```powershell
$PSVersionTable.PSVersion
```

**解決方法**:
- Windows PowerShell 5.1: Windows Updateで更新
- PowerShell 7+: [GitHub](https://github.com/PowerShell/PowerShell)からダウンロード

### Python が見つからない

**エラー**: `Python not found`

**解決方法**:
1. [Python公式サイト](https://www.python.org/downloads/)からPython 3.9-3.12をダウンロード
2. インストール時に「Add Python to PATH」をチェック
3. コマンドプロンプトを再起動

## 📊 インストール方法比較

| 方法 | 特徴 | 推奨度 | 対象ユーザー |
|------|------|--------|--------------|
| **PowerShell** | 高機能、カラー表示 | ⭐⭐⭐ | PowerShellユーザー |
| **コマンドプロンプト** | シンプル、互換性高 | ⭐⭐ | 一般ユーザー |
| **自動起動** | 選択可能 | ⭐⭐⭐ | 初心者 |

## 🎨 PowerShell版の出力例

```
高精度顔モザイク処理ツール - Windows PowerShell インストールスクリプト
=================================================================

PowerShell環境を確認中...
PowerShell バージョン: 5.1

Python環境を確認中...
検出されたPython: Python 3.11.0

Pythonバージョンを詳細確認中...
Python バージョン: 3.11
✓ MediaPipe対応バージョンです（最高精度で動作）

基本依存関係をインストール中...
  ✓ opencv-python
  ✓ numpy
  ✓ Pillow
  ✓ tqdm

MediaPipe をインストール中...
✓ MediaPipe のインストールが完了しました

インストール完了！

使用方法:
  CLI版: python cli_tool.py -i 入力フォルダ -o 出力フォルダ
  GUI版: python gui_tool.py

✓ 最高精度: MediaPipe が利用可能です
```

## 🚀 インストール後の使用方法

```powershell
# CLI版（基本）
python cli_tool.py -i .\input_images -o .\output_images

# CLI版（最高精度）
python cli_tool.py -i .\input -o .\output -m mediapipe

# GUI版
python gui_tool.py

# システム情報確認
python cli_tool.py --info

# テスト実行
python test_tool.py
```

PowerShell版により、より快適で詳細なインストール体験を提供します！
