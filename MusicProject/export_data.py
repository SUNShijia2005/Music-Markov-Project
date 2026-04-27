import os
import pandas as pd
import numpy as np
from parse_musicxml import Parser  # 确保你的 parse_musicxml.py 在同一个目录下


def export_to_excel(xml_file, output_name, top_n=30):
    """
    解析 XML 并将其转移矩阵保存为 Excel
    """
    print(f"正在处理: {xml_file}...")

    # 1. 初始化解析器
    if not os.path.exists(xml_file):
        print(f"❌ 找不到文件: {xml_file}")
        return

    parser = Parser(xml_file)

    # 2. 提取高频音符并排序（按音高排序，这样 Excel 里的顺序也是从低到高）
    sorted_states = sorted(parser.initial_transition_dict.items(), key=lambda x: x[1], reverse=True)
    top_states_raw = [s[0] for s in sorted_states[:top_n]]
    top_states = sorted(top_states_raw, key=lambda x: (x[0][-1], x[0]))
    indices = [parser.states.index(s) for s in top_states]

    # 3. 填充矩阵
    full_matrix = parser.normalized_transition_probability_matrix
    plot_matrix = np.zeros((top_n, top_n))

    for i, idx_from in enumerate(indices):
        cum_row = full_matrix[idx_from]
        for j, idx_to in enumerate(indices):
            current_cum = cum_row[idx_to]
            prev_cum = cum_row[idx_to - 1] if idx_to > 0 else 0
            plot_matrix[i, j] = current_cum - prev_cum

    # 4. 生成 DataFrame 并保存
    labels = [f"{s[0]}/{s[1][0]}" for s in top_states]
    df = pd.DataFrame(plot_matrix, index=labels, columns=labels)

    # 保存到桌面
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    save_path = os.path.join(desktop_path, output_name)

    df.to_excel(save_path)
    print(f"✅ 成功！矩阵已保存至: {save_path}")


if __name__ == "__main__":
    # 在这里填入你想处理的文件名
    # 你可以一次性跑多首曲子
    tasks = [
        ('bach_test.xml', 'Bach_Matrix_Data.xlsx'),
        ('TakeTheATrain.musicxml.xml', 'Jazz_Matrix_Data.xlsx')  # 确保你有这个xml
    ]

    for xml, excel in tasks:
        export_to_excel(xml, excel, top_n=15)  # Excel 可以多存点，设为 30 个音符