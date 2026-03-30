#include <iostream>
#include <vector>
#include <list>
#include <string>
#include <unordered_map>
#include <map>
#include <algorithm>
#include <queue>
#include <deque>
#include <cmath>
#include <stack>
#include <array>

/**
 * @brief 
 * 
 * 景轩单膝跪地，捂着流血的胸口慌忙的回答，在下……遭仇家暗算，误入仙子清修之地，实属无意！
 * ['景轩单膝跪地', '捂着流血的胸口慌忙的回答', '在下……遭仇家暗算', '误入仙子清修之地', '实属无意！']
 * 
 *  [
 * {'value': '锦轩单膝跪地', 'start': np.float64(0.7999999999999987), 'end': np.float64(2.3)},
 * {'value': '捂着流血的胸口', 'start': np.float64(2.3), 'end': np.float64(4.18)},
 * {'value': '慌忙地回答', 'start': np.float64(4.18), 'end': np.float64(5.34)},
 * {'value': '在下遭仇家暗算', 'start': np.float64(6.099999999999999), 'end': np.float64(8.24)},
 * {'value': '误入仙子清修之地', 'start': np.float64(8.24), 'end': np.float64(10.3)},
 * {'value': '实属无益', 'start': np.float64(10.3), 'end': np.float64(11.5)}
 * ]
 * 
 * 
 * 鯉魚家有頭小綠驢叫李屢屢. 綠鯉魚家有頭小紅驢叫呂里里
 * 李余家有頭小綠綠叫李余余
 */
class ASRMappingText {

    private:
        struct Alignment {
            std::string text;
            double      start_timestamp;
            double      end_timestamp;
            Alignment(): text(), start_timestamp(0), end_timestamp(0) {}
            Alignment(std::string v, double start, double end): text(v), start_timestamp(start), end_timestamp(end) {}
        };

    public:
        static inline float sub_cost(char32_t a, char32_t r) {
            return (a == r) ? 0.0f : 1.0f;
        }

        std::vector<int> map_text(std::u32string source_text, std::u32string asr_data) {
            const int n = source_text.size();
            const int m = asr_data.size();

            std::vector<std::vector<float>> dp(n + 1, std::vector<float>(m + 1, 0));

            // 0 diag, 1 up (del A), 2 left(ins R)
            std::vector<std::vector<int>> bt(n + 1, std::vector<int>(m + 1, 0));

            for (int i = 1; i <= n; i++) {
                dp[i][0] = dp[i - 1][0] + 1;
                bt[i][0] = 1;
            }

            for (int j = 1; j <= m; j++) {
                dp[0][j] = dp[0][j - 1] + 1;
                bt[0][j] = 2;
            }

            for (int i = 1; i <= n; i++) {
                for (int j = 1; j <= m; j++) {
                    float c_diag = dp[i-1][j-1] + sub_cost(source_text[i - 1], asr_data[j - 1]);
                    float c_up   = dp[i-1][j]   + 1;
                    float c_left = dp[i][j - 1] + 1;
                    float best = c_diag;
                    int dir = 0;
                    if (c_up < best) {
                        best = c_up;
                        dir = 1;
                    }
                    if (c_left < best) {
                        best = c_left;
                        dir = 2;
                    }
                    dp[i][j] = best;
                    bt[i][j] = dir;
                }
            }

            std::vector<int> mapA(n, INT_MAX);
            int i = n, j = m;
            while (i > 0 || j > 0) {
                int dir = bt[i][j];
                if (i > 0 && j > 0 && dir == 0) {
                    mapA[i-1] = j-1;
                    i--;
                    j--;
                } else if (i > 0 && (j == 0 || dir == 1)) {
                    mapA[i-1] = INT_MAX;
                    i--;
                } else {
                    j--;
                }
            }

            return mapA;
        }
};

int main(void) {
    class ASRMappingText asr;

    auto k = asr.map_text(U"捂着流血的胸口慌忙的回答", U"慌忙的回答");
    std::cout << k.size() << std::endl;
    for (int i = 0; i < k.size(); i++) {
        std::cout << k[i] << std::endl;
    }
    
    return 0;
}
