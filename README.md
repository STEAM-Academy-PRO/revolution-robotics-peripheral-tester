What are these?
===============

In the factory, we want to make sure each peripheral work as we expect. To do this, we prepare
a few Revvy brains to act as dedicated testers. Each of the brains have different SD card images,
and test different peripherals.

Writing tests
-------------

The test firmware is a modified version of the production pi firmware. The test code can be found
in `<folder>/revvy.py`. The actual test configuration and logic is inside the `with ProgrammedRobotController(robot_manager) as robot_controller:` block in this file.

### Sensors

To configure a sensor, add a `config.add_sensor_from_json` line to the configuration. The number of
`add_sensor_from_json` determines the position of the sensor port. The parameter is either a port
type and port name pair, or `None` to skip a particular port.

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

To configure a motor, add a `config.add_motor_from_json` line to the configuration. The rules are
similar to sensors: `None` to skip a port, type and name to configure one.

For the purposes of peripheral testing, it is enough to know that motors need to be configured with
type `1`.

The name of a sensor or motor will be used in the test logic to interact with them.

### Test logic

Test logic is implemented as a button-triggered test script, in the framework we use for automated testing.
The simplest way to develop a script is to use the mobile app's coding screen and its Run feature.
Create the script that does what you want it to, then copy the script to the interface at https://test.rr.scapps.io/desktop.html.
You can then paste the resulting python code into the test package, with added boilerplate to properly
hook the script up into the configuration.
For example, the button testing script looks as follows:

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

Motor
-----

The motors contain an encoder that we use to measure their rotation. We use this information for
both position and speed control.

The test firmware is located in the `Motor/` folder.

### Motor test procedure

The operator connects a motor to `M1`. The firmware will drive the motor at a low speed. The brain
checks whether the motor behaves as expected and displays a green LED ring if the motor is
considered working. If no motor is connected, or if the motor misbehaves, the LED ring will be red.

- Passing: after connecting the motor and letting the test run for 3 seconds, the LED ring
  shall display `green`.
- Failure: if, after waiting for 3 seconds the LED ring does NOT display `green`, the motor is faulty.

Button
------

The button is a simple digital input. The test makes sure we can detect that they are pressed.

The test firmware is located in the `Button/` folder.

### Button test procedure

The operator connects a button to `S1`. The operator then presses the button a few times.

- Passing: when the button is pressed, the LED ring shall display `green`. When the button is NOT
  pressed, the LED ring shall display `red`.
- Failure:
  - The LED ring does not display `green` when the operator presses the button.
  - The LED ring does not display `red` when the operator does NOT press the button.

Ultrasonic distance sensor
--------------------------

The ultrasonic sensor is a complex piece of digital electronics. We need to make sure it changes its
output based on some obstacle we place in front of it.

The test firmware is located in the `Distance/` folder.

### Ultrasonic distance sensor test procedure

The operator connects a sensor to `S2`. The sensor points towards the ceiling.
The operator then covers the sensor's transducers with their hand, and observes that on
the LED ring no LEDs are lit. Then the operator distances their hand from the sensor
and observes that the farther their hand is, the more LEDs are lit.

- Passing: when the sensor is covered, the LED ring displays 0 lit LEDs. When fully uncovered, the
  LED ring has all 12 LEDs lit. When the operator moves their hand up and down in front of the sensor,
  the number of lit LEDs changes.
- Failure:
  - The LED ring has lit LEDs when the sensor is fully covered.
  - The LED ring has unlit LEDs when the sensor is fully uncovered.
  - The number of lit LEDs does not follow the distance of the operator's hand.

Color sensor
------------

The test firmware is located in the `Color/` folder.

### Color sensor test procedure

The operator connects a color sensor to `S3`. The operator places the sensor on different colored
surfaces. The operator makes sure all 4 windows of the sensor are above a single color (for example,
all see the color red), and observes the colors displayed on the LED ring.

- Passing: the LED ring displays the same color on all LEDs.
- Failure: the LED ring displays different color LEDs.
