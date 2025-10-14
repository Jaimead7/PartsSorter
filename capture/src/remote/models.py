from typing import TypedDict


class CameraParams(TypedDict):
    camera_width: int
    camera_height: int
    brightness: int
    contrast: int
    saturation: int
    auto_exposure: int
    exposure: int
    auto_wb: int
    wb: int

class ActuatorParams(TypedDict):
    tape_speed: float
    sensors_distance: float
