#!/usr/bin/env bash
set -euo pipefail

download_dir="${1:-mobile-apps}"
mkdir -p "${download_dir}"

download_and_verify() {
  local url="$1"
  local output="$2"
  local expected_sha="$3"

  curl --fail --location --retry 3 --output "${output}" "${url}"
  local actual_sha
  actual_sha="$(shasum -a 256 "${output}" | awk '{print $1}')"
  if [[ "${actual_sha}" != "${expected_sha}" ]]; then
    echo "SHA-256 mismatch for ${output}" >&2
    echo "expected: ${expected_sha}" >&2
    echo "actual:   ${actual_sha}" >&2
    exit 1
  fi
}

download_and_verify \
  "https://github.com/appium/android-apidemos/releases/download/v6.0.14/ApiDemos-debug.apk" \
  "${download_dir}/ApiDemos-debug-v6.0.14.apk" \
  "892d4441a24757fc88852d29abe87d42d14f04921cbe89802e369dad6e46edba"

# My Demo App 的 Android/iOS Release 仍提供官方下载，但上游没有同时公开所有资产的
# SHA-256。为避免把未经复核的哈希写死，教程要求首次下载后自行记录哈希并人工复核来源。
curl --fail --location --retry 3 \
  --output "${download_dir}/mda-2.2.0-25.apk" \
  "https://github.com/saucelabs/my-demo-app-android/releases/download/2.2.0/mda-2.2.0-25.apk"

download_and_verify \
  "https://github.com/saucelabs/my-demo-app-ios/releases/download/2.2.2/SauceLabs-Demo-App.Simulator.zip" \
  "${download_dir}/SauceLabs-Demo-App-2.2.2-Simulator.zip" \
  "96b08d5ac74dd817d95fbd8332ae9385bb076af38d56d13d8465345cb1797139"

download_and_verify \
  "https://github.com/appium/ios-uicatalog/releases/download/v4.0.4/UIKitCatalog-iphonesimulator.zip" \
  "${download_dir}/UIKitCatalog-iphonesimulator-v4.0.4.zip" \
  "7862f5eae50f2858cae554e100775e1137a29c24a0087137bfcced02431865eb"

shasum -a 256 "${download_dir}"/*
