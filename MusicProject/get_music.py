from music21 import corpus
import os


def fetch_bach_score(work_name='bach/bwv846', output_name='bach_test.xml'):
    """
    从 music21 库中获取巴赫作品并保存为本地 musicxml 文件
    """
    print(f"正在从 music21 库加载: {work_name}...")

    try:
        # 获取作品
        bach_score = corpus.parse(work_name)

        # 写入本地文件
        # 获取当前脚本所在目录，确保文件保存在正确位置
        current_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(current_dir, output_name)

        bach_score.write('musicxml', fp=save_path)

        print(f"✅ 成功！文件已保存至: {save_path}")
        print(f"现在你可以运行你的分析程序来生成热力图了。")

    except Exception as e:
        print(f"❌ 出错啦: {e}")


if __name__ == "__main__":
    fetch_bach_score('bach/bwv26.6')