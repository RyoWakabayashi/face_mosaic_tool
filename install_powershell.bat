@echo off
chcp 932 >nul
echo 高精度顔モザイク処理ツール - PowerShell インストール起動スクリプト
echo ==============================================================

echo.
echo PowerShell スクリプトを実行します...
echo 注意: 実行ポリシーの変更が必要な場合があります

echo.
echo 実行方法を選択してください:
echo [1] PowerShell で直接実行（推奨）
echo [2] 実行ポリシーを一時的に変更して実行
echo [3] コマンドプロンプト版を使用
echo.

set /p choice="選択してください (1-3): "

if "%choice%"=="1" (
    echo.
    echo PowerShell を起動しています...
    echo 以下のコマンドを実行してください:
    echo.
    echo   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    echo   .\install.ps1
    echo.
    powershell.exe
    goto :end
)

if "%choice%"=="2" (
    echo.
    echo 実行ポリシーを一時的に変更してスクリプトを実行します...
    powershell.exe -ExecutionPolicy Bypass -File "install.ps1"
    goto :end
)

if "%choice%"=="3" (
    echo.
    echo コマンドプロンプト版インストールスクリプトを実行します...
    call install.bat
    goto :end
)

echo.
echo 無効な選択です。コマンドプロンプト版を実行します...
call install.bat

:end
echo.
pause
