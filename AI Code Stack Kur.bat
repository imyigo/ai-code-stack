@echo off
setlocal
rem Double-click launcher for Windows. Thin wrapper: delegates to scripts\install.ps1 / scripts\global-install.ps1 / scripts\replace-skills.ps1.
set "ROOT=%~dp0"
cd /d "%ROOT%"

echo === AI Code Stack kurulumu ===
echo Depo: %ROOT%
echo.

echo --- 1/3: Repo-local kurulum (manifests + adapters, eksik submodule fetch) ---
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\install.ps1"
if errorlevel 1 (
  echo.
  echo HATA: repo-local kurulum basarisiz oldu. Yukaridaki ciktiyi kontrol et.
  pause
  exit /b 1
)

echo.
echo --- 2/3: Global config (Codex AGENTS.md/MCP, Claude Code agentlari, Cursor kurali) ---
echo Bu adim sadece bu bilgisayarda kurulu olan platformlara, sadece bu arac tarafindan
echo uretilmis dosyalari yazar. Elle yazdigin mevcut dosyalarin uzerine asla yazmaz.
echo.
set /p REPLY="Global config'i simdi uygula? [e/H] "
if /i "%REPLY:~0,1%"=="e" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\global-install.ps1" -Apply
) else (
  echo Atlandi. Istediginde: scripts\global-install.ps1 -Apply
)

echo.
echo --- 3/3: Skilleri degistir (~\.claude\skills, ~\.codex\skills) ---
echo DIKKAT: mevcut skills klasoru SILINMEZ, kenara tasinir (skills.backup-^<tarih^>),
echo ardindan bu repodaki skill setiyle TAMAMEN degistirilir. Once plan:
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\replace-skills.ps1"
echo.
set /p REPLY="Skilleri yukaridaki plana gore degistir? [e/H] "
if /i "%REPLY:~0,1%"=="e" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\replace-skills.ps1" -Apply
) else (
  echo Atlandi. Istediginde: scripts\replace-skills.ps1 -Apply
)

echo.
echo === Bitti ===
pause
