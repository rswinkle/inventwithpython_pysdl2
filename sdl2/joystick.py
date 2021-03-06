from ctypes import Structure, c_int, c_char_p, POINTER
from .dll import _bind, nullfunc
from .stdinc import Sint16, Sint32, Uint16, Uint8, SDL_bool

__all__ = ["SDL_Joystick", "SDL_JoystickGUID", "SDL_JoystickID",
           "SDL_NumJoysticks", "SDL_JoystickNameForIndex", "SDL_JoystickOpen",
           "SDL_JoystickName", "SDL_JoystickGetDeviceGUID",
           "SDL_JoystickGetGUID", "SDL_JoystickGetGUIDString",
           "SDL_JoystickGetGUIDFromString", "SDL_JoystickGetAttached",
           "SDL_JoystickInstanceID", "SDL_JoystickNumAxes",
           "SDL_JoystickNumBalls", "SDL_JoystickNumHats",
           "SDL_JoystickNumButtons", "SDL_JoystickUpdate",
           "SDL_JoystickEventState", "SDL_JoystickGetAxis", "SDL_HAT_CENTERED",
           "SDL_HAT_UP", "SDL_HAT_RIGHT", "SDL_HAT_DOWN", "SDL_HAT_LEFT",
           "SDL_HAT_RIGHTUP", "SDL_HAT_RIGHTDOWN", "SDL_HAT_LEFTUP",
           "SDL_HAT_LEFTDOWN", "SDL_JoystickGetHat", "SDL_JoystickGetBall",
           "SDL_JoystickGetButton", "SDL_JoystickClose",
           "SDL_JOYSTICK_POWER_UNKNOWN", "SDL_JOYSTICK_POWER_EMPTY",
           "SDL_JOYSTICK_POWER_LOW", "SDL_JOYSTICK_POWER_MEDIUM",
           "SDL_JOYSTICK_POWER_FULL", "SDL_JOYSTICK_POWER_WIRED",
           "SDL_JOYSTICK_POWER_MAX", "SDL_JoystickPowerLevel",
           "SDL_JoystickCurrentPowerLevel", "SDL_JoystickFromInstanceID",
           "SDL_JoystickGetVendor", "SDL_JoystickGetProductVersion",
           "SDL_JoystickGetProduct", "SDL_JoystickGetAxisInitialState"
          ]

SDL_JoystickPowerLevel = c_int

SDL_JOYSTICK_POWER_UNKNOWN = -1
SDL_JOYSTICK_POWER_EMPTY = 0
SDL_JOYSTICK_POWER_LOW = 1
SDL_JOYSTICK_POWER_MEDIUM = 2
SDL_JOYSTICK_POWER_FULL = 3
SDL_JOYSTICK_POWER_WIRED = 4
SDL_JOYSTICK_POWER_MAX = 5


class SDL_Joystick(Structure):
    pass

class SDL_JoystickGUID(Structure):
    _fields_ = [("data", (Uint8 * 16))]

SDL_JoystickID = Sint32

SDL_NumJoysticks = _bind("SDL_NumJoysticks", None, c_int)
SDL_JoystickNameForIndex = _bind("SDL_JoystickNameForIndex", [c_int], c_char_p)
SDL_JoystickOpen = _bind("SDL_JoystickOpen", [c_int], POINTER(SDL_Joystick))
SDL_JoystickName = _bind("SDL_JoystickName", [POINTER(SDL_Joystick)], c_char_p)
SDL_JoystickGetDeviceGUID = _bind("SDL_JoystickGetDeviceGUID", [c_int], SDL_JoystickGUID)
SDL_JoystickGetGUID = _bind("SDL_JoystickGetGUID", [POINTER(SDL_Joystick)], SDL_JoystickGUID)
SDL_JoystickGetGUIDString = _bind("SDL_JoystickGetGUIDString", [SDL_JoystickGUID, c_char_p, c_int])
SDL_JoystickGetGUIDFromString = _bind("SDL_JoystickGetGUIDFromString", [c_char_p], SDL_JoystickGUID)
SDL_JoystickGetAttached = _bind("SDL_JoystickGetAttached", [POINTER(SDL_Joystick)], SDL_bool)
SDL_JoystickInstanceID = _bind("SDL_JoystickInstanceID", [POINTER(SDL_Joystick)], SDL_JoystickID)
SDL_JoystickNumAxes = _bind("SDL_JoystickNumAxes", [POINTER(SDL_Joystick)], c_int)
SDL_JoystickNumBalls = _bind("SDL_JoystickNumBalls", [POINTER(SDL_Joystick)], c_int)
SDL_JoystickNumHats = _bind("SDL_JoystickNumHats", [POINTER(SDL_Joystick)], c_int)
SDL_JoystickNumButtons = _bind("SDL_JoystickNumButtons", [POINTER(SDL_Joystick)], c_int)
SDL_JoystickUpdate = _bind("SDL_JoystickUpdate")
SDL_JoystickEventState = _bind("SDL_JoystickEventState", [c_int], c_int)
SDL_JoystickGetAxis = _bind("SDL_JoystickGetAxis", [POINTER(SDL_Joystick), c_int], Sint16)
SDL_HAT_CENTERED = 0x00
SDL_HAT_UP = 0x01
SDL_HAT_RIGHT = 0x02
SDL_HAT_DOWN = 0x04
SDL_HAT_LEFT = 0x08
SDL_HAT_RIGHTUP = SDL_HAT_RIGHT | SDL_HAT_UP
SDL_HAT_RIGHTDOWN = SDL_HAT_RIGHT | SDL_HAT_DOWN
SDL_HAT_LEFTUP = SDL_HAT_LEFT | SDL_HAT_UP
SDL_HAT_LEFTDOWN = SDL_HAT_LEFT | SDL_HAT_DOWN
SDL_JoystickGetHat = _bind("SDL_JoystickGetHat", [POINTER(SDL_Joystick), c_int], Uint8)
SDL_JoystickGetBall = _bind("SDL_JoystickGetBall", [POINTER(SDL_Joystick), c_int, POINTER(c_int), POINTER(c_int)], c_int)
SDL_JoystickGetButton = _bind("SDL_JoystickGetButton", [POINTER(SDL_Joystick), c_int], Uint8)
SDL_JoystickClose = _bind("SDL_JoystickClose", [POINTER(SDL_Joystick)])
SDL_JoystickCurrentPowerLevel = _bind("SDL_JoystickCurrentPowerLevel", [POINTER(SDL_Joystick)], SDL_JoystickPowerLevel, nullfunc)
SDL_JoystickFromInstanceID = _bind("SDL_JoystickFromInstanceID", [SDL_JoystickID], POINTER(SDL_Joystick), nullfunc)
SDL_JoystickGetVendor = _bind("SDL_JoystickGetVendor", [POINTER(SDL_Joystick)], Uint16, nullfunc)
SDL_JoystickGetProduct = _bind("SDL_JoystickGetProduct", [POINTER(SDL_Joystick)], Uint16, nullfunc)
SDL_JoystickGetProductVersion = _bind("SDL_JoystickGetProductVersion", [POINTER(SDL_Joystick)], Uint16, nullfunc)
SDL_JoystickGetAxisInitialState = _bind("SDL_JoystickGetAxisInitialState", [POINTER(SDL_Joystick), c_int, POINTER(Sint16)], SDL_bool, nullfunc)
