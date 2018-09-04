# Search and Rescue Lab - Microsoft AirSim and Custom Vision

## Overview
The goal of this lab is to work through how to bring real AI to the edge, by creating a custom vision model. Your mission, should you chose to accept it, is to work through the guided steps below and be able to export a working model from Custom Vision in TensorFlow format that can be run on an edge device.

The flow of the lab consists of the following steps:
1. Use AirSim to generate training data for your model by flying the virtual drone around the 3D-rendered environment and collecting images of all of the animals. 

2. Import the images and tag them into a new Custom Vision project, then use the training images to train and test the model.

3. Export the model into TensorFlow format.

---

### Create an Azure Virtual Machine 

> You can skip this step if you have your own laptop or desktop that has a GPU and supports DirectX 11

We are going to create a new Azure virtual machine utilizing GPUs. If you don't have a Microsoft Azure subscription you can create a trial account at https://azure.microsoft.com


1. Login to the Microsoft Azure portal https://portal.azure.com

2. Click **Create a resource** then search for and select **Windows Server 2016 VM** 

![drone-1](images/drone-1.png?raw=true "Title")

3. On the **Create virtual machine** slice complete the **Basics** mandatory options ensuring to select **HDD** for **VM disk type** and one of the supported regions for **NV-series**. You can find NV-series supported regions here https://azure.microsoft.com/global-infrastructure/services. Click **OK** to continue

![drone-2](images/drone-2.png?raw=true "Title")

4. On the **Size** slice change the compute type to **GPU**, select **NV6** and click **Select**

![drone-3](images/drone-3.png?raw=true "Title")

5. Review the **Settings** and complete the mandatory fields, click **OK** to continue

![drone-4](images/drone-4.png?raw=true "Title")

6. Review the **Summary** slice and click **Create** to continue

![drone-5](images/drone-5.png?raw=true "Title")

7. Once the new virtual machine provisions click **Connect** then download and open the RDP file using **Microsoft Remote Desktop**

![drone-6](images/drone-6.png?raw=true "Title")

