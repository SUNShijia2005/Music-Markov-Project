import os
import numpy as np
import pandas as pd
from parse_musicxml import Parser

# 1. 初始化并解析
parser = Parser('bach_test.xml')


def export_full_matrix_to_excel(parser):
    """
    将完整的状态转移矩阵导出为 Excel
    """
    # 1. 获取所有的状态及其标签
    # 格式化标签，例如 "C4/0.5" (音高/时长)
    all_states = parser.states
    labels = [f"{s[0]}/{s[1][0]}" for s in all_states]

    n = len(all_states)
    full_cum_matrix = parser.normalized_transition_probability_matrix

    # 2. 将累加概率矩阵还原为单步概率矩阵
    # 逻辑：Prob(j) = CumulativeProb(j) - CumulativeProb(j-1)
    prob_matrix = np.zeros((n, n))

    for i in range(n):
        cum_row = full_cum_matrix[i]
        for j in range(n):
            current_cum = cum_row[j]
            prev_cum = cum_row[j - 1] if j > 0 else 0
            prob_matrix[i, j] = current_cum - prev_cum

    # 3. 创建 Pandas DataFrame
    # 行索引 (Index) 代表“当前音符”，列索引 (Columns) 代表“下一个音符”
    df = pd.DataFrame(prob_matrix, index=labels, columns=labels)

    # 4. 设定保存路径（Mac 桌面）
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_name = "Bach_Full_Transition_Matrix.xlsx"
    save_path = os.path.join(desktop_path, file_name)

    # 5. 导出
    try:
        # 使用 xlsxwriter 引擎可以更好地处理格式，如果没有安装，默认引擎也可以
        df.to_excel(save_path, index=True, sheet_name='Transition Matrix')
        print(f"✅ 成功！完整矩阵（{n}x{n}）已保存至桌面：")
        print(f"路径: {save_path}")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        # 如果桌面保存失败，尝试保存在当前脚本目录下
        df.to_excel(file_name)
        print(f"已转为保存在项目根目录: {file_name}")


if __name__ == "__main__":
    print("--- 正在提取完整矩阵并转换格式... ---")

    # 执行导出函数
    export_full_matrix_to_excel(parser)

    print("\n--- 任务完成！ ---")