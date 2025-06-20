"""
高精度顔検出とモザイク処理のコアモジュール
OpenCV YuNetによる高精度検出を実現
"""

import os
import cv2
import numpy as np
import platform
from typing import List, Tuple, Optional
from PIL import Image, ImageFilter


def safe_import_check():
    """ライブラリのインポート状況を安全にチェック"""
    # YuNet専用のため、OpenCVのバージョンチェックのみ
    try:
        opencv_version = cv2.__version__.split('.')
        major, minor = int(opencv_version[0]), int(opencv_version[1])
        
        if major < 4 or (major == 4 and minor < 5):
            print(f"警告: YuNetにはOpenCV 4.5.4以上が必要です（現在: {cv2.__version__}）")
            return False
        return True
    except Exception as e:
        print(f"OpenCVバージョンチェックに失敗: {e}")
        return False


# 初期化時にチェック実行
safe_import_check()


class AdvancedFaceDetector:
    """YuNet専用高精度顔検出器"""
    
    def __init__(self, detection_method: str = 'yunet'):
        """
        YuNet専用顔検出器の初期化
        
        Args:
            detection_method: 検出手法（'yunet'固定）
        """
        self.detection_method = detection_method
        self.detectors = {}
        self._initialize_detectors()
    
    def _initialize_detectors(self):
        """YuNet検出器の初期化（専用）"""
        
        # OpenCV YuNet Face Detection（唯一の十分な精度を持つ手法）
        try:
            self._initialize_yunet()
        except Exception as e:
            print(f"YuNet初期化エラー: {e}")
            print("エラー: YuNetが利用できません。OpenCV 4.5.4以上が必要です。")
        
        # YuNetが利用できない場合の警告
        if 'yunet' not in self.detectors:
            print("警告: 高精度な顔検出手法が利用できません。")
            print("OpenCV 4.5.4以上をインストールしてください。")
        
        print(f"初期化完了: {len(self.detectors)}個の検出器が利用可能")
    
    def _initialize_yunet(self):
        """OpenCV YuNet顔検出器の初期化"""
        try:
            # OpenCV 4.5.4以上でYuNetが利用可能
            opencv_version = cv2.__version__.split('.')
            major, minor = int(opencv_version[0]), int(opencv_version[1])
            
            if major < 4 or (major == 4 and minor < 5):
                print(f"YuNetにはOpenCV 4.5.4以上が必要です（現在: {cv2.__version__}）")
                return
            
            # YuNetモデルファイルのダウンロード
            model_path = self._download_yunet_model()
            
            if model_path and os.path.exists(model_path):
                # YuNet検出器を初期化
                self.detectors['yunet'] = cv2.FaceDetectorYN.create(
                    model=model_path,
                    config="",
                    input_size=(320, 240),  # デフォルトサイズ、実行時に動的変更
                    score_threshold=0.6,    # 信頼度閾値
                    nms_threshold=0.3,      # NMS閾値
                    top_k=5000,            # 最大検出数
                    backend_id=cv2.dnn.DNN_BACKEND_DEFAULT,
                    target_id=cv2.dnn.DNN_TARGET_CPU
                )
                print("OpenCV YuNet Face Detection を初期化しました")
            else:
                print("YuNetモデルファイルが見つかりません")
                
        except Exception as e:
            print(f"YuNet初期化中にエラー: {e}")
    
    def _download_yunet_model(self) -> Optional[str]:
        """YuNetモデルのダウンロード（Proxy対応）"""
        model_path = "face_detection_yunet_2023mar.onnx"
        
        if os.path.exists(model_path):
            return model_path
        
        try:
            from proxy_utils import download_with_proxy, get_proxy_manager
            
            proxy_manager = get_proxy_manager()
            if proxy_manager.is_proxy_enabled():
                print("Proxy環境でYuNetモデルをダウンロードします")
            
            print("YuNetモデルをダウンロード中...")
            
            # YuNetモデルファイル（OpenCV公式）
            model_url = "https://github.com/opencv/opencv_zoo/raw/master/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
            
            # Proxy対応ダウンロード
            if download_with_proxy(model_url, model_path):
                print("YuNetモデルのダウンロードが完了しました")
                return model_path
            else:
                print("YuNetモデルのダウンロードに失敗しました")
                return None
                
        except ImportError:
            print("Proxy対応モジュールが見つかりません。従来の方法でダウンロードを試行します...")
            return self._download_yunet_model_fallback()
        except Exception as e:
            print(f"YuNetモデルのダウンロードに失敗: {e}")
            return self._download_yunet_model_fallback()
    
    def _download_yunet_model_fallback(self) -> Optional[str]:
        """YuNetモデルのダウンロード（従来方法）"""
        model_path = "face_detection_yunet_2023mar.onnx"
        
        try:
            import urllib.request
            
            print("従来の方法でYuNetモデルをダウンロード中...")
            model_url = "https://github.com/opencv/opencv_zoo/raw/master/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
            
            # ダウンロード
            urllib.request.urlretrieve(model_url, model_path)
            
            print("YuNetモデルのダウンロードが完了しました")
            return model_path
            
        except Exception as e:
            print(f"従来方法でのYuNetモデルダウンロードに失敗: {e}")
            return None
    
    def detect_faces_yunet(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """OpenCV YuNetによる顔検出"""
        if 'yunet' not in self.detectors:
            return []
        
        try:
            h, w = image.shape[:2]
            
            # 入力サイズを動的に設定
            self.detectors['yunet'].setInputSize((w, h))
            
            # 顔検出実行
            _, faces = self.detectors['yunet'].detect(image)
            
            detected_faces = []
            if faces is not None:
                for face in faces:
                    # YuNetの出力形式: [x, y, w, h, x_re, y_re, x_le, y_le, x_nt, y_nt, x_rcm, y_rcm, x_lcm, y_lcm, conf]
                    # 最初の4つが顔の境界ボックス
                    x, y, w_face, h_face = face[:4].astype(int)
                    
                    # 境界チェック
                    x = max(0, x)
                    y = max(0, y)
                    w_face = min(w_face, w - x)
                    h_face = min(h_face, h - y)
                    
                    if w_face > 10 and h_face > 10:  # 最小サイズチェック
                        detected_faces.append((x, y, w_face, h_face))
            
            return detected_faces
            
        except Exception as e:
            print(f"YuNet顔検出エラー: {e}")
            return []
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        YuNetによる高精度顔検出
        
        Args:
            image: 入力画像（BGR形式）
            
        Returns:
            検出された顔の座標リスト [(x, y, w, h), ...]
        """
        # YuNetのみを使用（検証により唯一十分な精度を持つ手法）
        if 'yunet' in self.detectors:
            return self.detect_faces_yunet(image)
        else:
            print("エラー: YuNetが利用できません。OpenCV 4.5.4以上が必要です。")
            return []
    
    def apply_mosaic(self, image: np.ndarray, x: int, y: int, w: int, h: int, 
                    mosaic_ratio: float = 0.1) -> np.ndarray:
        """
        指定領域にモザイク処理を適用
        
        Args:
            image: 入力画像
            x, y, w, h: モザイクを適用する領域
            mosaic_ratio: モザイクの粗さ（小さいほど粗い）
            
        Returns:
            モザイク処理後の画像
        """
        try:
            # 領域の境界チェック
            h_img, w_img = image.shape[:2]
            x = max(0, min(x, w_img - 1))
            y = max(0, min(y, h_img - 1))
            w = max(1, min(w, w_img - x))
            h = max(1, min(h, h_img - y))
            
            # 対象領域を抽出
            face_region = image[y:y+h, x:x+w]
            
            if face_region.size == 0:
                return image
            
            # モザイクサイズを計算（最小1ピクセル）
            mosaic_w = max(1, int(w * mosaic_ratio))
            mosaic_h = max(1, int(h * mosaic_ratio))
            
            # 縮小してから拡大することでモザイク効果を作成
            small = cv2.resize(face_region, (mosaic_w, mosaic_h), interpolation=cv2.INTER_LINEAR)
            mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
            
            # 元画像にモザイク領域を適用
            result = image.copy()
            result[y:y+h, x:x+w] = mosaic
            
            return result
            
        except Exception as e:
            print(f"モザイク処理エラー: {e}")
            return image
    
    def process_image(self, image_path: str, output_path: str, 
                     mosaic_ratio: float = 0.1) -> bool:
        """
        画像ファイルを処理してモザイクを適用
        
        Args:
            image_path: 入力画像パス
            output_path: 出力画像パス
            mosaic_ratio: モザイクの粗さ
            
        Returns:
            処理成功の可否
        """
        try:
            # 画像読み込み
            image = cv2.imread(image_path)
            if image is None:
                print(f"画像の読み込みに失敗: {image_path}")
                return False
            
            # 顔検出
            faces = self.detect_faces(image)
            
            if not faces:
                print(f"顔が検出されませんでした: {image_path}")
                # 顔が検出されなくても元画像を保存
                cv2.imwrite(output_path, image)
                return True
            
            print(f"{len(faces)}個の顔を検出: {image_path}")
            
            # 各顔にモザイクを適用
            result_image = image.copy()
            for x, y, w, h in faces:
                result_image = self.apply_mosaic(result_image, x, y, w, h, mosaic_ratio)
            
            # 結果を保存
            success = cv2.imwrite(output_path, result_image)
            if success:
                print(f"処理完了: {output_path}")
                return True
            else:
                print(f"画像の保存に失敗: {output_path}")
                return False
                
        except Exception as e:
            print(f"画像処理エラー ({image_path}): {e}")
            return False


def check_gpu_support() -> bool:
    """GPU対応状況をチェック"""
    gpu_info = {}
    
    # OpenCV CUDA
    try:
        gpu_info['opencv_cuda'] = cv2.cuda.getCudaEnabledDeviceCount() > 0
    except:
        gpu_info['opencv_cuda'] = False
    
    return any(gpu_info.values())


def get_system_info() -> dict:
    """システム情報の取得"""
    info = {
        'platform': platform.system(),
        'architecture': platform.architecture()[0],
        'opencv_version': cv2.__version__,
        'yunet_supported': is_yunet_supported(),
        'gpu_support': check_gpu_support(),
    }
    
    return info


def is_yunet_supported() -> bool:
    """YuNetがサポートされているかチェック"""
    try:
        opencv_version = cv2.__version__.split('.')
        major, minor = int(opencv_version[0]), int(opencv_version[1])
        
        # OpenCV 4.5.4以上でYuNetが利用可能
        if major > 4 or (major == 4 and minor >= 5):
            # FaceDetectorYNクラスが存在するかチェック
            return hasattr(cv2, 'FaceDetectorYN')
        return False
    except:
        return False


# 使用例
if __name__ == "__main__":
    # YuNet専用検出器を初期化
    detector = AdvancedFaceDetector()
    
    # システム情報表示
    info = get_system_info()
    print("=== システム情報 ===")
    for key, value in info.items():
        print(f"{key}: {value}")
    
    # テスト画像があれば処理
    test_image = "test.jpg"
    if os.path.exists(test_image):
        detector.process_image(test_image, "output.jpg")
    else:
        print("テスト画像が見つかりません")
