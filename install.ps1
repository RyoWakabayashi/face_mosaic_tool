# �����x�烂�U�C�N�����c�[�� - Windows PowerShell �C���X�g�[���X�N���v�g
# PowerShell 5.1�ȏ�œ���

param(
    [switch]$Force,
    [switch]$SkipVersionCheck
)

Write-Host "�����x�烂�U�C�N�����c�[�� - Windows PowerShell �C���X�g�[���X�N���v�g" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# PowerShell�o�[�W�����`�F�b�N
Write-Host ""
Write-Host "PowerShell�����m�F��..." -ForegroundColor Yellow
$psVersion = $PSVersionTable.PSVersion
Write-Host "PowerShell �o�[�W����: $($psVersion.Major).$($psVersion.Minor)" -ForegroundColor Green

if ($psVersion.Major -lt 5) {
    Write-Host "�G���[: PowerShell 5.0�ȏオ�K�v�ł�" -ForegroundColor Red
    Write-Host "Windows PowerShell 5.1 �܂��� PowerShell 7+ ���C���X�g�[�����Ă�������" -ForegroundColor Red
    exit 1
}

# Python���m�F
Write-Host ""
Write-Host "Python�����m�F��..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "���o���ꂽPython: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "�G���[: Python���C���X�g�[������Ă��܂���" -ForegroundColor Red
    Write-Host "Python 3.9-3.12���C���X�g�[�����Ă��������i����: 3.11�j" -ForegroundColor Red
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Blue
    
    if (-not $Force) {
        Read-Host "Enter�L�[�������ďI�����Ă�������"
        exit 1
    }
}

# Python�o�[�W�����ڍ׃`�F�b�N
if (-not $SkipVersionCheck) {
    Write-Host ""
    Write-Host "Python�o�[�W�������ڍ׊m�F��..." -ForegroundColor Yellow
    
    try {
        $versionInfo = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Version check failed"
        }
        
        Write-Host "Python �o�[�W����: $versionInfo" -ForegroundColor Green
        
        # MediaPipe�Ή��o�[�W�����`�F�b�N
        $supportedVersions = @("3.9", "3.10", "3.11", "3.12")
        $isMediaPipeCompatible = $versionInfo -in $supportedVersions
        
        if ($isMediaPipeCompatible) {
            Write-Host "? MediaPipe�Ή��o�[�W�����ł��i�ō����x�œ���j" -ForegroundColor Green
            $global:MediaPipeCompatible = $true
        } else {
            Write-Host "? MediaPipe��Ή��o�[�W�����ł�" -ForegroundColor Yellow
            Write-Host "  MediaPipe�ɂ� Python 3.9-3.12 ���K�v�ł�" -ForegroundColor Yellow
            Write-Host "  ���݂̃o�[�W�����ł� Dlib �� OpenCV �̂ݗ��p�\�ł�" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "�����A�N�V����:" -ForegroundColor Cyan
            Write-Host "  Python 3.11 ���C���X�g�[�����Ă�������" -ForegroundColor Cyan
            Write-Host "  https://www.python.org/downloads/" -ForegroundColor Blue
            Write-Host ""
            
            if (-not $Force) {
                $continue = Read-Host "���̂܂ܑ��s���܂����H (y/N)"
                if ($continue -notmatch "^[Yy]") {
                    Write-Host "�C���X�g�[���𒆎~���܂���" -ForegroundColor Yellow
                    exit 0
                }
            }
            $global:MediaPipeCompatible = $false
        }
    } catch {
        Write-Host "? Python�o�[�W�����̊m�F�Ɏ��s���܂���" -ForegroundColor Yellow
        $global:MediaPipeCompatible = $false
    }
} else {
    Write-Host "�o�[�W�����`�F�b�N���X�L�b�v���܂���" -ForegroundColor Yellow
    $global:MediaPipeCompatible = $true
}

# Visual C++ Build Tools �m�F
Write-Host ""
Write-Host "Visual C++ Build Tools ���m�F��..." -ForegroundColor Yellow
Write-Host "����: Dlib�̃C���X�g�[���ɂ� Visual C++ Build Tools ���K�v�ł�" -ForegroundColor Cyan
Write-Host "https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Blue

# ��{�ˑ��֌W�C���X�g�[��
Write-Host ""
Write-Host "��{�ˑ��֌W���C���X�g�[����..." -ForegroundColor Yellow
$basicPackages = @("opencv-python", "numpy", "Pillow", "tqdm")

foreach ($package in $basicPackages) {
    Write-Host "  �C���X�g�[����: $package" -ForegroundColor Gray
    try {
        python -m pip install $package --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ? $package" -ForegroundColor Green
        } else {
            Write-Host "  ? $package (�G���[)" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ? $package (��O)" -ForegroundColor Red
    }
}

