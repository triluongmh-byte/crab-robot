# Protection boundaries — integrated V0

Only bought sealed USB5V supplies are used; no mains or battery circuitry.
As explicitly required, there is no fuse, buck, MOSFET, crowbar or extra
protection circuit. One LDO and necessary passives replace LILYGO power.
USB-C is a5V sink with two5.1k CC resistors; no PD/high-voltage negotiation.
No external3V3 source is connected, so LDO reverse-feed through its internal
body diode has no sustained external supply path.3V3 stored31.3uF energy is
½CV²≈0.170mJ. No bus power fromSERVO_5V feedsPB1_5V. CommonGND is intentional.

J12 terminal is polarity-labelled +5V/GND; connect with both bank outputs
unplugged, never hot-plug servo headers. Reverse terminal wiring, wrong
adapter polarity, shorted servo leads or arbitrary external supplies are not
protected by this board. Use only specified USB bank/adapter and labelled
cables. This is documented user assembly behaviour, not an invented protector.
Native USB lacks an extra ESD array per the prohibition; ESD handling and
normal indoor plug use are required. It is not an industrial hot-plug product.

PCA /OE reset control and firmware dead-man stop are reviewed in power.md.
/ OE stops pulses, not servo power or every possible mechanically held pose.
Power-bank current protection is supplied by the bought product; no unknown
trip curve is claimed. Motor regeneration and stalls may reset/shut the bank;
assembly instructions require stopping and disconnecting on that symptom.
No lithium cells, hardware access, power cycling or motor testing occurred.
