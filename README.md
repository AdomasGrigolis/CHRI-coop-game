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
If, hoever, you want to run online, then you will need to allow port forwarding. Please refer to online sources on how to do this.  
**Note that port forwarding online can be risky.**
## Technical Details
### Engines
PyGame - game simulation and rendering  
PyMunk - 2D physics engine  
sockets - networking library  
