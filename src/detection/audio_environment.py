"""
This will define the types of sounds to detect for a given environment. 
The specific type of environment chosen defines the sound detection. 
"""

from dataclasses import dataclass



@dataclass
class AudioEnvironment:
    name: str #natural environment name 
    classes: list[str] #classes of sounds that could be detected 

#Keep all the ambient descirptors in one dictionarry for future retrieval
AMBIENT = {
    "forest": [
        "quiet forest ambience",
    ],
    "wetland": [
        "wind rustling through grass",
        "rain falling on still water",
        "quiet wetland ambience",
    ],
    "savanna": [
        "insects buzzing in grass",
        "wind sweeping across open ground",
        "quiet open grassland ambience",
    ],
    "arctic": [
        "ice cracking or shifting",
        "strong wind howling across open terrain",
        "water lapping against ice",
        "quiet arctic ambience with wind",
    ],
    "urban": [
        "distant traffic hum",
        "faint human speech",
        "quiet urban night ambience",
    ],
    "mountain": [
        "strong wind through a mountain pass",
        "rushing water over rocks",
        "quiet mountain ambience",
    ],
}

FOREST = AudioEnvironment("forest", [
    # vocal / biological
    "low-pitched growling or snarling",
    "howling or sustained barking",
    "high-pitched chittering or chattering",
    "deep grunting or bellowing",
    "hooting call",
    "melodic bird song",
    "rapid percussive tapping on wood",
    "hissing or rattling sound",
    # movement
    "heavy rustling through vegetation",
    
]+ AMBIENT["forest"])

WETLAND = AudioEnvironment("wetland", [
    # vocal / biological
    "repetitive croaking chorus",
    "loud honking or quacking calls",
    "sharp squawking or croaking call",
    "steady insect buzzing",
    "melodic bird song near water",
    # movement
    "splashing through shallow water",
    "loud slapping on water surface",

]+ AMBIENT["wetland"])

SAVANNA = AudioEnvironment("savanna", [
    # vocal / biological
    "loud trumpeting blast",
    "high-pitched laughing or whooping calls",
    "rhythmic grunting or braying",
    "melodic bird song",
    # movement
    "rumbling of many hooves on dry ground",
    "heavy footsteps through dry grass",
]+ AMBIENT["savanna"])

ARCTIC = AudioEnvironment("arctic", [
    # vocal / biological
    "deep growling or roaring",
    "sharp barking or yipping",
    "loud moaning or wailing call",
    "snorting or heavy breathing",
    # movement
    "crunching through snow or ice",
]+ AMBIENT["arctic"])

URBAN = AudioEnvironment("urban", [
    # vocal / biological
    "high-pitched chittering or hissing",
    "howling or barking at night",
    "squeaking and scratching",
    "soft repetitive cooing",
    "harsh cawing calls",
    "melodic bird song",
    # movement
    "rummaging through debris",
    "light scurrying on hard surface",
]+ AMBIENT["urban"])

MOUNTAIN = AudioEnvironment("mountain", [
    # vocal / biological
    "high-pitched screaming or shrieking call",
    "deep growling or grunting",
    "prolonged bugling or wailing call",
    "sharp whistling alarm call",
    "melodic bird song",
    # movement
    "rocks clattering on a slope",
    "heavy footsteps on rocky terrain",
]+ AMBIENT["mountain"])

#have a dictionary to easily grab all the environments above 
all_envs = {e.name: e for e in [FOREST, WETLAND, SAVANNA, ARCTIC, URBAN, MOUNTAIN]}

#function to call to make it easier to get a specific envionrmnet instead of importing all of the envs
def get(name: str) -> AudioEnvironment:
    env = all_envs.get(name.lower())
    if env is None:
        raise ValueError(f"Unknown environment '{name}'. Options: {list(all_envs)}")
    return env

#function to retrive only the ambient sounds 
def get_ambient(name: str) -> list[str]:
    ambient = AMBIENT.get(name.lower())
    if ambient is None:
        raise ValueError(f"Unknown environment '{name}'. Options: {list(AMBIENT)}")
    return ambient