from enum import Enum


class EventType(str, Enum):
    THEATER = "THEATER"
    CINEMA = "CINEMA"
    CONCERT = "CONCERT"
    SPORTS = "SPORTS"
    OTHER = "OTHER"
