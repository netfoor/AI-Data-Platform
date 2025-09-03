@echo off
chcp 65001 >nul

echo 🚀 AI Data Platform - Render Deployment
echo ========================================

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not installed. Please install Git first.
    pause
    exit /b 1
)

REM Check if we're in a git repository
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo ❌ Not in a git repository. Please run this from your project root.
    pause
    exit /b 1
)

echo 📋 Checking required files...

REM Check required files
set "missing_files="
if not exist "render.yaml" set "missing_files=1"
if not exist "requirements.txt" set "missing_files=1"
if not exist "Dockerfile.api" set "missing_files=1"
if not exist "Dockerfile.ui" set "missing_files=1"
if not exist "Dockerfile.n8n" set "missing_files=1"
if not exist "ui\app.py" set "missing_files=1"
if not exist "ai_data_platform\" set "missing_files=1"

if defined missing_files (
    echo ❌ Missing required files:
    if not exist "render.yaml" echo    - render.yaml
    if not exist "requirements.txt" echo    - requirements.txt
    if not exist "Dockerfile.api" echo    - Dockerfile.api
    if not exist "Dockerfile.ui" echo    - Dockerfile.ui
    if not exist "Dockerfile.n8n" echo    - Dockerfile.n8n
    if not exist "ui\app.py" echo    - ui\app.py
    if not exist "ai_data_platform\" echo    - ai_data_platform\
    echo.
    echo Please ensure all required files are present before deployment.
    pause
    exit /b 1
)

echo ✅ All required files present

REM Check git status
echo 📊 Checking git status...
git status --porcelain >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  You have uncommitted changes:
    git status --short
    echo.
    set /p "commit_changes=Do you want to commit these changes before deployment? (y/n): "
    if /i "%commit_changes%"=="y" (
        set /p "commit_message=Enter commit message: "
        if "%commit_message%"=="" (
            for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set "commit_message=Deploy to Render - %%a %%b %%c"
        )
        git add .
        git commit -m "%commit_message%"
        echo ✅ Changes committed
    )
)

REM Check current branch
for /f "tokens=*" %%i in ('git branch --show-current') do set "current_branch=%%i"
if not "%current_branch%"=="main" if not "%current_branch%"=="master" (
    echo ⚠️  You're currently on branch: %current_branch%
    set /p "switch_branch=Do you want to switch to main/master branch? (y/n): "
    if /i "%switch_branch%"=="y" (
        git show-ref --verify --quiet refs/heads/main >nul 2>&1
        if not errorlevel 1 (
            git checkout main
        ) else (
            git show-ref --verify --quiet refs/heads/master >nul 2>&1
            if not errorlevel 1 (
                git checkout master
            ) else (
                echo ❌ Neither main nor master branch found
                pause
                exit /b 1
            )
        )
        for /f "tokens=*" %%i in ('git branch --show-current') do set "current_branch=%%i"
        echo ✅ Switched to %current_branch% branch
    )
)

REM Push to remote
echo 📤 Pushing to remote repository...
git push
if errorlevel 1 (
    echo ❌ Failed to push to remote repository
    pause
    exit /b 1
)
echo ✅ Code pushed to remote

REM Display deployment information
echo.
echo 🎉 Deployment Preparation Complete!
echo ==================================
echo.
echo 📋 Next Steps:
echo 1. Go to https://render.com
echo 2. Sign up/Login to your account
echo 3. Click 'New +' → 'Blueprint'
echo 4. Connect your GitHub account
echo 5. Select this repository
echo 6. Click 'Apply' to deploy
echo.
echo 🔗 Your services will be available at:
echo    - API: https://ai-data-platform-api.onrender.com
echo    - Web UI: https://ai-data-platform-ui.onrender.com
echo    - n8n: https://ai-data-platform-n8n.onrender.com
echo.
echo 🔐 n8n Access:
echo    - Username: admin
echo    - Password: admin123
echo.
echo 📚 For detailed instructions, see: docs\deployment-guide.md
echo 📋 For deployment checklist, see: DEPLOYMENT_CHECKLIST.md
echo.
echo 🚀 Happy deploying!
echo.
pause
