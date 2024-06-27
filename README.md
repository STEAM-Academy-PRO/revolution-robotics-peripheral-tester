# Revolution Robotics peripherial tester

What's the purpose of this library?

During manufacturing, we need to ensure that each peripheral operates correctly. To do this, we use several Revvy brains as dedicated testers. Each tester has a different SD card image and is responsible for testing a specific peripheral.

This repository is responsible to create the operating code for each tester.

## Writing tests

The test firmware is a modified version of the production pi firmware. The test code can be found in `<folder>/revvy.py`. The actual test configuration and logic is inside the `with ProgrammedRobotController(robot_manager) as robot_controller:` block in this file.

### Sensors

To configure a sensor, add a `config.add_sensor_from_json` line to the configuration. The number of `add_sensor_from_json` determines the position of the sensor port. The parameter is either a port type and port name pair, or `None` to skip a particular port.

For example, the following snippet configures a distance sensor to S2:

```python
config = RobotConfig()
config.add_sensor_from_json(None) # skip S1
config.add_sensor_from_json({"type": 1, "name": "distance_sensor"}) # S2
```

The available port types are:

- `1`: distance sensor
- `2`: button
- `4`: color sensor

### Motors

To configure a motor, add a `config.add_motor_from_json` line to the configuration. The rules are similar to sensors: `None` to skip a port, type and name to configure one.

For the purposes of peripheral testing, it is enough to know that motors need to be configured with type `1`.

The name of a sensor or motor will be used in the test logic to interact with them.

### Test logic

Test logic is implemented as a button-triggered test script, in the framework we use for automated testing.
The simplest way to develop a script is to use the mobile app's coding screen and its Run feature.
Create the script that does what you want it to, then copy the script to the interface at https://test.rr.scapps.io/desktop.html.
You can then paste the resulting python code into the test package, with added boilerplate to properly hook the script up into the configuration. For example, the button testing script looks as follows:

```python
        config.process_script( # add a script to the setup
            {
                "assignments": {"buttons": [{"id": 1, "priority": 0}]}, # boilerplate, keep the same
                "pythonCode": b64_encode_str( # the contents of this function is the test script
                    """import time


while True:
    if robot.sensors["button"].read():
        robot.led.set(leds=[1,2,3,4,5,6,7,8,9,10,11,12], color='#009900')
    else:
        robot.led.set(leds=[1,2,3,4,5,6,7,8,9,10,11,12], color='#000000')
    time.sleep(0.05)  # allow other threads to run

"""
                ),
            },
            0, # boilerplate, keep the same
        )
```

Do not create multiple scripts for testing unless you know exactly how the programmed robot interface works for automated testing. Only modify the contents of `"pythonCode": b64_encode_str(`.

The remaining code in the test setup is as follows:

```python
robot_controller.configure(config) # Apply the test configuration.
robot_controller.press_button(1) # Start the test logic.

robot_controller.wait_for_scripts_to_end() # Do not exit the test firmware while the test script is running.
                                           # You want the test script to run in an infinite loop, so
                                           # this should never return.
```

## How to create a tester SD card

### Through GitHub actions
- Go to the `revolution-robotics-pi-os` repository actions: https://github.com/STEAM-Academy-PRO/revolution-robotics-pi-os/actions/workflows/build-peripherial-tester-images.yml
- Find the "Build Peripherial tester OS images action
- Trigger it manually - mind that it can only be triggered on the `peripherial-tester` branch.

### Manually

- Flash a new SD card with one of the [working releases](https://github.com/STEAM-Academy-PRO/revolution-robotics-pi-os/releases) image. Place the SD card into a robot and boot it up.
- Connect to the robot according to [the instructions](https://github.com/STEAM-Academy-PRO/revolution-robotics-robot-mind/blob/main/docs/pi/connect-ssh.md)
- Once connected via SSH, run the following commands:

```
sudo systemctl stop revvy
sudo mount -o rw,remount /
sudo rm -rf /home/pi/RevvyFramework/default/packages/*
sudo chmod 777 /home/pi/RevvyFramework/default/packages
```

- Then copy (e.g. by using the Secure FTP Total Commander extension) the tester directory of your
choice to `/home/pi/RevvyFramework/default/packages/`. For example, you should end up with
`/home/pi/RevvyFramework/default/packages/Distance`.

> TODO: we could provide once-click setup scripts based on pi-firmware's `x.py`

- After all this, you can `sudo reboot` the pi and it should start the test firmware.



## Peripherial test details

### Motor

The motors contain an encoder that we use to measure their rotation. We use this information for
both position and speed control.

The test firmware is located in the `Motor/` folder.

**Motor test procedure**

The operator connects a motor to one of `M1` `M2` `M3`. The firmware will drive the motor at a low, medium, high speed depending on the port. The brain checks whether the motor behaves as expected and displays the corresponding green LEDs if the motor is considered working. If no motor is connected, or if the motor misbehaves, the corresponding LEDs will be red.

- Passing: after connecting the motor and letting the test run for 3 seconds, the corresponding LEDs on the ring ring shall display `green`.
- Failure: if, after waiting for 3 seconds the corresponding LEDs NOT display `green`, the motor is faulty.
- Note that this test can only check the basic behavior of the motor. Issues with the encoder cannot really be detected without external hardware (e.g. a tachometer).

### Button

The button is a simple digital input. The test makes sure we can detect that they are pressed.

The test firmware is located in the `Button/` folder.

**Button test procedure**

The operator connects a button to `S1`. The operator then presses the button a few times.

- Passing: when the button is pressed, the LED ring shall display `green`. When the button is NOT
  pressed, the LED ring shall display `red`.
- Failure:
  - The LED ring does not display `green` when the operator presses the button.
  - The LED ring does not display `red` when the operator does NOT press the button.

### Ultrasonic distance sensor

The ultrasonic sensor is a complex piece of digital electronics. We need to make sure it changes its
output based on some obstacle we place in front of it.

The test firmware is located in the `Distance/` folder.

### Ultrasonic distance sensor test procedure

The operator connects a sensor to `S2`. The sensor points towards the ceiling.
The operator then covers the sensor's transducers with their hand, and observes that on
the LED ring no LEDs are lit. Then the operator distances their hand from the sensor
and observes that the farther their hand is, the more LEDs are lit.

- Passing: when the sensor is covered, the LED ring displays 0 or 1 lit LEDs. When fully uncovered,
  the LED ring has all 12 LEDs lit. When the operator moves their hand up and down in front of the
  sensor, the number of lit LEDs changes.
- Failure:
  - The LED ring has more than one lit LED when the sensor is fully covered.
  - The LED ring has unlit LEDs when the sensor is fully uncovered.
  - The number of lit LEDs does not follow the distance of the operator's hand.

### Color sensor

The test firmware is located in the `Color/` folder.

**Color sensor test procedure**

The operator connects a color sensor to `S3`. The operator places the sensor on different colored
surfaces. The operator makes sure all 4 windows of the sensor are above a single color (for example,
all see the color red), and observes the colors displayed on the LED ring.

- Passing: the LED ring displays the same color on all LEDs.
- Failure: the LED ring displays different color LEDs.
