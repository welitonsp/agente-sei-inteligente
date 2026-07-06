@echo off
title Agente 19 - Inicializador
color 0B
echo ========================================================
echo         AGENTE 19 - INTELIGENCIA ARTIFICIAL (19 CRPM)
echo ========================================================
echo.
echo Iniciando o sistema de forma segura... aguarde.
echo.

:: Vai para o diretorio onde o arquivo .bat esta localizado
cd /d "%~dp0"

:: Verifica se o ambiente virtual existe
if not exist ".venv\Scripts\python.exe" (
    color 0C
    echo ERRO CRITICO: O ambiente virtual motor de IA nao foi encontrado!
    echo Certifique-se de que o sistema foi instalado corretamente.
    pause
    exit /b
)

:: Abre a versao Desktop (Navegador Seguro)
echo Abrindo o Navegador Seguro...
.venv\Scripts\python.exe -m app.desktop

echo.
echo Sessao encerrada com seguranca.
pause