# MediaPipe�C���X�g�[��
Write-Host ""
if ($global:MediaPipeCompatible) {
    Write-Host "MediaPipe ���C���X�g�[����..." -ForegroundColor Yellow
    try {
        python -m pip install mediapipe --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "? MediaPipe �̃C���X�g�[�����������܂���" -ForegroundColor Green
        } else {
            Write-Host "? MediaPipe �̃C���X�g�[���Ɏ��s���܂���" -ForegroundColor Red
        }
    } catch {
        Write-Host "? MediaPipe �̃C���X�g�[�����ɗ�O���������܂���" -ForegroundColor Red
    }
} else {
    Write-Host "? MediaPipe ���X�L�b�v���܂��iPython �o�[�W������Ή��j" -ForegroundColor Yellow
}

# CMake�C���X�g�[��
Write-Host ""
Write-Host "CMake ���C���X�g�[����..." -ForegroundColor Yellow
try {
    python -m pip install cmake --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "? CMake �̃C���X�g�[�����������܂���" -ForegroundColor Green
    } else {
        Write-Host "? CMake �̃C���X�g�[���Ɏ��s���܂���" -ForegroundColor Yellow
    }
} catch {
    Write-Host "? CMake �̃C���X�g�[�����ɗ�O���������܂���" -ForegroundColor Yellow
}

# Dlib�C���X�g�[��
Write-Host ""
Write-Host "Dlib ���C���X�g�[�����i���Ԃ�������ꍇ������܂��j..." -ForegroundColor Yellow
try {
    python -m pip install dlib --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "? Dlib �̃C���X�g�[�����������܂���" -ForegroundColor Green
    } else {
        Write-Host "? Dlib �̃C���X�g�[���Ɏ��s���܂���" -ForegroundColor Yellow
        Write-Host "  Visual C++ Build Tools ���K�v�ł�" -ForegroundColor Yellow
        Write-Host "  ��ֈ�: pip install dlib-binary" -ForegroundColor Cyan
    }
} catch {
    Write-Host "? Dlib �̃C���X�g�[�����ɗ�O���������܂���" -ForegroundColor Yellow
}

# �C���X�g�[���m�F�e�X�g
Write-Host ""
Write-Host "�C���X�g�[���m�F�e�X�g�����s��..." -ForegroundColor Yellow

$testScript = @"
import sys
try:
    from face_detector import get_system_info
    info = get_system_info()
    print('=== �C���X�g�[���� ===')
    for key, value in info.items():
        print(f'{key}: {value}')
    
    print('\n=== ���p�\�Ȍ��o��@ ===')
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
    print(f'�G���[: {e}')
    sys.exit(1)
"@

try {
    $testResult = python -c $testScript 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $testResult -ForegroundColor White
        
        Write-Host ""
        Write-Host "�C���X�g�[�������I" -ForegroundColor Green -BackgroundColor Black
        Write-Host ""
        Write-Host "�g�p���@:" -ForegroundColor Cyan
        Write-Host "  CLI��: python cli_tool.py -i ���̓t�H���_ -o �o�̓t�H���_" -ForegroundColor White
        Write-Host "  GUI��: python gui_tool.py" -ForegroundColor White
        Write-Host "  �e�X�g���s: python test_tool.py" -ForegroundColor White
        Write-Host "  �f�f���s: python test_dlib_version.py" -ForegroundColor White
        Write-Host "  Proxy���: python cli_tool.py --proxy-info" -ForegroundColor White
        Write-Host "  Proxy�ڑ��e�X�g: python cli_tool.py --test-proxy" -ForegroundColor White
        Write-Host ""
        
        if ($global:MediaPipeCompatible) {
            Write-Host "? �ō����x: MediaPipe �����p�\�ł�" -ForegroundColor Green
            Write-Host "  ����: python cli_tool.py -i input -o output -m mediapipe" -ForegroundColor Cyan
        } else {
            Write-Host "? MediaPipe �����p�ł��܂���iPython 3.9-3.12 ���K�v�j" -ForegroundColor Yellow
            Write-Host "  ���p�\: Dlib �� OpenCV �ɂ�錟�o" -ForegroundColor White
        }
        
        Write-Host ""
        Write-Host "Proxy���ł̎g�p:" -ForegroundColor Cyan
        Write-Host "  `$env:HTTP_PROXY='http://proxy.company.com:8080'" -ForegroundColor Gray
        Write-Host "  `$env:HTTPS_PROXY='http://proxy.company.com:8080'" -ForegroundColor Gray
        
    } else {
        Write-Host "�C���X�g�[���m�F�e�X�g�ŃG���[���������܂���:" -ForegroundColor Red
        Write-Host $testResult -ForegroundColor Red
        Write-Host ""
        Write-Host "�ڍאf�f�����s���Ă�������: python test_dlib_version.py" -ForegroundColor Cyan
        exit 1
    }
} catch {
    Write-Host "�C���X�g�[���m�F�e�X�g���ɗ�O���������܂���:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "�ڍאf�f�����s���Ă�������: python test_dlib_version.py" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "PowerShell �C���X�g�[���X�N���v�g������Ɋ������܂����I" -ForegroundColor Green -BackgroundColor Black
