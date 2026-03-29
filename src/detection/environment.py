"""
This will define the types of animals to detect for a given environment. 
The specific type of environment chosen defines the animal detection. 
"""

from dataclasses import dataclass


@dataclass
class Environment:
    name: str #natural environment name 
    classes: list[str] #classes of animals that could be detected 

FOREST = Environment("forest", [
    "deer", "bear", "wolf", "fox", "raccoon", "rabbit",
    "squirrel", "moose", "elk", "owl", "hawk", "turkey",
    "snake", "wild boar", "bobcat", "porcupine","bird",
])

WETLAND = Environment("wetland", [
    "alligator", "turtle", "frog", "heron", "duck",
    "goose", "snake", "beaver", "otter", "crane", "bird",
])

SAVANNA = Environment("savanna", [
    "lion", "elephant", "giraffe", "zebra", "cheetah",
    "hyena", "wildebeest", "gazelle", "hippo", "rhino",
    "warthog", "baboon", "ostrich", "vulture", "bird",
])

ARCTIC = Environment("arctic", [
    "polar bear", "arctic fox", "caribou", "seal",
    "walrus", "snowy owl", "musk ox", "arctic hare",
])

URBAN = Environment("urban", [
    "raccoon", "squirrel", "rabbit", "skunk", "opossum",
    "coyote", "fox", "rat", "pigeon", "crow", "hawk", "bird",
])

MOUNTAIN = Environment("mountain", [
    "mountain goat", "bighorn sheep", "cougar", "lynx",
    "marmot", "eagle", "elk", "bear", "pika", "bird",
])

#have a dictionary to easily grab all the environments above 
all_envs = {e.name: e for e in [FOREST, WETLAND, SAVANNA, ARCTIC, URBAN, MOUNTAIN]}

#function to call to make it easier to get a specific envionrmnet instead of importing all of the envs
def get(name: str) -> Environment:
    env = all_envs.get(name.lower())
    if env is None:
        raise ValueError(f"Unknown environment '{name}'. Options: {list(all_envs)}")
    return env