import numpy as np
import re

try:
    from pypinyin import pinyin, Style
except ImportError:
    pinyin = None

class ASRMappingText:
    @staticmethod
    def sub_cost(a: str, r: str) -> float:
        return 0.0 if a == r else 1.0

    def map_text(self, source_text: str, asr_data: str) -> list[int]:
        n, m = len(source_text), len(asr_data)
        dp = [[0.0] * (m + 1) for _ in range(n + 1)]
        bt = [[0] * (m + 1) for _ in range(n + 1)]

        # 初始化邊界與 DP (同前)
        for i in range(1, n + 1): dp[i][0] = i; bt[i][0] = 1
        for j in range(1, m + 1): dp[0][j] = j; bt[0][j] = 2

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = 0.0 if source_text[i-1] == asr_data[j-1] else 1.0
                c_diag = dp[i-1][j-1] + cost
                c_up   = dp[i-1][j] + 1
                c_left = dp[i][j-1] + 1
                
                best = c_diag; dir_ = 0
                if c_up < best: best = c_up; dir_ = 1
                if c_left < best: best = c_left; dir_ = 2
                dp[i][j] = best; bt[i][j] = dir_

        # 1. 第一次回溯：僅記錄「完全匹配」的索引
        mapA = [None] * n
        curr_i, curr_j = n, m
        while curr_i > 0 or curr_j > 0:
            direction = bt[curr_i][curr_j]
            if curr_i > 0 and curr_j > 0 and direction == 0:
                if source_text[curr_i - 1] == asr_data[curr_j - 1]:
                    mapA[curr_i - 1] = curr_j - 1
                curr_i -= 1; curr_j -= 1
            elif curr_i > 0 and (curr_j == 0 or direction == 1):
                curr_i -= 1
            else:
                curr_j -= 1

        # 2. 第二次掃描：補足缺失的索引 (前一個 + 1)
        for i in range(n):
            if mapA[i] is None:
                if i == 0:
                    mapA[i] = 0 # 第一個字如果不匹配，從 0 開始
                else:
                    # 這裡採用「前一個字的索引 + 1」
                    mapA[i] = mapA[i-1] + 1
        
        # 確保索引不會超過 ASR 數據的最大長度
        return [min(idx, m - 1) for idx in mapA]

    def map_text_old(self, source_text: str, asr_data: str) -> list[int]:
        n = len(source_text)
        m = len(asr_data)
        
        # 初始化 DP 表與 Backtrack 表
        # dp[n+1][m+1], bt[n+1][m+1]
        dp = [[0.0] * (m + 1) for _ in range(n + 1)]
        bt = [[0] * (m + 1) for _ in range(n + 1)]

        # 初始化邊界條件
        for i in range(1, n + 1):
            dp[i][0] = dp[i - 1][0] + 1
            bt[i][0] = 1 # up (刪除 source)

        for j in range(1, m + 1):
            dp[0][j] = dp[0][j - 1] + 1
            bt[0][j] = 2 # left (插入 asr)

        # 填寫 DP 表
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                # 0: diag, 1: up, 2: left
                c_diag = dp[i-1][j-1] + self.sub_cost(source_text[i-1], asr_data[j-1])
                c_up   = dp[i-1][j] + 1
                c_left = dp[i][j-1] + 1

                best = c_diag
                dir_ = 0
                
                if c_up < best:
                    best = c_up
                    dir_ = 1
                if c_left < best:
                    best = c_left
                    dir_ = 2
                
                dp[i][j] = best
                bt[i][j] = dir_

        # 回溯路徑 (Backtracking)
        # Python 沒有 INT_MAX，通常用 float('inf') 或 -1 表示未對應
        mapA = [float('inf')] * n
        curr_i, curr_j = n, m
        
        while curr_i > 0 or curr_j > 0:
            direction = bt[curr_i][curr_j]
            if curr_i > 0 and curr_j > 0 and direction == 0:
                mapA[curr_i - 1] = curr_j - 1
                curr_i -= 1
                curr_j -= 1
            elif curr_i > 0 and (curr_j == 0 or direction == 1):
                mapA[curr_i - 1] = float('inf')
                curr_i -= 1
            else:
                curr_j -= 1
                
        return mapA

