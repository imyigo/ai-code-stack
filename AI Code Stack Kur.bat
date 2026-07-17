@echo off
setlocal
rem Double-click launcher for Windows. Thin wrapper: delegates to scripts\install.ps1 / scripts\global-install.ps1.
set "ROOT=%~dp0"
cd /d "%ROOT%"

echo === AI Code Stack kurulumu ===
echo Depo: %ROOT%
echo.

echo --- 1/2: Repo-local kurulum (manifests + adapters) ---
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\install.ps1"
if errorlevel 1 (
  echo.
  echo HATA: repo-local kurulum basarisiz oldu. Yukaridaki ciktiyi kontrol et.
  pause
  exit /b 1
)

echo.
echo --- 2/2: Global kurulum (Codex / Claude Code / Cursor) ---
echo Bu adim sadece bu bilgisayarda kurulu olan platformlara, sadece bu arac tarafindan
echo uretilmis dosyalari yazar. Elle yazdigin mevcut dosyalarin uzerine asla yazmaz.
echo.
set /p REPLY="Global kurulumu simdi uygula? [e/H] "
if /i "%REPLY:~0,1%"=="e" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\global-install.ps1" -Apply
) else (
  echo Global kurulum atlandi. Istediginde: scripts\global-install.ps1 -Apply
)

echo.
echo === Bitti ===
pause
