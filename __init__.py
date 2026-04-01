from . import WhisperInjection
from . import Utils

NODE_CLASS_MAPPINGS = {
    "WhisperSegAlignmentInjector": WhisperInjection.WhisperSegAlignmentInjector,
    "WhisperSegAlignmentMerge": WhisperInjection.WhisperSegAlignmentMerge,
    "WhisperSegAlignmentTimeoffsetFix": WhisperInjection.WhisperSegAlignmentTimeoffsetFix,
    "WhisperSegAlignmentAudioSaveToTemp": WhisperInjection.WhisperSegAlignmentAudioSaveToTemp,

    "StringToStringList": Utils.StringToStringList,
    "StringFilter": Utils.StringFilter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WhisperSegAlignmentInjector": "Whisper Segments Alignment Injector",
    "WhisperSegAlignmentMerge": "Whisper Segments Alignment Merge",
    "WhisperSegAlignmentTimeoffsetFix": "Whisper Segments Alignment TimeFix",
    "WhisperSegAlignmentAudioSaveToTemp": "Whisper Segments Alignment Audio Save And Get Path",
    "StringToStringList": "Convert String To String List",
    "StringFilter": "String Filter"
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]