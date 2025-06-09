@echo off
chcp 65001 > nul
SET PYTHON=python.exe
SET VENV_NAME=venv
SET REQUIREMENTS=requirements.txt
SET MAIN_SCRIPT=Parser.py
SET TEST_URL=ya.ru

echo [1/5] Проверка Python...
%PYTHON% --version || (
    echo Ошибка: Python не установлен
    pause
    exit /b 1
)

echo [2/5] Создание виртуального окружения...
%PYTHON% -m venv %VENV_NAME% || (
    echo Ошибка при создании venv
    pause
    exit /b 1
)

echo [3/5] Проверка интернет-подключения...
ping -n 1 %TEST_URL% > nul
if %errorlevel% neq 0 (
    echo ОШИБКА: Нет интернет-подключения к %TEST_URL%
    echo Пожалуйста, проверьте ваше соединение
    pause
    exit /b 1
)


echo [4/5] Активация venv и установка библиотек...
call %VENV_NAME%\Scripts\activate
%PYTHON% -m pip install --upgrade pip
if exist %REQUIREMENTS% (
    pip install -r %REQUIREMENTS%
) else (
    echo requirements.txt не найден, устанавливаем selenium
    pip install selenium
)

echo [5/5] Запуск...
cls||clear
%PYTHON% %MAIN_SCRIPT% || (
    echo Ошибка при запуске скрипта
    pause
    exit /b 1
)

pause