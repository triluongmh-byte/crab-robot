# Pin and pad audit
| Schematic pin | PCB pad | Net | Function |
|---|---|---|---|
| J1.1 | J1.1 | DUMMY_A | Integral solder landing |
| J2.1 | J2.1 | DUMMY_A | Integral solder landing |
| J3.1 | J3.1 | DUMMY_B | Integral solder landing |
| J4.1 | J4.1 | DUMMY_B | Integral solder landing |

MH1/MH2 are pinless Mechanical:MountingHole symbols and nonconducting Ø3.2 NPTHs. They have no electrical nets. Copper pads are 2 × 3 mm rounded rectangles, front copper and mask only, no paste, no installed connector. Net names intentionally have no relation to the robot's pins. Source table: tools/board/spec.json; generator: kicadpy.author. Local symbol definitions are flattened copies of bundled KiCad Connector_Generic:Conn_01x01 and Mechanical:MountingHole. Native netlist comparison measures every connected pin and PCB pad rather than trusting this table. No module pin map or manufacturer IC is relevant to this dummy.
