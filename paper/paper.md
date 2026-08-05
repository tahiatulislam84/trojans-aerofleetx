---
title: 'TROJANS AeroFleetX: An open mobile research artifact for connected aviation-maintenance workflows'
tags:
  - Android
  - aviation maintenance
  - augmented reality
  - research software
  - training
  - work orders
authors:
  - name: Tahiatul Islam Siddique
    affiliation: 1
affiliations:
  - name: Aviation and Aerospace University, Bangladesh
    index: 1
date: 5 August 2026
bibliography: paper.bib
---

# Summary

TROJANS AeroFleetX is an Android research and education artifact that demonstrates how several aviation-maintenance activities can be connected within one mobile workflow. The application combines synthetic fleet-health displays, transparent threshold-based risk simulation, camera-assisted three-dimensional inspection, scheduled-maintenance templates, work-order creation, local records, planning, and guided training scenarios. It is designed for controlled teaching, software-evaluation, and design-research use. It is not certified maintenance software, does not replace approved technical data, and must not be used for airworthiness or release-to-service decisions.

The Android application packages a local web interface inside a hardened WebView. This architecture supports an offline-first demonstration while preserving a clear separation between Android device functions and the main interface logic. Four synthetic aircraft profiles and eighteen component templates provide repeatable scenarios. The predictive module is deliberately rule based rather than presented as trained artificial intelligence. Its thresholds, risk bands, and bounded degradation simulation are visible in the source and documentation.

# Statement of need

Research and teaching demonstrations of aviation-maintenance digitalization often address condition monitoring, augmented-reality inspection, work-order management, scheduled checks, or technical training as separate activities. That separation makes it difficult for students and researchers to examine information flow across an end-to-end maintenance scenario. AeroFleetX provides a reusable artifact for studying that integration without claiming access to operational airline data or certified maintenance authority.

The intended users are aviation students, instructors, human-factors researchers, maintenance-technology researchers, and software designers who need an inspectable prototype. A typical scenario begins with fleet-level condition awareness, opens a component-level risk explanation, transitions to an inspection or work order, schedules follow-up activity, and records the result. The artifact therefore supports questions about workflow design, explainability, traceability, mobile interaction, and training—not questions about actual aircraft serviceability.

# State of the field

Commercial maintenance, repair, and overhaul suites already integrate substantial planning, engineering, records, inventory, and work-package functions. AeroFleetX does not claim to replace or outperform those systems. Its contribution is a small, openly inspectable research artifact that combines representative workflows with synthetic data and explicit safety boundaries. Academic work has separately examined digital-twin architectures for aircraft maintenance [@bisanti2023], augmented-reality maintenance training [@peng2022], virtual-reality aircraft-maintenance education [@wu2022; @gomez2023], and predictive-maintenance architectures [@heim2020]. AeroFleetX provides a common prototype in which related interaction concepts can be evaluated together.

# Software design

The repository separates the Android wrapper, local web assets, tests, validation records, and documentation. Android device capabilities are exposed through narrow interfaces, while the web layer implements navigation, synthetic data, risk calculations, maintenance-program demonstrations, and training content. The Android manifest disables cleartext traffic and backup and does not request Internet access. Private release-signing credentials are excluded.

Automated checks cover configuration, JavaScript structure, safety wording, aircraft and component counts, risk bounds, maintenance-priority wording, archived validation records, and the Android Java exception contract. A Playwright scenario exercises the principal browser workflow. A public continuous-integration definition provisions the Android toolchain and runs an unsigned clean compile, lint check, debug APK assembly, source tests, and browser tests. The final JOSS submission must cite a green public run and tagged release; this draft does not claim that gate has passed.

# Research impact statement

AeroFleetX has an archived preprint and a prepared preliminary usability protocol. Its immediate scholarly value is as a transparent design artifact for aviation-maintenance education and workflow research. Stronger evidence of impact will require public repository history, independent installation, a completed clean-build record, and documented use in a research or teaching activity. The candidate should not be submitted to JOSS until those non-aspirational signals are available.

# AI usage disclosure

Generative AI tools assisted with drafting documentation, manuscript language, test scaffolding, and code review. The author remains responsible for the design and all claims. Generated changes were inspected against the repository, regression tests, archived validation evidence, and explicit safety boundaries. No synthetic user-study results or operational-aircraft evidence were generated or reported.

# Acknowledgements

No external funding is reported. The author thanks future instructors, students, and reviewers who evaluate the artifact under controlled research or education conditions.

# References
