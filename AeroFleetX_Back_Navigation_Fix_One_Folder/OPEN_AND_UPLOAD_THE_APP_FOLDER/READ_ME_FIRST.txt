AeroFleetX Android build fix

1. Open this folder.
2. Drag the visible 'app' folder into GitHub's repository-root upload page.
3. GitHub should show these two updated paths:
   app/build.gradle.kts
   app/src/main/java/com/trojans/aerofleetx/mobileapp/AeroInspectActivity.java
4. Commit directly to main.
5. GitHub Actions will run automatically.

This replaces the deprecated onBackPressed override with AndroidX OnBackPressedDispatcher.
