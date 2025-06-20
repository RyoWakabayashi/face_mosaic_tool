#!/usr/bin/env python3
"""
GUI版エントリーポイント
リファクタリング後のGUI版を起動
"""

import sys
from pathlib import Path

# パッケージパスを追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from face_mosaic.gui.main import main

if __name__ == "__main__":
    main()
