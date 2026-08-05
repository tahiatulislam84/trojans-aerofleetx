# TROJANS AeroFleetX 1.0.0 — Release Validation

Package: `com.trojans.aerofleetx.mobileapp`  
Version: `1.0.0` (`1`)  
Minimum SDK: `23`  
Target/compile SDK: `36`  

## Automated checks

- PASS — Browser workflow passed
- PASS — Zero JavaScript runtime errors
- PASS — AAB JAR signature verified
- PASS — APK JAR signature verified
- PASS — AAB required entries present
- PASS — Target SDK 36 configured
- PASS — Permanent package ID configured
- PASS — No INTERNET permission in production source
- PASS — Cleartext traffic disabled
- PASS — Backups disabled
- PASS — No duplicate HTML IDs
- PASS — Java source avoids unsupported Map.of/Set.of/isBlank
- PASS — Store screenshots created

## Browser workflow checks

- PASS — app visible
- PASS — fleet command rendered
- PASS — fleet health value
- PASS — predictive visible
- PASS — component cards
- PASS — explainability shown
- PASS — schedule modal opens
- PASS — mission control opens
- PASS — xr opens
- PASS — training opens
- PASS — safety opens
- PASS — research boundary present

## Hashes

- AAB SHA-256: `c7eb14a40a4436ebce987dd076d7e57d768d4deb4c418248de9a4f69fd5e0c42`
- APK SHA-256: `e4141cdc6b2d70efd979e49483635072ab329e05706db0452db08967f80585c0`

## Important verification boundary

The AAB has been structurally checked and its JAR/upload-key signature verified. Google Play server-side ingestion and Play-generated APK processing cannot be tested without uploading it to a Play Console testing track.

Physical Android installation, camera, microphone, image picker, export behavior and device-specific WebView behavior still require real-device testing before production rollout.

The app remains a research, education and technology-demonstration platform and is not approved for operational maintenance or release-to-service decisions.
