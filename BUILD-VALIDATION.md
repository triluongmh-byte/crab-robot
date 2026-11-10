# Source build validation

The current source revision replaces the closed-body insertion proposal with staged assembly of two open frames and a real side-entry USB-C PCB. The old failed build record describes the superseded closed body and is not evidence for this revision.

An empty-clone run of `./build.sh` is required before publication. This document will record that exact source commit, exit status and checks once the run finishes. No manufactured-board or physical-frame result is claimed.

Generated outputs include native manufacturing exports, the populated PCB STEP, case STEP/STL and reports, the complete two-plate `case/print/production.3mf`, three separate test projects, `case/overview.html`, both complete firmware image sets and host/QR test evidence. They are ignored and regenerated from the committed sources. No printer, USB device, ordering or payment action is part of the build.

Toolchain: macOS, KiCad 10.0.5, CadQuery 2.7.0/OCP 7.8.1.1, Bambu Studio CLI, Arduino CLI 1.5.1/ESP32 core 2.0.14, clang, Node, Pillow and Swift/Apple Vision. Set `KICAD_HARNESS_PYTHON` and `KICAD_CASE_PYTHON` to the documented interpreters. The build fetches hash-pinned manufacturer inputs into an ignored cache and installs no software.