8. Next we will install the Nvidia drivers, download the **NV-series** driver from the [following site](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/n-series-driver-setup#nvidia-grid-drivers) and follow the instructions.

  > [!ALERT] On Azure NV VMs, a restart is required after driver installation.

---

### Install Python

> You can skip this step if you already have python 3 or higher installed

1. Open the following URL in a browser, you will need to install the **64-bit** version because we will run tensorflow later https://www.python.org/downloads/

2. Make sure to check **Add Python to PATH** and click **Install** 

3. Verify python 3 has been successfully installed by opening a command prompt and typing **python --version**. You should see the version number of your new python installation.

4. Verify pip has been installed by typing **pip --version**

---

### Install Required Packages
We need to install pillow, msgpackrpc, and numpy.
1. Open a command prompt and type **pip install pillow**

2. Type **pip install msgpack-rpc-python**

3. Type **pip install numpy**

---

### Install Microsoft Visual Studio Code

1. Open the following URL in a browser, click **Windows** and follow the installation instructions https://code.visualstudio.com/download you can accept all the installation defaults or customize.

---

### Install AirSim

Now we will install the latest version of AirSim from GitHub

1. Open the following URL in a browser https://github.com/Microsoft/AirSim

2. Select **Clone or download** then click **Download ZIP** to download the repository

3. Once the download completes, extract the contents of the ZIP file to `<your user home>\Documents\AirSim`.

4. Create a `settings.json` file in your **Documents\AirSim** folder and paste in the following AirSim settings:

```
{
  "SeeDocsAt": "https://github.com/Microsoft/AirSim/blob/master/docs/settings.md",
  "SettingsVersion": 1.2,
  "SimMode": "",
  "CameraDefaults": {
    "CaptureSettings": [
      {
        "ImageType": 0,
        "Width": 300,
        "Height": 300,
        "FOV_Degrees": 84,
        "TargetGamma": 2.0,
        "MotionBlurAmount": 1
      }
    ]
  }
}
```

---

### Install and Run Drone Rescue

Now we will install the drone rescue landscape from GitHub

1. Open the following URL in a browser `https://github.com/Microsoft/DroneRescue`.

2. Select **Clone or download** then click **Download ZIP** to download the repository

3. Once the download completes, extract the contents of the ZIP file 

4. Open the file explorer and navigate to the folder where you extracted DroneRescue

5. Double click **\Binaries\Win64\MSBuild2018.exe** to start our custom drone rescue landscape. Make sure to click **No** when prompted to use car simulation to start quadrotor simulation. NOTE: if you want to explore the area manually you can select **Yes** to drive a vehicle around, simply restart AirSim to change back to the drone.

6. If prompted to install Microsoft Visual C++ and DirectX, select **Yes** and follow the installation prompts. If you receive a message that Microsoft .NET 3.5 couldn't be installed you can ignore the message. Try running the drone rescue landscape again (see previous step).

> With the DroneRescue window in focus press **3** to open the drone camera window.

> If you lose your mouse, hit the **Windows** key to get it back.

---

### Capture Synthetic Images

In this step well will fly the drone around our 3D world and orbit each animal so we can take some photos. Ensure the custom drone rescue landscape world is running in AirSim as per the previous step, we ill connect to the running environment using Python.

1. Copy **search_sample.py** and **drone_orbit.py** from the extracted DroneRescue folder into the extracted **AirSim** folder **AirSim/PythonClient/multirotor/**

1. Using Visual Studio Code, open the **PythonClient** folder within the AirSim folder you extracted earlier. Click on **search_sample.py** you just copied to open the python script.

2. If prompted to install the Python Extension select **Install**, once installed, select **Relod** to activate the extension.

3. Select **View -> Command Palette** and type **Python:Select Interpreter**. You should see the directory you installed Python in earlier, select the directory location.

4. Select **Debug -> Start Without Debugging** then click **Python** to execute the **searh_sample.py** script.

5. Switch to the **DroneRescue** landscape you started earlier and observe the drone flying around the environment and orbiting one of the animals.

6. Wait until you see **Image capture complete** in the Visual Studio Code output windows and the drone return to the center of the landscape and land.

7. Inspect the images in the **Images** folder, you should see photo's of the black sheep.

> The animal should be in the center of the image as we are going to use them to build and train our Custom Vision model.

> If the drone stops responding, open **Task Manager** and end any **Soccer Field** or **DroneRescue** Unreal tasks.

---

### Create a Custom Vision Model

Now we will use the images we captured in the previous steps to build and train a Custom Vision Model.

1. Using Microsoft Edge, open the following URL in a browser and login using your MSA https://customvision.ai/

  > [!ALERT] Custom Vision doesn't support Internet Explorer.

2. Click **New Project** and name it **AirSim Animals**, select **General (compact)** domain and **Create Project**.

3. Now we are going to add the training images we captured from the AirSim search and rescue training environment. Select **Add images** then **Browse local files** and select all the images in the **Images** folder. Enter **BlackSheep** as your tag, click **+** to add the tag then select **Upload files**. Select **Done** once the images have uploaded successfully.

4. Upload and tag the images in the **TrainingImages** folder to your Custom Vision model.

5. Next, we will modify **search_sample.py** to locate our next animal and capture images. Return to Visual Studio Code and open **search_sample.py**. 

6. Nagivate to the bottom of the file and replace the **Blacksheep** location with the following animal location to the animals array to tell our drone where to locate the next animal:
`(-12.18, -13.56, "AlpacaRainbow")` 

7. Save **search_sample.py** and select **Debug -> Start Without Debugging** to execute the file. 

8. Upload and tag the **AlpacaRainbow** images from the **Images** folder into Custom Vision.

9. Now that we have uploaded and tagged two different animals, let's train the model and run a quick test to see how we're doing. Select **"Train"** to start our first training iteration. Once complete you will see the precision and recall for our tagged images, all going well you should see 100% across the board!

10.  Let's take a closer look at our training iteration, select **Training images** from the top navigation, then select **Iteration History** from the left hand navigation. Hover over the images to see the prediciton percentages, any images that have a red boarder could cause our model some trouble. Some common causes of bad images are when the animal is not centered or too small, or there are other objects in the image that shouldn't be there.

11.  Let's run a quick test using a real world photograph of our yellow alpaca and see what our newly trained model thinks about it. Select **Quick Test** then **Browse local files**, open the following file **DroneRescue\testimages\AlpacaRainbow.png**. If you have followed along so far you should see a probablility of 99.9% for the AlpacaRainbow. Now things get a little more interesting!

12. We don't know what angle or distance the real drone might fly over the lost animals, to help improve our chance of detection, let's add some more images to our dataset. To keep everything in order, move the previous images into another folder, in case we want to use them again later.

13. Our first image capture drone flew a 2 meter radius circle around the animal with the camera angle at 30-degrees. Let's capture some more images at a different radius and camera angle. Edit the following two line of code to move the drone to a 3 meter radius and a camera angle of 20-degrees: `OrbitAnimal(pos[0], pos[1], 3, 0.4, 1, -20, pos[2])`

14. Save **search_sample.py** and select **Debug -> Start Without Debugging** to execute the file. 

15. Return to **customvision.ai** and add the images as we did previously, tag the new images with **AlpacaRainbow**. Select **Done** once the images have uploaded successfully. 

16. Train the model with the new images and inspect the iteration results.

17. Well that's enough to get you on your way, go forth and search for the remaining animals. Remember the more images you add the better your model will perform. Train and test your model often, think of other interesting ways you could enhance your model, for example, fly low and close to the animals, try different heights, angles, and radius.

Just to keep things moving along, below are the coordinates where you can find the other animals... All of them except the unicorn. Add them to the `search_sample.py` file:

```
animals = [(19.8, -11, "AlpacaPink"),
        (5.42, -3.7, "AlpacaTeal"),
        (-12.18, -13.56, "AlpacaRainbow"),
        (19.6, 9.6, "BlackSheep"),
        (-1.9, -0.9, "Bunny"),
        (3.5, 9.4, "Chick"),
        (-13.2, -0.25, "Chipmunk"),
        (-6.55, 12.25, "Hippo")]
```

Also, comment the next line of code, we don't need to land until we have photographed all the animals:

```
    # that's enough fun for now. let's quit cleanly
    land()
```

To help you out we have provided one real world image of each animal to help refine the model. You can find the images in **TrainingImages** add these to your model with the correct tags.

---

### Finding the Unicorn

You're probably wondering how you're going to rescue the unicorn? Well, for this you'll need to find the unicorn's coordinates to provide to the script like all the animals above, and then add those images to the Custom Vision model as well. To find the coordinates of the unicorn, you'll need to switch into vehicle mode in AirSim and explore the area to locate the elusive unicorn. 

> You can press the **;** key to open the vehicle detail page that will show you your current position. 

Good luck!

---

### Exporting a Tensorflow Model

Once you are happy with your model you can export it in Tensorflow format.

1. In Custom Vision, select the **Performance** tab and then select **Export**. Choose **Android (Tensorflow)** as the platform then click **Export** and **Download**.

---

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
