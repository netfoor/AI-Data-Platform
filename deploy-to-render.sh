#!/bin/bash

# 🚀 AI Data Platform - Render Deployment Script
# This script helps automate the deployment process to Render

echo "🚀 AI Data Platform - Render Deployment"
echo "========================================"

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository. Please run this from your project root."
    exit 1
fi

# Check if we have the required files
echo "📋 Checking required files..."

required_files=(
    "render.yaml"
    "requirements.txt"
    "Dockerfile.api"
    "Dockerfile.ui"
    "Dockerfile.n8n"
    "ui/app.py"
    "ai_data_platform/"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -e "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Missing required files:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    echo "Please ensure all required files are present before deployment."
    exit 1
fi

echo "✅ All required files present"

# Check git status
echo "📊 Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes:"
    git status --short
    echo ""
    read -p "Do you want to commit these changes before deployment? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter commit message: " commit_message
        if [ -z "$commit_message" ]; then
            commit_message="Deploy to Render - $(date)"
        fi
        git add .
        git commit -m "$commit_message"
        echo "✅ Changes committed"
    fi
fi

# Check if we're on main/master branch
current_branch=$(git branch --show-current)
if [[ "$current_branch" != "main" && "$current_branch" != "master" ]]; then
    echo "⚠️  You're currently on branch: $current_branch"
    read -p "Do you want to switch to main/master branch? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if git show-ref --verify --quiet refs/heads/main; then
            git checkout main
        elif git show-ref --verify --quiet refs/heads/master; then
            git checkout master
        else
            echo "❌ Neither main nor master branch found"
            exit 1
        fi
        echo "✅ Switched to $(git branch --show-current) branch"
    fi
fi

# Push to remote
echo "📤 Pushing to remote repository..."
if ! git push; then
    echo "❌ Failed to push to remote repository"
    exit 1
fi
echo "✅ Code pushed to remote"

# Display deployment information
echo ""
echo "🎉 Deployment Preparation Complete!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo "1. Go to https://render.com"
echo "2. Sign up/Login to your account"
echo "3. Click 'New +' → 'Blueprint'"
echo "4. Connect your GitHub account"
echo "5. Select this repository"
echo "6. Click 'Apply' to deploy"
echo ""
echo "🔗 Your services will be available at:"
echo "   - API: https://ai-data-platform-api.onrender.com"
echo "   - Web UI: https://ai-data-platform-ui.onrender.com"
echo "   - n8n: https://ai-data-platform-n8n.onrender.com"
echo ""
echo "🔐 n8n Access:"
echo "   - Username: admin"
echo "   - Password: admin123"
echo ""
echo "📚 For detailed instructions, see: docs/deployment-guide.md"
echo "📋 For deployment checklist, see: DEPLOYMENT_CHECKLIST.md"
echo ""
echo "�� Happy deploying!"
