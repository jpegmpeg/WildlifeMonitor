"""
Species registration
Because BioCLIP requires scientific name, we require a mapping
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class Species:
    common: str
    scientific: str = None #scientific name of the common name
    taxonomy: tuple = None #full taxonomy name best for BioCLIP

    def bioclip_label(self) -> str:
        return " ".join(self.taxonomy) + " " + self.scientific

# Different templates for various animals based on class
def _mammal(common, sci, order, family, genus):
    return Species(common, sci, ("Animalia", "Chordata", "Mammalia", order, family, genus))
 
def _bird(common, sci, order, family, genus):
    return Species(common, sci, ("Animalia", "Chordata", "Aves", order, family, genus))
 
def _reptile(common, sci, order, family, genus):
    return Species(common, sci, ("Animalia", "Chordata", "Reptilia", order, family, genus))
 
def _amphibian(common, sci, order, family, genus):
    return Species(common, sci, ("Animalia", "Chordata", "Amphibia", order, family, genus))

#Registry of all possible animals being considered right now 
REGISTRY: dict[str, Species] = {
 
    # --- Forest / generic N. American mammals ---
    #common               #common       #scientific name        #order          #family             #genus
    "deer":       _mammal("deer",      "Odocoileus virginianus", "Artiodactyla", "Cervidae",       "Odocoileus"),
    "bear":       _mammal("bear",      "Ursus americanus",       "Carnivora",    "Ursidae",        "Ursus"),
    "wolf":       _mammal("wolf",      "Canis lupus",            "Carnivora",    "Canidae",        "Canis"),
    "fox":        _mammal("fox",       "Vulpes vulpes",          "Carnivora",    "Canidae",        "Vulpes"),
    "raccoon":    _mammal("raccoon",   "Procyon lotor",          "Carnivora",    "Procyonidae",    "Procyon"),
    "rabbit":     _mammal("rabbit",    "Sylvilagus floridanus",  "Lagomorpha",   "Leporidae",      "Sylvilagus"),
    "squirrel":   _mammal("squirrel",  "Sciurus carolinensis",   "Rodentia",     "Sciuridae",      "Sciurus"),
    "moose":      _mammal("moose",     "Alces alces",            "Artiodactyla", "Cervidae",       "Alces"),
    "elk":        _mammal("elk",       "Cervus canadensis",      "Artiodactyla", "Cervidae",       "Cervus"),
    "wild boar":  _mammal("wild boar", "Sus scrofa",             "Artiodactyla", "Suidae",         "Sus"),
    "bobcat":     _mammal("bobcat",    "Lynx rufus",             "Carnivora",    "Felidae",        "Lynx"),
    "porcupine":  _mammal("porcupine", "Erethizon dorsatum",     "Rodentia",     "Erethizontidae", "Erethizon"),
    "beaver":     _mammal("beaver",    "Castor canadensis",      "Rodentia",     "Castoridae",     "Castor"),
    "otter":      _mammal("otter",     "Lontra canadensis",      "Carnivora",    "Mustelidae",     "Lontra"),
 
    # --- Forest / urban birds ---
    "owl":        _bird("owl",    "Bubo virginianus",    "Strigiformes",    "Strigidae",    "Bubo"),
    "hawk":       _bird("hawk",   "Buteo jamaicensis",   "Accipitriformes", "Accipitridae", "Buteo"),
    "turkey":     _bird("turkey", "Meleagris gallopavo", "Galliformes",     "Phasianidae",  "Meleagris"),
 
    # --- Reptiles / amphibians ---
    "snake":      _reptile("snake",     "Thamnophis sirtalis",         "Squamata",   "Colubridae",     "Thamnophis"),
    "alligator":  _reptile("alligator", "Alligator mississippiensis",  "Crocodylia", "Alligatoridae",  "Alligator"),
    "turtle":     _reptile("turtle",    "Chrysemys picta",             "Testudines", "Emydidae",       "Chrysemys"),
    "frog":       _amphibian("frog",    "Lithobates catesbeianus",     "Anura",      "Ranidae",        "Lithobates"),
 
    # --- Wetland birds ---
    "heron":      _bird("heron", "Ardea herodias",      "Pelecaniformes", "Ardeidae", "Ardea"),
    "duck":       _bird("duck",  "Anas platyrhynchos",  "Anseriformes",   "Anatidae", "Anas"),
    "goose":      _bird("goose", "Branta canadensis",   "Anseriformes",   "Anatidae", "Branta"),
    "crane":      _bird("crane", "Antigone canadensis", "Gruiformes",     "Gruidae",  "Antigone"),
 
    # --- Savanna ---
    "lion":       _mammal("lion",     "Panthera leo",           "Carnivora",      "Felidae",        "Panthera"),
    "elephant":   _mammal("elephant", "Loxodonta africana",     "Proboscidea",    "Elephantidae",   "Loxodonta"),
    "giraffe":    _mammal("giraffe",  "Giraffa camelopardalis", "Artiodactyla",   "Giraffidae",     "Giraffa"),
    "zebra":      _mammal("zebra",    "Equus quagga",           "Perissodactyla", "Equidae",        "Equus"),
    "cheetah":    _mammal("cheetah",  "Acinonyx jubatus",       "Carnivora",      "Felidae",        "Acinonyx"),
    "hyena":      _mammal("hyena",    "Crocuta crocuta",        "Carnivora",      "Hyaenidae",      "Crocuta"),
    "gazelle":    _mammal("gazelle",  "Eudorcas thomsonii",     "Artiodactyla",   "Bovidae",        "Eudorcas"),
    "hippo":      _mammal("hippo",    "Hippopotamus amphibius", "Artiodactyla",   "Hippopotamidae", "Hippopotamus"),
    "rhino":      _mammal("rhino",    "Ceratotherium simum",    "Perissodactyla", "Rhinocerotidae", "Ceratotherium"),
    "warthog":    _mammal("warthog",  "Phacochoerus africanus", "Artiodactyla",   "Suidae",         "Phacochoerus"),
    "baboon":     _mammal("baboon",   "Papio anubis",           "Primates",       "Cercopithecidae","Papio"),
    "ostrich":    _bird("ostrich",    "Struthio camelus",       "Struthioniformes", "Struthionidae", "Struthio"),
    "vulture":    _bird("vulture",    "Gyps africanus",         "Accipitriformes",  "Accipitridae",  "Gyps"),
 
    # --- Arctic ---
    "polar bear":  _mammal("polar bear",  "Ursus maritimus",   "Carnivora",    "Ursidae",    "Ursus"),
    "arctic fox":  _mammal("arctic fox",  "Vulpes lagopus",    "Carnivora",    "Canidae",    "Vulpes"),
    "caribou":     _mammal("caribou",     "Rangifer tarandus", "Artiodactyla", "Cervidae",   "Rangifer"),
    "seal":        _mammal("seal",        "Pusa hispida",      "Carnivora",    "Phocidae",   "Pusa"),
    "walrus":      _mammal("walrus",      "Odobenus rosmarus", "Carnivora",    "Odobenidae", "Odobenus"),
    "snowy owl":   _bird("snowy owl",     "Bubo scandiacus",   "Strigiformes", "Strigidae",  "Bubo"),
    "musk ox":     _mammal("musk ox",     "Ovibos moschatus",  "Artiodactyla", "Bovidae",    "Ovibos"),
    "arctic hare": _mammal("arctic hare", "Lepus arcticus",    "Lagomorpha",   "Leporidae",  "Lepus"),
 
    # --- Urban ---
    "cat":       _mammal("cat",     "Felis catus",           "Carnivora",       "Felidae",    "Felis"),
    "dog":       _mammal("dog",     "Canis familiaris",      "Carnivora",       "Canidae",    "Canis"),
    "skunk":     _mammal("skunk",   "Mephitis mephitis",     "Carnivora",       "Mephitidae", "Mephitis"),
    "opossum":   _mammal("opossum", "Didelphis virginiana",  "Didelphimorphia", "Didelphidae","Didelphis"),
    "groundhog":  _mammal("groundhog", "Marmota monax",          "Rodentia",     "Sciuridae",      "Marmota"),
    "coyote":    _mammal("coyote",  "Canis latrans",         "Carnivora",       "Canidae",    "Canis"),
    "rat":       _mammal("rat",     "Rattus norvegicus",     "Rodentia",        "Muridae",    "Rattus"),
    "pigeon":    _bird("pigeon", "Columba livia",            "Columbiformes",   "Columbidae", "Columba"),
    "crow":      _bird("crow",   "Corvus brachyrhynchos",    "Passeriformes",   "Corvidae",   "Corvus"),
 
    # --- Mountain ---
    "mountain goat": _mammal("mountain goat", "Oreamnos americanus",  "Artiodactyla",    "Bovidae",      "Oreamnos"),
    "bighorn sheep": _mammal("bighorn sheep", "Ovis canadensis",      "Artiodactyla",    "Bovidae",      "Ovis"),
    "cougar":        _mammal("cougar",        "Puma concolor",        "Carnivora",       "Felidae",      "Puma"),
    "lynx":          _mammal("lynx",          "Lynx canadensis",      "Carnivora",       "Felidae",      "Lynx"),
    "marmot":        _mammal("marmot",        "Marmota flaviventris", "Rodentia",        "Sciuridae",    "Marmota"),
    "eagle":         _bird("eagle",           "Aquila chrysaetos",    "Accipitriformes", "Accipitridae", "Aquila"),
    "pika":          _mammal("pika",          "Ochotona princeps",    "Lagomorpha",      "Ochotonidae",  "Ochotona"),
 
    # --- Group-level fallback ---
    # "bird" isn't a species; use the class rank so BioCLIP compares it at the
    # right level rather than matching against a specific taxon.
    "bird":      Species("bird", "Aves", ("Animalia", "Chordata")),
}