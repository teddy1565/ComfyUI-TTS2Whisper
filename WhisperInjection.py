
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
        mapper = ASRMapper.ASRMappingText()
        
        for alignment in segments_alignment:
            r = mapper.map_text(alignment["value"], replace_input_str)
            first_index = next((x for x in r if not math.isinf(x)), None)
            last_index = next((x for x in reversed(r) if not math.isinf(x)), None)
            alignment["value"] = replace_input_str[first_index:last_index]
        
        return (segments_alignment, )