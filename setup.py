"""
リファクタリング後のセットアップスクリプト
"""

from setuptools import setup, find_packages
from pathlib import Path

# README読み込み
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# 依存関係
install_requires = [
    "opencv-python>=4.5.4",
    "numpy>=1.21.0",
    "Pillow>=8.0.0",
    "tqdm>=4.60.0",
]

# 開発用依存関係
dev_requires = [
    "black>=22.0.0",
    "flake8>=4.0.0",
    "pytest>=7.0.0",
    "pytest-cov>=3.0.0",
]

setup(
    name="face-mosaic-tool",
    version="2.0.0",
    author="Face Mosaic Tool Team",
    author_email="",
    description="YuNet専用高精度顔モザイク処理ツール",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/face-mosaic-tool",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
    },
    entry_points={
        "console_scripts": [
            "face-mosaic-cli=face_mosaic.cli.main:main",
            "face-mosaic-gui=face_mosaic.gui.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "face_mosaic": ["*.md", "*.txt"],
    },
    zip_safe=False,
)
