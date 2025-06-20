#!/usr/bin/env python3
"""
Dlibのバージョン確認とエラー診断スクリプト
"""

def test_dlib_installation():
    """Dlibのインストール状況をテスト"""
    print("=== Dlib インストール診断 ===")
    
    # 1. インポートテスト
    try:
        import dlib
        print("✓ Dlib のインポートに成功")
    except ImportError as e:
        print(f"✗ Dlib のインポートに失敗: {e}")
        print("解決方法:")
        print("  pip install dlib")
        print("  または")
        print("  pip install cmake")
        print("  pip install dlib")
        return False
    
    # 2. バージョン情報取得
    print("\n--- バージョン情報 ---")
    version_found = False
    
    # __version__ 属性をチェック
    if hasattr(dlib, '__version__'):
        print(f"✓ dlib.__version__: {dlib.__version__}")
        version_found = True
    else:
        print("✗ dlib.__version__ 属性が見つかりません")
    
    # DLIB_VERSION 属性をチェック
    if hasattr(dlib, 'DLIB_VERSION'):
        print(f"✓ dlib.DLIB_VERSION: {dlib.DLIB_VERSION}")
        version_found = True
    else:
        print("✗ dlib.DLIB_VERSION 属性が見つかりません")
    
    if not version_found:
        print("⚠ バージョン情報を取得できませんが、Dlibは利用可能です")
    
    # 3. 基本機能テスト
    print("\n--- 基本機能テスト ---")
    try:
        detector = dlib.get_frontal_face_detector()
        print("✓ HOG顔検出器の初期化に成功")
    except Exception as e:
        print(f"✗ HOG顔検出器の初期化に失敗: {e}")
        return False
    
    # 4. CUDA対応チェック
    print("\n--- CUDA対応チェック ---")
    try:
        if hasattr(dlib, 'cuda'):
            print("✓ CUDA対応版のDlibです")
        else:
            print("- CPU版のDlibです（通常の使用には問題ありません）")
    except Exception as e:
        print(f"⚠ CUDA対応チェック中にエラー: {e}")
    
    # 5. 利用可能な属性一覧
    print("\n--- 利用可能な属性（一部） ---")
    important_attrs = [
        '__version__', 'DLIB_VERSION', 'get_frontal_face_detector',
        'cnn_face_detection_model_v1', 'cuda'
    ]
    
    for attr in important_attrs:
        if hasattr(dlib, attr):
            print(f"✓ {attr}")
        else:
            print(f"✗ {attr}")
    
    return True


def test_mediapipe_installation():
    """MediaPipeのインストール状況をテスト"""
    print("\n=== MediaPipe インストール診断 ===")
    
    # 1. インポートテスト
    try:
        import mediapipe as mp
        print("✓ MediaPipe のインポートに成功")
    except ImportError as e:
        print(f"✗ MediaPipe のインポートに失敗: {e}")
        print("解決方法:")
        print("  pip install mediapipe")
        return False
    
    # 2. バージョン情報
    try:
        print(f"✓ MediaPipe バージョン: {mp.__version__}")
    except:
        print("⚠ MediaPipe のバージョン情報を取得できません")
    
    # 3. 顔検出機能テスト
    try:
        face_detection = mp.solutions.face_detection
        drawing_utils = mp.solutions.drawing_utils
        detector = face_detection.FaceDetection(min_detection_confidence=0.3)
        print("✓ MediaPipe 顔検出器の初期化に成功")
    except Exception as e:
        print(f"✗ MediaPipe 顔検出器の初期化に失敗: {e}")
        return False
    
    return True


def main():
    """メイン診断関数"""
    print("ライブラリインストール診断ツール")
    print("=" * 50)
    
    dlib_ok = test_dlib_installation()
    mediapipe_ok = test_mediapipe_installation()
    
    print("\n" + "=" * 50)
    print("診断結果サマリー:")
    
    if dlib_ok:
        print("✓ Dlib: 正常に動作します")
    else:
        print("✗ Dlib: 問題があります")
    
    if mediapipe_ok:
        print("✓ MediaPipe: 正常に動作します")
    else:
        print("✗ MediaPipe: 問題があります")
    
    if dlib_ok or mediapipe_ok:
        print("\n少なくとも1つの高精度検出手法が利用可能です。")
        print("face_detector.py は動作するはずです。")
    else:
        print("\n高精度検出手法が利用できません。")
        print("基本版（face_detector.py）をご利用ください。")
    
    # 修正されたコードのテスト
    print("\n=== 修正版コードのテスト ===")
    try:
        from face_detector import get_system_info, get_dlib_version
        info = get_system_info()
        print("✓ 修正版 get_system_info() の実行に成功")
        print(f"  Dlib バージョン: {info.get('dlib_version', 'N/A')}")
        print(f"  MediaPipe 利用可能: {info.get('mediapipe_available', False)}")
        print(f"  Dlib 利用可能: {info.get('dlib_available', False)}")
    except Exception as e:
        print(f"✗ 修正版コードのテストに失敗: {e}")


if __name__ == "__main__":
    main()
