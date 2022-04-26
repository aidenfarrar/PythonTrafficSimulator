# Traffic Simulator

Traffic modeling is an important topic with many applications in city planning, supply chain management, and construction. For our project we are hoping to model the influence of public transit on a microscopic level. We will be creating a model of Georgia Tech’s road network and connection to the city of Atlanta as well as all of the bus, bike, car, and pedestrian traffic that moves within the model. With our model we will experiment to determine the impact of various ideas of traffic limiting on the actual traffic level experienced by users.

This project build off the work of the following repo: https://github.com/BilHim/trafficSimulator

## Installation & Run Guide

### Requirements
This project requires `numpy`, `pygame`, and `scipy`, and works with Python 3.
This guide assumes you have the correct Python and pip version installed and a working terminal/command prompt.

### Clone Repo & Install Dependencies
To get the project files, download the project zip file from github. Alternatively use git to clone the project repository:

`git clone https://github.gatech.edu/bwei42/CX4320-Team100-Project`

To install the required dependencies, open a terminal in the root directory of the project and run the following command:

`pip install -r requirements.txt`

Note that the exact versions of the dependencies are needed to run the project, so it is recommended to create a virtual python enviornment if you have conflicts. To install a virtual python enviornment, please refer to the following tutorial: https://realpython.com/python-virtual-environments-a-primer/

### Running the Project
Open a terminal in the root directory. Navigate to the tests directory:

`cd src`

copy the gatech_test.py file and gt-model.txt file to the src directory using a file explorer or the terminal:

`mv tests/gateh_test.py gatech_test.py`

`mv tests/gt-model.txt.py gt-model.txt.py`

Run the project using the following command:

`python gatech_test.py`

A pygame window should appear and show the running simulation!






