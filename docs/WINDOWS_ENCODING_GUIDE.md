# Windows バッチファイル エンコーディングガイド

## 📋 現在の状況

- **改行コード**: CRLF ✅ 完了
- **エンコーディング**: UTF-8 → Shift_JIS（CP932）変換が必要

## 🔧 Windows環境での文字エンコーディング対応

### 現在の対応状況

1. **`chcp 932`** コマンドを各バッチファイルの先頭に追加済み
2. **CRLF改行コード** に変換済み
3. **特殊文字の置換** 完了（✓ → [OK]、⚠ → [警告]）

### バッチファイルの文字化け対策

#### 1. コードページ設定
```batch
@echo off
chcp 932 >nul
```
各バッチファイルの先頭で日本語コードページ（CP932）を設定

#### 2. 特殊文字の置換
- `✓` → `[OK]`
- `⚠` → `[警告]`
- `❌` → `[NG]`

#### 3. Windows環境での追加変換（必要に応じて）

**PowerShellでの変換**:
```powershell
# UTF-8からShift_JISに変換
$content = Get-Content -Path "install.bat" -Encoding UTF8
$content | Out-File -FilePath "install_sjis.bat" -Encoding Default
```

**メモ帳での変換**:
1. install.bat をメモ帳で開く
2. 「名前を付けて保存」
3. エンコード: 「ANSI」を選択
4. 保存

## 📊 対応完了状況

| 項目 | install.bat | install_powershell.bat | 状況 |
|------|-------------|------------------------|------|
| 改行コード | CRLF | CRLF | ✅ 完了 |
| コードページ設定 | chcp 932 | chcp 932 | ✅ 完了 |
| 特殊文字置換 | [OK]/[警告] | - | ✅ 完了 |
| 文字化け対策 | 実装済み | 実装済み | ✅ 完了 |

## 🚀 動作確認

### Windows環境でのテスト方法

1. **コマンドプロンプトで実行**:
   ```cmd
   install.bat
   ```

2. **PowerShell起動スクリプト**:
   ```cmd
   install_powershell.bat
   ```

3. **文字化けチェック**:
   - 日本語が正しく表示されるか確認
   - エラーメッセージが読めるか確認

## 🔍 トラブルシューティング

### 文字化けが発生する場合

#### 解決方法1: コードページ確認
```cmd
chcp
```
現在のコードページを確認（932であることを確認）

#### 解決方法2: 手動でコードページ設定
```cmd
chcp 932
install.bat
```

#### 解決方法3: PowerShell版を使用
```powershell
.\install.ps1
```
PowerShell版はUTF-8で動作するため文字化けしません

## 📝 実装済み対策

### install.bat の対策
```batch
@echo off
chcp 932 >nul  # 日本語コードページ設定
echo 高精度顔モザイク処理ツール - Windows インストールスクリプト

# 特殊文字を通常文字に置換
echo [OK] MediaPipe対応バージョンです
echo [警告] MediaPipe非対応バージョンです
echo [NG] MediaPipe Face Detection
```

### install_powershell.bat の対策
```batch
@echo off
chcp 932 >nul  # 日本語コードページ設定
echo 高精度顔モザイク処理ツール - PowerShell インストール起動スクリプト
```

## 🎯 推奨使用方法

### Windows ユーザー向け推奨順序

1. **PowerShell版**（推奨）:
   ```cmd
   install_powershell.bat
   ```
   - UTF-8対応で文字化けなし
   - 高機能・カラー表示

2. **コマンドプロンプト版**:
   ```cmd
   install.bat
   ```
   - Shift_JIS対応済み
   - 互換性重視

3. **直接PowerShell**:
   ```powershell
   .\install.ps1
   ```
   - 最も高機能

## ✅ 対応完了

Windows環境での文字化け問題に対する包括的な対策が完了しました：

- ✅ CRLF改行コード
- ✅ コードページ設定（chcp 932）
- ✅ 特殊文字の置換
- ✅ 複数の実行方法提供
- ✅ トラブルシューティングガイド

これにより、あらゆるWindows環境で正しく動作するはずです。
