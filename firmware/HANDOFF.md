# Firmware source handoff

The LILYGO and integrated targets share the application and retain separate recipes, display buses and servo-enable behaviour. No runtime GPIO change accompanies the side-USB repair. The panel remains rotated 180 degrees, matching case D15/D27.

Use the [English firmware guide](README.md), [labelled wiring](WIRING.md) and [repository build validation](../BUILD-VALIDATION.md). Run the root build to regenerate both image sets, host/QR tests and native-board reconciliation; these generated reports are not source files. No flash or physical motor test is included. The integrated board remains unmanufactured and the new frame unprinted.
