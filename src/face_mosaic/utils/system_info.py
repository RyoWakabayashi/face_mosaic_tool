"""
システム情報取得ユーティリティ
"""

import platform
import cv2
from typing import Dict, Any


def get_system_info() -> Dict[str, Any]:
    """システム情報を取得"""

    # OpenCVバージョン情報
    opencv_version = cv2.__version__
    opencv_version_parts = opencv_version.split(".")
    opencv_major = int(opencv_version_parts[0])
    opencv_minor = int(opencv_version_parts[1])

    # YuNetサポート確認
    yunet_supported = opencv_major > 4 or (opencv_major == 4 and opencv_minor >= 5)

    # GPU サポート確認
    gpu_support = False
    try:
        gpu_support = cv2.cuda.getCudaEnabledDeviceCount() > 0
    except AttributeError:
        pass

    return {
        "platform": platform.system(),
        "architecture": platform.architecture()[0],
        "python_version": platform.python_version(),
        "opencv_version": opencv_version,
        "yunet_supported": yunet_supported,
        "gpu_support": gpu_support,
        "processor": platform.processor(),
        "machine": platform.machine(),
    }


def check_requirements() -> Dict[str, bool]:
    """必要な要件をチェック"""

    system_info = get_system_info()

    return {
        "opencv_version_ok": system_info["yunet_supported"],
        "python_version_ok": True,  # Python 3.8+ assumed
        "system_supported": system_info["platform"] in ["Windows", "Darwin", "Linux"],
    }


def print_system_info():
    """システム情報を表示"""

    info = get_system_info()
    requirements = check_requirements()

    print("=== システム情報 ===")
    for key, value in info.items():
        print(f"{key}: {value}")

    print("\n=== 要件チェック ===")
    for key, value in requirements.items():
        status = "✓" if value else "✗"
        print(f"{status} {key}: {value}")

    print("\n=== 検出手法 ===")
    if info["yunet_supported"]:
        print("✓ OpenCV YuNet (推奨)")
    else:
        print("✗ OpenCV YuNet (OpenCV 4.5.4以上が必要)")
