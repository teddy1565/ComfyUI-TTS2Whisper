import os
import time
import json
import math
import random
import numpy as np
import uuid
import torchaudio
import torch


import nodes
import folder_paths
import comfy.utils
import comfy_execution
from server import PromptServer
from . import ASRMapper


MAIN_CATEGORY = "TTS2Whisper/UnionModuleTools/MontrealForcedAligner(MFA)"

class MFASegAlignmentRecovery:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "segments_alignment": ("whisper_alignment", {
                    "forceInput": True,
                }),
                "replace_input_str": ("STRING", { "forceInput": True })
            },
            "hidden": {
                "unique_id": "UNIQUE_ID"
            }
        }
    
    RETURN_TYPES = ("whisper_alignment",)
    RETURN_NAMES = ("segments_alignment",)
    CATEGORY = f'{MAIN_CATEGORY}'
    FUNCTION = "replace_injector"
    
    def replace_injector(self, segments_alignment, replace_input_str, unique_id):
        if not segments_alignment or not replace_input_str:
            return (segments_alignment, )

        mapper = ASRMapper.ASRMappingTextV3() # 確認這裡呼叫到你的類別
        
        # 1. 將所有 MFA 片段拼接成完整的字串，並紀錄每個片段在總字串中的 index 範圍
        mfa_full_text = ""
        seg_ranges = [] # 儲存格式: (start_idx, end_idx)
        
        for seg in segments_alignment:
            start_idx = len(mfa_full_text)
            mfa_full_text += seg["value"]
            end_idx = len(mfa_full_text)
            seg_ranges.append((start_idx, end_idx))

        # 2. 進行全局 DP 映射
        # 這樣 mapping 陣列的長度會等於 len(replace_input_str)
        # mapping[i] 代表 replace_input_str[i] 這個字，對應到 mfa_full_text 的第幾個字元
        mapping = mapper.map_text(replace_input_str, mfa_full_text)

        # 3. 準備用來裝回填後文字的陣列
        new_seg_values = ["" for _ in range(len(segments_alignment))]

        # 4. 根據 mapping 結果，把原始文稿的字元分配回各個片段
        for i, char in enumerate(replace_input_str):
            target_mfa_idx = mapping[i]

            # 尋找 target_mfa_idx 屬於哪一個片段 (Segment)
            assigned_seg_idx = 0
            for seg_idx, (start_idx, end_idx) in enumerate(seg_ranges):
                if start_idx <= target_mfa_idx < end_idx:
                    assigned_seg_idx = seg_idx
                    break
                # 防呆：如果映射剛好超出範圍，歸入最後一個片段
                if target_mfa_idx >= seg_ranges[-1][1]:
                    assigned_seg_idx = len(segments_alignment) - 1

            new_seg_values[assigned_seg_idx] += char

        # 5. 更新原本的 segments_alignment 並清理空白
        for i, seg in enumerate(segments_alignment):
            # 去除可能因為標點符號造成的頭尾空白
            seg["value"] = new_seg_values[i].strip()

        return (segments_alignment, )