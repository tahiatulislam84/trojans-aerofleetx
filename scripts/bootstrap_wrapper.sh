#!/usr/bin/env sh
set -eu
if ! command -v gradle >/dev/null 2>&1; then
  echo "Gradle is not installed. Install Gradle 8.13 or use the GitHub Actions clean-build workflow." >&2
  exit 1
fi
gradle --version
gradle wrapper --gradle-version 8.13 --distribution-type bin
grep -F 'distributionUrl=https\://services.gradle.org/distributions/gradle-8.13-bin.zip' gradle/wrapper/gradle-wrapper.properties
grep -F 'distributionSha256Sum=20f1b1176237254a6fc204d8434196fa11a4cfb387567519c61556e8710aed78' gradle/wrapper/gradle-wrapper.properties
./gradlew --no-daemon --version
