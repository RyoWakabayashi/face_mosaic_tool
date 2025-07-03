"""
画像処理クラス
モザイク処理とファイル操作を担当
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from PIL import Image, ImageFilter

from ..config.settings import MosaicConfig, ProcessingConfig
from ..core.exceptions import ImageProcessingError, InvalidImageError
from ..core.face_detector import FaceDetector
from ..core.object_detector import ObjectDetector
from ..utils.file_utils import validate_image_format, ensure_directory


class ImageProcessor:
    """画像処理クラス"""

    def __init__(
        self,
        face_detector: FaceDetector,
        mosaic_config: MosaicConfig,
        processing_config: ProcessingConfig,
        object_detector: ObjectDetector = None,
        object_labels: list = None,
        use_object_detection: bool = False,
    ):
        """
        初期化

        Args:
            face_detector: 顔検出インスタンス
            mosaic_config: モザイク設定
            processing_config: 処理設定
            object_detector: 物体検出インスタンス（オプション）
            object_labels: モザイクをかける物体のラベルリスト（オプション）
            use_object_detection: 物体検出を使用するかどうか（オプション）
        """
        self.face_detector = face_detector
        self.mosaic_config = mosaic_config
        self.processing_config = processing_config
        self.object_detector = object_detector
        self.object_labels = object_labels or []
        self.use_object_detection = use_object_detection

    def apply_mosaic(
        self, image: np.ndarray, faces: List[Tuple[int, int, int, int]]
    ) -> np.ndarray:
        """
        画像に顔モザイクを適用

        Args:
            image: 入力画像（BGR形式）
            faces: 顔座標リスト [(x, y, w, h), ...]

        Returns:
            モザイク処理済み画像

        Raises:
            ImageProcessingError: 処理失敗時
        """
        if image is None or image.size == 0:
            raise InvalidImageError("無効な画像です")

        try:
            result_image = image.copy()

            for x, y, w, h in faces:
                # マージンを追加
                margin_w = int(w * self.mosaic_config.margin_ratio)
                margin_h = int(h * self.mosaic_config.margin_ratio)

                # 座標を調整（マージン付き）
                x1 = max(0, x - margin_w)
                y1 = max(0, y - margin_h)
                x2 = min(image.shape[1], x + w + margin_w)
                y2 = min(image.shape[0], y + h + margin_h)

                # 顔領域を抽出
                face_region = result_image[y1:y2, x1:x2]

                if face_region.size == 0:
                    continue

                # モザイク処理を適用
                if self.mosaic_config.pixelate:
                    mosaic_region = self._apply_pixelate_mosaic(face_region)
                else:
                    mosaic_region = self._apply_blur_mosaic(face_region)

                # 処理済み領域を元画像に戻す
                result_image[y1:y2, x1:x2] = mosaic_region

            return result_image

        except Exception as e:
            raise ImageProcessingError(f"モザイク処理に失敗しました: {e}")

    def _apply_pixelate_mosaic(self, region: np.ndarray) -> np.ndarray:
        """
        ピクセル化モザイクを適用

        Args:
            region: 処理対象領域

        Returns:
            モザイク処理済み領域
        """
        height, width = region.shape[:2]

        # モザイクサイズを計算
        mosaic_size = max(1, int(min(width, height) * self.mosaic_config.ratio))

        # 縮小してから拡大（ピクセル化効果）
        small_region = cv2.resize(
            region, (mosaic_size, mosaic_size), interpolation=cv2.INTER_LINEAR
        )
        mosaic_region = cv2.resize(
            small_region, (width, height), interpolation=cv2.INTER_NEAREST
        )

        return mosaic_region

    def _apply_blur_mosaic(self, region: np.ndarray) -> np.ndarray:
        """
        ブラーモザイクを適用

        Args:
            region: 処理対象領域

        Returns:
            モザイク処理済み領域
        """
        # ガウシアンブラーを適用
        blur_strength = self.mosaic_config.blur_strength
        if blur_strength % 2 == 0:
            blur_strength += 1  # 奇数にする

        mosaic_region = cv2.GaussianBlur(region, (blur_strength, blur_strength), 0)

        return mosaic_region

    def process_image_file(self, input_path: Path, output_path: Path) -> Dict[str, Any]:
        """
        画像ファイルを処理

        Args:
            input_path: 入力ファイルパス
            output_path: 出力ファイルパス

        Returns:
            処理結果辞書

        Raises:
            ImageProcessingError: 処理失敗時
        """
        # 入力ファイル検証
        validate_image_format(input_path, self.processing_config.supported_formats)

        # 画像読み込み
        image = cv2.imread(str(input_path))
        if image is None:
            raise InvalidImageError(f"画像を読み込めません: {input_path}")

        # 画像サイズチェック
        height, width = image.shape[:2]
        max_size = self.processing_config.max_image_size
        if max(width, height) > max_size:
            # リサイズ
            scale = max_size / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height))
            print(
                f"画像をリサイズしました: {width}x{height} -> {new_width}x{new_height}"
            )

        # 顔検出
        faces = self.face_detector.detect_faces(image)
        # 物体検出（オプション）
        objects = []
        if self.use_object_detection and self.object_detector and self.object_labels:
            # OpenCVはBGR, torchvisionはRGBなので変換
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            detected = self.object_detector.detect(
                rgb_image, target_labels=self.object_labels
            )
            for obj in detected:
                x1, y1, x2, y2 = obj["box"]
                w, h = x2 - x1, y2 - y1
                objects.append((x1, y1, w, h))

        # モザイク処理
        all_targets = faces + objects
        if all_targets:
            processed_image = self.apply_mosaic(image, all_targets)
            print(
                f"{len(faces)}個の顔, {len(objects)}個の物体を検出: {input_path.name}"
            )
        else:
            processed_image = image
            print(f"顔・物体が検出されませんでした: {input_path.name}")

        # 出力ディレクトリ作成
        ensure_directory(output_path.parent)

        # 画像保存
        success = cv2.imwrite(
            str(output_path),
            processed_image,
            [cv2.IMWRITE_JPEG_QUALITY, self.processing_config.quality],
        )

        if not success:
            raise ImageProcessingError(f"画像の保存に失敗しました: {output_path}")

        print(f"処理完了: {output_path}")

        return {
            "success": True,
            "faces_detected": len(faces),
            "objects_detected": len(objects),
            "input_path": str(input_path),
            "output_path": str(output_path),
            "original_size": (width, height),
            "processed_size": processed_image.shape[:2][::-1],
        }

    def get_processor_info(self) -> Dict[str, Any]:
        """
        プロセッサ情報を取得

        Returns:
            プロセッサ情報辞書
        """
        return {
            "mosaic_config": {
                "ratio": self.mosaic_config.ratio,
                "blur_strength": self.mosaic_config.blur_strength,
                "pixelate": self.mosaic_config.pixelate,
                "margin_ratio": self.mosaic_config.margin_ratio,
            },
            "processing_config": {
                "supported_formats": self.processing_config.supported_formats,
                "max_image_size": self.processing_config.max_image_size,
                "quality": self.processing_config.quality,
            },
            "face_detector": self.face_detector.get_detector_info(),
        }
