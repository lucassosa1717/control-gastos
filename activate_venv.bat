@echo off
echo Activando entorno virtual...
call .venv\Scripts\activate

echo Entorno virtual activado. Ahora puedes ejecutar comandos de Django.
echo Ejemplos:
echo   python manage.py runserver
echo   python manage.py makemigrations
echo   python manage.py migrate
echo   python manage.py shell

cmd /k