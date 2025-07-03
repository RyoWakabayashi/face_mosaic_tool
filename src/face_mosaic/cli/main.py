"""
CLI版メインモジュール
コマンドライン インターフェース
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Optional

from ..core.application import FaceMosaicApplication
from ..config.settings import AppConfig
from ..core.exceptions import FaceMosaicError
from ..core.object_detector import ObjectDetector
from ..utils.system_info import print_system_info


class CLIApplication:
    """CLI版アプリケーション"""

    def __init__(self):
        """初期化"""
        self.app: Optional[FaceMosaicApplication] = None

    def create_parser(self) -> argparse.ArgumentParser:
        """引数パーサーを作成"""
        parser = argparse.ArgumentParser(
            description="YuNet専用高精度顔モザイク処理ツール",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用例:
  %(prog)s -i input_dir -o output_dir
  %(prog)s -i input_dir -o output_dir -r 0.05
  %(prog)s -i input_dir -o output_dir --dry-run
  %(prog)s --info
            """,
        )

        # 基本オプション
        parser.add_argument(
            "-i", "--input", type=Path, help="入力ディレクトリまたはファイルパス"
        )
        parser.add_argument(
            "-o", "--output", type=Path, help="出力ディレクトリまたはファイルパス"
        )

        # 処理オプション
        parser.add_argument(
            "-r",
            "--ratio",
            type=float,
            default=0.1,
            help="モザイク比率 (0.01-1.0, デフォルト: 0.1)",
        )
        parser.add_argument(
            "-c",
            "--confidence",
            type=float,
            default=0.6,
            help="顔検出信頼度閾値 (0.1-1.0, デフォルト: 0.6)",
        )
        parser.add_argument(
            "--blur", action="store_true", help="ピクセル化の代わりにブラーを使用"
        )

        # 物体検出オプション
        parser.add_argument(
            "--object-detect",
            action="store_true",
            help="PyTorchによる物体検出を有効化（FasterRCNN, COCOラベル）",
        )
        parser.add_argument(
            "--object-labels",
            type=str,
            default="",
            help="モザイク対象の物体ラベル（カンマ区切り, 例: person,car,dog）",
        )

        # 実行オプション
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="実際の処理は行わず、対象ファイルのみ表示",
        )
        parser.add_argument(
            "--no-confirm", action="store_true", help="確認プロンプトをスキップ"
        )
        parser.add_argument("--estimate", action="store_true", help="処理時間を推定")

        # 情報表示オプション
        parser.add_argument("--info", action="store_true", help="システム情報を表示")
        parser.add_argument(
            "--verbose", "-v", action="store_true", help="詳細ログを表示"
        )
        parser.add_argument("--version", action="version", version="%(prog)s 2.0.0")

        return parser

    def validate_arguments(self, args: argparse.Namespace) -> bool:
        """引数を検証"""
        # --info, --version は単独実行可能
        if args.info:
            return True

        # その他の場合は入力・出力が必須
        if not args.input or not args.output:
            print("エラー: 入力パス(-i)と出力パス(-o)は必須です")
            print(
                "システム情報のみを表示する場合は --info オプションを使用してください"
            )
            return False

        # 入力パスの存在確認
        if not args.input.exists():
            print(f"エラー: 入力パスが見つかりません: {args.input}")
            return False

        # モザイク比率の検証
        if not (0.01 <= args.ratio <= 1.0):
            print("エラー: モザイク比率は0.01から1.0の間で指定してください")
            return False

        # 信頼度閾値の検証
        if not (0.1 <= args.confidence <= 1.0):
            print("エラー: 信頼度閾値は0.1から1.0の間で指定してください")
            return False

        return True

    def initialize_application(self, args: argparse.Namespace) -> None:
        """アプリケーションを初期化"""
        try:
            # 設定を作成
            config = AppConfig()
            config.mosaic.ratio = args.ratio
            config.detection.confidence_threshold = args.confidence
            config.mosaic.pixelate = not args.blur

            # 物体検出オプション
            object_detector = None
            object_labels = []
            use_object_detection = getattr(args, "object_detect", False)
            if use_object_detection:
                object_detector = ObjectDetector()
                if args.object_labels:
                    object_labels = [
                        s.strip() for s in args.object_labels.split(",") if s.strip()
                    ]

            # アプリケーション初期化
            self.app = FaceMosaicApplication(config)
            # ImageProcessorへ物体検出器を渡す
            self.app.image_processor.object_detector = object_detector
            self.app.image_processor.object_labels = object_labels
            self.app.image_processor.use_object_detection = use_object_detection

            if not self.app.is_ready():
                print("エラー: アプリケーションの初期化に失敗しました")
                print("システム要件を確認してください（--info オプション）")
                sys.exit(1)

        except Exception as e:
            print(f"エラー: アプリケーションの初期化に失敗しました: {e}")
            sys.exit(1)

    def show_info(self) -> None:
        """システム情報を表示"""
        print_system_info()

        if self.app:
            app_info = self.app.get_application_info()
            print(f"\n=== アプリケーション情報 ===")
            print(f"バージョン: {app_info['version']}")
            print(f"名前: {app_info['name']}")
            print(f"説明: {app_info['description']}")

    def estimate_processing_time(self, args: argparse.Namespace) -> None:
        """処理時間を推定"""
        if not args.input.is_dir():
            print("処理時間推定はディレクトリに対してのみ実行できます")
            return

        print("処理時間を推定中...")
        estimation = self.app.estimate_processing_time(args.input)

        print(f"\n=== 処理時間推定 ===")
        print(f"対象ファイル数: {estimation['total_files']}")
        print(f"推定処理時間: {estimation['estimated_time']:.1f} 秒")

        if estimation["estimated_time"] > 60:
            minutes = estimation["estimated_time"] / 60
            print(f"              {minutes:.1f} 分")

    def confirm_processing(self, args: argparse.Namespace) -> bool:
        """処理実行の確認"""
        if args.no_confirm:
            return True

        print(f"\n入力: {args.input}")
        print(f"出力: {args.output}")
        print(f"モザイク比率: {args.ratio}")
        print(f"信頼度閾値: {args.confidence}")
        print(f"モザイク方式: {'ブラー' if args.blur else 'ピクセル化'}")

        response = input("\n処理を開始しますか？ (y/N): ").strip().lower()
        return response in ["y", "yes"]

    def process_files(self, args: argparse.Namespace) -> None:
        """ファイル処理を実行"""
        start_time = time.time()

        try:
            if args.input.is_file():
                # 単一ファイル処理
                result = self.app.process_single_image(args.input, args.output)
                self.show_single_result(result, start_time)
            else:
                # ディレクトリ処理
                stats = self.app.process_directory(
                    args.input, args.output, dry_run=args.dry_run
                )
                self.show_batch_results(stats, start_time)

        except FaceMosaicError as e:
            print(f"処理エラー: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n\n処理が中断されました")
            sys.exit(1)
        except Exception as e:
            print(f"予期しないエラー: {e}")
            if args.verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)

    def show_single_result(self, result: dict, start_time: float) -> None:
        """単一ファイル処理結果を表示"""
        elapsed_time = time.time() - start_time

        print(f"\n=== 処理結果 ===")
        if result["success"]:
            print(f"✓ 処理成功")
            print(f"検出された顔: {result['faces_detected']} 個")
            print(f"出力ファイル: {result['output_path']}")
        else:
            print(f"✗ 処理失敗: {result['error']}")

        print(f"処理時間: {elapsed_time:.2f} 秒")

    def show_batch_results(self, stats: dict, start_time: float) -> None:
        """バッチ処理結果を表示"""
        elapsed_time = time.time() - start_time

        print(f"\n=== 処理結果 ===")
        print(f"対象ファイル数: {stats['total']}")
        print(f"成功: {stats['success']} ファイル")
        print(f"失敗: {stats['failed']} ファイル")
        print(f"検出された顔: {stats['faces_detected']} 個")
        print(f"処理時間: {elapsed_time:.2f} 秒")

        if stats["success"] > 0:
            avg_time = elapsed_time / stats["success"]
            print(f"平均処理時間: {avg_time:.2f} 秒/ファイル")

        if stats["failed"] > 0:
            print(f"\n{stats['failed']} 個のファイルで処理に失敗しました")
            sys.exit(1)
        else:
            print("\n全ての処理が正常に完了しました")

    def run(self, args: list = None) -> None:
        """メイン実行関数"""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        # 引数検証
        if not self.validate_arguments(parsed_args):
            sys.exit(1)

        # システム情報表示のみの場合
        if parsed_args.info:
            self.initialize_application(parsed_args)
            self.show_info()
            return

        # アプリケーション初期化
        self.initialize_application(parsed_args)

        # 処理時間推定
        if parsed_args.estimate:
            self.estimate_processing_time(parsed_args)
            return

        # ドライラン
        if parsed_args.dry_run:
            print("=== ドライラン ===")
            self.process_files(parsed_args)
            return

        # 確認プロンプト
        if not self.confirm_processing(parsed_args):
            print("処理をキャンセルしました")
            return

        # 処理実行
        self.process_files(parsed_args)


def main():
    """CLI版メイン関数"""
    cli_app = CLIApplication()
    cli_app.run()


if __name__ == "__main__":
    main()
