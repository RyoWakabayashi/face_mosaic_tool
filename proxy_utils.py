"""
Proxyサーバー対応ユーティリティ
環境変数からProxy設定を検出し、適切にダウンロードを行う
"""

import os
import urllib.request
import urllib.parse
import ssl
from typing import Optional, Dict, Any
import logging


class ProxyManager:
    """Proxyサーバー管理クラス"""
    
    def __init__(self):
        self.proxy_config = self._detect_proxy_settings()
        self.logger = logging.getLogger(__name__)
        
    def _detect_proxy_settings(self) -> Dict[str, Any]:
        """環境変数からProxy設定を検出"""
        proxy_config = {
            'enabled': False,
            'http_proxy': None,
            'https_proxy': None,
            'no_proxy': None,
            'proxy_auth': None
        }
        
        # HTTP Proxy検出
        http_proxy = (
            os.environ.get('HTTP_PROXY') or 
            os.environ.get('http_proxy')
        )
        
        # HTTPS Proxy検出
        https_proxy = (
            os.environ.get('HTTPS_PROXY') or 
            os.environ.get('https_proxy')
        )
        
        # No Proxy検出
        no_proxy = (
            os.environ.get('NO_PROXY') or 
            os.environ.get('no_proxy')
        )
        
        if http_proxy or https_proxy:
            proxy_config['enabled'] = True
            proxy_config['http_proxy'] = http_proxy
            proxy_config['https_proxy'] = https_proxy
            proxy_config['no_proxy'] = no_proxy
            
            # Proxy認証情報の抽出
            proxy_url = https_proxy or http_proxy
            if proxy_url and '@' in proxy_url:
                # proxy_url形式: http://user:pass@proxy.example.com:8080
                parsed = urllib.parse.urlparse(proxy_url)
                if parsed.username and parsed.password:
                    proxy_config['proxy_auth'] = {
                        'username': parsed.username,
                        'password': parsed.password
                    }
        
        return proxy_config
    
    def is_proxy_enabled(self) -> bool:
        """Proxy設定が有効かどうか"""
        return self.proxy_config['enabled']
    
    def get_proxy_info(self) -> Dict[str, Any]:
        """Proxy設定情報を取得"""
        return self.proxy_config.copy()
    
    def create_proxy_handler(self) -> urllib.request.BaseHandler:
        """Proxy用のURLハンドラーを作成"""
        if not self.is_proxy_enabled():
            return urllib.request.HTTPHandler()
        
        proxy_dict = {}
        
        if self.proxy_config['http_proxy']:
            proxy_dict['http'] = self.proxy_config['http_proxy']
        
        if self.proxy_config['https_proxy']:
            proxy_dict['https'] = self.proxy_config['https_proxy']
        
        proxy_handler = urllib.request.ProxyHandler(proxy_dict)
        return proxy_handler
    
    def create_opener(self) -> urllib.request.OpenerDirector:
        """Proxy対応のOpenerを作成"""
        handlers = []
        
        # Proxy handler
        if self.is_proxy_enabled():
            handlers.append(self.create_proxy_handler())
            
            # Proxy認証が必要な場合
            if self.proxy_config.get('proxy_auth'):
                auth_info = self.proxy_config['proxy_auth']
                
                # Basic認証ハンドラー
                password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
                
                # Proxy URLから認証情報を設定
                proxy_url = (self.proxy_config['https_proxy'] or 
                           self.proxy_config['http_proxy'])
                parsed = urllib.parse.urlparse(proxy_url)
                
                password_mgr.add_password(
                    None, 
                    f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
                    auth_info['username'], 
                    auth_info['password']
                )
                
                proxy_auth_handler = urllib.request.ProxyBasicAuthHandler(password_mgr)
                handlers.append(proxy_auth_handler)
        
        # HTTPS handler（SSL証明書検証を緩和する場合）
        if self._should_ignore_ssl():
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            https_handler = urllib.request.HTTPSHandler(context=ssl_context)
            handlers.append(https_handler)
        
        # デフォルトハンドラー
        if not handlers:
            handlers = [urllib.request.HTTPHandler(), urllib.request.HTTPSHandler()]
        
        opener = urllib.request.build_opener(*handlers)
        
        # User-Agentを設定
        opener.addheaders = [
            ('User-Agent', 'Face-Mosaic-Tool/2.0 (Python urllib)')
        ]
        
        return opener
    
    def _should_ignore_ssl(self) -> bool:
        """SSL証明書検証を無視するかどうか"""
        # 企業環境でのSSL証明書問題に対応
        return (
            os.environ.get('PYTHONHTTPSVERIFY', '1') == '0' or
            os.environ.get('CURL_CA_BUNDLE') == '' or
            os.environ.get('REQUESTS_CA_BUNDLE') == ''
        )
    
    def download_file(self, url: str, output_path: str, 
                     chunk_size: int = 8192) -> bool:
        """Proxy経由でファイルをダウンロード"""
        try:
            opener = self.create_opener()
            
            self.logger.info(f"ダウンロード開始: {url}")
            if self.is_proxy_enabled():
                self.logger.info(f"Proxy経由でダウンロード: {self.proxy_config}")
            
            # ダウンロード実行
            with opener.open(url) as response:
                total_size = response.headers.get('Content-Length')
                if total_size:
                    total_size = int(total_size)
                    self.logger.info(f"ファイルサイズ: {total_size:,} bytes")
                
                downloaded = 0
                with open(output_path, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 進捗表示（10%刻み）
                        if total_size and downloaded % (total_size // 10 + 1) == 0:
                            progress = (downloaded / total_size) * 100
                            self.logger.info(f"ダウンロード進捗: {progress:.1f}%")
            
            self.logger.info(f"ダウンロード完了: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"ダウンロードエラー ({url}): {e}")
            return False
    
    def test_connection(self, test_url: str = "https://www.google.com") -> bool:
        """Proxy経由での接続テスト"""
        try:
            opener = self.create_opener()
            with opener.open(test_url, timeout=10) as response:
                return response.status == 200
        except Exception as e:
            self.logger.error(f"接続テストエラー: {e}")
            return False
    
    def print_proxy_info(self):
        """Proxy設定情報を表示"""
        if not self.is_proxy_enabled():
            print("Proxy設定: 無効")
            return
        
        print("=== Proxy設定情報 ===")
        print(f"HTTP Proxy: {self.proxy_config.get('http_proxy', 'なし')}")
        print(f"HTTPS Proxy: {self.proxy_config.get('https_proxy', 'なし')}")
        print(f"No Proxy: {self.proxy_config.get('no_proxy', 'なし')}")
        
        if self.proxy_config.get('proxy_auth'):
            print("Proxy認証: 有効")
        else:
            print("Proxy認証: 無効")


def get_proxy_manager() -> ProxyManager:
    """ProxyManagerのシングルトンインスタンスを取得"""
    if not hasattr(get_proxy_manager, '_instance'):
        get_proxy_manager._instance = ProxyManager()
    return get_proxy_manager._instance


def download_with_proxy(url: str, output_path: str) -> bool:
    """Proxy対応のダウンロード関数"""
    proxy_manager = get_proxy_manager()
    return proxy_manager.download_file(url, output_path)


def test_proxy_connection() -> bool:
    """Proxy接続テスト"""
    proxy_manager = get_proxy_manager()
    return proxy_manager.test_connection()


# 環境変数の例
def print_proxy_env_examples():
    """Proxy環境変数の設定例を表示"""
    print("""
=== Proxy環境変数設定例 ===

# 基本的なProxy設定
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# 認証付きProxy設定
export HTTP_PROXY=http://username:password@proxy.company.com:8080
export HTTPS_PROXY=http://username:password@proxy.company.com:8080

# 除外設定
export NO_PROXY=localhost,127.0.0.1,.company.com

# SSL証明書検証を無効化（企業環境）
export PYTHONHTTPSVERIFY=0

# Windows (コマンドプロンプト)
set HTTP_PROXY=http://proxy.company.com:8080
set HTTPS_PROXY=http://proxy.company.com:8080

# Windows (PowerShell)
$env:HTTP_PROXY="http://proxy.company.com:8080"
$env:HTTPS_PROXY="http://proxy.company.com:8080"
""")


if __name__ == "__main__":
    # テスト実行
    proxy_manager = ProxyManager()
    proxy_manager.print_proxy_info()
    
    if proxy_manager.is_proxy_enabled():
        print("\nProxy接続テスト中...")
        if proxy_manager.test_connection():
            print("✓ Proxy経由での接続に成功しました")
        else:
            print("✗ Proxy経由での接続に失敗しました")
    
    print_proxy_env_examples()
