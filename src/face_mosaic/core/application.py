"""
メインアプリケーションクラス
全体の処理を統合管理
"""

from pathlib import Path
from typing import Dict, Any, Optional, Callable

from ..config.settings import AppConfig, default_config
from ..core.model_manager import ModelManager
from ..core.face_detector import FaceDetector
from ..core.image_processor import ImageProcessor
from ..core.batch_processor import BatchProcessor
from ..utils.system_info import get_system_info, check_requirements


class FaceMosaicApplication:
    """顔モザイクアプリケーションクラス"""

    def __init__(self, config: Optional[AppConfig] = None):
        """
        初期化

        Args:
            config: アプリケーション設定（Noneの場合はデフォルト設定を使用）
        """
        self.config = config or default_config

        # コンポーネント初期化
        self.model_manager = ModelManager(self.config.model)
        self.face_detector = FaceDetector(self.config.detection, self.model_manager)
        self.image_processor = ImageProcessor(
            self.face_detector, self.config.mosaic, self.config.processing
        )
        self.batch_processor = BatchProcessor(
            self.image_processor, self.config.processing
        )

    def process_single_image(
        self, input_path: Path, output_path: Path
    ) -> Dict[str, Any]:
        """
        単一画像を処理

        Args:
            input_path: 入力画像パス
            output_path: 出力画像パス

        Returns:
            処理結果
        """
        return self.image_processor.process_image_file(input_path, output_path)

    def process_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        ディレクトリを処理

        Args:
            input_dir: 入力ディレクトリ
            output_dir: 出力ディレクトリ
            progress_callback: 進捗コールバック
            dry_run: ドライラン

        Returns:
            処理結果統計
        """
        return self.batch_processor.process_directory(
            input_dir, output_dir, progress_callback, dry_run
        )

    def get_file_list(self, input_dir: Path) -> list:
        """
        処理対象ファイル一覧を取得

        Args:
            input_dir: 入力ディレクトリ

        Returns:
            ファイルパスリスト
        """
        return self.batch_processor.get_file_list(input_dir)

    def estimate_processing_time(
        self, input_dir: Path, sample_size: int = 5
    ) -> Dict[str, Any]:
        """
        処理時間を推定

        Args:
            input_dir: 入力ディレクトリ
            sample_size: サンプルサイズ

        Returns:
            推定結果
        """
        return self.batch_processor.estimate_processing_time(input_dir, sample_size)

    def get_system_info(self) -> Dict[str, Any]:
        """
        システム情報を取得

        Returns:
            システム情報
        """
        return get_system_info()

    def check_requirements(self) -> Dict[str, bool]:
        """
        システム要件をチェック

        Returns:
            要件チェック結果
        """
        return check_requirements()

    def get_application_info(self) -> Dict[str, Any]:
        """
        アプリケーション情報を取得

        Returns:
            アプリケーション情報
        """
        return {
            "version": "2.0.0",
            "name": "Face Mosaic Tool",
            "description": "YuNet専用高精度顔モザイク処理ツール",
            "system_info": self.get_system_info(),
            "requirements_check": self.check_requirements(),
            "detector_info": self.face_detector.get_detector_info(),
            "processor_info": self.image_processor.get_processor_info(),
            "config": {
                "detection": {
                    "method": self.config.detection.method,
                    "confidence_threshold": self.config.detection.confidence_threshold,
                },
                "mosaic": {
                    "ratio": self.config.mosaic.ratio,
                    "pixelate": self.config.mosaic.pixelate,
                },
                "processing": {
                    "supported_formats": self.config.processing.supported_formats,
                    "max_image_size": self.config.processing.max_image_size,
                },
            },
        }

    def update_mosaic_ratio(self, ratio: float) -> None:
        """
        モザイク比率を更新

        Args:
            ratio: 新しいモザイク比率
        """
        if 0.01 <= ratio <= 1.0:
            self.config.mosaic.ratio = ratio
        else:
            raise ValueError("モザイク比率は0.01から1.0の間で指定してください")

    def update_confidence_threshold(self, threshold: float) -> None:
        """
        信頼度閾値を更新

        Args:
            threshold: 新しい信頼度閾値
        """
        if 0.1 <= threshold <= 1.0:
            self.config.detection.confidence_threshold = threshold
            # 検出器を再初期化
            self.face_detector = FaceDetector(self.config.detection, self.model_manager)
            self.image_processor.face_detector = self.face_detector
        else:
            raise ValueError("信頼度閾値は0.1から1.0の間で指定してください")

    def clear_model_cache(self) -> bool:
        """
        モデルキャッシュをクリア

        Returns:
            クリア成功の可否
        """
        return self.model_manager.clear_cache()

    def is_ready(self) -> bool:
        """
        アプリケーションが使用可能かチェック

        Returns:
            使用可能かどうか
        """
        try:
            requirements = self.check_requirements()
            detector_available = self.face_detector.is_available()

            return (
                requirements.get("opencv_version_ok", False)
                and requirements.get("system_supported", False)
                and detector_available
            )
        except Exception:
            return False
