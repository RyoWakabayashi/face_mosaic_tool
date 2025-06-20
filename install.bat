@echo off
chcp 932 >nul
echo 高精度顔モザイク処理ツール - Windows インストールスクリプト
echo ========================================================

echo.
echo Python環境を確認中...
python --version >nul 2>&1
if errorlevel 1 (
    echo エラー: Pythonがインストールされていません
    echo Python 3.9-3.12をインストールしてください（推奨: 3.11）
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Pythonバージョンを確認中...
for /f "tokens=2" %%i in ('python -c "import sys; print(sys.version_info.major, sys.version_info.minor)" 2^>nul') do set PYTHON_MINOR=%%i
for /f "tokens=1" %%i in ('python -c "import sys; print(sys.version_info.major, sys.version_info.minor)" 2^>nul') do set PYTHON_MAJOR=%%i

if "%PYTHON_MAJOR%"=="3" (
    if "%PYTHON_MINOR%"=="9" set MEDIAPIPE_COMPATIBLE=true
    if "%PYTHON_MINOR%"=="10" set MEDIAPIPE_COMPATIBLE=true
    if "%PYTHON_MINOR%"=="11" set MEDIAPIPE_COMPATIBLE=true
    if "%PYTHON_MINOR%"=="12" set MEDIAPIPE_COMPATIBLE=true
)

if "%MEDIAPIPE_COMPATIBLE%"=="true" (
    echo [OK] MediaPipe対応バージョンです（最高精度で動作）
) else (
    echo [警告] MediaPipe非対応バージョンです
    echo   MediaPipeには Python 3.9-3.12 が必要です
    echo   現在のバージョンでは Dlib と OpenCV のみ利用可能です
    echo.
    echo 推奨アクション:
    echo   Python 3.11 をインストールしてください
    echo   https://www.python.org/downloads/
    echo.
    set /p CONTINUE="このまま続行しますか？ (y/N): "
    if /i not "%CONTINUE%"=="y" exit /b 1
)

echo.
echo Visual C++ Build Tools を確認中...
echo 注意: Dlibのインストールには Visual C++ Build Tools が必要です
echo https://visualstudio.microsoft.com/visual-cpp-build-tools/

echo.
echo 基本依存関係をインストール中...
pip install opencv-python numpy Pillow tqdm
if errorlevel 1 (
    echo エラー: 基本依存関係のインストールに失敗しました
    pause
    exit /b 1
)

echo.
if "%MEDIAPIPE_COMPATIBLE%"=="true" (
    echo MediaPipe をインストール中...
    pip install mediapipe
    if errorlevel 1 (
        echo 警告: MediaPipe のインストールに失敗しました
    ) else (
        echo [OK] MediaPipe のインストールが完了しました
    )
) else (
    echo [警告] MediaPipe をスキップします（Python バージョン非対応）
)

echo.
echo CMake をインストール中...
pip install cmake
if errorlevel 1 (
    echo 警告: CMake のインストールに失敗しました
) else (
    echo CMake のインストールが完了しました
)

echo.
echo Dlib をインストール中（時間がかかる場合があります）...
pip install dlib
if errorlevel 1 (
    echo 警告: Dlib のインストールに失敗しました
    echo Visual C++ Build Tools が必要です
    echo 代替案: pip install dlib-binary
) else (
    echo Dlib のインストールが完了しました
)

echo.
echo インストール確認テストを実行中...
python -c "
import sys
try:
    from face_detector import get_system_info
    info = get_system_info()
    print('=== インストール状況 ===')
    for key, value in info.items():
        print(f'{key}: {value}')
    
    print('\n=== 利用可能な検出手法 ===')
    if info['mediapipe_available']:
        print('[OK] MediaPipe Face Detection')
    else:
        print('[NG] MediaPipe Face Detection')
        
    if info['dlib_available']:
        print('[OK] Dlib Face Detection')
    else:
        print('[NG] Dlib Face Detection')
        
    print('[OK] OpenCV Haar Cascade')
    
except Exception as e:
    print(f'エラー: {e}')
    exit(1)
"

if errorlevel 1 (
    echo.
    echo インストールに問題があります。エラーメッセージを確認してください。
    pause
    exit /b 1
)

echo.
echo インストール完了！
echo.
echo 使用方法:
echo   CLI版: python cli_tool.py -i 入力フォルダ -o 出力フォルダ
echo   GUI版: python gui_tool.py
echo   テスト実行: python test_tool.py
echo   診断実行: python test_dlib_version.py
echo.
if "%MEDIAPIPE_COMPATIBLE%"=="true" (
    echo [OK] 最高精度: MediaPipe が利用可能です
    echo   推奨: python cli_tool.py -i input -o output -m mediapipe
) else (
    echo [警告] MediaPipe が利用できません（Python 3.9-3.12 が必要）
    echo   利用可能: Dlib と OpenCV による検出
)
echo.
pause
