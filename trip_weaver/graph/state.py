from typing import TypedDict


class TripweverState(TypedDict):
    query: str
    parsed_params: dict
    research: dict
    plan: str
