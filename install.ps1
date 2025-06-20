# 高精度顔モザイク処理ツール - Windows PowerShell インストールスクリプト
# PowerShell 5.1以上で動作

param(
    [switch]$Force,
    [switch]$SkipVersionCheck
)

Write-Host "高精度顔モザイク処理ツール - Windows PowerShell インストールスクリプト" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# PowerShellバージョンチェック
Write-Host ""
Write-Host "PowerShell環境を確認中..." -ForegroundColor Yellow
$psVersion = $PSVersionTable.PSVersion
Write-Host "PowerShell バージョン: $($psVersion.Major).$($psVersion.Minor)" -ForegroundColor Green

if ($psVersion.Major -lt 5) {
    Write-Host "エラー: PowerShell 5.0以上が必要です" -ForegroundColor Red
    Write-Host "Windows PowerShell 5.1 または PowerShell 7+ をインストールしてください" -ForegroundColor Red
    exit 1
}

# Python環境確認
Write-Host ""
Write-Host "Python環境を確認中..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "検出されたPython: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "エラー: Pythonがインストールされていません" -ForegroundColor Red
    Write-Host "Python 3.9-3.12をインストールしてください（推奨: 3.11）" -ForegroundColor Red
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Blue
    
    if (-not $Force) {
        Read-Host "Enterキーを押して終了してください"
        exit 1
    }
}

# Pythonバージョン詳細チェック
if (-not $SkipVersionCheck) {
    Write-Host ""
    Write-Host "Pythonバージョンを詳細確認中..." -ForegroundColor Yellow
    
    try {
        $versionInfo = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Version check failed"
        }
        
        Write-Host "Python バージョン: $versionInfo" -ForegroundColor Green
        
        # MediaPipe対応バージョンチェック
        $supportedVersions = @("3.9", "3.10", "3.11", "3.12")
        $isMediaPipeCompatible = $versionInfo -in $supportedVersions
        
        if ($isMediaPipeCompatible) {
            Write-Host "? MediaPipe対応バージョンです（最高精度で動作）" -ForegroundColor Green
            $global:MediaPipeCompatible = $true
        } else {
            Write-Host "? MediaPipe非対応バージョンです" -ForegroundColor Yellow
            Write-Host "  MediaPipeには Python 3.9-3.12 が必要です" -ForegroundColor Yellow
            Write-Host "  現在のバージョンでは Dlib と OpenCV のみ利用可能です" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "推奨アクション:" -ForegroundColor Cyan
            Write-Host "  Python 3.11 をインストールしてください" -ForegroundColor Cyan
            Write-Host "  https://www.python.org/downloads/" -ForegroundColor Blue
            Write-Host ""
            
            if (-not $Force) {
                $continue = Read-Host "このまま続行しますか？ (y/N)"
                if ($continue -notmatch "^[Yy]") {
                    Write-Host "インストールを中止しました" -ForegroundColor Yellow
                    exit 0
                }
            }
            $global:MediaPipeCompatible = $false
        }
    } catch {
        Write-Host "? Pythonバージョンの確認に失敗しました" -ForegroundColor Yellow
        $global:MediaPipeCompatible = $false
    }
} else {
    Write-Host "バージョンチェックをスキップしました" -ForegroundColor Yellow
    $global:MediaPipeCompatible = $true
}

# Visual C++ Build Tools 確認
Write-Host ""
Write-Host "Visual C++ Build Tools を確認中..." -ForegroundColor Yellow
Write-Host "注意: Dlibのインストールには Visual C++ Build Tools が必要です" -ForegroundColor Cyan
Write-Host "https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Blue

# 基本依存関係インストール
Write-Host ""
Write-Host "基本依存関係をインストール中..." -ForegroundColor Yellow
$basicPackages = @("opencv-python", "numpy", "Pillow", "tqdm")

foreach ($package in $basicPackages) {
    Write-Host "  インストール中: $package" -ForegroundColor Gray
    try {
        python -m pip install $package --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ? $package" -ForegroundColor Green
        } else {
            Write-Host "  ? $package (エラー)" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ? $package (例外)" -ForegroundColor Red
    }
}

# MediaPipeインストール
Write-Host ""
if ($global:MediaPipeCompatible) {
    Write-Host "MediaPipe をインストール中..." -ForegroundColor Yellow
    try {
        python -m pip install mediapipe --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "? MediaPipe のインストールが完了しました" -ForegroundColor Green
        } else {
            Write-Host "? MediaPipe のインストールに失敗しました" -ForegroundColor Red
        }
    } catch {
        Write-Host "? MediaPipe のインストール中に例外が発生しました" -ForegroundColor Red
    }
} else {
    Write-Host "? MediaPipe をスキップします（Python バージョン非対応）" -ForegroundColor Yellow
}

