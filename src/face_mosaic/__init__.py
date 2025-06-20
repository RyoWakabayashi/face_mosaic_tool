"""
Face Mosaic Tool - YuNet専用高精度顔モザイク処理ツール

高精度な顔検出とモザイク処理を提供するPythonパッケージ
"""

__version__ = "2.0.0"
__author__ = "Face Mosaic Tool Team"
__description__ = "YuNet専用高精度顔モザイク処理ツール"

# メインクラスのインポート
from .core.application import FaceMosaicApplication
from .config.settings import AppConfig, default_config

# 例外クラスのインポート
from .core.exceptions import (
    FaceMosaicError,
    ModelError,
    DetectionError,
    ImageProcessingError,
    ConfigurationError,
    ValidationError,
)

# ユーティリティ関数のインポート
from .utils.system_info import get_system_info, check_requirements, print_system_info

__all__ = [
    # メインクラス
    "FaceMosaicApplication",
    # 設定
    "AppConfig",
    "default_config",
    # 例外
    "FaceMosaicError",
    "ModelError",
    "DetectionError",
    "ImageProcessingError",
    "ConfigurationError",
    "ValidationError",
    # ユーティリティ
    "get_system_info",
    "check_requirements",
    "print_system_info",
    # メタ情報
    "__version__",
    "__author__",
    "__description__",
]


def create_application(config=None):
    """
    アプリケーションインスタンスを作成

    Args:
        config: アプリケーション設定（Noneの場合はデフォルト設定）

    Returns:
        FaceMosaicApplicationインスタンス
    """
    return FaceMosaicApplication(config)


def quick_process(input_path, output_path, mosaic_ratio=0.1):
    """
    クイック処理関数

    Args:
        input_path: 入力パス（ファイルまたはディレクトリ）
        output_path: 出力パス
        mosaic_ratio: モザイク比率

    Returns:
        処理結果
    """
    from pathlib import Path

    app = create_application()
    app.update_mosaic_ratio(mosaic_ratio)

    input_path = Path(input_path)
    output_path = Path(output_path)

    if input_path.is_file():
        return app.process_single_image(input_path, output_path)
    elif input_path.is_dir():
        return app.process_directory(input_path, output_path)
    else:
        raise FileNotFoundError(f"入力パスが見つかりません: {input_path}")
