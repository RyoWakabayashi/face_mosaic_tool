@echo off
chcp 932 >nul
echo �����x�烂�U�C�N�����c�[�� - PowerShell �C���X�g�[���N���X�N���v�g
echo ==============================================================

echo.
echo PowerShell �X�N���v�g�����s���܂�...
echo ����: ���s�|���V�[�̕ύX���K�v�ȏꍇ������܂�

echo.
echo ���s���@��I�����Ă�������:
echo [1] PowerShell �Œ��ڎ��s�i�����j
echo [2] ���s�|���V�[���ꎞ�I�ɕύX���Ď��s
echo [3] �R�}���h�v�����v�g�ł��g�p
echo.

set /p choice="�I�����Ă������� (1-3): "

if "%choice%"=="1" (
    echo.
    echo PowerShell ���N�����Ă��܂�...
    echo �ȉ��̃R�}���h�����s���Ă�������:
    echo.
    echo   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    echo   .\install.ps1
    echo.
    powershell.exe
    goto :end
)

if "%choice%"=="2" (
    echo.
    echo ���s�|���V�[���ꎞ�I�ɕύX���ăX�N���v�g�����s���܂�...
    powershell.exe -ExecutionPolicy Bypass -File "install.ps1"
    goto :end
)

if "%choice%"=="3" (
    echo.
    echo �R�}���h�v�����v�g�ŃC���X�g�[���X�N���v�g�����s���܂�...
    call install.bat
    goto :end
)

echo.
echo �����ȑI���ł��B�R�}���h�v�����v�g�ł����s���܂�...
call install.bat

:end
echo.
pause
