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

## Servo experiment remains separate and not started

The AP fix has passed independent source/host review and a full empty-clone
build. The separate servo experiment has not been implemented. No actuator
setting or one-channel servo experiment is included in these binaries. The existing
positional boot/gait/raw-centre logic remains unchanged, so do not run it with
the owner's continuous/unknown servos. Continuous servos cannot hold joint
angles or produce the positional walking gait; timed pulses do not add angle
feedback. A 1500 us pulse can cause creep/spin. Servo type and health per unit
remain unknown. The owner's current parts include **no servo supply of
established rating**; any later unloaded one-servo test needs a supply decision
first. The exposed 18650 and unidentified module are not recommended or wired
as a supply here. No purchases, flashing or motor operation were performed.

Build: `python3 tools/firmware/build.py --target all` from the project root.
Host checks: `python3 tools/firmware/check.py`; focused AP checks:
`python3 tools/firmware/check.py web http core`. Wiring and both hardware pin
profiles are unchanged. See the [firmware guide](README.md) and [source validation](../BUILD-VALIDATION.md).