class ASRMappingTextV2:
    def __init__(self):
        # 設定權重：完全匹配=0, 同音字=0.2, 不匹配=1.0
        self.match_cost = 0.0
        self.pinyin_match_cost = 0.2
        self.mismatch_cost = 1.0

    def get_pinyin(self, char):
        if pinyin:
            res = pinyin(char, style=Style.NORMAL)
            return res[0][0] if res else None
        return None

    def sub_cost(self, a, r):
        if a == r:
            return self.match_cost
        # 同音字檢查 (處理 姓物/信物)
        if self.get_pinyin(a) == self.get_pinyin(r):
            return self.pinyin_match_cost
        return self.mismatch_cost

    def map_text(self, source_text: str, asr_data: str) -> list[int]:
        n, m = len(source_text), len(asr_data)
        if n == 0: return []
        
        # 1. DP 表初始化
        dp = [[0.0] * (m + 1) for _ in range(n + 1)]
        bt = [[0] * (m + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            dp[i][0] = i
            bt[i][0] = 1 # Up
        for j in range(1, m + 1):
            dp[0][j] = j
            bt[0][j] = 2 # Left

        # 2. 填寫 DP 表 (計算編輯距離路徑)
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = self.sub_cost(source_text[i-1], asr_data[j-1])
                c_diag = dp[i-1][j-1] + cost
                c_up   = dp[i-1][j] + 1
                c_left = dp[i][j-1] + 1

                best = c_diag
                dir_ = 0 # Diagonal
                if c_up < best:
                    best = c_up
                    dir_ = 1
                if c_left < best:
                    best = c_left
                    dir_ = 2
                dp[i][j] = best
                bt[i][j] = dir_

        # 3. 第一次回溯：找出精確或近似匹配的點
        mapA = [None] * n
        curr_i, curr_j = n, m
        while curr_i > 0 or curr_j > 0:
            direction = bt[curr_i][curr_j]
            if curr_i > 0 and curr_j > 0 and direction == 0:
                # 只有當代價小於 1.0 (完全相同或同音) 時才算對應成功
                if self.sub_cost(source_text[curr_i-1], asr_data[curr_j-1]) < 1.0:
                    mapA[curr_i - 1] = curr_j - 1
                curr_i -= 1
                curr_j -= 1
            elif curr_i > 0 and (curr_j == 0 or direction == 1):
                curr_i -= 1
            else:
                curr_j -= 1

        # 4. 第二次掃描：補足缺失的索引 (處理斷尾與漏字)
        known_indices = [idx for idx, val in enumerate(mapA) if val is not None]
        
        if not known_indices:
            # 極端情況：完全沒對上，給出均勻分佈
            return [int(i * (m-1) / max(1, n-1)) for i in range(n)]

        # A. 補齊開頭
        first_known = known_indices[0]
        for i in range(first_known - 1, -1, -1):
            mapA[i] = max(0, mapA[i+1] - 1)

        # B. 補齊中間與結尾
        for k in range(len(known_indices)):
            curr_i = known_indices[k]
            
            if k == len(known_indices) - 1: # 處理斷尾處
                for i in range(curr_i + 1, n):
                    # 遞增但不超過 ASR 長度
                    mapA[i] = min(m - 1, mapA[i-1] + 1)
            else: # 處理兩個已知點之間的空隙 (插值)
                next_i = known_indices[k+1]
                gap_len = next_i - curr_i
                val_diff = mapA[next_i] - mapA[curr_i]
                for i in range(curr_i + 1, next_i):
                    # 使用線性分佈補齊缺失索引
                    mapA[i] = mapA[curr_i] + int((i - curr_i) * val_diff / gap_len)
                    
        return mapA
    
class ASRMappingTextV3:
    def __init__(self):
        # 權重設定
        self.COST_MATCH = 0.0      # 完全匹配
        self.COST_PINYIN = 0.4     # 拼音相同 (如: 引离/云璃, 性物/信物)
        self.COST_MISMATCH = 1.2   # 完全不同 (調高一點，強迫走對角線)

    def _get_pinyin(self, char):
        """取得單個漢字的拼音"""
        if not re.match(r'[\u4e00-\u9fa5]', char):
            return char
        res = pinyin(char, style=Style.NORMAL)
        return res[0][0] if res else char

    def _is_valid(self, char):
        """判斷是否為有效字元（排除標點符號）"""
        return re.match(r'[\u4e00-\u9fa5a-zA-Z0-9]', char) is not None

    def sub_cost(self, a, r):
        """計算替換代價"""
        if a == r:
            return self.COST_MATCH
        if self._get_pinyin(a) == self._get_pinyin(r):
            return self.COST_PINYIN
        return self.COST_MISMATCH

    def map_text(self, source_text: str, asr_data: str) -> list[int]:
        """
        this function bigO is O(n x m)
        """
        # 1. 預處理：分離標點，只對有效字元做 DP
        src_info = [(i, c) for i, c in enumerate(source_text) if self._is_valid(c)]
        src_chars = [x[1] for x in src_info]
        
        n = len(src_chars)
        m = len(asr_data)
        
        if n == 0: return [0] * len(source_text)
        if m == 0: return [0] * len(source_text)

        # 2. DP 表初始化
        dp = [[0.0] * (m + 1) for _ in range(n + 1)]
        bt = [[0] * (m + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            dp[i][0] = i * 1.0
            bt[i][0] = 1 # Up
        for j in range(1, m + 1):
            dp[0][j] = j * 1.0
            bt[0][j] = 2 # Left

        # 3. 填寫 DP 表
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = self.sub_cost(src_chars[i-1], asr_data[j-1])
                c_diag = dp[i-1][j-1] + cost
                c_up   = dp[i-1][j] + 1.0
                c_left = dp[i][j-1] + 1.0

                best = c_diag
                dir_ = 0
                if c_up < best:
                    best = c_up
                    dir_ = 1
                if c_left < best:
                    best = c_left
                    dir_ = 2
                dp[i][j] = best
                bt[i][j] = dir_

        # 4. 第一次回溯：找出對應點
        raw_map = [None] * n
        curr_i, curr_j = n, m
        while curr_i > 0 or curr_j > 0:
            direction = bt[curr_i][curr_j]
            if curr_i > 0 and curr_j > 0 and direction == 0:
                # 只要不是完全不匹配(1.2)，就視為對應成功
                if self.sub_cost(src_chars[curr_i-1], asr_data[curr_j-1]) < self.COST_MISMATCH:
                    raw_map[curr_i - 1] = curr_j - 1
                curr_i -= 1
                curr_j -= 1
            elif curr_i > 0 and (curr_j == 0 or direction == 1):
                curr_i -= 1
            else:
                curr_j -= 1

        # 5. 線性插值補全（解決開頭錯誤與結尾斷字）
        known = [i for i, v in enumerate(raw_map) if v is not None]
        
        if not known:
            filled_map = [int(i * (m-1) / (n-1)) if n > 1 else 0 for i in range(n)]
        else:
            filled_map = list(raw_map)
            # 補頭
            first_k = known[0]
            for i in range(first_k - 1, -1, -1):
                filled_map[i] = max(0, filled_map[i+1] - 1)
            # 補中間
            for k in range(len(known) - 1):
                idx_start, idx_end = known[k], known[k+1]
                val_start, val_end = filled_map[idx_start], filled_map[idx_end]
                for i in range(idx_start + 1, idx_end):
                    ratio = (i - idx_start) / (idx_end - idx_start)
                    filled_map[i] = int(val_start + ratio * (val_end - val_start))
            # 補尾
            last_k = known[-1]
            for i in range(last_k + 1, n):
                filled_map[i] = min(m - 1, filled_map[i-1] + 1)

        # 6. 映射回原始帶標點的字串
        final_result = [0] * len(source_text)
        valid_idx = 0
        for i, char in enumerate(source_text):
            if self._is_valid(char):
                final_result[i] = filled_map[valid_idx]
                valid_idx += 1
            else:
                # 標點符號跟隨前一個有效字的索引
                final_result[i] = final_result[i-1] if i > 0 else 0
                
        return final_result
    
class ASRMappingTextV4:
    def __init__(self):
        # 權重設定：同音字 0.4, 完全不同 1.5
        self.COST_MATCH = 0.0
        self.COST_PINYIN = 0.4
        self.COST_MISMATCH = 1.5

    def _get_pinyin(self, char):
        if not re.match(r'[\u4e00-\u9fa5]', char): return char
        res = pinyin(char, style=Style.NORMAL)
        return res[0][0] if res else char

    def _is_valid(self, char):
        return re.match(r'[\u4e00-\u9fa5a-zA-Z0-9]', char) is not None

    def sub_cost(self, a, r):
        if a == r: return self.COST_MATCH
        if self._get_pinyin(a) == self._get_pinyin(r): return self.COST_PINYIN
        return self.COST_MISMATCH

    def map_text(self, source_text: str, asr_segments: list) -> list:
        # 1. 串聯 ASR 片段並建立「字元 -> 時間」映射表
        asr_full_text = ""
        char_times = [] # 儲存每個 ASR 字元對應的 (start, end)
        
        for seg in asr_segments:
            val = seg['value'].strip()
            if not val: continue
            # 計算該片段內每個字的預估時間 (均分)
            duration = (seg['end'] - seg['start']) / len(val)
            for i, char in enumerate(val):
                asr_full_text += char
                char_times.append({
                    'start': seg['start'] + i * duration,
                    'end': seg['start'] + (i + 1) * duration
                })

        # 2. 提取 Source 有效字元位置
        src_valid_chars = [c for c in source_text if self._is_valid(c)]
        n, m = len(src_valid_chars), len(asr_full_text)
        if n == 0 or m == 0: return []

        # 3. DP 矩陣計算
        dp = [[0.0] * (m + 1) for _ in range(n + 1)]
        bt = [[0] * (m + 1) for _ in range(n + 1)]

        for i in range(1, n + 1): dp[i][0] = i * 1.0; bt[i][0] = 1
        for j in range(1, m + 1): dp[0][j] = j * 1.0; bt[0][j] = 2

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = self.sub_cost(src_valid_chars[i-1], asr_full_text[j-1])
                c_diag = dp[i-1][j-1] + cost
                c_up   = dp[i-1][j] + 1.0
                c_left = dp[i][j-1] + 1.0
                
                best = c_diag; dir_ = 0
                if c_up < best: best = c_up; dir_ = 1
                if c_left < best: best = c_left; dir_ = 2
                dp[i][j] = best; bt[i][j] = dir_

        # 4. 回溯：找出初步對齊 (僅保留代價低於 1.0 的對應點)
        raw_map = [None] * n
        curr_i, curr_j = n, m
        while curr_i > 0 or curr_j > 0:
            direction = bt[curr_i][curr_j]
            if curr_i > 0 and curr_j > 0 and direction == 0:
                if self.sub_cost(src_valid_chars[curr_i-1], asr_full_text[curr_j-1]) < 1.0:
                    raw_map[curr_i - 1] = curr_j - 1
                curr_i -= 1; curr_j -= 1
            elif curr_i > 0 and (curr_j == 0 or direction == 1):
                curr_i -= 1
            else:
                curr_j -= 1

        # 5. 強力插值補全 (處理結尾「死」或開頭「景軒」)
        known = [i for i, v in enumerate(raw_map) if v is not None]
        if not known:
            # 沒對上任何字，強制線性分佈
            final_indices = [int(i * (m-1) / (n-1)) if n > 1 else 0 for i in range(n)]
        else:
            final_indices = list(raw_map)
            # 補頭：若第一個字沒對上，從對上的點往回推
            for i in range(known[0] - 1, -1, -1):
                final_indices[i] = max(0, final_indices[i+1] - 1)
            # 補中間：線性插值
            for k in range(len(known) - 1):
                s, e = known[k], known[k+1]
                v_s, v_e = final_indices[s], final_indices[e]
                for i in range(s + 1, e):
                    final_indices[i] = v_s + int((i - s) * (v_e - v_s) / (e - s))
            # 補尾：重點修正！若最後一個字沒對上，強制對應到 ASR 最後一個索引
            for i in range(known[-1] + 1, n):
                # 這裡不再只是 +1，而是確保最後一個字一定指向 m-1
                dist_to_end = n - 1 - known[-1]
                val_dist = (m - 1) - final_indices[known[-1]]
                final_indices[i] = final_indices[i-1] + max(1, int(val_dist / dist_to_end))
                final_indices[i] = min(final_indices[i], m - 1)
            
            # 強制最後一個有效字元指向 ASR 的末尾字
            final_indices[-1] = m - 1

        # 6. 組裝回原本包含標點符號的清單
        final_mapping = []
        valid_ptr = 0
        for char in source_text:
            if self._is_valid(char):
                idx = final_indices[valid_ptr]
                final_mapping.append({
                    'char': char,
                    'asr_idx': idx,
                    'time': char_times[idx]
                })
                valid_ptr += 1
            else:
                # 標點符號跟隨前一字時間
                prev_time = final_mapping[-1]['time'] if final_mapping else char_times[0]
                final_mapping.append({'char': char, 'asr_idx': -1, 'time': prev_time})

        return final_mapping