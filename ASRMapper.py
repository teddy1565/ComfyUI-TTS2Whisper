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