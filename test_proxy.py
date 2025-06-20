#!/usr/bin/env python3
"""
Proxy対応機能のテストスクリプト
"""

import os
import sys
from proxy_utils import ProxyManager, get_proxy_manager, print_proxy_env_examples


def test_proxy_detection():
    """Proxy設定検出のテスト"""
    print("=== Proxy設定検出テスト ===")
    
    proxy_manager = ProxyManager()
    
    if proxy_manager.is_proxy_enabled():
        print("✓ Proxy設定が検出されました")
        proxy_manager.print_proxy_info()
    else:
        print("- Proxy設定が検出されませんでした")
        print("  環境変数 HTTP_PROXY, HTTPS_PROXY が設定されていません")
    
    return proxy_manager.is_proxy_enabled()


def test_proxy_connection():
    """Proxy接続テスト"""
    print("\n=== Proxy接続テスト ===")
    
    proxy_manager = get_proxy_manager()
    
    test_urls = [
        "https://www.google.com",
        "https://github.com",
        "http://dlib.net"
    ]
    
    for url in test_urls:
        print(f"テスト中: {url}")
        try:
            if proxy_manager.test_connection(url):
                print(f"  ✓ 接続成功")
            else:
                print(f"  ✗ 接続失敗")
        except Exception as e:
            print(f"  ✗ エラー: {e}")
    
    return True


def test_model_download():
    """モデルダウンロードテスト"""
    print("\n=== モデルダウンロードテスト ===")
    
    try:
        from face_detector import AdvancedFaceDetector
        
        print("顔検出器を初期化中...")
        detector = AdvancedFaceDetector(detection_method='dlib')
        
        # Dlibモデルのダウンロードテスト
        if 'dlib_cnn' in detector.detectors:
            print("✓ Dlib CNNモデルが利用可能です")
        else:
            print("- Dlib CNNモデルは利用できません")
        
        # OpenCV DNNモデルのテスト
        if 'opencv_dnn' in detector.detectors:
            print("✓ OpenCV DNNモデルが利用可能です")
        else:
            print("- OpenCV DNNモデルは利用できません")
        
        return True
        
    except Exception as e:
        print(f"✗ モデルダウンロードテストでエラー: {e}")
        return False


def test_environment_variables():
    """環境変数のテスト"""
    print("\n=== 環境変数確認 ===")
    
    proxy_vars = [
        'HTTP_PROXY', 'http_proxy',
        'HTTPS_PROXY', 'https_proxy',
        'NO_PROXY', 'no_proxy',
        'PYTHONHTTPSVERIFY'
    ]
    
    found_vars = []
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            # パスワードを含む場合はマスク
            if '@' in value and ':' in value:
                # user:pass@proxy.com:8080 -> user:***@proxy.com:8080
                masked_value = value.replace(value.split('@')[0].split(':')[1], '***')
                print(f"  {var}: {masked_value}")
            else:
                print(f"  {var}: {value}")
            found_vars.append(var)
    
    if not found_vars:
        print("  Proxy関連の環境変数は設定されていません")
    
    return len(found_vars) > 0


def simulate_proxy_environment():
    """Proxy環境のシミュレーション"""
    print("\n=== Proxy環境シミュレーション ===")
    
    # テスト用のProxy設定
    test_proxy_settings = {
        'HTTP_PROXY': 'http://proxy.example.com:8080',
        'HTTPS_PROXY': 'http://proxy.example.com:8080',
        'NO_PROXY': 'localhost,127.0.0.1,.local'
    }
    
    print("テスト用Proxy設定を適用中...")
    original_env = {}
    
    try:
        # 元の環境変数を保存
        for key in test_proxy_settings:
            original_env[key] = os.environ.get(key)
        
        # テスト用設定を適用
        for key, value in test_proxy_settings.items():
            os.environ[key] = value
            print(f"  {key}: {value}")
        
        # 新しいProxyManagerで検出テスト
        test_proxy_manager = ProxyManager()
        
        if test_proxy_manager.is_proxy_enabled():
            print("✓ シミュレーション環境でProxy設定が検出されました")
            test_proxy_manager.print_proxy_info()
        else:
            print("✗ シミュレーション環境でProxy設定が検出されませんでした")
        
        return True
        
    finally:
        # 元の環境変数を復元
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def main():
    """メインテスト関数"""
    print("Proxy対応機能テストスイート")
    print("=" * 50)
    
    tests = [
        ("環境変数確認", test_environment_variables),
        ("Proxy設定検出", test_proxy_detection),
        ("Proxy接続テスト", test_proxy_connection),
        ("Proxy環境シミュレーション", simulate_proxy_environment),
        ("モデルダウンロード", test_model_download),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}テストを実行中...")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "成功" if result else "完了"
            print(f"{test_name}テスト: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"{test_name}テスト: エラー - {e}")
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("テスト結果サマリー:")
    
    success_count = 0
    for test_name, result in results:
        status = "✓" if result else "○"
        print(f"  {status} {test_name}")
        if result:
            success_count += 1
    
    print(f"\n完了: {success_count}/{len(results)}")
    
    # Proxy設定例の表示
    print_proxy_env_examples()
    
    print("\nProxy対応機能のテストが完了しました。")
    print("企業環境等でProxy設定が必要な場合は、上記の環境変数を設定してください。")


if __name__ == "__main__":
    main()
