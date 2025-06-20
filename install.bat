@echo off
chcp 932 >nul
echo �����x�烂�U�C�N�����c�[�� - Windows �C���X�g�[���X�N���v�g
echo ========================================================

echo.
echo Python�����m�F��...
python --version >nul 2>&1
if errorlevel 1 (
    echo �G���[: Python���C���X�g�[������Ă��܂���
    echo Python 3.9-3.12���C���X�g�[�����Ă��������i����: 3.11�j
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Python�o�[�W�������m�F��...
for /f "tokens=2" %%i in ('python -c "import sys; print(sys.version_info.major, sys.version_info.minor)" 2^>nul') do set PYTHON_MINOR=%%i
for /f "tokens=1" %%i in ('python -c "import sys; print(sys.version_info.major, sys.version_info.minor)" 2^>nul') do set PYTHON_MAJOR=%%i

if "%PYTHON_MAJOR%"=="3" (
    if "%PYTHON_MINOR%"=="9" set MEDIAPIPE_COMPATIBLE=true
    if "%PYTHON_MINOR%"=="10" set MEDIAPIPE_COMPATIBLE=true
    if "%PYTHON_MINOR%"=="11" set MEDIAPIPE_COMPATIBLE=true
    if "%PYTHON_MINOR%"=="12" set MEDIAPIPE_COMPATIBLE=true
)

if "%MEDIAPIPE_COMPATIBLE%"=="true" (
    echo [OK] MediaPipe�Ή��o�[�W�����ł��i�ō����x�œ���j
) else (
    echo [�x��] MediaPipe��Ή��o�[�W�����ł�
    echo   MediaPipe�ɂ� Python 3.9-3.12 ���K�v�ł�
    echo   ���݂̃o�[�W�����ł� Dlib �� OpenCV �̂ݗ��p�\�ł�
    echo.
    echo �����A�N�V����:
    echo   Python 3.11 ���C���X�g�[�����Ă�������
    echo   https://www.python.org/downloads/
    echo.
    set /p CONTINUE="���̂܂ܑ��s���܂����H (y/N): "
    if /i not "%CONTINUE%"=="y" exit /b 1
)

echo.
echo Visual C++ Build Tools ���m�F��...
echo ����: Dlib�̃C���X�g�[���ɂ� Visual C++ Build Tools ���K�v�ł�
echo https://visualstudio.microsoft.com/visual-cpp-build-tools/

echo.
echo ��{�ˑ��֌W���C���X�g�[����...
pip install opencv-python numpy Pillow tqdm
if errorlevel 1 (
    echo �G���[: ��{�ˑ��֌W�̃C���X�g�[���Ɏ��s���܂���
    pause
    exit /b 1
)

echo.
if "%MEDIAPIPE_COMPATIBLE%"=="true" (
    echo MediaPipe ���C���X�g�[����...
    pip install mediapipe
    if errorlevel 1 (
        echo �x��: MediaPipe �̃C���X�g�[���Ɏ��s���܂���
    ) else (
        echo [OK] MediaPipe �̃C���X�g�[�����������܂���
    )
) else (
    echo [�x��] MediaPipe ���X�L�b�v���܂��iPython �o�[�W������Ή��j
)

echo.
echo CMake ���C���X�g�[����...
pip install cmake
if errorlevel 1 (
    echo �x��: CMake �̃C���X�g�[���Ɏ��s���܂���
) else (
    echo CMake �̃C���X�g�[�����������܂���
)

echo.
echo Dlib ���C���X�g�[�����i���Ԃ�������ꍇ������܂��j...
pip install dlib
if errorlevel 1 (
    echo �x��: Dlib �̃C���X�g�[���Ɏ��s���܂���
    echo Visual C++ Build Tools ���K�v�ł�
    echo ��ֈ�: pip install dlib-binary
) else (
    echo Dlib �̃C���X�g�[�����������܂���
)

echo.
echo �C���X�g�[���m�F�e�X�g�����s��...
python -c "
import sys
try:
    from face_detector import get_system_info
    info = get_system_info()
    print('=== �C���X�g�[���� ===')
    for key, value in info.items():
        print(f'{key}: {value}')
    
    print('\n=== ���p�\�Ȍ��o��@ ===')
    if info['mediapipe_available']:
        print('[OK] MediaPipe Face Detection')
    else:
        print('[NG] MediaPipe Face Detection')
        
    if info['dlib_available']:
        print('[OK] Dlib Face Detection')
    else:
        print('[NG] Dlib Face Detection')
        
    print('[OK] OpenCV Haar Cascade')
    
except Exception as e:
    print(f'�G���[: {e}')
    exit(1)
"

if errorlevel 1 (
    echo.
    echo �C���X�g�[���ɖ�肪����܂��B�G���[���b�Z�[�W���m�F���Ă��������B
    pause
    exit /b 1
)

echo.
echo �C���X�g�[�������I
echo.
echo �g�p���@:
echo   CLI��: python cli_tool.py -i ���̓t�H���_ -o �o�̓t�H���_
echo   GUI��: python gui_tool.py
echo   �e�X�g���s: python test_tool.py
echo   �f�f���s: python test_dlib_version.py
echo.
if "%MEDIAPIPE_COMPATIBLE%"=="true" (
    echo [OK] �ō����x: MediaPipe �����p�\�ł�
    echo   ����: python cli_tool.py -i input -o output -m mediapipe
) else (
    echo [�x��] MediaPipe �����p�ł��܂���iPython 3.9-3.12 ���K�v�j
    echo   ���p�\: Dlib �� OpenCV �ɂ�錟�o
)
echo.
pause
