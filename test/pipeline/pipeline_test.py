"""
Test to check if the the whole pipeline works. 
More of a scratchpad to script test than automated validation tests. 
"""

from src.wildlife_monitor import wildlife_monitor
#run from root folder, this is a test video
path = './data/raw_input/NamibiaCam： Baby Giraffe with family - 6⧸12⧸2021.mp4'
environment = "SAVANNA"

wildlife_monitor(path, environment)


