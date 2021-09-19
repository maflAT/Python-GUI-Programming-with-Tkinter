import tkinter.constants as tkc
from enum import Enum

EW = tkc.EW


class FieldTypes:
    string = 1
    string_list = 2
    iso_date_string = 3
    long_string = 4
    decimal = 5
    integer = 6
    boolean = 7


class TkAction(Enum):
    DEL: str = "0"
    INSERT: str = "1"
    OTHER: str = "-1"


class TkEvent(Enum):
    FOCUS_OUT: str = "<FocusOut>"
