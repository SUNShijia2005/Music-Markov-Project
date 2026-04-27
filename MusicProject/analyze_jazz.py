import os
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import numpy as np
import pandas as pd
from parse_musicxml import Parser

# 1. 初始化并解析
parser = Parser('TakeTheATrain.musicxml.xml')


def show_transition_matrix(parser, top_n=12):
    """
    展示状态转移矩阵的高频部分
    """
    # 找出作品中出现频率最高的前 N 个状态（音高+时长组合）
    sorted_states = sorted(parser.initial_transition_dict.items(), key=lambda x: x[1], reverse=True)
    top_states = [s[0] for s in sorted_states[:top_n]]

    # 获取这些高频状态在 parser.states 中的索引
    indices = [parser.states.index(s) for s in top_states]

    # 打印表头 (目标状态)
    print(f"\n{'[转移概率矩阵]':^80}")
    header = "从 \ 到".ljust(18)
    for s in top_states:
        label = f"{s[0]}/{s[1][0]}"
        header += f"{label:>10}"
    print(header)
    print("-" * len(header))

    # 打印每一行 (起始状态)
    for i, idx_from in enumerate(indices):
        state_from = top_states[i]
        row_label = f"{state_from[0]}/{state_from[1][0]}".ljust(15) + " |"

        row_probs = ""
        for j, idx_to in enumerate(indices):
            cum_row = parser.normalized_transition_probability_matrix[idx_from]
            current_cum = cum_row[idx_to]
            prev_cum = cum_row[idx_to - 1] if idx_to > 0 else 0
            prob = current_cum - prev_cum

            if prob > 0.005:
                row_probs += f"{prob:10.2f}"
            else:
                row_probs += f"{'.':>10}"

        print(row_label + row_probs)


def draw_heatmap(parser, top_n=20):
    """
    绘制热力图并直接保存到 Mac 桌面
    """
    # 1. 选出前 N 个高频音符
    sorted_states = sorted(parser.initial_transition_dict.items(), key=lambda x: x[1], reverse=True)
    top_states_raw = [s[0] for s in sorted_states[:top_n]]

    # 2. 对这 N 个音符按音高进行二次排序
    top_states = sorted(top_states_raw, key=lambda x: (x[0][-1], x[0]))
    indices = [parser.states.index(s) for s in top_states]

    full_matrix = parser.normalized_transition_probability_matrix
    plot_matrix = np.zeros((top_n, top_n))

    for i, idx_from in enumerate(indices):
        cum_row = full_matrix[idx_from]
        for j, idx_to in enumerate(indices):
            current_cum = cum_row[idx_to]
            prev_cum = cum_row[idx_to - 1] if idx_to > 0 else 0
            plot_matrix[i, j] = current_cum - prev_cum

    labels = [f"{s[0]}/{s[1][0]}" for s in top_states]
    df = pd.DataFrame(plot_matrix, index=labels, columns=labels)

    # 2. 绘图设置
    plt.figure(figsize=(14, 12))
    sns.set_style("white")

    colors = ['#FFFFFF', '#D1DBE4', '#85A1BA', '#4A6984']
    custom_blue_cmap = LinearSegmentedColormap.from_list('custom_blue', colors, N=256)

    annot_data = df.map(lambda v: f"{v:.2f}" if v > 0 else "")
    ax = sns.heatmap(
        df,
        annot=annot_data,
        fmt="",
        cmap=custom_blue_cmap,
        cbar_kws={'label': 'Probability P(Next | Current)'},
        linewidths=2,
        linecolor='white',
        square=True,
        annot_kws={"size": 10, "weight": "bold", "color": "#333333"}
    )

    # 加标签
    ax.set_xlabel('Next Note', fontsize=15, weight='bold', color='#555555')
    ax.set_ylabel('Current Note', fontsize=15, weight='bold', color='#555555')

    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.yticks(rotation=0, fontsize=11)

    plt.tight_layout()

    # 3. 保存到桌面核心代码
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    save_path = os.path.join(desktop_path, "Take_The_A_Train.png")

    print(f"正在尝试保存图片到: {save_path}")
    plt.savefig(save_path, dpi=300)
    plt.savefig("Take_The_A_Train.png", dpi=300)

    plt.close()
    print("✅ 图片已保存到桌面和项目文件夹中！")


if __name__ == "__main__":
    # 1. 打印文本矩阵
    show_transition_matrix(parser)

    # 2. 生成并保存热力图
    print("\n--- 开始执行绘图程序... ---")
    draw_heatmap(parser, top_n=15)

    print("\n--- 全部任务完成！ ---")