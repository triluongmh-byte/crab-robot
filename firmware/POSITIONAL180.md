# First connection of the replacement180° servos

The180° firmware is prepared on the original LILYGO. The owner reports servo power disconnected; no replacement motor was tested during the update. Use only the delivered positional motors. Keep the old360° units unplugged.

## Centre one unloaded motor first

1. Keep servo5V disconnected. Unplug the old motors. Remove the horn/printed leg from one new servo's shaft and plug that servo into **CH0** as a complete three-wire plug: orange→S/PWM,red→V+,brown→GND.
2. Power LILYGO by USB, join its Wi-Fi and open the controller. Boot leaves every servo output off. Open **Ráp**.
3. Supply the PCA servo terminal with the correctly polarised5V supply. Press **Bật servo180°**, then **Giữa thô ·1500µs**. Wait until status reaches8/8 (approximately3seconds); the one connected servo is commanded to the nominal centre. The other empty channels may be enabled but contain no motors.
4. Confirm it turns to a position and holds rather than spinning continuously. If it spins, buzzes against a stop, binds or resets the board, disconnect servo power. Do not attach a leg to resolve it. Record what happened for the next adjustment.
5. Disconnect servo5V before unplugging that motor, attaching its horn or moving to the next one. Keep the shaft's centred position while fitting the horn in the mechanical neutral pose. Repeat this unloaded-centre procedure for the replacement set.

## Connect the complete set

Use the [same photo wiring sheet and CH0–CH7 map](WIRING.md). Hip channels are0/2/4/6; knees are1/3/5/7. After wiring, leave power off and check that each leg can move without catching the body, another leg or a tight wire. Do not force the gears.

Support the body with the feet clear. Reapply power, enable the positional servos and use **Ráp → Tư thế đứng**. Adjust small +/− trims, use **Lưu tâm**, then **Xong ráp**. Old experiment-era trim data is not loaded into this release; the new trim namespace starts at zero.

Normal-speed firmware defaults to **Bình thường**. Choose **Chậm** and a short held direction for the first direction check while the body is supported. Release stops the walking sequence and settles towards standing. **Ngắt servo** turns PWM off; removing servo5V is the physical power disconnect. Only try the floor after direction, neutral, clearance, cable slack and supply behavior are satisfactory. Stable walking has not been demonstrated with these motors.

All degree labels are nominal: the initial pulse span is conservative, and actual loaded angles/torque depend on the received units. Firmware has no external encoder or collision detector. Increasing pulse ranges is not part of this first setup.
