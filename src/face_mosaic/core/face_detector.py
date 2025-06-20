"""
顔検出クラス
YuNetを使用した高精度顔検出
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path

from ..config.settings import DetectionConfig
from ..core.exceptions import DetectionError, ModelLoadError
from ..core.model_manager import ModelManager


class FaceDetector:
    """YuNet顔検出クラス"""

    def __init__(self, config: DetectionConfig, model_manager: ModelManager):
        """
        初期化

        Args:
            config: 検出設定
            model_manager: モデル管理インスタンス
        """
        self.config = config
        self.model_manager = model_manager
        self.detector = None
        self._initialize_detector()

    def _initialize_detector(self) -> None:
        """
        検出器を初期化

        Raises:
            ModelLoadError: モデル読み込み失敗時
        """
        try:
            # モデルファイルを確保
            model_path = self.model_manager.ensure_model_available()

            # YuNet検出器を初期化
            self.detector = cv2.FaceDetectorYN.create(
                str(model_path),
                "",
                self.config.input_size,
                self.config.confidence_threshold,
                self.config.nms_threshold,
                self.config.top_k,
            )

            print("OpenCV YuNet Face Detection を初期化しました")

        except Exception as e:
            raise ModelLoadError(f"YuNet検出器の初期化に失敗しました: {e}")

    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        画像から顔を検出

        Args:
            image: 入力画像（BGR形式）

        Returns:
            検出された顔の座標リスト [(x, y, w, h), ...]

        Raises:
            DetectionError: 検出処理失敗時
        """
        if self.detector is None:
            raise DetectionError("検出器が初期化されていません")

        if image is None or image.size == 0:
            raise DetectionError("無効な画像です")

        try:
            # 画像サイズを設定
            height, width = image.shape[:2]
            self.detector.setInputSize((width, height))

            # 顔検出実行
            _, faces = self.detector.detect(image)

            if faces is None:
                return []

            # 結果を整数座標に変換
            face_list = []
            for face in faces:
                x, y, w, h = face[:4].astype(int)
                # 負の値や画像外の座標をクリップ
                x = max(0, min(x, width - 1))
                y = max(0, min(y, height - 1))
                w = max(1, min(w, width - x))
                h = max(1, min(h, height - y))
                face_list.append((x, y, w, h))

            return face_list

        except Exception as e:
            raise DetectionError(f"顔検出に失敗しました: {e}")

    def detect_faces_with_confidence(
        self, image: np.ndarray
    ) -> List[Tuple[int, int, int, int, float]]:
        """
        信頼度付きで顔を検出

        Args:
            image: 入力画像（BGR形式）

        Returns:
            検出された顔の座標と信頼度リスト [(x, y, w, h, confidence), ...]

        Raises:
            DetectionError: 検出処理失敗時
        """
        if self.detector is None:
            raise DetectionError("検出器が初期化されていません")

        if image is None or image.size == 0:
            raise DetectionError("無効な画像です")

        try:
            # 画像サイズを設定
            height, width = image.shape[:2]
            self.detector.setInputSize((width, height))

            # 顔検出実行
            _, faces = self.detector.detect(image)

            if faces is None:
                return []

            # 結果を整数座標と信頼度に変換
            face_list = []
            for face in faces:
                x, y, w, h = face[:4].astype(int)
                confidence = float(face[14])  # YuNetの信頼度は14番目の要素

                # 負の値や画像外の座標をクリップ
                x = max(0, min(x, width - 1))
                y = max(0, min(y, height - 1))
                w = max(1, min(w, width - x))
                h = max(1, min(h, height - y))

                face_list.append((x, y, w, h, confidence))

            return face_list

        except Exception as e:
            raise DetectionError(f"顔検出に失敗しました: {e}")

    def is_available(self) -> bool:
        """
        検出器が利用可能かチェック

        Returns:
            利用可能かどうか
        """
        return self.detector is not None

    def get_detector_info(self) -> dict:
        """
        検出器情報を取得

        Returns:
            検出器情報辞書
        """
        return {
            "available": self.is_available(),
            "method": "YuNet",
            "confidence_threshold": self.config.confidence_threshold,
            "nms_threshold": self.config.nms_threshold,
            "input_size": self.config.input_size,
            "model_info": self.model_manager.get_model_info(),
        }
