"""
設定管理モジュール
アプリケーション全体の設定を一元管理
"""

from dataclasses import dataclass
from typing import Tuple
from pathlib import Path


@dataclass
class DetectionConfig:
    """顔検出設定"""

    method: str = "yunet"
    confidence_threshold: float = 0.6
    nms_threshold: float = 0.3
    top_k: int = 5000
    input_size: Tuple[int, int] = (320, 320)


@dataclass
class MosaicConfig:
    """モザイク処理設定"""

    ratio: float = 0.1
    blur_strength: int = 15
    pixelate: bool = True
    margin_ratio: float = 0.1


@dataclass
class ProcessingConfig:
    """処理設定"""

    supported_formats: Tuple[str, ...] = (
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".tiff",
        ".webp",
    )
    max_image_size: int = 4096
    quality: int = 95
    preserve_metadata: bool = False


@dataclass
class ModelConfig:
    """モデル設定"""

    yunet_model_url: str = (
        "https://github.com/opencv/opencv_zoo/raw/main/models/"
        "face_detection_yunet/face_detection_yunet_2023mar.onnx"
    )
    model_filename: str = "face_detection_yunet_2023mar.onnx"
    model_cache_dir: Path = Path.cwd()


@dataclass
class AppConfig:
    """アプリケーション設定"""

    # GUI設定
    window_size: Tuple[int, int] = (800, 600)
    theme: str = "default"

    # ログ設定
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def __post_init__(self):
        """初期化後処理"""
        self.detection = DetectionConfig()
        self.mosaic = MosaicConfig()
        self.processing = ProcessingConfig()
        self.model = ModelConfig()


# デフォルト設定インスタンス
default_config = AppConfig()
