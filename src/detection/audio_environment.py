"""
This will define the types of sounds to detect for a given environment. 
The specific type of environment chosen defines the sound detection. 
"""

from dataclasses import dataclass


@dataclass
class AudioEnvironment:
    name: str #natural environment name 
    classes: list[str] #classes of sounds that could be detected 

FOREST = AudioEnvironment("forest", [
    "large animal growling or snarling aggressively",
    "canine howling or barking in the distance",
    "small animal chittering or chattering",
    "deer or elk bugling or grunting",
    "owl hooting",
    "bird singing or calling",
    "woodpecker drumming on wood",
    "snake hissing or rattling",
    "turkey gobbling",
    "heavy animal moving through brush and undergrowth",
    "small animal scurrying through dry leaves",
    "wind and rain in forest canopy",
    "stream or creek flowing",
    "quiet forest ambience with faint rustling",
    "suddent burst of movement"
])

WETLAND = AudioEnvironment("wetland", [
    "frog croaking or chorus of frogs",
    "waterfowl quacking or honking",
    "wading bird squawking or croaking",
    "alligator bellowing or hissing",
    "small mammal chirping or squealing near water",
    "insect buzzing over water",
    "bird singing or calling near water",
    "animal splashing through shallow water",
    "beaver tail slapping on water",
    "wind rustling through marsh grass",
    "rain falling on still water",
    "quiet wetland ambience with distant water",
    "suddent burst of movement"
])

SAVANNA = AudioEnvironment("savanna", [
    "lion or large cat roaring",
    "elephant trumpeting",
    "hyena laughing or whooping",
    "hoofed animal braying or grunting",
    "primate barking or screaming",
    "bird singing or calling",
    "large herd running on dry ground",
    "heavy animal walking through dry grass",
    "animal grazing or tearing grass",
    "animals fighting with growls and impacts",
    "insects buzzing in tall grass",
    "wind sweeping across open grassland",
    "quiet savanna ambience",
    "suddent burst of movement"
])

ARCTIC = AudioEnvironment("arctic", [
    "large animal growling or roaring",
    "canine barking or yipping",
    "hoofed animal snorting or grunting",
    "seal barking or moaning",
    "walrus bellowing",
    "owl hooting",
    "animal crunching through snow or ice",
    "ice cracking or shifting",
    "strong wind howling across open tundra",
    "water lapping against ice",
    "quiet arctic ambience with wind",
    "suddent burst of movement"
])

URBAN = AudioEnvironment("urban", [
    "small mammal chittering or hissing",
    "coyote or fox howling or barking at night",
    "rat or rodent squeaking and scratching",
    "pigeon cooing",
    "crow or raven cawing",
    "bird singing or calling",
    "animal rummaging through trash or debris",
    "small animal scurrying on hard surface",
    "dog barking in neighborhood",
    "distant traffic or road noise",
    "human speech or conversation",
    "quiet urban night with faint background hum",
    "suddent burst of movement"
])

MOUNTAIN = AudioEnvironment("mountain", [
    "large cat screaming or snarling",
    "bear growling or grunting",
    "elk bugling or calling",
    "goat or sheep bleating",
    "marmot or pika whistling alarm call",
    "eagle or hawk screeching",
    "bird singing or calling",
    "hooves or rocks clattering on slope",
    "heavy animal walking on rocky terrain",
    "strong wind howling through mountain pass",
    "mountain stream rushing",
    "quiet mountain ambience with light wind",
    "suddent burst of movement"
])

#have a dictionary to easily grab all the environments above 
all_envs = {e.name: e for e in [FOREST, WETLAND, SAVANNA, ARCTIC, URBAN, MOUNTAIN]}

#function to call to make it easier to get a specific envionrmnet instead of importing all of the envs
def get(name: str) -> AudioEnvironment:
    env = all_envs.get(name.lower())
    if env is None:
        raise ValueError(f"Unknown environment '{name}'. Options: {list(all_envs)}")
    return env