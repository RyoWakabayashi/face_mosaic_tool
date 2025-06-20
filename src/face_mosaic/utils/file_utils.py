"""
ファイル操作ユーティリティ
"""

import os
import urllib.request
from pathlib import Path
from typing import List, Optional, Tuple
from ..core.exceptions import ModelDownloadError, UnsupportedFormatError


def download_file(url: str, filepath: str, chunk_size: int = 8192) -> bool:
    """
    ファイルをダウンロード

    Args:
        url: ダウンロードURL
        filepath: 保存先パス
        chunk_size: チャンクサイズ

    Returns:
        ダウンロード成功の可否

    Raises:
        ModelDownloadError: ダウンロード失敗時
    """
    try:
        print(f"ダウンロード中: {url}")

        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(filepath, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r進捗: {progress:.1f}%", end="", flush=True)

        print(f"\nダウンロード完了: {filepath}")
        return True

    except Exception as e:
        raise ModelDownloadError(f"ダウンロードに失敗しました: {e}")


def get_image_files(
    directory: Path, supported_formats: Tuple[str, ...], recursive: bool = True
) -> List[Path]:
    """
    ディレクトリから画像ファイルを取得

    Args:
        directory: 検索対象ディレクトリ
        supported_formats: サポートする画像形式
        recursive: 再帰検索の有効/無効

    Returns:
        画像ファイルパスのリスト

    Raises:
        FileNotFoundError: ディレクトリが存在しない場合
    """
    if not directory.exists():
        raise FileNotFoundError(f"ディレクトリが見つかりません: {directory}")

    image_files = []

    # 検索パターンを作成
    search_func = directory.rglob if recursive else directory.glob

    for ext in supported_formats:
        # 小文字と大文字の両方に対応
        image_files.extend(search_func(f"*{ext}"))
        image_files.extend(search_func(f"*{ext.upper()}"))

    # 重複を除去してソート
    unique_files = list(set(image_files))
    unique_files.sort()

    return unique_files


def validate_image_format(filepath: Path, supported_formats: Tuple[str, ...]) -> bool:
    """
    画像形式を検証

    Args:
        filepath: ファイルパス
        supported_formats: サポートする形式

    Returns:
        サポートされている形式かどうか

    Raises:
        UnsupportedFormatError: サポートされていない形式の場合
    """
    suffix = filepath.suffix.lower()

    if suffix not in supported_formats:
        raise UnsupportedFormatError(
            f"サポートされていない形式です: {suffix}\n"
            f"サポート形式: {', '.join(supported_formats)}"
        )

    return True


def ensure_directory(directory: Path) -> None:
    """
    ディレクトリの存在を確認し、必要に応じて作成

    Args:
        directory: ディレクトリパス
    """
    directory.mkdir(parents=True, exist_ok=True)


def get_file_size_mb(filepath: Path) -> float:
    """
    ファイルサイズをMB単位で取得

    Args:
        filepath: ファイルパス

    Returns:
        ファイルサイズ（MB）
    """
    if not filepath.exists():
        return 0.0

    size_bytes = filepath.stat().st_size
    return size_bytes / (1024 * 1024)


def create_backup_path(filepath: Path) -> Path:
    """
    バックアップファイルパスを作成

    Args:
        filepath: 元のファイルパス

    Returns:
        バックアップファイルパス
    """
    counter = 1
    backup_path = filepath.with_suffix(f".backup{filepath.suffix}")

    while backup_path.exists():
        backup_path = filepath.with_suffix(f".backup{counter}{filepath.suffix}")
        counter += 1

    return backup_path
