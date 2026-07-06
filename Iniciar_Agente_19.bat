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

:: Liga o Cérebro do Agente (API Local para a Extensao do Chrome)
echo O Cerebro do Agente 19 esta ATIVO!
echo.
echo Va para o seu Google Chrome e abra o SEI.
echo O robo flutuante ja estara la aguardando suas ordens.
echo.
echo ^(Pode minimizar esta janela, ela e o motor da Inteligencia Artificial^)
.venv\Scripts\python.exe -m app.dashboard

echo.
echo Sessao encerrada com seguranca.
pause
