# Space Station Saver
For CHRI Assignment 3, TU Delft MSC Robotics

© 2025 Adomas Grigolis, Sem Traas and Hua Jiang. All rights reserved.  
This project is licensed under the MIT license. See the [LICENSE](./LICENSE) file for details.  

## What it is
The codebase is both a fun little online/coop game and an experiment to test user experience interacting with haptic devices that can provide force feedback to the user from virtual environment. It is also a platform to develop collaborative haptic interface enabled experiments.  

## The game
The objective of the game is to move the asteroid and keep over the black hole for three seconds. If, however, the pressure is applied to the asteroid for too long, it will be crushed and you will fail. This will cause space catastrophe as you will make a bunch of space dust. In this game, you have to collaboratively work with your colleagues to save space stations.

## How to run
Required packages can be installed with:

    pip install -r requirements.txt

We recommend to do this in a virtual environment.  
### On a terminal
You will need three terminals. Note that `PYTHONPATH` must be set as the workspace. This can be done in multiple ways, however, easiest one on Linux is running these commands on the project workspace:  

    PYTHONPATH=$(pwd) python src/server.py
    PYTHONPATH=$(pwd) python src/client.py

The client command needs to be run twice to start two clients.
### In VS Code
Start 'server.py' with 'Run python file in a dedicated terminal'. Then, do the same for 'client.py'. Note that in vscode the local environment also needs to have `PYTHONPATH` set as workspace. This is platform dependent, however, on Linux this can be done with the following line in .env file (sometimes VS Code needs to be restarted for this to take effect):  

    PYTHONPATH=${PYTHONPATH}:${workspaceFolder}

Because VS Code will not let you run the same file twice and will instead restart the terminal, open another new terminal by clicking + icon. Run command `python src/client.py`.
### Two mice on local setup
The experimental setup requires one of the following:  
1. One mouse and one haptic device. The mouse can control Client 2 and the haptic device - Client 1.  
2. Two mice.  

To have two mice and two cursors, on Windows [MouseMux](https://www.mousemux.com/) application was used. On Linux, there is a feature on many distros called [xinput](https://stackoverflow.com/questions/4012352/linux-dual-mice-multiple-mice-with-multiple-mouse-pointers). Note that to make this work in Ubuntu, user needs to be logged-in in `xorg` mode by following these steps:  
1. Log Out  
2. Click on the user  
3. On bottom-right corner, click on Settings ⚙️  
4. Select xorg  
5. Login as normal  

### Running remotely
If you have both devices on the same network (for example connected by a cable) then there likely is no setup needed. One will simply need to change the ip address of the server to network ip in [setting.json](/config/settings.json). If there are some security settings, they can quite easily be changed in firewall settings. On Linux, useful tools are `socat` and `iptables`.  
If, however, you want to run online, then you will need to allow port forwarding. Please refer to online sources on how to do this.  
**Note that port forwarding online can be risky and we give no guarantees as per LICENSE.**  
## Technical Details
### Engines
PyGame - game simulation and rendering  
PyMunk - 2D physics engine  
sockets - networking library  
[physics.py](/utils/physics.py) and [HaplyHAPI.py](utils/HaplyHAPI.py) - provided by course for Haply device interface.  
### Software
[Arduino IDE](https://www.arduino.cc/) - haptic device drivers  
[MouseMux](https://www.mousemux.com/) - two mice cursors on Windows

## Experiments
The following condenses what kinds of experiments will be run with the application.  
The main subject of the experiment is visual force feedback versus haptic force feedback. Furthermore, the effect of increased task difficulty will be evaluated between haptic vs no haptic and across trials.  

### Qualitative
Qualitative experiments are common in HRI since humans are naturally difficult to quantify. It is, hence, often more meaningful to find data trends in relative measures rather than absolute. The following **qualitative** hypotheses will be tested:  
- It is easier* for participants to grasp objects using force enabled haptic interface.  
- Effects* of the haptic interface are more substantial when objects are more difficult to grasp. (Future work)  
- The environment will be experienced as more real with the haptic device. WDQ 3  
- Participants will feel higher stress with haptic device (NASA TLX).  
- The haptic device will score higher on task autonomy and task significance compared to the mouse. (WDQ 1)  
- The haptic device will lead to higher physical demand but a greater sense of task engagement than the mouse. (WDQ 3, NASA-TLX)  

\* Effects, performance are defined by both task completion speed and perceived task difficulty. Perceived task difficulty is measured by a variant of Godspeed Questionnaire Series (GQS).  

### Quantitative
- Task completion will be faster with the haptic device.  
- The object grasping difficulty will be less steep with haptic device than with the mouse.  

### Task difficulty
The following variations in task difficulty will be tested:  
- Object shape: ball, square, other polygon...
- Object properties: friction, elasticity.
- Random perturbations.
### Statistical tests
We will use the following statistical tests:  
- Task time mouse vs haptic: paired samples t-test  
- Difficulty levels, task time and errors: ANOVA  
- Subjective ratings: Wilcoxon Signed-Rank Test  
- Feedback gain and realism: Pearson correlation
