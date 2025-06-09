@echo off
chcp 65001 > nul

echo Удаление зависимостей и созданных файлов.

if exist "venv" (
    echo Найдена папка venv, удаление...
    rmdir /s /q "venv"
    if errorlevel 1 (
        echo Ошибка при удалении папки venv
    ) else (
        echo Папка venv успешно удалена
    )
) else (
    echo Папка venv не найдена
)

if exist "images" (
    echo Найдена папка images, удаление...
    rmdir /s /q "images"
    if errorlevel 1 (
        echo Ошибка при удалении папки images
    ) else (
        echo Папка images успешно удалена
    )
) else (
    echo Папка images не найдена
)

echo Готово
pause