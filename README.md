# CHRI coop space game
CHRI Assignment 3

© 2025 Adomas Grigolis, Sem Traas and Hua Jiang. All rights reserved.  
This project is licensed under the MIT license. See the [LICENSE](./LICENSE) file for details.

## What it is
The codebase is both a fun little online/coop game and an experiment to test user experience interacting with haptic devices that can provide force feedback to the user from virtual environment.

## How to run
### On the same computer
You will need three terminals. If using VS Code, start 'server.py' with 'Run python file in a dedicated terminal'. Then, do the same for 'client.py'.  
Because VS Code will not let you run the same file twice and will instead restart the terminal, open another new terminal by clicking + icon. Run command `python src/client.py`. If your environment is setup correctly, it should pick up the file structure automatically.
### Running remotely
If you have both devices on the same network (for example connected by a cable) then there likely is no setup needed. If there are some security settings, they can quite easily be changed in firewall settings. Note that VS Code port forwarder does not support UDP by default. On Linux, useful tools are `socat` and `iptables`.  
If, however, you want to run online, then you will need to allow port forwarding. Please refer to online sources on how to do this.  
**Note that port forwarding online can be risky.**
## Technical Details
### Engines
PyGame - game simulation and rendering  
PyMunk - 2D physics engine  
sockets - networking library  

## Experiments
The following condenses what kinds of experiments will be run with the application.  
The main subject of the experiment is visual force feedback versus haptic force feedback. Furthermore, the effect of increased task difficulty will be evaluated between haptic vs no haptic and across trials.  

### Qualitative
Qualitative experiments are common in HRI since humans are naturally difficult to quantify. It is, hence, often more meaningful to find data trends in relative measures rather than absolute. The following **qualitative** hypotheses will be tested:  
- It is easier* for participants to grasp objects using force enabled haptic interface.  
- Effects* of the haptic interface are more substantial when objects are more difficult to grasp.  
- The environment will be experienced as more real with higher feedback gains. (How real question)  
- Participants will feel higher stress with haptic device (NASA TLX).  
- The haptic device will score higher on task autonomy and task significance compared to the mouse. (WDQ)  
- The haptic device will lead to higher physical demand but a greater sense of task engagement than the mouse. (WDQ)  

\* Effects, performance are defined by both task completion speed and perceived task difficulty. Perceived task difficulty is measured by a variant of Godspeed Questionnaire Series (GQS).  

### Quantitative
- The participants will loose the object with haptic interface less (fewer errors) than with mouse interface.  
- Task completion will be faster with the haptic device.  
- The object grasping difficulty will be less steep with haptic device than with the mouse.  

### Task difficulty
The following variations in task difficulty will be tested:  
- Object shape: ball, square, other polygon...
- Object properties: friction, elasticity.
- Random perturbations.
### Statistical tests
We will use the following statistical tests:  
- Task time and errors mouse vs haptic: paired samples t-test  
- Difficulty levels, task time and errors: ANOVA  
- Subjective ratings: Wilcoxon Signed-Rank Test  
- Feedback gain and realism: Pearson correlation
