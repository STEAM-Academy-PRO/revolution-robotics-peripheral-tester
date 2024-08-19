#!/usr/bin/python3

import sys
from revvy.firmware_updater import update_firmware_if_needed

from revvy.hardware_dependent.rrrc_transport_i2c import RevvyTransportI2C
from revvy.robot_config import RobotConfig
from revvy.robot_manager import RobotManager, RevvyStatusCode
from revvy.api.programmed import ProgrammedRobotController

from revvy.utils.functions import b64_encode_str
from revvy.utils.logger import get_logger
from revvy.utils.directories import CURRENT_INSTALLATION_PATH
from revvy.utils.check_manifest import check_manifest

# Load the error reporter and init the singleton that'll catch system errors.
from revvy.utils.error_reporter import revvy_error_handler

log = get_logger("revvy.py")

if __name__ == "__main__":
    revvy_error_handler.register_uncaught_exception_handler()

    log(f"pack: {CURRENT_INSTALLATION_PATH}")
    log(f"file: {__file__}")

    # Check SW version package. If the manifest file is broken, do not launch!
    if not check_manifest("manifest.json"):
        log("Revvy not started because manifest is invalid")
        sys.exit(RevvyStatusCode.INTEGRITY_ERROR)

    interface = RevvyTransportI2C(bus=1)

    ### Before we enter the main loop, let's load up
    if not update_firmware_if_needed(interface):
        log("Revvy not started because the robot has no functional firmware")
        # exiting with integrity error forces the loader to try a previous package
        sys.exit(RevvyStatusCode.INTEGRITY_ERROR)

    # Handles robot state
    robot_manager = RobotManager(interface)

    # Receives commands from the control interface, acts on the robot_manager.

    with ProgrammedRobotController(robot_manager) as robot_controller:
        config = RobotConfig()
        config.add_motor_from_json({"type": 1, "name": "motor1"})
        config.add_motor_from_json({"type": 1, "name": "motor2"})
        config.add_motor_from_json({"type": 1, "name": "motor3"})
        config.add_motor_from_json({"type": 1, "name": "motor4"})
        config.add_motor_from_json({"type": 1, "name": "motor5"})
        config.add_motor_from_json({"type": 1, "name": "motor6"})
        config.process_script(
            {
                "assignments": {"buttons": [{"id": 1, "priority": 0}]},
                "pythonCode": b64_encode_str(
                    """import time

robot.led.set(leds=[1,2,3,4,5,6,7,8,9,10,11,12], color='#ffcc00')
while True:
  robot.motors["motor1"].spin(direction=Motor.DIRECTION_FWD, rotation=30, unit_rotation=Motor.UNIT_SPEED_RPM)
  robot.motors["motor2"].spin(direction=Motor.DIRECTION_FWD, rotation=85, unit_rotation=Motor.UNIT_SPEED_RPM)
  robot.motors["motor3"].spin(direction=Motor.DIRECTION_FWD, rotation=135, unit_rotation=Motor.UNIT_SPEED_RPM)  
  robot.motors["motor4"].spin(direction=Motor.DIRECTION_FWD, rotation=10, unit_rotation=Motor.UNIT_SPEED_RPM)
  robot.motors["motor5"].spin(direction=Motor.DIRECTION_FWD, rotation=75, unit_rotation=Motor.UNIT_SPEED_RPM)
  robot.motors["motor6"].spin(direction=Motor.DIRECTION_FWD, rotation=120, unit_rotation=Motor.UNIT_SPEED_RPM)  
  
  time.sleep(3)

  if (robot.motors["motor1"].speed >= 25) and (robot.motors["motor1"].speed <= 35):
    robot.led.set(leds=[1], color='#33cc00')
  else:
    robot.led.set(leds=[1], color='#ff0000')

  if (robot.motors["motor2"].speed >= 80) and (robot.motors["motor2"].speed <= 90):
    robot.led.set(leds=[3], color='#33cc00')
  else:
    robot.led.set(leds=[3], color='#ff0000')

  if (robot.motors["motor3"].speed >= 130) and (robot.motors["motor3"].speed <= 140):
    robot.led.set(leds=[5], color='#33cc00')
  else:
    robot.led.set(leds=[5], color='#ff0000')

  if (robot.motors["motor4"].speed >= 5) and (robot.motors["motor4"].speed <= 15):
    robot.led.set(leds=[11], color='#33cc00')
  else:
    robot.led.set(leds=[11], color='#ff0000')

  if (robot.motors["motor5"].speed >= 70) and (robot.motors["motor5"].speed <= 80):
    robot.led.set(leds=[9], color='#33cc00')
  else:
    robot.led.set(leds=[9], color='#ff0000')

  if (robot.motors["motor6"].speed >= 115) and (robot.motors["motor6"].speed <= 125):
    robot.led.set(leds=[7], color='#33cc00')
  else:
    robot.led.set(leds=[7], color='#ff0000')

  time.sleep(1)
  
  robot.motors["motor1"].spin(direction=Motor.DIRECTION_BACK, rotation=30, unit_rotation=Motor.UNIT_SPEED_RPM)
  robot.motors["motor2"].spin(direction=Motor.DIRECTION_BACK, rotation=85, unit_rotation=Motor.UNIT_SPEED_RPM)
  robot.motors["motor3"].spin(direction=Motor.DIRECTION_BACK, rotation=135, unit_rotation=Motor.UNIT_SPEED_RPM)
  robot.motors["motor4"].spin(direction=Motor.DIRECTION_BACK, rotation=10, unit_rotation=Motor.UNIT_SPEED_RPM)
  robot.motors["motor5"].spin(direction=Motor.DIRECTION_BACK, rotation=75, unit_rotation=Motor.UNIT_SPEED_RPM)
  robot.motors["motor6"].spin(direction=Motor.DIRECTION_BACK, rotation=120, unit_rotation=Motor.UNIT_SPEED_RPM)

  time.sleep(3)

  if (robot.motors["motor1"].speed >= -35) and (robot.motors["motor1"].speed <= -25):
    robot.led.set(leds=[2], color='#33cc00')
  else:
    robot.led.set(leds=[2], color='#ff0000')

  if (robot.motors["motor2"].speed >= -90) and (robot.motors["motor2"].speed <= -80):
    robot.led.set(leds=[4], color='#33cc00')
  else:
    robot.led.set(leds=[4], color='#ff0000')

  if (robot.motors["motor3"].speed >= -140) and (robot.motors["motor3"].speed <= -130):
    robot.led.set(leds=[6], color='#33cc00')
  else:
    robot.led.set(leds=[6], color='#ff0000')

  if (robot.motors["motor4"].speed >= -15) and (robot.motors["motor4"].speed <= -5):
    robot.led.set(leds=[12], color='#33cc00')
  else:
    robot.led.set(leds=[12], color='#ff0000')

  if (robot.motors["motor5"].speed >= -80) and (robot.motors["motor5"].speed <= -70):
    robot.led.set(leds=[10], color='#33cc00')
  else:
    robot.led.set(leds=[10], color='#ff0000')

  if (robot.motors["motor6"].speed >= -125) and (robot.motors["motor6"].speed <= -115):
    robot.led.set(leds=[8], color='#33cc00')
  else:
    robot.led.set(leds=[8], color='#ff0000')

  time.sleep(0.05)  # allow other threads to run

"""
                ),
            },
            0,
        )

        robot_controller.configure(config)
        robot_controller.press_button(1)

        robot_controller.wait_for_scripts_to_end()
    # manual exit
    ret_val = RevvyStatusCode.OK

    log("terminated")
    sys.exit(ret_val)
