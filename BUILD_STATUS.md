# Android clean-build status

Status: **GitHub-ready release candidate; a public green CI run is still required before claiming independently verified Android reproducibility.**

## Corrected defects

1. `AeroInspectActivity.writeExport()` now catches and rethrows only exceptions allowed by its declared Java contract.
2. The verification workflow performs an unsigned debug build and does not require private signing secrets.
3. The workflow provisions JDK 17, Gradle 8.13, Android platform 36, and Build Tools 35.0.0.
4. The Gradle distribution SHA-256 is pinned in `gradle-wrapper.properties`.
5. Regression tests cover the Java exception contract, Android configuration, safety wording, predictive profiles, and CI commands.
6. The workflow uploads the debug APK and lint reports as build evidence.

## Local result in the preparation environment

- Source-level regression checks: 12 passed.
- JavaScript syntax checks: passed.
- Archived browser validation: 12 recorded assertions passed with zero recorded JavaScript runtime errors.
- Full Android Gradle clean build: not executed in the preparation container because the Android SDK and Gradle distribution were unavailable there.

## Publication rule

Do not write that the Android build is independently reproducible until the public workflow has passed for the exact source commit. After it passes, record the workflow URL and commit SHA in `docs/BUILD_VERIFICATION.md` and create a tagged source release.
