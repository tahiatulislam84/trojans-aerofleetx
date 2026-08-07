# AeroFleetX CI Stabilization Release Notes

**Date:** 2026-08-07  
**Validated source commit:** `a412f381a5d9547d00d2fbcf87f73ffb502dec5d`  
**Successful public workflow:** `AeroFleetX Current Main CI` run `31138794643`

## Release classification

This milestone is a **debug and testing build**, not a production release. The successful workflow produces a debug APK for validation and reproducibility purposes.

Production distribution requires a separately signed release build created in a controlled release environment. Private keystores, signing files, signing passwords, tokens, and other credentials must never be committed to this repository or shared in release notes, issues, build logs, or artifacts.

## CI validation result

The public workflow completed successfully with all required stages passing:

- exact source revision checkout and verification;
- stale browser-selector rejection;
- Android clean compilation;
- Android lint;
- debug APK assembly;
- 12 source-level regression tests;
- integrated Playwright browser workflow validation; and
- reproducibility-evidence artifact upload.

Evidence artifact:

`aerofleetx-clean-build-evidence-a412f381a5d9547d00d2fbcf87f73ffb502dec5d`

## Android back-navigation migration

The Android host activity was migrated away from the deprecated direct back-press override to AndroidX back handling:

- the activity now extends `ComponentActivity`;
- back navigation is handled through `OnBackPressedDispatcher` and `OnBackPressedCallback`;
- the callback preserves WebView history navigation before allowing the activity to finish; and
- `androidx.activity:activity:1.8.0` was added as the supporting AndroidX dependency.

This keeps back behavior lifecycle-aware and compatible with current Android guidance while preserving the application's existing WebView navigation behavior.

## Kotlin dependency alignment

The application dependencies now import the Kotlin BOM at version `1.8.22`.

This aligns Kotlin standard-library variants and removes the duplicate-class conflict caused by mixing Kotlin standard library `1.8.22` with older `kotlin-stdlib-jdk7` and `kotlin-stdlib-jdk8` `1.6.21` artifacts.

## Android API-level resource and WebView fixes

Two minimum-SDK compatibility issues were corrected without raising `minSdk` or suppressing lint:

1. `WebView.startSafeBrowsing` is now guarded at API level 27 (`Build.VERSION_CODES.O_MR1`), matching the API where the method is available.
2. `android:windowLightNavigationBar` was removed from the base `values/styles.xml` theme and moved into `values-v27/styles.xml`.

For API levels 23 through 26, the base theme uses a dark navigation-bar color suitable for light navigation icons. API level 27 and newer use the light navigation-bar appearance with a white navigation bar.

## Browser-validation corrections

The browser workflow was repaired while preserving its functional assertions:

- predictive-maintenance cards are validated with the actual `.predictive-component` class instead of the obsolete `.prediction-card` selector;
- the first-launch tutorial is dismissed before interacting with the predictive scheduling screen;
- the uniquely named **Close tutorial** control is used to avoid Playwright strict-mode ambiguity between two close buttons;
- the test still requires at least four predictive component cards, warning/explainability content, scheduling-modal behavior, and navigation across mission control, XR, training, and safety screens; and
- the CI workflow records and verifies the exact checked-out commit SHA and rejects the obsolete predictive selector early.

## Deferred CI maintenance

The successful workflow emitted non-blocking deprecation warnings related to GitHub Actions moving from Node.js 20 to Node.js 24 and `actions/setup-java@v4` being deprecated.

These warnings did not affect compilation, lint, testing, APK assembly, artifact generation, or the successful workflow conclusion. They are intentionally deferred to a separate maintenance change so the validated stabilization patch remains focused and reproducible.

## Production-release boundary

A green debug workflow demonstrates that the current source compiles, passes lint, assembles a debug APK, and passes the included source and browser tests. It does **not** certify production signing, store readiness, operational safety, regulatory compliance, or suitability for real aircraft maintenance decisions.
