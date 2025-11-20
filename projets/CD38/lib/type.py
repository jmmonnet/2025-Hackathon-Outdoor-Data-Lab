from typing import NamedTuple


class BoundingBox(NamedTuple):
    x1: float
    y1: float
    x2: float
    y2: float

class Ponderation(NamedTuple):
    species_presence: float
    user_presence: float
    hiking_trail_presence: float
    habitat_presence: float


    
