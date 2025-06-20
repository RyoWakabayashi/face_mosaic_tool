#!/usr/bin/env python3
"""
CLI版エントリーポイント
リファクタリング後のCLI版を起動
"""

import sys
from pathlib import Path

# パッケージパスを追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from face_mosaic.cli.main import main

if __name__ == "__main__":
    main()
