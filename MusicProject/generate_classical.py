import parse_musicxml
import random
import numpy as np
import sys
import re
import os
from midiutil import MIDIFile

def find_nearest_above(my_array, target):
    diff = my_array - target
    mask = np.ma.less(diff, 0)
    if np.all(mask):
        return None
    masked_diff = np.ma.masked_array(diff, mask)
    return masked_diff.argmin()

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
    if note == 'R' or note is None: return None
    note_str = str(note)
    octave_info = re.findall(r'\d+', note_str)
    if len(octave_info) > 0:
        octave = int(octave_info[0])
        step_part = ''.join([i for i in note_str if not i.isdigit()]).replace("'", "").replace("(", "").strip()
        return 12 * (octave + 1) + get_note_offset_midi_val(step_part)
    return None


# core generating logic
def generate(seq_len, parser):
    sequence = [None] * seq_len
    idx = 0
    sequence[0] = parser.states[idx]

    curr_index = 1
    while curr_index < seq_len:
        best_next_idx = None
        attempts = 0

        while attempts < 15:
            note_prob = random.uniform(0, 1)
            next_idx = find_nearest_above(parser.normalized_transition_probability_matrix[idx], note_prob)

            if next_idx is None:
                attempts += 1
                continue

            prev_note_raw = sequence[curr_index - 1][0]
            curr_note_raw = parser.states[next_idx][0]

            prev_p = get_pitch(prev_note_raw[0] if isinstance(prev_note_raw, tuple) else prev_note_raw)
            curr_p = get_pitch(curr_note_raw[0] if isinstance(curr_note_raw, tuple) else curr_note_raw)

            if prev_p and curr_p:
                interval = abs(prev_p - curr_p)

                if interval > 12:
                    if random.random() < 0.9:
                        attempts += 1
                        continue

                if interval == 0:
                    if random.random() < 0.7:
                        attempts += 1
                        continue

            best_next_idx = next_idx
            break

        if best_next_idx is None:
            best_next_idx = parser.normalized_transition_probability_matrix[idx].argmax()

        sequence[curr_index] = parser.states[best_next_idx]
        idx = best_next_idx
        curr_index += 1

    return sequence

if __name__ == "__main__":
    target_xml = 'bach_test.xml'
    if not os.path.exists(target_xml):
        print(f"❌ 找不到文件: {target_xml}")
        sys.exit(1)

    parser = parse_musicxml.Parser(target_xml)
    print(f"正在处理: {parser.filename}")

    seq_length = 120
    sequence = generate(seq_length, parser)

    output_midi = MIDIFile(1)
    track, channel, time = 0, 0, 0.0
    tempo = parser.tempo if parser.tempo is not None else 85
    output_midi.addTempo(track, time, tempo)
    output_midi.addProgramChange(track, channel, time, 0) 

    notes_added = 0
    for sound_obj in sequence:
        rhythm_val = parser.rhythm_to_float(sound_obj[1])
        duration = float(rhythm_val) if rhythm_val is not None else 1.0

        grid_time = round(time * 4) 
        if grid_time % 16 == 0: 
            dynamic_volume = 112
        elif grid_time % 8 == 0: 
            dynamic_volume = 98
        elif grid_time % 4 == 0: 
            dynamic_volume = 85
        else:  
            dynamic_volume = 72

        sound_info = sound_obj[0]
        pitches = []
        if isinstance(sound_info, str):
            p = get_pitch(sound_info)
            if p: pitches.append(p)
        elif isinstance(sound_info, tuple):
            for n in sound_info:
                p = get_pitch(n)
                if p: pitches.append(p)

        for pitch in pitches:
            output_midi.addNote(track, channel, pitch, time, duration, dynamic_volume)
            notes_added += 1

        time += duration

    last_p = None
    for item in reversed(sequence):
        info = item[0]
        p = get_pitch(info[0] if isinstance(info, tuple) else info)
        if p:
            last_p = p
            break

    if last_p:
        base_tonic = (last_p % 12) + 48
        output_midi.addNote(track, channel, base_tonic, time, 4.0, 105)
        output_midi.addNote(track, channel, base_tonic + 12, time, 4.0, 105)

    
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_name = target_xml.replace('.xml', '') + "_refined_classical.mid"
    full_save_path = os.path.join(desktop_path, output_name)

    with open(full_save_path, "wb") as output_file:
        output_midi.writeFile(output_file)

    print("-" * 30)
    print(f"总计: {notes_added + 2} 个音符")
    print(f"导出路径: {full_save_path}")
