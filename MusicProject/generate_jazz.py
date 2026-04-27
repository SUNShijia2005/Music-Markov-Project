import parse_musicxml
import random
import numpy as np
from midiutil import MIDIFile
import sys
import re
import os
import math  # 引入 math 库用于处理拍子


def find_nearest_above(my_array, target):
    diff = my_array - target
    mask = np.ma.less(diff, 0)
    if np.all(mask):
        return None
    masked_diff = np.ma.masked_array(diff, mask)
    return masked_diff.argmin()


def generate(seq_len, parser):
    sequence = [None] * seq_len

    # 初始状态选择
    note_prob = random.uniform(0, 1)
    note_index = find_nearest_above(parser.normalized_initial_transition_matrix, note_prob)
    check_null_index(note_index, "错误：无法在初始转移矩阵中获取索引")

    sequence[0] = parser.states[note_index]
    curr_index = 1

    while (curr_index < seq_len):
        note_prob = random.uniform(0, 1)
        # 根据当前音符预测下一个音符
        note_index = find_nearest_above(parser.normalized_transition_probability_matrix[note_index], note_prob)
        check_null_index(note_index, "错误：无法在概率转移矩阵中获取索引")

        # 爵士乐不需要像古典那样严格限制大跳，Take The A Train 本身就有很多琶音跳跃，让它自由发挥！
        sequence[curr_index] = parser.states[note_index]
        curr_index += 1

    return sequence


def check_null_index(index, error_message):
    if (index == None):
        print(error_message)
        sys.exit(1)


def get_note_offset_midi_val(note):
    note = note.upper().strip()
    switcher = {
        "C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3,
        "E": 4, "FB": 4, "E#": 5, "F": 5, "F#": 6, "GB": 6,
        "G": 7, "G#": 8, "AB": 8, "A": 9, "A#": 10, "BB": 10,
        "B": 11, "CB": 11
    }
    return switcher.get(note, 0)


def get_pitch(note):
    if note == 'R' or note is None:
        return None

    note_str = str(note)
    octave_info = re.findall(r'\d+', note_str)

    if len(octave_info) > 0:
        octave = int(octave_info[0])
        step_part = ''.join([i for i in note_str if not i.isdigit()]).replace("'", "").replace("(", "").strip()
        base_octave_val = 12 * (octave + 1)
        note_val = base_octave_val + get_note_offset_midi_val(step_part)
        return note_val
    return None


if __name__ == "__main__":
    target_xml = 'TakeTheATrain.musicxml.xml'

    if not os.path.exists(target_xml):
        print(f"❌ 找不到文件: {target_xml}，请确保它在当前文件夹下。")
        sys.exit(1)

    parser = parse_musicxml.Parser(target_xml)
    print(f"🎷 正在处理: {parser.filename} (爵士摇摆模式)...")

    # 爵士乐段落通常较长，可以生成 120 个音符
    seq_length = 120
    sequence = generate(seq_length, parser)

    track = 0
    channel = 0
    time = 0.0

    # 爵士通常速度较快且轻快，默认给个 160 BPM 的 Swing 速度
    tempo = parser.tempo if parser.tempo is not None else 160

    output_midi = MIDIFile(1)
    output_midi.addTempo(track, time, tempo)
    output_midi.addProgramChange(track, channel, time, 0)  # 钢琴

    notes_added = 0
    for sound_obj in sequence:
        rhythm_str = sound_obj[1]
        rhythm_val = parser.rhythm_to_float(rhythm_str)
        duration = float(rhythm_val) if rhythm_val is not None else 1.0

        sound_info = sound_obj[0]
        pitches = []
        if isinstance(sound_info, str):
            p = get_pitch(sound_info)
            if p: pitches.append(p)
        elif isinstance(sound_info, tuple):
            for n in sound_info:
                p = get_pitch(n)
                if p: pitches.append(p)

        # ---------------- 爵士魔法核心逻辑 ----------------

        # 1. 摇摆节奏 (Swing Feel): 2:1 比例模拟
        play_time = time
        play_duration = duration

        # 判断是否在“反拍”上（例如 0.5, 1.5, 2.5 拍）
        is_off_beat = (time % 1.0) >= 0.4 and (time % 1.0) <= 0.6

        # 如果是连续的八分音符 (duration <= 0.5)
        if duration <= 0.5:
            if is_off_beat:
                play_time += 0.15  # 反拍延迟出现，制造慵懒感
                play_duration -= 0.15  # 反拍缩短
            else:
                play_duration += 0.15  # 正拍延长

        # 2. 爵士重音律动 (Backbeat & Syncopation)
        beat_pos = time % 4
        if beat_pos >= 1.0 and beat_pos < 2.0 or beat_pos >= 3.0 and beat_pos < 4.0:
            # 重音在 2、4 拍（也就是军鼓打的点）
            dynamic_volume = 115
        elif (time % 1.0) != 0:
            # 所有反拍/切分音加重力度
            dynamic_volume = 110
        else:
            # 1、3 拍（正拍）弱下来
            dynamic_volume = 85
        # ------------------------------------------------

        for pitch in pitches:
            output_midi.addNote(track, channel, pitch, play_time, play_duration, dynamic_volume)
            notes_added += 1

        time += duration

    # ---------------- 爵士魔法 3：经典六九和弦收尾 ----------------
    # 把结尾时间推到下一个小节的正拍上
    end_time = math.ceil(time)

    # 一个极具大乐团色彩的 C 6/9 和弦 (C, E, G, A, D)
    jazz_ending_chord = [48, 52, 55, 57, 62]
    for p in jazz_ending_chord:
        output_midi.addNote(track, channel, p, end_time, 3.0, 105)
    # -----------------------------------------------------------

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    # 清理一下文件名，让它更好看
    clean_name = target_xml.replace('.musicxml.xml', '').replace('.xml', '')
    output_name = clean_name + "_Jazz_Swing.mid"
    full_save_path = os.path.join(desktop_path, output_name)

    with open(full_save_path, "wb") as output_file:
        output_midi.writeFile(output_file)

    print("-" * 30)
    print(f"✅ 爵士大乐团已就绪！")
    print(f"🎹 写入音符数: {notes_added + 5} (含爵士结尾和弦)")
    print(f"📂 快去桌面听听看: {output_name}")