# CMakeインストール
Write-Host ""
Write-Host "CMake をインストール中..." -ForegroundColor Yellow
try {
    python -m pip install cmake --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "? CMake のインストールが完了しました" -ForegroundColor Green
    } else {
        Write-Host "? CMake のインストールに失敗しました" -ForegroundColor Yellow
    }
} catch {
    Write-Host "? CMake のインストール中に例外が発生しました" -ForegroundColor Yellow
}

# Dlibインストール
Write-Host ""
Write-Host "Dlib をインストール中（時間がかかる場合があります）..." -ForegroundColor Yellow
try {
    python -m pip install dlib --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "? Dlib のインストールが完了しました" -ForegroundColor Green
    } else {
        Write-Host "? Dlib のインストールに失敗しました" -ForegroundColor Yellow
        Write-Host "  Visual C++ Build Tools が必要です" -ForegroundColor Yellow
        Write-Host "  代替案: pip install dlib-binary" -ForegroundColor Cyan
    }
} catch {
    Write-Host "? Dlib のインストール中に例外が発生しました" -ForegroundColor Yellow
}

# インストール確認テスト
Write-Host ""
Write-Host "インストール確認テストを実行中..." -ForegroundColor Yellow

$testScript = @"
import sys
try:
    from face_detector import get_system_info
    info = get_system_info()
    print('=== インストール状況 ===')
    for key, value in info.items():
        print(f'{key}: {value}')
    
    print('\n=== 利用可能な検出手法 ===')
    if info['mediapipe_available']:
        print('? MediaPipe Face Detection')
    else:
        print('? MediaPipe Face Detection')
        
    if info['dlib_available']:
        print('? Dlib Face Detection')
    else:
        print('? Dlib Face Detection')
        
    print('? OpenCV Haar Cascade')
    
except Exception as e:
    print(f'エラー: {e}')
    sys.exit(1)
"@

try {
    $testResult = python -c $testScript 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $testResult -ForegroundColor White
        
        Write-Host ""
        Write-Host "インストール完了！" -ForegroundColor Green -BackgroundColor Black
        Write-Host ""
        Write-Host "使用方法:" -ForegroundColor Cyan
        Write-Host "  CLI版: python cli_tool.py -i 入力フォルダ -o 出力フォルダ" -ForegroundColor White
        Write-Host "  GUI版: python gui_tool.py" -ForegroundColor White
        Write-Host "  テスト実行: python test_tool.py" -ForegroundColor White
        Write-Host "  診断実行: python test_dlib_version.py" -ForegroundColor White
        Write-Host "  Proxy情報: python cli_tool.py --proxy-info" -ForegroundColor White
        Write-Host "  Proxy接続テスト: python cli_tool.py --test-proxy" -ForegroundColor White
        Write-Host ""
        
        if ($global:MediaPipeCompatible) {
            Write-Host "? 最高精度: MediaPipe が利用可能です" -ForegroundColor Green
            Write-Host "  推奨: python cli_tool.py -i input -o output -m mediapipe" -ForegroundColor Cyan
        } else {
            Write-Host "? MediaPipe が利用できません（Python 3.9-3.12 が必要）" -ForegroundColor Yellow
            Write-Host "  利用可能: Dlib と OpenCV による検出" -ForegroundColor White
        }
        
        Write-Host ""
        Write-Host "Proxy環境での使用:" -ForegroundColor Cyan
        Write-Host "  `$env:HTTP_PROXY='http://proxy.company.com:8080'" -ForegroundColor Gray
        Write-Host "  `$env:HTTPS_PROXY='http://proxy.company.com:8080'" -ForegroundColor Gray
        
    } else {
        Write-Host "インストール確認テストでエラーが発生しました:" -ForegroundColor Red
        Write-Host $testResult -ForegroundColor Red
        Write-Host ""
        Write-Host "詳細診断を実行してください: python test_dlib_version.py" -ForegroundColor Cyan
        exit 1
    }
} catch {
    Write-Host "インストール確認テスト中に例外が発生しました:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "詳細診断を実行してください: python test_dlib_version.py" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "PowerShell インストールスクリプトが正常に完了しました！" -ForegroundColor Green -BackgroundColor Black
