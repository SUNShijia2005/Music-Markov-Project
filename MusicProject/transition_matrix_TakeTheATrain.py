import os
import numpy as np
import pandas as pd
from parse_musicxml import Parser


parser = Parser('TakeTheATrain.musicxml.xml')


def export_full_matrix_to_excel(parser):

    all_states = parser.states
    labels = [f"{s[0]}/{s[1][0]}" for s in all_states]

    n = len(all_states)
    full_cum_matrix = parser.normalized_transition_probability_matrix

    # Prob(j) = CumulativeProb(j) - CumulativeProb(j-1)
    prob_matrix = np.zeros((n, n))

    for i in range(n):
        cum_row = full_cum_matrix[i]
        for j in range(n):
            current_cum = cum_row[j]
            prev_cum = cum_row[j - 1] if j > 0 else 0
            prob_matrix[i, j] = current_cum - prev_cum

    # Index: current note，Columns: next note
    df = pd.DataFrame(prob_matrix, index=labels, columns=labels)

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_name = "TakeTheATrain_Full_Transition_Matrix.xlsx"
    save_path = os.path.join(desktop_path, file_name)

    try:
        df.to_excel(save_path, index=True, sheet_name='Transition Matrix')
        print(f"成功！完整矩阵（{n}x{n}）已保存至桌面：")
        print(f"路径: {save_path}")
    except Exception as e:
        print(f"保存失败: {e}")
        df.to_excel(file_name)
        print(f"已转为保存在项目根目录: {file_name}")


if __name__ == "__main__":
    export_full_matrix_to_excel(parser)
