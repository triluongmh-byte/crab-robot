# Integrated V0 power and reset states

PB1_5V enters USB-C J1; separate5.1k CC resistors identify a sink. It feeds
only U2 and USB/VBUS testpoint. U2 is TI TLV1117LV33DCYR1A, not TLV1117-33
or AMS1117: the flattened symbol is pin-compatible, its value/BOM identify
LV explicitly. Inputs4.75–5.25V are inside2–5.5V. Dropout at1A max0.7V
leaves at least4.75-3.3-0.7=0.75V headroom. Output±1.5% plus line/load
allowance remains inside ESP/PCA/module3.3V supply ranges.

Design reserve: ESP recommended500mA source capability +Waveshare40mA
+PCA10mA max +10mA backlight-control pulldown/pulls =560mA;1A LDO has
440mA electrical headroom. Estimated continuous worst RF TX355mA+40+10+10
=415mA; thermal analysis uses this and separately evaluates560mA transient.
These are datasheet/estimated budgets, not measured currents.

Actual C2=4.7uF andC3=0.1uF onPB1_5V total4.8uF; +10% tolerance5.28uF <10uF.
C4/C5/C7=3×10uF +C9=1uF +C6/C8/C10=3×0.1uF on3V3 total31.3uF.
Output capacitor requirement1uF remains met even at severe ceramic derating.
Actual IC-to-cap distances from native pads: U1.2→C6.1 2.730mm;
U3.28→C8.1 2.158mm; U2 output tab→C4.1 2.000mm; output lead→C5.1 2.600mm.
U2 input→C2.1 2.600mm; C3 is a nearby second input bypass.

Tool limitation: kicadpy.verify power's rail-name heuristic does not recognise
PB1_5V/SERVO_5V and prints PB1_5V 'NO capacitor' despite actual C2/C3 pad nets.
Do not rename contract nets or patch checker. tools/board/check.py independently
sums every actual two-pad capacitor by exact net, enforces5.28uF worst-case,
and stores the measurement in build/board/geometry.json. Product still declares
PB1_5V10uF; publisher's own unmodified cap-distance checks remain active.

SERVO_5V J12(+) feeds eight red-wire pins, C11 1000uF16V, and J11LED5V.
J12GND, all brown pins, LEDGND and USBGND join on PCB. No positive rail bridge
exists.2.4A port is a source limit, not an eight-servo stall-current claim:
8×0.7A estimated stall +0.48ALED =6.08A, above source. Sequential startup,
slew limits and phase offsets are mandatory. Bulk only supplies ΔV=IΔt/C;
1000uF can supply1A for1ms at1V droop, not a sustained stall. User assembly
checks source shutdown and reduces speed/load or changes the bought bank.

Reset/empty flash/ROM download: GPIO21 is high impedance, R9 10k holds /OE
high. PCA OUTNE00 POR gives low outputs; no stale PWM pulses reach servos.
Warm MCU reset also disables old PCA PWM via /OE, even though PCA retains
registers. Firmware writes all FULL_OFF before enabling GPIO21 low. Servo5V
is always physically present; signal disable is not current isolation.
GPIO0 has10k pullup; SW1 grounds it. EN has10k/1uF RC and SW2 reset.45/46/3
are not driven by a display; octalPSRAM35–37, UART43/44 and4/16 are unused.
GPIO15 isNC; its previous LCD power role no longer exists.

LCD reset held low10k, CS held high10k. Backlight has330Ω host pulldown to
overcome vendor module pullups while MCU resets; high drive costs about10mA.
Vendor schematic TXS0108 +S8050 path reviewed; assembled start/QR test checks
that module revision behaves as documented. SPI GPIO8/39 avoid strap loading.
WS2812 DIN GPIO1 remains direct3.3V, a retained reference assumption. A powered
WS2812 keeps its last colour on warm MCU reset; no default-off LED claim is
made. Firmware sends black first. Switch both bank ports off to clear it.

Note9: J1 moved to+Y; USB-RELOCATION.md and usb-relocation-audit.json measure
the actual new0.6mm PB1 feeder. Conservative560mA drop≈60mV at20°C/72mV
at70°C, still0.678V dropout reserve. Rail nets/caps/LDO and loads unchanged.
