#!/usr/bin/env python3
"""
高精度顔モザイク処理CLI版
OpenCV YuNetによる高精度検出
"""

import argparse
import sys
import time
from pathlib import Path
from tqdm import tqdm
from face_detector import AdvancedImageProcessor, get_system_info


def main():
    parser = argparse.ArgumentParser(
        description='指定ディレクトリの画像ファイルに高精度顔モザイク処理を適用',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python cli_tool.py -i ./input_images -o ./output_images
  python cli_tool.py -i /path/to/input -o /path/to/output -r 0.05
  python cli_tool.py --input ./photos --output ./processed --info
  
検出手法:
  yunet     - OpenCV YuNet（検証により唯一十分な精度を持つ手法）
        """
    )
    
    parser.add_argument('-i', '--input', 
                       help='入力ディレクトリパス')
    parser.add_argument('-o', '--output',
                       help='出力ディレクトリパス')
    parser.add_argument('-r', '--ratio', type=float, default=0.1,
                       help='モザイクの粗さ (0.01-1.0, デフォルト: 0.1)')
    parser.add_argument('-m', '--method', 
                       choices=['yunet'],
                       default='yunet',
                       help='顔検出手法 (YuNetのみ利用可能)')
    parser.add_argument('--info', action='store_true',
                       help='システム情報を表示')
    parser.add_argument('--dry-run', action='store_true',
                       help='実際の処理は行わず、対象ファイルのみ表示')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='詳細ログを表示')
    
    args = parser.parse_args()
    
    # システム情報表示
    if args.info:
        print("=== システム情報 ===")
        info = get_system_info()
        for key, value in info.items():
            print(f"{key}: {value}")
        print()
        
        # 利用可能な検出手法
        print("=== 検出手法 ===")
        if info['yunet_supported']:
            print("✓ OpenCV YuNet (唯一の十分な精度を持つ手法)")
        else:
            print("✗ OpenCV YuNet (OpenCV 4.5.4以上が必要)")
            print("  エラー: 高精度な顔検出手法が利用できません")
        
        print("\n注意: YuNetのみが実用的な精度を提供します。")
        print("他の手法は検証により精度不十分と判明したため削除されました。")
        print()
    
    # --info以外の場合は入力・出力ディレクトリが必須
    if not args.info:
        if not args.input or not args.output:
            print("エラー: 入力ディレクトリ(-i)と出力ディレクトリ(-o)は必須です")
            print("システム情報のみを表示する場合は --info オプションを使用してください")
            sys.exit(1)
    
    # --infoのみの場合は処理を終了
    if args.info:
        sys.exit(0)
    
    # 引数検証
    if not (0.01 <= args.ratio <= 1.0):
        print("エラー: モザイク比率は0.01から1.0の間で指定してください")
        sys.exit(1)
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"エラー: 入力ディレクトリが存在しません: {args.input}")
        sys.exit(1)
    
    if not input_path.is_dir():
        print(f"エラー: 入力パスがディレクトリではありません: {args.input}")
        sys.exit(1)
    
    # 処理開始
    print(f"入力ディレクトリ: {input_path.absolute()}")
    print(f"出力ディレクトリ: {output_path.absolute()}")
    print(f"モザイク比率: {args.ratio}")
    print(f"検出手法: {args.method}")
    print()
    
    processor = AdvancedImageProcessor(detection_method=args.method)
    
    # 対象ファイル取得
    image_files = processor.get_image_files(str(input_path))
    
    if not image_files:
        print("処理対象の画像ファイルが見つかりません")
        print("対応形式: .jpg, .jpeg, .png, .bmp, .tiff, .tif")
        sys.exit(1)
    
    print(f"処理対象ファイル数: {len(image_files)}")
    
    if args.dry_run:
        print("\n=== 処理対象ファイル一覧 ===")
        for file_path in image_files:
            rel_path = Path(file_path).relative_to(input_path)
            print(f"  {rel_path}")
        print("\n※ --dry-run モードのため実際の処理は行いません")
        return
    
    # 確認プロンプト
    response = input("\n処理を開始しますか？ (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("処理をキャンセルしました")
        return
    
    start_time = time.time()
    
    try:
        stats = processor.process_directory(
            str(input_path), 
            str(output_path), 
            args.ratio
        )
        
        # 結果表示
        elapsed_time = time.time() - start_time
        print(f"\n=== 処理結果 ===")
        print(f"成功: {stats['success']} ファイル")
        print(f"失敗: {stats['failed']} ファイル")
        print(f"検出された顔: {stats['faces_detected']} 個")
        print(f"処理時間: {elapsed_time:.2f} 秒")
        
        if stats['success'] > 0:
            avg_time = elapsed_time / stats['success']
            print(f"平均処理時間: {avg_time:.2f} 秒/ファイル")
        
        if stats['failed'] > 0:
            print(f"\n{stats['failed']} 個のファイルで処理に失敗しました")
            if not args.verbose:
                print("詳細は --verbose オプションで確認できます")
            sys.exit(1)
        else:
            print("\n全ての処理が正常に完了しました")
            
    except KeyboardInterrupt:
        print("\n\n処理が中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n処理中にエラーが発生しました: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
