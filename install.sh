#!/bin/bash

echo "高精度顔モザイク処理ツール - macOS インストールスクリプト"
echo "========================================================"

# Python環境確認
echo ""
echo "Python環境を確認中..."
if ! command -v python3 &> /dev/null; then
    echo "エラー: Python3がインストールされていません"
    echo "Python 3.9-3.12をインストールしてください（推奨: 3.11）:"
    echo "  brew install python@3.11"
    exit 1
fi

# Pythonバージョンチェック
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "検出されたPythonバージョン: $PYTHON_VERSION"

# MediaPipe対応バージョンチェック
if [[ "$PYTHON_VERSION" == "3.9" ]] || [[ "$PYTHON_VERSION" == "3.10" ]] || [[ "$PYTHON_VERSION" == "3.11" ]] || [[ "$PYTHON_VERSION" == "3.12" ]]; then
    echo "✓ MediaPipe対応バージョンです（最高精度で動作）"
    MEDIAPIPE_COMPATIBLE=true
else
    echo "⚠ MediaPipe非対応バージョンです"
    echo "  MediaPipeには Python 3.9-3.12 が必要です"
    echo "  現在のバージョンでは Dlib と OpenCV のみ利用可能です"
    echo ""
    echo "推奨アクション:"
    echo "  brew install python@3.11"
    echo "  python3.11 -m pip install --upgrade pip"
    echo ""
    read -p "このまま続行しますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    MEDIAPIPE_COMPATIBLE=false
fi

# tkinter確認（macOS特有）
echo ""
echo "tkinter環境を確認中..."
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "警告: tkinterが利用できません"
    echo "Homebrewでpython-tkをインストールしてください:"
    echo "  brew install python-tk"
    echo ""
    read -p "続行しますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# CMake確認（Dlib用）
echo ""
echo "CMake環境を確認中..."
if ! command -v cmake &> /dev/null; then
    echo "警告: CMakeがインストールされていません（Dlib用）"
    echo "Homebrewでインストールすることを推奨します:"
    echo "  brew install cmake"
    echo ""
    read -p "CMakeなしで続行しますか？（Dlibは利用できません） (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    cmake --version
fi

# 基本依存関係インストール
echo ""
echo "基本依存関係をインストール中..."
pip3 install opencv-python numpy Pillow tqdm
if [ $? -ne 0 ]; then
    echo "エラー: 基本依存関係のインストールに失敗しました"
    exit 1
fi

# MediaPipeインストール
echo ""
if [ "$MEDIAPIPE_COMPATIBLE" = true ]; then
    echo "MediaPipe をインストール中..."
    pip3 install mediapipe
    if [ $? -eq 0 ]; then
        echo "✓ MediaPipe のインストールが完了しました"
    else
        echo "✗ MediaPipe のインストールに失敗しました"
    fi
else
    echo "⚠ MediaPipe をスキップします（Python バージョン非対応）"
fi

# Dlibインストール（時間がかかる可能性があります）
echo ""
echo "Dlib をインストール中（時間がかかる場合があります）..."
pip3 install dlib
if [ $? -eq 0 ]; then
    echo "✓ Dlib のインストールが完了しました"
else
    echo "✗ Dlib のインストールに失敗しました"
    echo "  CMakeが必要です: brew install cmake"
    echo "  または事前コンパイル版を試してください: pip3 install dlib-binary"
fi

# 実行権限付与
chmod +x cli_tool_advanced.py
chmod +x gui_tool_advanced.py
chmod +x test_advanced.py

# インストール確認テスト
echo ""
echo "インストール確認テストを実行中..."
python3 -c "
import sys
try:
    from face_detector import get_system_info
    info = get_system_info()
    print('=== インストール状況 ===')
    for key, value in info.items():
        print(f'{key}: {value}')
    
    print('\n=== 利用可能な検出手法 ===')
    if info['mediapipe_available']:
        print('✓ MediaPipe Face Detection')
    else:
        print('✗ MediaPipe Face Detection')
        
    if info['dlib_available']:
        print('✓ Dlib Face Detection')
    else:
        print('✗ Dlib Face Detection')
        
    print('✓ OpenCV Haar Cascade')
    
    # 少なくとも1つの高精度手法が利用可能かチェック
    if info['mediapipe_available'] or info['dlib_available']:
        print('\n✓ 高精度検出が利用可能です')
        sys.exit(0)
    else:
        print('\n⚠ 高精度検出手法が利用できませんが、基本機能は動作します')
        sys.exit(0)
        
except Exception as e:
    print(f'エラー: {e}')
    print('詳細診断を実行してください: python3 test_dlib_version.py')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "インストール完了！"
    echo ""
    echo "使用方法:"
    echo "  CLI版: python3 cli_tool.py -i 入力フォルダ -o 出力フォルダ"
    echo "  GUI版: python3 gui_tool.py"
    echo "  テスト実行: python3 test_tool.py"
    echo "  診断実行: python3 test_dlib_version.py"
    echo "  Proxy情報: python3 cli_tool.py --proxy-info"
    echo "  Proxy接続テスト: python3 cli_tool.py --test-proxy"
    echo ""
    if [ "$MEDIAPIPE_COMPATIBLE" = true ]; then
        echo "✓ 最高精度: MediaPipe が利用可能です"
        echo "  推奨: python3 cli_tool.py -i input -o output -m mediapipe"
    else
        echo "⚠ MediaPipe が利用できません（Python 3.9-3.12 が必要）"
        echo "  利用可能: Dlib と OpenCV による検出"
    fi
    echo ""
    echo "Proxy環境での使用:"
    echo "  export HTTP_PROXY=http://proxy.company.com:8080"
    echo "  export HTTPS_PROXY=http://proxy.company.com:8080"
else
    echo ""
    echo "インストールに問題があります。"
    echo "詳細診断を実行してください: python3 test_dlib_version.py"
    exit 1
fi
