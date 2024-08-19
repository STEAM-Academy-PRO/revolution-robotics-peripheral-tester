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
        config.add_sensor_from_json({"type": 1, "name": "distance_sensor"})
        config.process_script(
            {
                "assignments": {"buttons": [{"id": 1, "priority": 0}]},
                "pythonCode": b64_encode_str(
                    """import math
from numbers import Number
import time

var_variable1 = None
var_i = None


while True:
  var_variable1 = (robot.sensors["distance_sensor"].read()) / 3
  ReportVariableChanged("variable1",var_variable1)
  var_i = 0
  ReportVariableChanged("i",var_i)
  for count in range(int(round(var_variable1))):
    var_i = (var_i if isinstance(var_i, Number) else 0) + 1
    ReportVariableChanged("i",var_i)
    robot.led.set(leds=[(var_i % 12)], color='#009900')
  var_i = 12
  ReportVariableChanged("i",var_i)
  for count2 in range(int(12 - round(var_variable1))):
    robot.led.set(leds=[var_i], color='#000000')
    var_i = (var_i if isinstance(var_i, Number) else 0) + -1
    ReportVariableChanged("i",var_i)
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
