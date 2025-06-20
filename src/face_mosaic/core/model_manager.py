"""
モデル管理クラス
YuNetモデルのダウンロードと管理を担当
"""

import os
from pathlib import Path
from typing import Optional

from ..config.settings import ModelConfig
from ..core.exceptions import ModelDownloadError, ModelLoadError
from ..utils.file_utils import download_file


class ModelManager:
    """YuNetモデル管理クラス"""

    def __init__(self, config: ModelConfig):
        """
        初期化

        Args:
            config: モデル設定
        """
        self.config = config
        self.model_path = config.model_cache_dir / config.model_filename

    def ensure_model_available(self) -> Path:
        """
        モデルファイルの存在を確認し、必要に応じてダウンロード

        Returns:
            モデルファイルパス

        Raises:
            ModelDownloadError: ダウンロード失敗時
            ModelLoadError: モデル読み込み失敗時
        """
        if self.model_path.exists():
            if self._validate_model():
                return self.model_path
            else:
                print("既存のモデルファイルが無効です。再ダウンロードします。")
                self.model_path.unlink()

        return self._download_model()

    def _download_model(self) -> Path:
        """
        モデルをダウンロード

        Returns:
            ダウンロードしたモデルファイルパス

        Raises:
            ModelDownloadError: ダウンロード失敗時
        """
        try:
            # ディレクトリ作成
            self.config.model_cache_dir.mkdir(parents=True, exist_ok=True)

            # ダウンロード実行
            download_file(self.config.yunet_model_url, str(self.model_path))

            # ダウンロード後の検証
            if not self._validate_model():
                raise ModelDownloadError("ダウンロードしたモデルファイルが無効です")

            return self.model_path

        except Exception as e:
            if self.model_path.exists():
                self.model_path.unlink()
            raise ModelDownloadError(f"モデルのダウンロードに失敗しました: {e}")

    def _validate_model(self) -> bool:
        """
        モデルファイルを検証

        Returns:
            モデルファイルが有効かどうか
        """
        if not self.model_path.exists():
            return False

        # ファイルサイズチェック（最小サイズ）
        file_size = self.model_path.stat().st_size
        if file_size < 100000:  # 100KB未満は無効とみなす
            return False

        # 拡張子チェック
        if self.model_path.suffix.lower() != ".onnx":
            return False

        return True

    def get_model_info(self) -> dict:
        """
        モデル情報を取得

        Returns:
            モデル情報辞書
        """
        info = {
            "model_path": str(self.model_path),
            "exists": self.model_path.exists(),
            "size_mb": 0.0,
            "valid": False,
        }

        if self.model_path.exists():
            info["size_mb"] = self.model_path.stat().st_size / (1024 * 1024)
            info["valid"] = self._validate_model()

        return info

    def clear_cache(self) -> bool:
        """
        モデルキャッシュをクリア

        Returns:
            クリア成功の可否
        """
        try:
            if self.model_path.exists():
                self.model_path.unlink()
                print(f"モデルキャッシュをクリアしました: {self.model_path}")
                return True
            return False
        except Exception as e:
            print(f"キャッシュクリアに失敗しました: {e}")
            return False
