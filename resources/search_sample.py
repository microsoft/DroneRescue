import setup_path 
import airsim

import drone_orbit
import os
import time
import math
from PIL import Image

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

landed = client.getMultirotorState().landed_state

if landed == airsim.LandedState.Landed:
    print("taking off...")
    pos = client.getMultirotorState().kinematics_estimated.position
    z = pos.z_val - 1
    client.takeoffAsync().join()
else:
    print("already flying...")
    client.hover()
    pos = client.getMultirotorState().kinematics_estimated.position
    z = pos.z_val

image_dir = "./images/"

def OrbitAnimal(cx, cy, radius, speed, altitude, camera_angle, animal):
    """
    @param cx: The x position of our orbit starting location
    @param cy: The x position of our orbit starting location
    @param radius: The radius of the orbit circle
    @param speed: The speed the drone should more, it's hard to take photos when flying fast
    @param altitude: The altidude we want to fly at, dont fly too high!
    @param camera_angle: The angle of the camera
    @param animal: The name of the animal, used to prefix the photos
    """
    x = cx - radius
    y = cy

    # set camera angle
    client.simSetCameraOrientation(0, airsim.to_quaternion(camera_angle * math.pi / 180, 0, 0)); #radians

    # move the drone to the requested location
    print("moving to position...")
    client.moveToPositionAsync(x, y, z, 1, 60, drivetrain = airsim.DrivetrainType.MaxDegreeOfFreedom, yaw_mode = airsim.YawMode(False, 0)).join()
    pos = client.getMultirotorState().kinematics_estimated.position
    
    dx = x - pos.x_val
    dy = y - pos.y_val
    yaw = airsim.to_eularian_angles(client.getMultirotorState().kinematics_estimated.orientation)[2]

    # keep the drone on target, it's windy out there!
    print("correcting position and yaw...")
    while abs(dx) > 1 or abs(dy) > 1 or abs(yaw) > 0.1:
        client.moveToPositionAsync(x, y, z, 0.25, 60, drivetrain = airsim.DrivetrainType.MaxDegreeOfFreedom, yaw_mode = airsim.YawMode(False, 0)).join()
        pos = client.getMultirotorState().kinematics_estimated.position
        dx = x - pos.x_val
        dy = y - pos.y_val
        yaw = airsim.to_eularian_angles(client.getMultirotorState().kinematics_estimated.orientation)[2]
        print("yaw is {}".format(yaw))

    print("location is off by {},{}".format(dx, dy))

    o = airsim.to_eularian_angles(client.getMultirotorState().kinematics_estimated.orientation)
    print("yaw is {}".format(o[2]))

    # let's orbit around the animal and take some photos
    nav = drone_orbit.OrbitNavigator(photo_prefix = animal, radius = radius, altitude = altitude, speed = speed, iterations = 1, center = [cx - pos.x_val, cy - pos.y_val], snapshots = 30)
    nav.start()

    # that's enough fun for now. let's quit cleanly
    land()

def land():
    print("landing...")
    client.landAsync().join()

    print("disarming.")
    client.armDisarm(False)

    client.reset()
    client.enableApiControl(False)

def CropImages():
    width=800
    height=800

    os.chdir(image_dir)

    directory = os.fsencode("./")
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".png"):
            img = Image.open(filename)
            print("Image Size ({},{})".format(img.size[0], img.size[1]))
            middle = ((img.size[0] / 2), (img.size[1] / 2))
            img_x_offset = middle[0] - (width / 2)
            img_y_offset = middle[1] - (height / 2)
            print("Image Offset ({},{})".format(img_x_offset, img_y_offset))
            print("New Size ({},{})".format(img_x_offset + width, img_y_offset + height))
            
            box = (img_x_offset, img_y_offset, img_x_offset + width, img_y_offset + height)

            cropped_image = img.crop(box)
            cropped_image.save(filename, "PNG")

            continue

if __name__ == '__main__':
    animals = [(5.42, -3.7, "AlpacaTeal")]

    # let's find the animals and take some photos
    for pos in animals:
        print(pos[2])
        OrbitAnimal(pos[0], pos[1], 2, 0.4, 1, -30, pos[2])


    print("Image capture complete...")