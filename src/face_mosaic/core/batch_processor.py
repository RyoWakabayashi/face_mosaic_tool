"""
バッチ処理クラス
複数画像の一括処理を担当
"""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from tqdm import tqdm

from ..config.settings import ProcessingConfig
from ..core.image_processor import ImageProcessor
from ..utils.file_utils import get_image_files


class BatchProcessor:
    """バッチ処理クラス"""

    def __init__(
        self, image_processor: ImageProcessor, processing_config: ProcessingConfig
    ):
        """
        初期化

        Args:
            image_processor: 画像処理インスタンス
            processing_config: 処理設定
        """
        self.image_processor = image_processor
        self.processing_config = processing_config

    def process_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        ディレクトリ内の画像を一括処理

        Args:
            input_dir: 入力ディレクトリ
            output_dir: 出力ディレクトリ
            progress_callback: 進捗コールバック関数
            dry_run: ドライラン（実際の処理は行わない）

        Returns:
            処理結果統計
        """
        # 画像ファイルを取得
        image_files = get_image_files(
            input_dir, self.processing_config.supported_formats
        )

        if not image_files:
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "faces_detected": 0,
                "processing_time": 0.0,
                "files": [],
            }

        print(f"対象ファイル数: {len(image_files)}")

        # ドライランの場合はファイル一覧のみ表示
        if dry_run:
            print("\n=== 処理対象ファイル一覧 ===")
            for img_file in image_files:
                rel_path = img_file.relative_to(input_dir)
                print(f"  {rel_path}")

            return {
                "total": len(image_files),
                "success": 0,
                "failed": 0,
                "faces_detected": 0,
                "processing_time": 0.0,
                "files": [str(f.relative_to(input_dir)) for f in image_files],
            }

        # 統計情報初期化
        stats = {
            "total": len(image_files),
            "success": 0,
            "failed": 0,
            "faces_detected": 0,
            "processing_time": 0.0,
            "files": [],
        }

        # 処理開始
        start_time = time.time()

        # 進捗バー付きで処理
        with tqdm(image_files, desc="画像処理中", unit="files") as pbar:
            for i, img_file in enumerate(pbar):
                try:
                    # 出力パスを決定（相対パス構造を保持）
                    rel_path = img_file.relative_to(input_dir)
                    output_file = output_dir / rel_path

                    # 画像処理実行
                    result = self.image_processor.process_image_file(
                        img_file, output_file
                    )

                    # 統計更新
                    if result["success"]:
                        stats["success"] += 1
                        stats["faces_detected"] += result["faces_detected"]
                    else:
                        stats["failed"] += 1

                    stats["files"].append(result)

                    # 進捗バー更新
                    pbar.set_postfix(
                        {
                            "Success": stats["success"],
                            "Failed": stats["failed"],
                            "Faces": stats["faces_detected"],
                        }
                    )

                    # 進捗コールバック呼び出し
                    if progress_callback:
                        progress_callback(i + 1, len(image_files))

                except Exception as e:
                    stats["failed"] += 1
                    stats["files"].append(
                        {
                            "success": False,
                            "error": str(e),
                            "input_path": str(img_file),
                            "output_path": str(
                                output_dir / img_file.relative_to(input_dir)
                            ),
                        }
                    )

                    print(f"エラー ({img_file.name}): {e}")

        # 処理時間計算
        stats["processing_time"] = time.time() - start_time

        return stats

    def get_file_list(self, input_dir: Path) -> List[Path]:
        """
        処理対象ファイル一覧を取得

        Args:
            input_dir: 入力ディレクトリ

        Returns:
            ファイルパスリスト
        """
        return get_image_files(input_dir, self.processing_config.supported_formats)

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
        image_files = self.get_file_list(input_dir)

        if not image_files:
            return {"total_files": 0, "estimated_time": 0.0, "sample_size": 0}

        # サンプルファイルを選択
        sample_files = image_files[: min(sample_size, len(image_files))]

        # サンプル処理時間を測定
        total_sample_time = 0.0
        successful_samples = 0

        for img_file in sample_files:
            try:
                start_time = time.time()

                # 画像読み込みと顔検出のみ実行（保存はしない）
                import cv2

                image = cv2.imread(str(img_file))
                if image is not None:
                    self.image_processor.face_detector.detect_faces(image)

                sample_time = time.time() - start_time
                total_sample_time += sample_time
                successful_samples += 1

            except Exception:
                continue

        if successful_samples == 0:
            return {
                "total_files": len(image_files),
                "estimated_time": 0.0,
                "sample_size": 0,
            }

        # 平均処理時間を計算
        avg_time_per_file = total_sample_time / successful_samples
        estimated_total_time = avg_time_per_file * len(image_files)

        return {
            "total_files": len(image_files),
            "estimated_time": estimated_total_time,
            "sample_size": successful_samples,
            "avg_time_per_file": avg_time_per_file,
        }
