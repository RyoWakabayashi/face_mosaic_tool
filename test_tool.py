#!/usr/bin/env python3
"""
高精度顔モザイク処理ツールのテスト用サンプル
MediaPipe、Dlib、OpenCV DNNの各手法をテスト
"""

import cv2
import numpy as np
import os
from pathlib import Path
from face_detector import AdvancedFaceDetector, AdvancedImageProcessor, get_system_info
import time


def create_test_images():
    """テスト用の様々な顔画像を生成"""
    test_images = []
    
    # 1. 大きな顔
    img1 = np.ones((480, 640, 3), dtype=np.uint8) * 255
    center = (320, 240)
    cv2.ellipse(img1, center, (120, 140), 0, 0, 360, (200, 180, 160), -1)
    cv2.circle(img1, (280, 200), 20, (0, 0, 0), -1)
    cv2.circle(img1, (360, 200), 20, (0, 0, 0), -1)
    cv2.circle(img1, (320, 260), 10, (150, 120, 100), -1)
    cv2.ellipse(img1, (320, 300), (40, 20), 0, 0, 180, (100, 50, 50), 3)
    test_images.append(("large_face.jpg", img1))
    
    # 2. 小さな顔
    img2 = np.ones((480, 640, 3), dtype=np.uint8) * 255
    center = (320, 240)
    cv2.ellipse(img2, center, (40, 50), 0, 0, 360, (200, 180, 160), -1)
    cv2.circle(img2, (305, 225), 5, (0, 0, 0), -1)
    cv2.circle(img2, (335, 225), 5, (0, 0, 0), -1)
    cv2.circle(img2, (320, 240), 3, (150, 120, 100), -1)
    cv2.ellipse(img2, (320, 255), (12, 6), 0, 0, 180, (100, 50, 50), 2)
    test_images.append(("small_face.jpg", img2))
    
    # 3. 複数の顔
    img3 = np.ones((480, 640, 3), dtype=np.uint8) * 255
    # 顔1
    center1 = (200, 200)
    cv2.ellipse(img3, center1, (60, 70), 0, 0, 360, (200, 180, 160), -1)
    cv2.circle(img3, (180, 180), 8, (0, 0, 0), -1)
    cv2.circle(img3, (220, 180), 8, (0, 0, 0), -1)
    cv2.circle(img3, (200, 200), 5, (150, 120, 100), -1)
    cv2.ellipse(img3, (200, 220), (15, 8), 0, 0, 180, (100, 50, 50), 2)
    
    # 顔2
    center2 = (440, 280)
    cv2.ellipse(img3, center2, (50, 60), 0, 0, 360, (180, 160, 140), -1)
    cv2.circle(img3, (425, 260), 7, (0, 0, 0), -1)
    cv2.circle(img3, (455, 260), 7, (0, 0, 0), -1)
    cv2.circle(img3, (440, 280), 4, (130, 100, 80), -1)
    cv2.ellipse(img3, (440, 300), (12, 6), 0, 0, 180, (80, 30, 30), 2)
    test_images.append(("multiple_faces.jpg", img3))
    
    # 4. 角度のある顔（楕円を回転）
    img4 = np.ones((480, 640, 3), dtype=np.uint8) * 255
    center = (320, 240)
    cv2.ellipse(img4, center, (80, 100), 30, 0, 360, (200, 180, 160), -1)
    # 回転した目の位置を計算
    angle_rad = np.radians(30)
    eye1_x = int(320 + (-40) * np.cos(angle_rad) - (-30) * np.sin(angle_rad))
    eye1_y = int(240 + (-40) * np.sin(angle_rad) + (-30) * np.cos(angle_rad))
    eye2_x = int(320 + (40) * np.cos(angle_rad) - (-30) * np.sin(angle_rad))
    eye2_y = int(240 + (40) * np.sin(angle_rad) + (-30) * np.cos(angle_rad))
    cv2.circle(img4, (eye1_x, eye1_y), 10, (0, 0, 0), -1)
    cv2.circle(img4, (eye2_x, eye2_y), 10, (0, 0, 0), -1)
    test_images.append(("angled_face.jpg", img4))
    
    return test_images


