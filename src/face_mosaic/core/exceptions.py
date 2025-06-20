"""
カスタム例外クラス
アプリケーション固有のエラーハンドリング
"""


class FaceMosaicError(Exception):
    """基底例外クラス"""

    pass


class ModelError(FaceMosaicError):
    """モデル関連エラー"""

    pass


class ModelDownloadError(ModelError):
    """モデルダウンロードエラー"""

    pass


class ModelLoadError(ModelError):
    """モデル読み込みエラー"""

    pass


class DetectionError(FaceMosaicError):
    """顔検出エラー"""

    pass


class ImageProcessingError(FaceMosaicError):
    """画像処理エラー"""

    pass


class InvalidImageError(ImageProcessingError):
    """無効な画像エラー"""

    pass


class UnsupportedFormatError(ImageProcessingError):
    """サポートされていない形式エラー"""

    pass


class ConfigurationError(FaceMosaicError):
    """設定エラー"""

    pass


class ValidationError(FaceMosaicError):
    """バリデーションエラー"""

    pass
