@echo off 

echo Attente du démarrage de MySQL et Apache...
timeout /t 10 /nobreak

cd .\API\ 
flask run --host=0.0.0.0
pause