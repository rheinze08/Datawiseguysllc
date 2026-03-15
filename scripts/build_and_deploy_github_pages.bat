@echo off
setlocal

set "ROOT_DIR=%~dp0.."
set "TEMPLATE_FILE=%ROOT_DIR%\templates\datawise_home.html.j2"
set "OUTPUT_FILE=%ROOT_DIR%\index.html"

if not exist "%TEMPLATE_FILE%" (
  echo Template not found: %TEMPLATE_FILE%
  exit /b 1
)

python "%ROOT_DIR%\scripts\render_index.py"
if errorlevel 1 exit /b 1

echo Generated: %OUTPUT_FILE%

if /I "%~1"=="--deploy" (
  git -C "%ROOT_DIR%" remote get-url origin >nul 2>nul
  if errorlevel 1 (
    echo No git remote named 'origin' is configured. Skipping deploy.
    exit /b 2
  )

  for /f "delims=" %%b in ('git -C "%ROOT_DIR%" rev-parse --abbrev-ref HEAD') do set "CURRENT_BRANCH=%%b"
  git -C "%ROOT_DIR%" add index.html
  git -C "%ROOT_DIR%" diff --cached --quiet
  if errorlevel 1 git -C "%ROOT_DIR%" commit -m "Build GitHub Pages index.html"

  git -C "%ROOT_DIR%" push origin %CURRENT_BRANCH%:gh-pages
  if errorlevel 1 exit /b 1
  echo Deployed branch '%CURRENT_BRANCH%' to 'gh-pages'.
)
