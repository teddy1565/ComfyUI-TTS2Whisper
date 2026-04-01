
import os
import time
import json
import math
import random
import numpy as np


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
        
        punctuation_list = [",", ".", "!", "，", "。", ":", "；", " ", "？", "?", "：", "「", "」"]


        
        for alignment in segments_alignment:
            punctuation_count = 0
            n = len(alignment["value"])
            input_str_last_index = input_str_head_index + n
            
            for c in alignment["value"]:
                if c in punctuation_list:
                    punctuation_count += 1

            k = replace_input_str[input_str_head_index:(input_str_last_index + 2 + punctuation_count)]
            r = mapper.map_text(alignment["value"], k)
            first_index = next((x for x in r if not math.isinf(x)), None)
            last_index = next((x for x in reversed(r) if not math.isinf(x)), None)
            alignment["value"] = k[first_index:(last_index + 1)]
            input_str_head_index = input_str_last_index + 1
        return (segments_alignment, )
    
class WhisperSegAlignmentMerge:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "segments_alignment": ("whisper_alignment", {
                    "forceInput": True,
                }),
                "max_str_size": ("INT", { "default": 30, "min": 0 })
            },
            "hidden": {
                "unique_id": "UNIQUE_ID"
            }
        }
    
    RETURN_TYPES = ("whisper_alignment",)
    RETURN_NAMES = ("segments_alignment",)
    CATEGORY = f'{MAIN_CATEGORY}'
    FUNCTION = "merge_injector"
    
    def merge_injector(self, segments_alignment, max_str_size=30, unique_id=0):
        start_timestamp_list = [x["start"] for x in segments_alignment]
        start_timestamp = np.min(start_timestamp_list)
        end_timestamp_list = [x["end"] for x in segments_alignment]
        end_timestamp = math.ceil(np.max(end_timestamp_list))

        # total_time = end_timestamp - start_timestamp
        total_time = end_timestamp - 0
        
        text = [x["value"] for x in segments_alignment]
        text = "".join(text)

        result = [text[i:i+max_str_size] for i in range(0, len(text), max_str_size)]
        print(result)

        segments_size = len(result)
        if segments_size == 0 or total_time == 0:
            interval_time = 0.0
        else:
            interval_time = total_time / segments_size
        
        print(f"whisperMerge interval_time: {interval_time}")

        result_i = 0
        i = start_timestamp
        res = []
        while i < end_timestamp:
            alignment_dict = {
                "value": result[result_i],
                "start": i,
                "end": i + interval_time
            }
            result_i += 1
            result_i = result_i % len(result)
            i += interval_time
            res.append(alignment_dict)
        
        return (res, )