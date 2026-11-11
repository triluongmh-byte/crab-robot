# Direct phone connection (release note 10)

The physical target the owner has is the original LILYGO T-Display-S3 with a
PCA9685 module. The integrated PCB has a separate build; it is unmanufactured
and is not authorized for flashing. Both targets contain this AP fix.

Join the open **CuaRobot-XXXX** network from QR #1. Keep the connection when the
phone says it has no internet, then open **http://192.168.4.1/**. Captive portal
probes serve the same control page. Home Wi-Fi is optional. The control page,
light and assembly page work without a station connection; status polls never
navigate. The product interface remains Vietnamese.

To configure home Wi-Fi, explicitly press **Wi-Fi**, scan, select a 2.4 GHz
network and enter its password. Wrong passwords and the 18-second timeout show
Vietnamese errors on the display and current page. They do not change pages or
save the failed credentials. Successful setup stores credentials privately in
NVS and displays QR #2 with the station web address. Credentials are never
returned in status or logged. Holding BOOT for 8 seconds while firmware runs
erases Wi-Fi credentials only. The AP remains available.

Saved networks are joined automatically on boot. Background retries run about
every 30 seconds only while no AP client is attached. An AP client arriving
cancels an unfinished background attempt. Manual scan/setup can preempt it.
The AP is never deliberately restarted by retry handling. The ESP32-S3 shares
one radio between AP and station: an attempt already underway before the phone
joins, manual scanning/joining, or an upstream channel change may interrupt the
link. Host tests cannot prove radio continuity; actual phone/range/channel
behaviour is unverified. Release and reconnect before pressing again after any
interruption. The independent 500 ms command lease still stops stale motion;
station loss alone no longer stops a valid AP control session. Hold/release,
session ordering and the persistent assembly lock are unchanged.

## Servo mode stays independent

Boot leaves all 16 outputs off. The light and page navigation remain available independently. Open [360° thử nghiệm](CONTINUOUS360.md) for per-channel measured calibration, a manual-reference confirmation and bounded estimated-angle jogs. Stored/RAM values never auto-arm after reboot. The legacy diagnostic is under **Chi tiết → Thử cũ** and invalidates the reference. Continuous servos cannot use the retained positional angular gait; drive arrows remain disabled. No physical motor operation is part of building or flashing.

Build: `python3 tools/firmware/build.py --target all` from the project root.
Host checks: `python3 tools/firmware/check.py`; focused AP checks:
`python3 tools/firmware/check.py web http core`. Wiring and both hardware pin
profiles are unchanged. See the [firmware guide](README.md) and [source validation](../BUILD-VALIDATION.md).
