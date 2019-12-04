#!/usr/bin/python

import sys
import os

import threading
from threading import Thread
import time
import signal
import subprocess

airsimprocess = subprocess.Popen(["/home/nvagent/Blocks/Blocks.sh"])

exit_flag = False

def exit_properly_runtime_test():
    global exit_flag
    
    print("CREATING SUCCESS RESULT FILE")
   
    print("CREATING SUCCESS RESULT FILE")
    f = open("result.txt", "w")
    f.write("0")
    f.close()

    exit_flag = True
    airsimprocess.kill()
    airsimprocess.wait()
    time.sleep(10)
    print("EXITING")
    
    sys.exit(0)

#timeout countdown
def start_countdown(seconds):
    def timeout_countdown(seconds):
        global exit_flag
        time.sleep(seconds)
        print("COUNTDOWN ERROR RUNTIME TEST")
        exit_flag = True
        sys.exit(1)
        
    t= Thread(target = lambda: timeout_countdown(seconds))
    t.start()

start_countdown(320)

#-------------------------------------------------------------------
#-------------------------------------------------------------------
# launch countdown

print ("HELLO WORLD. Waiting 30 seconds to server...")
time.sleep(30)

import airsim

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

client.reset()
client.enableApiControl(False)


print("taking off...")
pos = client.getMultirotorState().kinematics_estimated.position
client.takeoffAsync().join()
print("taking off DONE")
time.sleep(1)
print("going to z=10")

client.moveToPositionAsync(0, 0, 10, 0.25, 60, drivetrain=airsim.DrivetrainType.MaxDegreeOfFreedom, yaw_mode=airsim.YawMode(False, 0)).join()

print("DONE")

pos = client.getMultirotorState().kinematics_estimated.position
if pos.z_val > 1:
    exit_properly_runtime_test()
else:
    print("DID NOT TAKE OFF. TEST NOT PASSED.")
    airsimprocess.kill()
    airsimprocess.wait()
    sys.exit(1)