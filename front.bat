@echo off 

echo Attente du démarrage de MySQL et Apache...
timeout /t 10 /nobreak

npm run dev
pause