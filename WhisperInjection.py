
import os
import time
import json
import math
import random



import nodes
import folder_paths
import comfy.utils
import comfy_execution
from server import PromptServer
from . import ASRMapper

MAIN_CATEGORY = "TTS2Whisper/InjectTools"

class WhisperSegAlignmentInjector:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "segments_alignment": ("whisper_alignment", {
                    "forceInput": True,
                }),
                "replace_input_str": ("STRING", { "forceInput": True })            },
            "hidden": {
                "unique_id": "UNIQUE_ID"
            }
        }
    
    RETURN_TYPES = ("whisper_alignment",)
    RETURN_NAMES = ("segments_alignment",)
    CATEGORY = f'{MAIN_CATEGORY}'
    FUNCTION = "replace_injector"
    
    def replace_injector(self, segments_alignment, replace_input_str, unique_id):
        mapper = ASRMapper.ASRMappingTextV3()
        input_str_head_index = 0
        input_str_last_index = 0
        
        for alignment in segments_alignment:
            n = len(alignment["value"])
            input_str_last_index = input_str_head_index + n
            k = replace_input_str[input_str_head_index:(input_str_last_index + 2)]
            r = mapper.map_text(alignment["value"], k)
            first_index = next((x for x in r if not math.isinf(x)), None)
            last_index = next((x for x in reversed(r) if not math.isinf(x)), None)
            alignment["value"] = k[first_index:(last_index + 1)]
            input_str_head_index = input_str_last_index + 1
        return (segments_alignment, )