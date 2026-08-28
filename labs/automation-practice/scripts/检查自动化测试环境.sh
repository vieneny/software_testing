#!/usr/bin/env bash
set -euo pipefail

echo "== Core tools =="
python --version
node --version
npm --version

echo
echo "== Appium =="
appium --version
appium driver list --installed

echo
echo "== Android devices =="
adb devices -l

if command -v xcodebuild >/dev/null 2>&1; then
  echo
  echo "== Xcode and iOS simulators =="
  xcodebuild -version
  xcrun simctl list devices available
else
  echo
  echo "Xcode is not installed; skip iOS checks."
fi

