import pydirectinput
import keyboard
import time
import re
import random
import threading
import tkinter as tk
from tkinter import filedialog

# ==== Configuration ====
TEMPO_BPM = 300                  # Initial tempo
NOTE_DURATION = 30 / TEMPO_BPM   # Seconds per note
ERROR_CHANCE = 0.0               # Chance to simulate typing error
DEBUG = True                     # Toggle debug prints

# ==== Nearby Key Map ====
NEARBY_KEYS = {
    'q': 'was', 'w': 'qase', 'e': 'wsdr', 'r': 'edft', 't': 'rfgy', 'y': 'tghu', 'u': 'yhji', 'i': 'ujko', 'o': 'iklp', 'p': 'ol', 'a': 'qwsz', 's': 'qwedxza', 'd': 'ersfcx', 'f': 'rtdgvc', 'g': 'tfhbv', 'h': 'gyjnvb', 'j': 'huikmn', 'k': 'jiolm', 'l': 'kop', 'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk', '1': '2q', '2': '13w', '3': '24e', '4': '35r', '5': '46t', '6': '57y', '7': '68u', '8': '79i', '9': '80o', '0': '9p'
}

def ask_for_file():
    root = tk.Tk()
    root.withdraw() 
    file_path = filedialog.askopenfilename(
        title="Select song text file",
        filetypes=[("Text Files", "*.txt")]
    )
    return file_path

def load_song(filename):
    with open(filename, 'r') as file:
        raw = file.read()
        return re.findall(r'\[[^\[\]]+\]|[^\s]', raw)

def maybe_make_error(note):
    if random.random() < ERROR_CHANCE:
        note_lower = note.lower()
        if note_lower in NEARBY_KEYS:
            wrong_key = random.choice(NEARBY_KEYS[note_lower])
            if DEBUG:
                print(f"Simulated error: '{wrong_key}' instead of '{note}'")
            pydirectinput.press(wrong_key)
        else:
            wrong_key = random.choice('asdfghjklqwertyuiopzxcvbnm1234567890')
            if DEBUG:
                print(f"No nearby key for '{note}', random error: '{wrong_key}'")
            pydirectinput.press(wrong_key)
        time.sleep(0.05)
        return True
    return False

def press_keys_simultaneously(keys):
    if DEBUG:
        print(f"Chord: {keys}")
    threads = [threading.Thread(target=pydirectinput.keyDown, args=(key,)) for key in keys]
    for t in threads: t.start()
    for t in threads: t.join()
    time.sleep(0.01)
    threads = [threading.Thread(target=pydirectinput.keyUp, args=(key,)) for key in keys]
    for t in threads: t.start()
    for t in threads: t.join()

def play_song(notes):
    global TEMPO_BPM, NOTE_DURATION
    i = 0
    paused = False

    print("Starting in 5 seconds...")
    time.sleep(5)
    print("Playing. Press 'p' to pause/resume, 'esc' to stop, '+' / '-' to change tempo.")

    while i < len(notes):
        if keyboard.is_pressed('esc'):
            print("\nStopped.")
            break

        if keyboard.is_pressed('p'):
            paused = not paused
            print("\nPaused." if paused else "\nResumed.")
            while keyboard.is_pressed('p'):
                time.sleep(0.1)
            time.sleep(0.3)
            continue

        if keyboard.is_pressed('+'):
            TEMPO_BPM += 10
            NOTE_DURATION = 60 / TEMPO_BPM
            print(f"\nTempo increased to {TEMPO_BPM} BPM")
            while keyboard.is_pressed('+'):
                time.sleep(0.1)

        if keyboard.is_pressed('-'):
            TEMPO_BPM = max(10, TEMPO_BPM - 10)
            NOTE_DURATION = 60 / TEMPO_BPM
            print(f"\nTempo decreased to {TEMPO_BPM} BPM")
            while keyboard.is_pressed('-'):
                time.sleep(0.1)

        if paused:
            time.sleep(0.1)
            continue

        note = notes[i]

        if note == '|':
            time.sleep(NOTE_DURATION)
        elif note.startswith('[') and note.endswith(']'):
            keys = list(note[1:-1].replace(" ", ""))
            press_keys_simultaneously(keys)
            time.sleep(NOTE_DURATION)
        else:
            if not maybe_make_error(note):
                if DEBUG:
                    print(f"Note: {note}")
                pydirectinput.press(note)
            time.sleep(NOTE_DURATION)

        i += 1

if __name__ == "__main__":
    try:
        FILENAME = ask_for_file()
        if not FILENAME:
            print("No file selected, exiting.")
            exit()
        if DEBUG:
            print(f"Selected song file: {FILENAME}")
        song_notes = load_song(FILENAME)
        play_song(song_notes)
    except FileNotFoundError:
        print(f"ERROR: File not found — {FILENAME}")
    except KeyboardInterrupt:
        print("\nPlayback manually interrupted.")
