# Project-scoped firmware flashing authorization

The owner authorized updating this project's original LILYGO T-Display-S3 non-touch ESP32-S3 on 2026-11-09. The owner renewed the request on 2026-11-10: “nạp hết đi fen.” The owner renewed code, flash and push authorization on 2026-11-11 after reporting the manual reference pose. This is standing permission for completed, tested firmware updates to that identified device. Current motor isolation remains a separate prerequisite. A later instruction not to flash overrides it. It does not authorize flashing the new integrated PCB, another device, motor operation, printing, purchases or publication of private device dumps.

Before every write:

1. Build and test the current LILYGO target; preserve the exact source, build configuration, tool versions, binary hashes and upload offsets.
2. Confirm current physical isolation: all servo plugs removed and PCA servo V+ power disconnected. Flash permission alone does not authorize testing motors.
3. Identify the exact chip, unique identity and current USB port. A vendor ID alone is insufficient. Resolve only the target's serial-port conflict and restore its prior listener state afterwards.
4. Read the complete detected old flash, verify the readback against the device, and preserve it locally with hashes and an exact restoration command. Keep older stable checkpoints unchanged. If the installed source is unknown, preserve its exact bytes without claiming a source-to-binary match.
5. Upload only the verified LILYGO image set using the project's recipe; verify the written bytes and check nonmotor boot/protocol behavior. Restore and verify the pinned previous image if the new image fails. Retain the successful new image.

Store each attempt and its receipt in a new private local recovery directory. Device dumps can contain Wi-Fi credentials and calibration data: never commit or publish them. Keep previous attempts immutable. A missing device, failed backup, unresolved serial owner or unconfirmed motor isolation is an unmet prerequisite; do not erase blindly or ask for the same flashing authorization again.

Design/build checks, USB byte verification, an observed LCD QR, successful web control and physical walking are separate evidence. Report only the checks actually performed.

## Owner update —2026-11-12

The owner explicitly requests writing, flashing and pushing the dedicated180° firmware, and reports that servo power has been unplugged. This confirms reported supply disconnection, not removal of all servo plugs. Preserve that distinction in the flash receipt; do not invent complete physical isolation. Earlier explicit skip-fresh-readback instructions remain in effect: retain the previously written and verified image set as rollback, verify every new written image and restore the pinned set on a failed write. These owner instructions supersede the stronger isolation/readback prerequisites above for this identified original LILYGO update only. No powered servo or walking test is authorized or performed as part of this update.
