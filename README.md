# TROJANS AeroFleetX

**Author:** Tahiatul Islam Siddique  
**Affiliation:** Aviation and Aerospace University Bangladesh  
**Research paper:** *TROJANS AeroFleetX: Design and Implementation of an Integrated Mobile Research Platform for Aviation Maintenance Intelligence*  
**Preprint:** [Zenodo DOI 10.5281/zenodo.21732389](https://doi.org/10.5281/zenodo.21732389)

TROJANS AeroFleetX is an offline-first Android research and education prototype for connected aviation-maintenance workflows. It combines synthetic fleet-health presentation, explainable rule-based maintenance-risk simulation, camera-assisted 3D inspection, maintenance programs, scheduling, digital work orders, local records, and training scenarios.

## Research status and safety boundary

This repository is a research artifact. It is **not** certified airline maintenance software and must not be used to determine airworthiness, approve maintenance, replace approved maintenance manuals, or support release-to-service decisions. Aircraft values, thresholds, histories, risk outputs, and task templates are synthetic demonstrations unless explicitly stated otherwise.

## Reproducibility scope

The repository includes:

- the Android Studio project;
- packaged HTML, CSS, JavaScript, and 3D-rendering assets;
- source-level regression checks;
- a Playwright browser workflow test;
- recorded browser and signed-release validation evidence from the earlier release process;
- an unsigned public Android clean-build workflow;
- documentation of the predictive-risk formula and validation boundaries.

Functional tests verify implementation behavior. They do not validate real-aircraft maintenance accuracy, learning outcomes, safety improvement, or predictive performance.

## Quick start

### Run the web interface

```bash
cd app/src/main/assets/web
python3 -m http.server 8000
```

Open `http://127.0.0.1:8000` in a modern browser.

### Run source-level tests

```bash
python3 -m pip install -r requirements-dev.txt
pytest -m "not browser" -q
```

### Run browser workflow tests

```bash
python3 -m playwright install chromium
pytest -m browser -q
```

### Build Android application

The public verification workflow performs an unsigned clean build with JDK 17, Gradle 8.13, Android platform 36, and Build Tools 35.0.0. It does not require signing secrets.

For local use, install Gradle 8.13 and the Android SDK, then run:

```bash
./scripts/bootstrap_wrapper.sh
./gradlew --no-daemon --stacktrace clean lintDebug assembleDebug
```

Release signing credentials are intentionally excluded. A green public CI run is required before the source release is described as independently clean-build verified.

## Demonstration dataset

The application includes four synthetic aircraft profiles and 18 component templates:

- Boeing 777: 6 components
- Boeing 737: 4 components
- Boeing 787: 4 components
- C-130J training profile: 4 components

Each aircraft can be presented using routine, degrading, and check-preparation profiles. The risk engine is deterministic and threshold-based, except for the optional ten-cycle demonstration, which introduces bounded random degradation for visualization.

## Publication and citation

### Preprint

Tahiatul Islam Siddique (2026).  
*TROJANS AeroFleetX: Design and Implementation of an Integrated Mobile Research Platform for Aviation Maintenance Intelligence.*  
Zenodo.  
https://doi.org/10.5281/zenodo.21732389

The manuscript is a non-peer-reviewed preprint and is licensed under CC BY 4.0.

### BibTeX

```bibtex
@misc{siddique2026trojans,
  author = {Siddique, Tahiatul Islam},
  title = {TROJANS AeroFleetX: Design and Implementation of an Integrated Mobile Research Platform for Aviation Maintenance Intelligence},
  year = {2026},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.21732389},
  url = {https://doi.org/10.5281/zenodo.21732389}
}
```

The paper remains CC BY 4.0. The source code is MIT licensed. The active publication path uses only CC BY-compatible publication options and does not depend on an editor licensing exception.

## Licence

Software code is released under the MIT Licence. The TROJANS/AeroFleetX names and branding remain identifiers of the author. Third-party aircraft and company names are used only to identify synthetic demonstration profiles and do not imply endorsement.
