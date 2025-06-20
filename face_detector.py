"""
高精度顔検出とモザイク処理のコアモジュール
MediaPipe、Dlib、OpenCVの複数手法を組み合わせて高精度検出を実現
"""

import cv2
import numpy as np
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import platform
import logging

# 高精度顔検出ライブラリ
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("警告: MediaPipeが利用できません。pip install mediapipe でインストールしてください。")

try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    DLIB_AVAILABLE = False
    print("警告: Dlibが利用できません。pip install dlib でインストールしてください。")


def safe_import_check():
    """ライブラリのインポート状況を安全にチェック"""
    global MEDIAPIPE_AVAILABLE, DLIB_AVAILABLE
    
    # MediaPipeの詳細チェック
    if MEDIAPIPE_AVAILABLE:
        try:
            # 実際に使用する機能をテスト
            mp.solutions.face_detection
            mp.solutions.drawing_utils
        except Exception as e:
            print(f"MediaPipe機能テストに失敗: {e}")
            MEDIAPIPE_AVAILABLE = False
    
    # Dlibの詳細チェック
    if DLIB_AVAILABLE:
        try:
            # 実際に使用する機能をテスト
            dlib.get_frontal_face_detector()
        except Exception as e:
            print(f"Dlib機能テストに失敗: {e}")
            DLIB_AVAILABLE = False


# 初期化時にチェック実行
safe_import_check()


