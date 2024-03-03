# Cloud-detection-with-sky-brightness
This repository contains all the code used to create the graphs in the poster and paper. 

The code for the visual graphs can be found in the folder Code for visual graphs. This has a Python file with a class containing all the functions used in the other python files in this repository. 
The Python file Usage contains the code to create the graphs.

The folder animations contains a Python file that creates an image sequence of all the data files from Washetdonker.nl for a given duration and year. Default this is the whole year 2023. 
Alle the .mp4 files are created with the image sequences from animations.py. These image sequences are later edited in blender and exported with 10 fps.

The folder Databestanden + code contains the Python file used to automaticaly download al the data from Washetdonker.nl Open Meteo API and Skyfield API. Default this is the whole year 2023. 
All the data is writen to 1 .csv file. All the .csv files used for the data analysis can also be found in here.



