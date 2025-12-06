#!/bin/bash

# Clean previous builds
rm -rf build dist

# Build the app
# --noconfirm: Replace output directory without asking
# --onedir: Create a one-folder bundle (faster startup than onefile)
# --windowed: Mac OS X app bundle (no console window)
# --add-data: Include assets folder
# --name: App name

echo "🚀 Building Spotit.app..."

echo "🚀 Building Spotit.app from spec..."

pyinstaller --noconfirm --clean "/Users/apple/Desktop/life/university/placement/projects/spotit/Spotit.spec"

echo "✅ Build complete! You can find the app in the 'dist' folder."
echo "📂 Opening dist folder..."
open dist
