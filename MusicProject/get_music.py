from music21 import corpus
import os


def fetch_bach_score(work_name='bach/bwv846', output_name='bach_test.xml'):
    print(f"正在从 music21 库加载: {work_name}...")

    try:
        bach_score = corpus.parse(work_name)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(current_dir, output_name)

        bach_score.write('musicxml', fp=save_path)

        print(f"文件已保存至: {save_path}")

    except Exception as e:
        print(f"出错啦: {e}")


if __name__ == "__main__":
    fetch_bach_score('bach/bwv26.6')
