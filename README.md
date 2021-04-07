# Engine-Performance-Analysis
 
Requirements:     - an installation of Python 3.9.0 or above with the alias 'python'
                  - an installation of the following libraries:
                    (1) os  
                    (2) numpy  
                    (3) pandas  
                    (4) nptdms  
                    (5) datetime  
                    (6) plotnine  

Step 1: Navigate to the directory containing EPA.py (in my case that is /scripts)
Step 2: Enter a python environment by entering 'python' into your command terminal.
Step 3: Now you can execute EPA.py via exec(open("EPA.py").read())



Now you have access to the following functions:
* createcsv("path/file.txt")	for creating a csv file of the recorded data. enter whatever path you want ([ex] "/Users/jonathan/Desktop/file.txt")
* enginecalcs()			for calculating av. thrust, av. mass flow rate, ISP
* plot_thrust_curve()          for plotting a thrust curve
* plot_tank_weight()           for plotting both propellant tank weights
* plot_tank_pressure()         for plotting both propellant tank pressures
* plot_inj_pressure()          for plotting injector pressures
* plot_thermocouples()         for plotting engine temperature
* plot_thermocouples_He()		    for plotting helium line temperature

Cancel your session with ctrl + z
