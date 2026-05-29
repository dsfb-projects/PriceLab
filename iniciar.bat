@echo off
echo ============================================
echo   PriceLab — Iniciando servidor
echo ============================================
echo.

cd /d "%~dp0"

echo [1/2] Subindo Django na porta 8000...
start "PriceLab Backend" cmd /k "cd backend && python manage.py runserver"

timeout /t 3 /nobreak >nul

echo [2/2] Subindo Cloudflare Tunnel...
echo.
echo  Acesse o link "trycloudflare.com" que aparecer no console do tunnel.
echo  Compartilhe esse link com quem precisar acessar o sistema.
echo.
start "PriceLab Tunnel" cmd /k "cloudflared tunnel --url http://localhost:8000"

echo.
echo Pronto! Dois terminais abertos:
echo  - Backend Django (porta 8000)
echo  - Cloudflare Tunnel (link publico)
echo.
pause
