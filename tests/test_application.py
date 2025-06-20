"""
アプリケーションクラスのテスト
"""

import pytest
import tempfile
import cv2
import numpy as np
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from face_mosaic import FaceMosaicApplication, AppConfig


class TestFaceMosaicApplication:
    """FaceMosaicApplicationのテストクラス"""
    
    @pytest.fixture
    def app(self):
        """テスト用アプリケーションインスタンス"""
        config = AppConfig()
        return FaceMosaicApplication(config)
    
    @pytest.fixture
    def test_image(self):
        """テスト用画像を作成"""
        # 200x200の白い画像を作成
        image = np.ones((200, 200, 3), dtype=np.uint8) * 255
        # 中央に赤い四角を描画（顔の代わり）
        cv2.rectangle(image, (75, 75), (125, 125), (0, 0, 255), -1)
        return image
    
    def test_initialization(self, app):
        """初期化テスト"""
        assert app is not None
        assert app.config is not None
        assert app.face_detector is not None
        assert app.image_processor is not None
        assert app.batch_processor is not None
    
    def test_system_info(self, app):
        """システム情報取得テスト"""
        info = app.get_system_info()
        assert isinstance(info, dict)
        assert "platform" in info
        assert "opencv_version" in info
        assert "yunet_supported" in info
    
    def test_requirements_check(self, app):
        """要件チェックテスト"""
        requirements = app.check_requirements()
        assert isinstance(requirements, dict)
        assert "opencv_version_ok" in requirements
        assert "system_supported" in requirements
    
    def test_application_info(self, app):
        """アプリケーション情報取得テスト"""
        info = app.get_application_info()
        assert isinstance(info, dict)
        assert "version" in info
        assert "name" in info
        assert "system_info" in info
        assert "config" in info
    
    def test_mosaic_ratio_update(self, app):
        """モザイク比率更新テスト"""
        # 正常な値
        app.update_mosaic_ratio(0.2)
        assert app.config.mosaic.ratio == 0.2
        
        # 異常な値
        with pytest.raises(ValueError):
            app.update_mosaic_ratio(1.5)
        
        with pytest.raises(ValueError):
            app.update_mosaic_ratio(0.005)
    
    def test_confidence_threshold_update(self, app):
        """信頼度閾値更新テスト"""
        # 正常な値
        app.update_confidence_threshold(0.8)
        assert app.config.detection.confidence_threshold == 0.8
        
        # 異常な値
        with pytest.raises(ValueError):
            app.update_confidence_threshold(1.5)
        
        with pytest.raises(ValueError):
            app.update_confidence_threshold(0.05)
    
    def test_single_image_processing(self, app, test_image):
        """単一画像処理テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # テスト画像を保存
            input_path = temp_path / "test_input.jpg"
            output_path = temp_path / "test_output.jpg"
            cv2.imwrite(str(input_path), test_image)
            
            # 処理実行
            result = app.process_single_image(input_path, output_path)
            
            # 結果検証
            assert isinstance(result, dict)
            assert "success" in result
            assert output_path.exists()
    
    def test_directory_processing_dry_run(self, app, test_image):
        """ディレクトリ処理（ドライラン）テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_dir = temp_path / "input"
            output_dir = temp_path / "output"
            input_dir.mkdir()
            
            # テスト画像を複数作成
            for i in range(3):
                cv2.imwrite(str(input_dir / f"test_{i}.jpg"), test_image)
            
            # ドライラン実行
            stats = app.process_directory(input_dir, output_dir, dry_run=True)
            
            # 結果検証
            assert isinstance(stats, dict)
            assert stats["total"] == 3
            assert stats["success"] == 0  # ドライランなので実際の処理はなし
            assert stats["failed"] == 0
    
    def test_file_list_retrieval(self, app, test_image):
        """ファイル一覧取得テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_dir = temp_path / "input"
            input_dir.mkdir()
            
            # テスト画像を作成
            cv2.imwrite(str(input_dir / "test1.jpg"), test_image)
            cv2.imwrite(str(input_dir / "test2.png"), test_image)
            
            # テキストファイルも作成（除外されるべき）
            (input_dir / "readme.txt").write_text("test")
            
            # ファイル一覧取得
            files = app.get_file_list(input_dir)
            
            # 結果検証
            assert len(files) == 2
            assert all(f.suffix.lower() in ['.jpg', '.png'] for f in files)
    
    def test_is_ready(self, app):
        """準備状態チェックテスト"""
        ready = app.is_ready()
        assert isinstance(ready, bool)
        # 実際の値は環境に依存するため、型のみチェック
