
import os
import time
import json
import math
import random
import re

import nodes
import folder_paths
import comfy.utils
import comfy_execution
from server import PromptServer

MAIN_CATEGORY = "TTS2Whisper/Utils"

class StringToStringList:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "single_string": ("STRING", {
                    "forceInput": True,
                }),
                "delimiter": ("STRING", { }),
                "is_escape_char": ("BOOLEAN", { "default": False, "tooltip": "if use ascii escape char, must enable" })
            },
            "hidden": {
                "unique_id": "UNIQUE_ID"
            }
        }
    
    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("string list",)
    CATEGORY = f'{MAIN_CATEGORY}/String'
    FUNCTION = "convert_to_list"
    
    def convert_to_list(self, single_string, delimiter, is_escape_char=False, unique_id=0):

        if is_escape_char == True:
            escape_map = {
                "\\n": "\n",
                "\\t": "\t",
                "\\r": "\r",
                "\\\"": "\"",
                "\\\'": "\'",
                "\\\\": "\\"
            }

            for escaped, real in escape_map.items():
                delimiter = delimiter.replace(escaped, real)

        pattern = "[" + delimiter + "]" + "+"
        result = re.split(pattern, single_string)
        return (result, )


class StringFilter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "single_string": ("STRING", {
                    "forceInput": True,
                }),
                "delimiter": ("STRING", { }),
                "is_escape_char": ("BOOLEAN", { "default": False, "tooltip": "if use ascii escape char, must enable" })
            },
            "hidden": {
                "unique_id": "UNIQUE_ID"
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filtered_string",)
    CATEGORY = f'{MAIN_CATEGORY}/String'
    FUNCTION = "str_filter"
    
    def str_filter(self, single_string, delimiter, is_escape_char=False, unique_id=0):

        if is_escape_char == True:
            escape_map = {
                "\\n": "\n",
                "\\t": "\t",
                "\\r": "\r",
                "\\\"": "\"",
                "\\\'": "\'",
                "\\\\": "\\"
            }

            for escaped, real in escape_map.items():
                delimiter = delimiter.replace(escaped, real)

        pattern = "[" + delimiter + "]" + "+"
        result = re.split(pattern, single_string)
        result = "".join(result)
        return (result, )
    