def test_detection_methods():
    """各検出手法のテスト"""
    print("=== 検出手法比較テスト ===")
    
    # テスト画像作成
    test_images = create_test_images()
    test_input_dir = "test_detection_input"
    os.makedirs(test_input_dir, exist_ok=True)
    
    for filename, img in test_images:
        cv2.imwrite(os.path.join(test_input_dir, filename), img)
    
    # 各検出手法をテスト
    methods = ['auto', 'mediapipe', 'yunet', 'dlib', 'opencv']
    results = {}
    
    for method in methods:
        print(f"\n--- {method.upper()} 検出手法テスト ---")
        try:
            detector = AdvancedFaceDetector(detection_method=method)
            method_results = []
            
            for filename, img in test_images:
                start_time = time.time()
                faces = detector.detect_faces(img)
                detection_time = time.time() - start_time
                
                print(f"{filename}: {len(faces)}個の顔を検出 ({detection_time:.3f}秒)")
                method_results.append({
                    'filename': filename,
                    'face_count': len(faces),
                    'detection_time': detection_time,
                    'faces': faces
                })
                
                # 検出結果を画像に描画して保存
                result_img = img.copy()
                for (x, y, w, h) in faces:
                    cv2.rectangle(result_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(result_img, f'{method}', (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                output_filename = f"result_{method}_{filename}"
                cv2.imwrite(output_filename, result_img)
            
            results[method] = method_results
            
        except Exception as e:
            print(f"{method}検出手法でエラー: {e}")
            results[method] = None
    
    # 結果サマリー
    print("\n=== 検出結果サマリー ===")
    print(f"{'手法':<12} {'画像':<20} {'顔数':<6} {'時間(秒)':<10}")
    print("-" * 50)
    
    for method, method_results in results.items():
        if method_results:
            for result in method_results:
                print(f"{method:<12} {result['filename']:<20} {result['face_count']:<6} {result['detection_time']:<10.3f}")
        else:
            print(f"{method:<12} {'エラー':<20} {'-':<6} {'-':<10}")
    
    return results


def test_mosaic_quality():
    """モザイク品質のテスト"""
    print("\n=== モザイク品質テスト ===")
    
    try:
        detector = AdvancedFaceDetector(detection_method='auto')
        
        # テスト画像作成
        test_img = create_test_images()[0][1]  # 大きな顔の画像
        
        # 異なるモザイク比率でテスト
        ratios = [0.05, 0.1, 0.2, 0.5]
        
        for ratio in ratios:
            faces = detector.detect_faces(test_img)
            if faces:
                result_img = test_img.copy()
                for (x, y, w, h) in faces:
                    result_img = detector.apply_mosaic(result_img, x, y, w, h, ratio)
                
                output_filename = f"mosaic_test_ratio_{ratio}.jpg"
                cv2.imwrite(output_filename, result_img)
                print(f"モザイク比率 {ratio}: {output_filename} に保存")
            else:
                print(f"モザイク比率 {ratio}: 顔が検出されませんでした")
        
        return True
        
    except Exception as e:
        print(f"モザイク品質テストでエラー: {e}")
        return False


def test_batch_processing():
    """バッチ処理のテスト"""
    print("\n=== バッチ処理テスト ===")
    
    try:
        processor = AdvancedImageProcessor(detection_method='auto')
        
        # テスト用ディレクトリ作成
        test_input_dir = "test_batch_input"
        test_output_dir = "test_batch_output"
        
        os.makedirs(test_input_dir, exist_ok=True)
        os.makedirs(test_output_dir, exist_ok=True)
        
        # テスト画像を複数作成
        test_images = create_test_images()
        for filename, img in test_images:
            cv2.imwrite(os.path.join(test_input_dir, filename), img)
        
        # バッチ処理実行
        start_time = time.time()
        success_count, error_count = processor.process_directory(
            test_input_dir, test_output_dir, mosaic_ratio=0.1
        )
        processing_time = time.time() - start_time
        
        print(f"バッチ処理結果:")
        print(f"  成功: {success_count} ファイル")
        print(f"  失敗: {error_count} ファイル")
        print(f"  処理時間: {processing_time:.2f} 秒")
        
        return success_count > 0
        
    except Exception as e:
        print(f"バッチ処理テストでエラー: {e}")
        return False


def test_system_info():
    """システム情報のテスト"""
    print("=== システム情報テスト ===")
    
    try:
        info = get_system_info()
        for key, value in info.items():
            print(f"{key}: {value}")
        
        print("\n=== 利用可能な検出手法 ===")
        if info['mediapipe_available']:
            print("✓ MediaPipe Face Detection")
        else:
            print("✗ MediaPipe Face Detection (pip install mediapipe)")
            
        if info['dlib_available']:
            print("✓ Dlib Face Detection")
        else:
            print("✗ Dlib Face Detection (pip install dlib)")
            
        print("✓ OpenCV Haar Cascade")
        
        return True
        
    except Exception as e:
        print(f"システム情報テストでエラー: {e}")
        return False


def main():
    """メインテスト関数"""
    print("高精度顔モザイク処理ツール - 拡張テストスイート")
    print("=" * 60)
    
    tests = [
        ("システム情報", test_system_info),
        ("検出手法比較", test_detection_methods),
        ("モザイク品質", test_mosaic_quality),
        ("バッチ処理", test_batch_processing),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}テストを実行中...")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "成功" if result else "失敗"
            print(f"{test_name}テスト: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"{test_name}テスト: エラー - {e}")
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー:")
    
    success_count = 0
    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"  {status} {test_name}")
        if result:
            success_count += 1
    
    print(f"\n成功: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("全てのテストが成功しました！")
        return True
    else:
        print("一部のテストが失敗しました。")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
