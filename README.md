# Crab Robot — integrated controller prototype

**UNPUBLISHED WORK IN PROGRESS — do not order this revision.** Electrical and firmware checks pass, but the current PCB cannot be inserted into the protected case and three mounting screws cannot be reached. The real PCB needs the corner, mounting-hole and USB-position changes in `case/DEVIATIONS.md` D18. The virtual revision passes an insertion sweep; that is not a revised routed board. `build.sh` deliberately rejects this incomplete assembly. Main is unchanged.

One **88 × 62 mm custom PCB** contains the ESP32-S3-WROOM-1-N16R8, PCA9685 eight-servo controller, 3.3 V regulator, USB-C and BOOT/RESET buttons. It replaces the LILYGO development board and separate PCA9685 breakout in the robot. A small Waveshare 1.9-inch LCD connects by an eight-wire harness and keeps the QR setup flow.

This branch is the integrated hardware variant. The original modular build remains on `main`.

![Integrated controller and external connections](docs/images/integrated-connections.svg)

## Start here

1. Read [what to buy and ask the assembler to fit](docs/AFTER-ORDER.md). Choose **assembled PCBA**, rather than a bare board requiring fine-pitch soldering.
2. Use the [PCB/PCBA ordering guide](docs/PCB-ORDERING.md) and generated manufacturing packet to request a quote.
3. Follow the [illustrated wiring guide](docs/INTEGRATED-WIRING.md). The bought servos, light and power bank remain external.
4. Build and flash the **integrated** firmware using the [firmware guide](docs/INTEGRATED-FIRMWARE.md).
5. Assemble the [integrated skeleton case](case/README.md). Its base/lid are new; the plate-2 legs and clamp bars retain their frozen r1 geometry and placement.

## What it does

On first start the LCD shows a setup QR. Connect your phone, choose the Wi-Fi network and enter its password, then open the robot's web controller. The firmware provides directional driving, speed, LED control and servo-centering/trim controls for assembly. Hold the running application's BOOT button for eight seconds to return to Wi-Fi setup.

Eight SG90 servos plug directly into the labeled CH0–CH7 sockets: two per leg. Port 1 of the existing 5 V power bank feeds USB-C logic power; port 2 feeds the servo/LED terminal through the USB adapter. Their positive rails stay separate; their grounds are joined on the PCB. No loose-cell battery pack is needed.

## Prototype status

Native schematic/PCB checks, manufacturing checks, firmware host tests and CAD/slicer checks are desk checks. The new board has **not** been manufactured, powered or flashed; the new case has **not** been physically fit-tested. No walking, radio-range, temperature or servo-load result is claimed. The owner's successful QR test was on the earlier LILYGO board, not this PCB.

The release validation record is in [BUILD-VALIDATION.md](BUILD-VALIDATION.md). Generated reports bind their results to the files produced by your build.

## What may need hands-on adjustment

Ask the assembler to inspect soldering, mounting insulation and regulator temperature. The through-hole connector service covers 37 PCB joints if not included in the PCBA quote. Use the LCD's supplied cable; the module connector is MX1.25. The case's rear tunnel needs a USB-C plug body at most **11.4 mm wide**.

The first assembled prototype still needs checks for servo/horn fit, actual joint directions, cable routing, screen readability and QR scanning, power-bank shutoff/surges, floor grip and skeleton strength. Direct 3.3 V WS2812 data is an assumption to check on the actual light bar. BOOT access with the lid closed uses an angled pin path; the native checker does not verify that path. See [remaining purchases and manual work](docs/AFTER-ORDER.md) and the case deviations for the recorded limits.

## Build from source

```sh
./build.sh
```

Run in the documented macOS KiCad Harness toolchain: KiCad 10.0.5 and its pinned model library, CadQuery 2.7.0/OCP 7.8.1.1, Bambu Studio CLI, Arduino CLI with ESP32 core 2.0.14, Python/Pillow, clang/clang++, Node and Swift/Vision. Set `KICAD_HARNESS_PYTHON` and `KICAD_CASE_PYTHON` to the supplied interpreters. The first build downloads two hash-pinned Waveshare reference inputs into an ignored cache; vendor datasheets are not stored in Git. The script reports missing dependencies and does not install software, flash hardware, print or order anything.

Build order is library/model preparation → native board checks/exports/STEP/manufacturing packet → source-recreated frozen parts → current case/CAD checks → print plates → interactive assembly overview → both firmware targets and host/interface tests. Native copper is an authored input; the release build does not rerun the placement-draft generator over accepted routes.

Generated CAD, Gerbers, reports, firmware binaries, plates and overview remain outside Git. After a successful build, open `case/overview.html`, `case/print/production.3mf` and the manufacturing packet under `boards/`. See [build requirements and validation](BUILD-VALIDATION.md) for exact output paths and commands.

[Native KiCad sources](design/) · [PCB BOM and engineering](engineering/) · [Firmware source](firmware/crab/) · [Case source](case/)
