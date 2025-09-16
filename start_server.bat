@echo off
echo Activando entorno virtual...
call .venv\Scripts\activate

echo Iniciando servidor de desarrollo Django...
python manage.py runserver

pause