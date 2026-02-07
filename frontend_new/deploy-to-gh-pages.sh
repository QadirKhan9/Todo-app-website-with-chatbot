#!/bin/bash

# Script to build and deploy Next.js app to GitHub Pages

set -e  # Exit on any error

echo "Starting GitHub Pages deployment process..."

# Navigate to the frontend directory
cd /mnt/e/hackathon/todo\ app\ Phase\ 3/frontend_new

# Install dependencies if not already installed
echo "Installing dependencies..."
npm install

# Build the app for static export
echo "Building the app for GitHub Pages..."
cp next.config.github-pages.js next.config.js
npm run build

# Rename the out directory to docs (GitHub Pages default for /docs folder)
echo "Preparing files for GitHub Pages..."
mv out docs

# Commit and push to GitHub
echo "Committing changes..."
git add docs/
git commit -m "Deploy frontend to GitHub Pages" || echo "No changes to commit"

echo "Deployment preparation complete!"
echo "To finalize deployment:"
echo "1. Push changes: git push origin root"
echo "2. Go to GitHub repository settings"
echo "3. Under 'Pages' section, set source to 'Deploy from a branch'"
echo "4. Select 'root' branch and '/docs' folder"
echo ""
echo "Your site will be available at https://qadirkhan9.github.io/Todo-app-website/"