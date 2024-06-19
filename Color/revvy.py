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
        config.add_sensor_from_json(None)
        config.add_sensor_from_json(None)
        config.add_sensor_from_json({"type": 4, "name": "color_sensor"})
        config.process_script(
            {
                "assignments": {"buttons": [{"id": 1, "priority": 0}]},
                "pythonCode": b64_encode_str(
                    """import time


while True:
  robot.led.set(leds=[12], color=(robot.read_color(1)))
  robot.led.set(leds=[1], color=(robot.read_color(1)))
  robot.led.set(leds=[2], color=(robot.read_color(1)))
  robot.led.set(leds=[3], color=(robot.read_color(2)))
  robot.led.set(leds=[4], color=(robot.read_color(2)))
  robot.led.set(leds=[5], color=(robot.read_color(2)))
  robot.led.set(leds=[6], color=(robot.read_color(4)))
  robot.led.set(leds=[7], color=(robot.read_color(4)))
  robot.led.set(leds=[8], color=(robot.read_color(4)))
  robot.led.set(leds=[9], color=(robot.read_color(3)))
  robot.led.set(leds=[10], color=(robot.read_color(3)))
  robot.led.set(leds=[11], color=(robot.read_color(3)))
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
