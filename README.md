# ManufacturingSim
####John Breton, Ryan Godfrey, Rahel Gunaratne

*The current state of the application does not contain all expected functionality to form a fully functional model. It 
has not undergone proper verification or validation. What is being presented is a work in progress of the initial model 
translation that compiles and runs but will continue to be improved upon and expanded for future iteration deliverables.*

##Table of Contents
**fel.py**
- This file provides classes and functionalities to maintain a future event list (FEL) and a list of blocked tasks.
- The FEL is iterated through by "jumping" to the next event time, since real-time evaluation would not be effective in 
this simulation

**main.py**
- This file is responsible for coordinating the interactions between classes and running the simulation 

**processors.py**
- This file contains the source code relating to entities that have processing responsibilities such as *Inspectors* and 
*Workstations* 
- The functionalities allow these entities to receive/send components to other entities as well as preform their 
processing duties

**requirements.txt**
- This file contains all information about system requirements for running the simulation. It effectively 
has no functionality other than to provide support when initially setting up the simulation

##Installation Requirements
To install and run the simulation:
1. Clone to repo to a local directory. This will save a Python project that can be run via a terminal.
2. Ensure Python and pip have been installed on your machine (see step 4 for help)
3. From the root of the project directory use the following commands to install required libraries and execute the simulation:


    $ pip install -r .\requirements.txt    
    $ python .\main.py

4. To install both Python and Pip, follow the links below for detailed installation steps:

   •	https://www.python.org/downloads/   
   •	https://pip.pypa.io/en/stable/installation/

