# Space Station Saver
For CHRI Assignment 3, TU Delft MSC Robotics

© 2025 Adomas Grigolis, Sem Traas and Hua Jiang. All rights reserved.  
This project is licensed under the MIT license. See the [LICENSE](./LICENSE) file for details.  

## What it is
The codebase is both a fun little online/co-op game and an experiment to test user experience interacting with haptic devices that can provide force feedback to the user from virtual environment. It is also a platform to develop collaborative haptic interface enabled experiments.  

## The game
The objective of the game is to move the asteroid and keep over the black hole to get rid of it. If, however, the pressure is applied on the asteroid for too long, it will be crushed and you will fail. This will cause space catastrophe as you will make a bunch of space dust. In this game, you have to collaboratively work with your colleagues to save space stations.

## Feedback
When playing the game with a mouse, you will see a force indicator on the left-top corner of the screen. When using a haptic device, you will feel the impact with the asteroid.  

## How to run
Required packages can be installed with:

    pip install -r requirements.txt

We recommend to do this in a virtual environment.  
### On a terminal
You will need three terminals. Note that `PYTHONPATH` must be set as the workspace. This can be done in multiple ways, however, easiest one on Linux is running these commands on the project workspace:  

    PYTHONPATH=$(pwd) python src/server.py
    PYTHONPATH=$(pwd) python src/client.py

The server must be started first, otherwise the clients will not connect. The client command needs to be run twice to start two clients.  
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
### Repeat the statistical analysis
Simply run the [data_analysis.py](data_analysis/data_analysis.py) script, which will generate plots in [data](/data/) and report statistics on the terminal.  

    PYTHONPATH=$(pwd) python data_analysis/data_analysis.py

Data structure:  

data/  
├── questionnaires.xlsx  
├── success_rate.csv  
├── times.csv  
├── trials.csv  
├── plot1.png  
└── ...  

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
- It is easier* for participants to grasp objects using force enabled haptic interface. (Q2)**  
- The environment will be experienced as more real with the haptic device. (WDQ 3)  
- Participants will feel higher stress with haptic device (NASA-TLX).  
- The haptic device will score higher on task autonomy and task significance compared to the mouse. (WDQ 1)  
- The haptic device will lead to higher physical demand but a greater sense of task engagement than the mouse. (WDQ 3, NASA-TLX)  
- Effects* of the haptic interface are more substantial when objects are more difficult to grasp. (See: Future work)  

\* Effects, performance are defined by both task completion speed (quantitative) and perceived task difficulty (qualitative). Perceived task difficulty is measured by questions on the form.  
** Q1 was removed as some participants forgot to answer the question.

### Quantitative
- Task completion will be faster with the haptic device.  
- The completion time will have higher downwards trend (learning curve) across trials for the haptic condition.

### Statistical tests
Paired samples t-test and Wilcoxon signed-rank test were used extensively. p_value threshold is chosen to be 0.10, which is typical for exploratory studies such as ours.  
To be completely transparent, we cannot use low p_value such as 0.05 found in most literature as the number of participants is not large enough. Please refer to the data for final count of participants.  
The study is within-subjects to increase statistical power. Counterbalancing was used to decrease carry-over effects.  

### Future work
Due to time constraints and small participant numbers, the following things could not be implemented or tested.  

The following variations in task difficulty have been discussed:  
- Object shape: ball, square, other polygons...  
- Object properties: friction, elasticity.  
- Haptic gain.  
- Random perturbations.  
