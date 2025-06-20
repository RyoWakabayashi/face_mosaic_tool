#!/usr/bin/env python3
"""
Face Mosaic Tool v2.0 - 基本的な使用例
"""

import sys
from pathlib import Path

# パッケージパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from face_mosaic import FaceMosaicApplication, AppConfig


def basic_single_image_processing():
    """単一画像処理の基本例"""
    print("=== 単一画像処理の例 ===")
    
    # アプリケーション初期化
    app = FaceMosaicApplication()
    
    # 処理実行（実際のファイルパスに変更してください）
    input_path = Path("input.jpg")
    output_path = Path("output.jpg")
    
    if input_path.exists():
        result = app.process_single_image(input_path, output_path)
        
        if result["success"]:
            print(f"✅ 処理成功")
            print(f"検出された顔: {result['faces_detected']} 個")
            print(f"出力ファイル: {result['output_path']}")
        else:
            print(f"❌ 処理失敗: {result['error']}")
    else:
        print(f"入力ファイルが見つかりません: {input_path}")


def basic_directory_processing():
    """ディレクトリ処理の基本例"""
    print("\n=== ディレクトリ処理の例 ===")
    
    # アプリケーション初期化
    app = FaceMosaicApplication()
    
    # 処理実行（実際のディレクトリパスに変更してください）
    input_dir = Path("input_directory")
    output_dir = Path("output_directory")
    
    if input_dir.exists():
        # ドライラン（対象ファイル確認）
        print("ドライラン実行中...")
        stats = app.process_directory(input_dir, output_dir, dry_run=True)
        print(f"対象ファイル数: {stats['total']}")
        
        # 実際の処理
        if stats['total'] > 0:
            print("実際の処理を実行中...")
            stats = app.process_directory(input_dir, output_dir)
            
            print(f"✅ 処理完了")
            print(f"成功: {stats['success']} ファイル")
            print(f"失敗: {stats['failed']} ファイル")
            print(f"検出された顔: {stats['faces_detected']} 個")
            print(f"処理時間: {stats['processing_time']:.2f} 秒")
    else:
        print(f"入力ディレクトリが見つかりません: {input_dir}")


def custom_configuration_example():
    """カスタム設定の例"""
    print("\n=== カスタム設定の例 ===")
    
    # カスタム設定を作成
    config = AppConfig()
    config.mosaic.ratio = 0.05  # 細かいモザイク
    config.detection.confidence_threshold = 0.8  # 高い信頼度
    config.mosaic.pixelate = False  # ブラーモザイク
    
    # アプリケーション初期化
    app = FaceMosaicApplication(config)
    
    # 設定情報表示
    app_info = app.get_application_info()
    print(f"モザイク比率: {app_info['config']['mosaic']['ratio']}")
    print(f"信頼度閾値: {app_info['config']['detection']['confidence_threshold']}")
    print(f"モザイク方式: {'ブラー' if not config.mosaic.pixelate else 'ピクセル化'}")


def processing_time_estimation():
    """処理時間推定の例"""
    print("\n=== 処理時間推定の例 ===")
    
    app = FaceMosaicApplication()
    
    # 推定対象ディレクトリ（実際のパスに変更してください）
    input_dir = Path("large_directory")
    
    if input_dir.exists():
        print("処理時間を推定中...")
        estimation = app.estimate_processing_time(input_dir)
        
        print(f"対象ファイル数: {estimation['total_files']}")
        print(f"推定処理時間: {estimation['estimated_time']:.1f} 秒")
        
        if estimation['estimated_time'] > 60:
            minutes = estimation['estimated_time'] / 60
            print(f"              {minutes:.1f} 分")
    else:
        print(f"ディレクトリが見つかりません: {input_dir}")


def system_information():
    """システム情報の表示例"""
    print("\n=== システム情報の例 ===")
    
    app = FaceMosaicApplication()
    
    # システム情報取得
    system_info = app.get_system_info()
    print("システム情報:")
    for key, value in system_info.items():
        print(f"  {key}: {value}")
    
    # 要件チェック
    requirements = app.check_requirements()
    print("\n要件チェック:")
    for key, value in requirements.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {value}")
    
    # アプリケーション準備状態
    ready = app.is_ready()
    print(f"\nアプリケーション準備状態: {'✅ 準備完了' if ready else '❌ 準備未完了'}")


def error_handling_example():
    """エラーハンドリングの例"""
    print("\n=== エラーハンドリングの例 ===")
    
    from face_mosaic import ModelError, DetectionError, ImageProcessingError
    
    app = FaceMosaicApplication()
    
    try:
        # 存在しないファイルを処理
        result = app.process_single_image(
            Path("nonexistent.jpg"), 
            Path("output.jpg")
        )
        
    except ModelError as e:
        print(f"モデルエラー: {e}")
    except DetectionError as e:
        print(f"検出エラー: {e}")
    except ImageProcessingError as e:
        print(f"画像処理エラー: {e}")
    except Exception as e:
        print(f"その他のエラー: {e}")


def main():
    """メイン関数"""
    print("Face Mosaic Tool v2.0 - 使用例")
    print("=" * 50)
    
    # 各例を実行
    basic_single_image_processing()
    basic_directory_processing()
    custom_configuration_example()
    processing_time_estimation()
    system_information()
    error_handling_example()
    
    print("\n" + "=" * 50)
    print("使用例の実行が完了しました")


if __name__ == "__main__":
    main()
