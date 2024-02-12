@echo off

rem Set the path to your virtual environment directory
set VENV_PATH=%~dp0venv
call %VENV_PATH%\Scripts\activate

rem Set the path to your Django project directory
set DJANGO_PROJECT_PATH=%~dp0

rem Run Django server in a separate CMD window
start "Django Server" cmd /k "python %DJANGO_PROJECT_PATH%\manage.py runserver"

rem Wait for Django server to start (adjust the delay as needed)
timeout /t 5

rem Run Celery in a separate CMD window
start "Celery Worker" cmd /k "cd %DJANGO_PROJECT_PATH% && celery -A myapp worker --loglevel=info"

rem Wait for Celery to start (adjust the delay as needed)
timeout /t 5

rem Run Ngrok in a separate CMD window
start "Ngrok" cmd /k "C:\ngrok.exe http 8000"



@REM @echo off

@REM rem Set the path to your virtual environment directory
@REM set VENV_PATH=C:\Users\ilham\Desktop\uty_creative_hub_django\venv
@REM call %VENV_PATH%\Scripts\activate

@REM rem Set the path to your Django project directory
@REM set DJANGO_PROJECT_PATH=C:\Users\ilham\Desktop\uty_creative_hub_django

@REM rem Run Django server in a separate CMD window
@REM start "Django Server" cmd /k "python %DJANGO_PROJECT_PATH%\manage.py runserver"

@REM rem Wait for Django server to start (adjust the delay as needed)
@REM timeout /t 5

@REM rem Run Celery in a separate CMD window
@REM start "Celery Worker" cmd /k "cd %DJANGO_PROJECT_PATH% && celery -A myapp worker --loglevel=info"

@REM rem Wait for Celery to start (adjust the delay as needed)
@REM timeout /t 5

@REM rem Run Ngrok in a separate CMD window
@REM start "Ngrok" cmd /k "C:\ngrok.exe http 8000"
