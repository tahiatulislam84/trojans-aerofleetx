# CRESCO / Cessna 172 camera study

An isolated research page that reuses the existing generic WebGL landing-gear renderer. No existing app files, assets, routing, records, or workflows are modified.

Run `python3 -m http.server 8000` inside `app/src/main/assets/web`, then visit `http://localhost:8000/experiments/landing-gear-camera/`. On a phone, serve over HTTPS; plain HTTP on a remote host cannot request the camera. Permit camera access, select the aircraft context, and manually position the generic model. The highlighted points are illustrative orientation prompts only.

## What is needed for automatic alignment

Camera access alone does not establish aircraft identity, depth, pose, or component geometry. Before implementing markerless registration, obtain (with permission) the precise CRESCO and Cessna 172 model/variant and gear configuration, representative labeled video from several phones and lighting/viewing conditions, aircraft-specific 3D geometry with defined coordinate landmarks, and a validation set with measured ground-truth landmark positions. Evaluate registration error, loss of tracking, false aircraft/part matches, and explicit refusal when confidence is low. Approved inspection documents must supply any real sequence, criteria, and limits; none are inferred from this prototype.