class AdvancedFaceDetector:
    def __init__(self, detection_method='auto'):
        """
        高精度顔検出器の初期化
        
        Args:
            detection_method: 検出手法 ('mediapipe', 'dlib', 'opencv', 'auto')
        """
        self.detection_method = detection_method
        self.detectors = {}
        self._initialize_detectors()
        
    def _initialize_detectors(self):
        """YuNet検出器の初期化（専用）"""
        
        # MediaPipe Face Detection（削除 - 精度不十分）
        # MediaPipeは検証の結果、十分な精度が得られませんでした
        
        # Dlib Face Detection（削除 - 精度不十分）
        # Dlibは検証の結果、十分な精度が得られませんでした
        
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
                # input_size: (width, height) - 検出する画像サイズ
                # conf_threshold: 信頼度閾値
                # nms_threshold: Non-Maximum Suppression閾値
                self.detectors['yunet'] = cv2.FaceDetectorYN.create(
                    model=model_path,
                    config="",
                    input_size=(320, 240),  # デフォルトサイズ、実行時に動的変更
                    score_threshold=0.6,    # 信頼度閾値（小さい顔も検出するため少し下げる）
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
            model_url = "https://github.com/opencv/opencv_zoo/raw/refs/heads/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
            
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
            model_url = "https://github.com/opencv/opencv_zoo/raw/refs/heads/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
            
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
        指定された領域にモザイクを適用
        
        Args:
            image: 入力画像
            x, y, w, h: モザイクを適用する領域
            mosaic_ratio: モザイクの粗さ（小さいほど粗い）
            
        Returns:
            モザイク処理後の画像
        """
        # 境界チェック
        h_img, w_img = image.shape[:2]
        x = max(0, min(x, w_img - 1))
        y = max(0, min(y, h_img - 1))
        w = max(1, min(w, w_img - x))
        h = max(1, min(h, h_img - y))
        
        # 領域を切り出し
        face_region = image[y:y+h, x:x+w]
        
        # モザイクサイズを計算
        mosaic_h = max(1, int(h * mosaic_ratio))
        mosaic_w = max(1, int(w * mosaic_ratio))
        
        # 縮小してから拡大することでモザイク効果を作成
        small = cv2.resize(face_region, (mosaic_w, mosaic_h), 
                          interpolation=cv2.INTER_LINEAR)
        mosaic = cv2.resize(small, (w, h), 
                           interpolation=cv2.INTER_NEAREST)
        
        # 元の画像にモザイク領域を貼り付け
        result = image.copy()
        result[y:y+h, x:x+w] = mosaic
        
        return result
    
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
                # 顔が検出されなくても元画像をコピー
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                success = cv2.imwrite(output_path, image)
                return success
            
            print(f"{len(faces)}個の顔を検出: {image_path}")
            
            # 各顔にモザイクを適用
            result_image = image.copy()
            for (x, y, w, h) in faces:
                result_image = self.apply_mosaic(result_image, x, y, w, h, mosaic_ratio)
            
            # 出力ディレクトリを作成
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 画像保存
            success = cv2.imwrite(output_path, result_image)
            if not success:
                print(f"画像の保存に失敗: {output_path}")
                return False
                
            return True
            
        except Exception as e:
            print(f"画像処理エラー ({image_path}): {e}")
            return False


class AdvancedImageProcessor:
    def __init__(self, detection_method='auto'):
        """高精度画像処理クラスの初期化"""
        self.detector = AdvancedFaceDetector(detection_method)
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
    def get_image_files(self, input_dir: str) -> List[str]:
        """
        指定ディレクトリから画像ファイルを取得
        
        Args:
            input_dir: 入力ディレクトリパス
            
        Returns:
            画像ファイルパスのリスト
        """
        image_files = []
        input_path = Path(input_dir)
        
        if not input_path.exists():
            print(f"入力ディレクトリが存在しません: {input_dir}")
            return []
        
        # 再帰的に画像ファイルを検索
        for file_path in input_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                image_files.append(str(file_path))
                
        return sorted(image_files)
    
    def process_directory(self, input_dir: str, output_dir: str, 
                         mosaic_ratio: float = 0.1, 
                         progress_callback: Optional[callable] = None) -> Tuple[int, int]:
        """
        ディレクトリ内の全画像を処理
        
        Args:
            input_dir: 入力ディレクトリ
            output_dir: 出力ディレクトリ
            mosaic_ratio: モザイクの粗さ
            progress_callback: 進捗コールバック関数
            
        Returns:
            (成功数, 失敗数)のタプル
        """
        image_files = self.get_image_files(input_dir)
        
        if not image_files:
            print("処理対象の画像ファイルが見つかりません")
            return 0, 0
        
        success_count = 0
        error_count = 0
        
        for i, image_path in enumerate(image_files):
            try:
                # 相対パスを計算
                rel_path = os.path.relpath(image_path, input_dir)
                output_path = os.path.join(output_dir, rel_path)
                
                # 画像処理
                if self.detector.process_image(image_path, output_path, mosaic_ratio):
                    success_count += 1
                    print(f"処理完了: {rel_path}")
                else:
                    error_count += 1
                    print(f"処理失敗: {rel_path}")
                
                # 進捗コールバック
                if progress_callback:
                    progress_callback(i + 1, len(image_files))
                    
            except Exception as e:
                error_count += 1
                print(f"処理エラー ({image_path}): {e}")
        
        return success_count, error_count


def check_gpu_support() -> bool:
    """GPU対応の確認"""
    gpu_info = {}
    
    # OpenCV CUDA
    try:
        gpu_info['opencv_cuda'] = cv2.cuda.getCudaEnabledDeviceCount() > 0
    except:
        gpu_info['opencv_cuda'] = False
    
    # Dlib CUDA
    try:
        gpu_info['dlib_cuda'] = DLIB_AVAILABLE and hasattr(dlib, 'cuda')
    except:
        gpu_info['dlib_cuda'] = False
    
    return any(gpu_info.values())


def get_dlib_version():
    """Dlibのバージョンを取得（複数の属性名に対応）"""
    if not DLIB_AVAILABLE:
        return "Not Available"
    
    try:
        # 新しいバージョンのDlib
        if hasattr(dlib, '__version__'):
            return dlib.__version__
        # 古いバージョンのDlib
        elif hasattr(dlib, 'DLIB_VERSION'):
            return dlib.DLIB_VERSION
        # バージョン情報が取得できない場合
        else:
            return "Unknown"
    except:
        return "Unknown"


def get_system_info() -> dict:
    """システム情報の取得"""
    info = {
        'platform': platform.system(),
        'architecture': platform.architecture()[0],
        'opencv_version': cv2.__version__,
        'yunet_supported': is_yunet_supported(),
        'gpu_support': check_gpu_support(),
        'mediapipe_available': MEDIAPIPE_AVAILABLE,
        'dlib_available': DLIB_AVAILABLE,
    }
    
    if MEDIAPIPE_AVAILABLE:
        try:
            info['mediapipe_version'] = mp.__version__
        except:
            info['mediapipe_version'] = "Unknown"
    
    if DLIB_AVAILABLE:
        info['dlib_version'] = get_dlib_version()
    
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
