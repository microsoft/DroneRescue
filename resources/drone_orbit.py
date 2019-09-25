import airsim

import os
import sys
import math
import time
import argparse
from PIL import Image


class Position:
    def __init__(self, pos):
        self.x = pos.x_val
        self.y = pos.y_val
        self.z = pos.z_val

# Make the drone fly in a circle.


class OrbitNavigator:
    def __init__(self, photo_prefix="photo_", radius=2, altitude=10, speed=2, iterations=1, center=[1, 0], snapshots=None, image_dir="./images/"):
        self.radius = radius
        self.altitude = altitude
        self.speed = speed
        self.iterations = iterations
        self.snapshots = snapshots
        self.snapshot_delta = None
        self.next_snapshot = None
        self.image_dir = image_dir
        self.z = None
        self.snapshot_index = 0
        self.photo_prefix = photo_prefix
        self.takeoff = True  # whether we did a take off

        if self.snapshots is not None and self.snapshots > 0:
            self.snapshot_delta = 360 / self.snapshots

        if self.iterations <= 0:
            self.iterations = 1

        if len(center) != 2:
            raise Exception(
                "Expecting '[x,y]' for the center direction vector")

        # center is just a direction vector, so normalize it to compute the actual cx,cy locations.
        cx = float(center[0])
        cy = float(center[1])
        length = math.sqrt(cx*cx)+(cy*cy)
        cx /= length
        cy /= length
        cx *= self.radius
        cy *= self.radius

        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True)

        self.home = self.client.getMultirotorState().kinematics_estimated.position
        # check that our home position is stable
        start = time.time()
        count = 0
        while count < 100:
            pos = self.home
            if abs(pos.z_val - self.home.z_val) > 1:
                count = 0
                self.home = pos
                if time.time() - start > 10:
                    print(
                        "Drone position is drifting, we are waiting for it to settle down...")
                    start = time
            else:
                count += 1

        self.center = self.client.getMultirotorState().kinematics_estimated.position
        self.center.x_val += cx
        self.center.y_val += cy

    def start(self):
        print("arming the drone...")
        self.client.armDisarm(True)

        # AirSim uses NED coordinates so negative axis is up.
        start = self.client.getMultirotorState().kinematics_estimated.position
        landed = self.client.getMultirotorState().landed_state
        if not self.takeoff and landed == airsim.LandedState.Landed:
            self.takeoff = True
            print("taking off...")
            self.client.takeoffAsync().join()
            start = self.client.getMultirotorState().kinematics_estimated.position
            z = -self.altitude + self.home.z_val
        else:
            print("already flying so we will orbit at current altitude {}".format(
                start.z_val))
            z = start.z_val  # use current altitude then

        print("climbing to position: {},{},{}".format(
            start.x_val, start.y_val, z))
        self.client.moveToPositionAsync(
            start.x_val, start.y_val, z, self.speed).join()
        self.z = z

        print("ramping up to speed...")
        count = 0
        self.start_angle = None
        self.next_snapshot = None

        # ramp up time
        ramptime = self.radius / 10
        self.start_time = time.time()

        while count < self.iterations and self.snapshot_index < self.snapshots:
            # ramp up to full speed in smooth increments so we don't start too aggressively.
            now = time.time()
            speed = self.speed
            diff = now - self.start_time
            if diff < ramptime:
                speed = self.speed * diff / ramptime
            elif ramptime > 0:
                print("reached full speed...")
                ramptime = 0

            lookahead_angle = speed / self.radius

            # compute current angle
            pos = self.client.getMultirotorState().kinematics_estimated.position
            dx = pos.x_val - self.center.x_val
            dy = pos.y_val - self.center.y_val
            actual_radius = math.sqrt((dx*dx) + (dy*dy))
            angle_to_center = math.atan2(dy, dx)

            camera_heading = (angle_to_center - math.pi) * 180 / math.pi

            # compute lookahead
            lookahead_x = self.center.x_val + self.radius * \
                math.cos(angle_to_center + lookahead_angle)
            lookahead_y = self.center.y_val + self.radius * \
                math.sin(angle_to_center + lookahead_angle)

            vx = lookahead_x - pos.x_val
            vy = lookahead_y - pos.y_val

            if self.track_orbits(angle_to_center * 180 / math.pi):
                count += 1
                print("completed {} orbits".format(count))

            self.camera_heading = camera_heading
            self.client.moveByVelocityZAsync(
                vx, vy, z, 1, airsim.DrivetrainType.MaxDegreeOfFreedom, airsim.YawMode(False, camera_heading))

        self.client.moveToPositionAsync(start.x_val, start.y_val, z, 2).join()

    def track_orbits(self, angle):
        # tracking # of completed orbits is surprisingly tricky to get right in order to handle random wobbles
        # about the starting point.  So we watch for complete 1/2 orbits to avoid that problem.
        if angle < 0:
            angle += 360

        if self.start_angle is None:
            self.start_angle = angle
            if self.snapshot_delta:
                self.next_snapshot = angle + self.snapshot_delta
            self.previous_angle = angle
            self.shifted = False
            self.previous_sign = None
            self.previous_diff = None
            self.quarter = False
            return False

        # now we just have to watch for a smooth crossing from negative diff to positive diff
        if self.previous_angle is None:
            self.previous_angle = angle
            return False

        # ignore the click over from 360 back to 0
        if self.previous_angle > 350 and angle < 20:
            if self.snapshot_delta and self.next_snapshot >= 360:
                self.next_snapshot -= 360
            return False

        diff = self.previous_angle - angle
        crossing = False
        self.previous_angle = angle

        if self.snapshot_delta and angle > self.next_snapshot:
            print("Taking snapshot at angle {}".format(angle))
            self.take_snapshot()
            self.next_snapshot += self.snapshot_delta

        diff = abs(angle - self.start_angle)
        if diff > 45:
            self.quarter = True

        if self.quarter and self.previous_diff is not None and diff != self.previous_diff:
            # watch direction this diff is moving if it switches from shrinking to growing
            # then we passed the starting point.
            direction = self.sign(self.previous_diff - diff)
            if self.previous_sign is None:
                self.previous_sign = direction
            elif self.previous_sign > 0 and direction < 0:
                if diff < 45:
                    self.quarter = False
                    if self.snapshots <= self.snapshot_index + 1:
                        crossing = True
            self.previous_sign = direction
        self.previous_diff = diff

        return crossing

    def take_snapshot(self):
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

        # first hold our current position so drone doesn't try and keep flying while we take the picture.
        pos = self.client.getMultirotorState().kinematics_estimated.position
        self.client.moveToPositionAsync(pos.x_val, pos.y_val, self.z, 0.25, 3, airsim.DrivetrainType.MaxDegreeOfFreedom,
                                        airsim.YawMode(False, self.camera_heading))
        responses = self.client.simGetImages([airsim.ImageRequest(
            0, airsim.ImageType.Scene)])  # scene vision image in png format
        response = responses[0]
        filename = self.photo_prefix + \
            str(self.snapshot_index) + "_" + str(int(time.time()))
        self.snapshot_index += 1
        airsim.write_file(os.path.normpath(
            self.image_dir + filename + '.png'), response.image_data_uint8)
        print("Saved snapshot: {}".format(filename))
        # cause smooth ramp up to happen again after photo is taken.
        self.start_time = time.time()

    def sign(self, s):
        if s < 0:
            return -1
        return 1


if __name__ == "__main__":
    args = sys.argv
    args.pop(0)
    arg_parser = argparse.ArgumentParser(
        "Orbit.py makes drone fly in a circle with camera pointed at the given center vector")
    arg_parser.add_argument("--radius", type=float,
                            help="radius of the orbit", default=10)
    arg_parser.add_argument("--altitude", type=float,
                            help="altitude of orbit (in positive meters)", default=20)
    arg_parser.add_argument("--speed", type=float,
                            help="speed of orbit (in meters/second)", default=3)
    arg_parser.add_argument(
        "--center", help="x,y direction vector pointing to center of orbit from current starting position (default 1,0)", default="1,0")
    arg_parser.add_argument("--iterations", type=float,
                            help="number of 360 degree orbits (default 3)", default=3)
    arg_parser.add_argument("--snapshots", type=float,
                            help="number of FPV snapshots to take during orbit (default 0)", default=0)
    args = arg_parser.parse_args(args)
    nav = OrbitNavigator(args.radius, args.altitude, args.speed,
                         args.iterations, args.center.split(','), args.snapshots)
    nav.start()
