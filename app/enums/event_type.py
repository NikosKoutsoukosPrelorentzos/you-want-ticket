from enum import Enum


class EventType(str, Enum):
    THEATER = "THEATER"
    CINEMA = "CINEMA"
    CONCERT = "CONCERT"
    FESTIVAL = "FESTIVAL"
    RACE = "RACE"
    OTHER = "OTHER"
