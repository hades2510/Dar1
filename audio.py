from machine import Pin, PWM, Timer

tones = {
    "B0": 31,
    "C1": 33,
    "CS1": 35,
    "D1": 37,
    "DS1": 39,
    "E1": 41,
    "F1": 44,
    "FS1": 46,
    "G1": 49,
    "GS1": 52,
    "A1": 55,
    "AS1": 58,
    "B1": 62,
    "C2": 65,
    "CS2": 69,
    "D2": 73,
    "DS2": 78,
    "E2": 82,
    "F2": 87,
    "FS2": 93,
    "G2": 98,
    "GS2": 104,
    "A2": 110,
    "AS2": 117,
    "B2": 123,
    "C3": 131,
    "CS3": 139,
    "D3": 147,
    "DS3": 156,
    "E3": 165,
    "F3": 175,
    "FS3": 185,
    "G3": 196,
    "GS3": 208,
    "A3": 220,
    "AS3": 233,
    "B3": 247,
    "C4": 262,
    "CS4": 277,
    "D4": 294,
    "DS4": 311,
    "E4": 330,
    "F4": 349,
    "FS4": 370,
    "G4": 392,
    "GS4": 415,
    "A4": 440,
    "AS4": 466,
    "B4": 494,
    "C5": 523,
    "CS5": 554,
    "D5": 587,
    "DS5": 622,
    "E5": 659,
    "F5": 698,
    "FS5": 740,
    "G5": 784,
    "GS5": 831,
    "A5": 880,
    "AS5": 932,
    "B5": 988,
    "C6": 1047,
    "CS6": 1109,
    "D6": 1175,
    "DS6": 1245,
    "E6": 1319,
    "F6": 1397,
    "FS6": 1480,
    "G6": 1568,
    "GS6": 1661,
    "A6": 1760,
    "AS6": 1865,
    "B6": 1976,
    "C7": 2093,
    "CS7": 2217,
    "D7": 2349,
    "DS7": 2489,
    "E7": 2637,
    "F7": 2794,
    "FS7": 2960,
    "G7": 3136,
    "GS7": 3322,
    "A7": 3520,
    "AS7": 3729,
    "B7": 3951,
    "C8": 4186,
    "CS8": 4435,
    "D8": 4699,
    "DS8": 4978
}

GAME_OVER_TUNE=[
    ["C5", 250, 100/127],
    ["E5", 250, 100/127],
    ["G5", 250, 100/127],
    ["C6", 250, 100/127],

    ["B5", 250, 100/127],
    ["A5", 250, 100/127],
    ["F5", 250, 100/127],
    ["C5", 250, 100/127],

    ["E5", 250, 100/127],
    ["G5", 250, 100/127],
    ["B5", 250, 100/127],
    ["E6", 250, 100/127],

    ["C6", 250, 100/127],
    ["D6", 250, 110/127],
    ["C6", 500, 100/127],

    ["C3", 1000, 90/127],

    ["F3", 250, 90/127],
    ["E3", 250, 90/127],
    ["D3", 250, 90/127],
    ["C3", 250, 90/127],
    ["C3", 250, 80/127],
]

SAMPLING_RATE = 11025
PERIOD_MS = 1000 / SAMPLING_RATE
_MAX_VOLUME = 1 << 15

speaker = None

timer = Timer()

_current_volume = 0
_next_cb = lambda *args: None

def volume(val):
    global _current_volume
    _current_volume = val
    speaker.duty_u16(int(_MAX_VOLUME * val))
    
def _set_volume():
    speaker.duty_u16(int(_MAX_VOLUME * _current_volume))

def init(speaker_pin):
    global speaker
        
    speaker = PWM(Pin(speaker_pin))
    speaker.duty_u16(0)
    
def _end_one_time_timer(t):
    speaker.duty_u16(0)
    _next_cb()

def play_sound(freq, duration):
    _set_volume()
    speaker.freq(freq)

    timer.init(mode=Timer.ONE_SHOT, period=duration, callback=_end_one_time_timer)
    
def play_note(note, duration):
    play_sound(tones[note], duration)
    
def play_silence(duration):
    timer.init(mode=Timer.ONE_SHOT, period=duration, callback=_end_one_time_timer)
    
def play_tune(notes, tempo, repeat=1):
    global _next_cb
    
    current = 1

    def next_note():
        nonlocal current
        nonlocal repeat

        if current >= len(notes):
            # if repeat, do it again
            if repeat > 0:
                repeat = repeat - 1
                current = 1
                play_note(notes[0], tempo)
            else:
                _next_cb = lambda *args: None
            return

        if notes[current] == "P":
            play_silence(tempo)
        else:
            play_note(notes[current], tempo)
        current = current + 1
    
    _next_cb = next_note

    play_note(notes[0], tempo)
    repeat = repeat - 1
    
def play_tune_with_volume(notes):
    global _next_cb

    current = 1
    
    def next_note():
        nonlocal current
        
        if current >= len(notes):
            _next_cb = lambda *args: None
            return
        
        if notes[current][0] == "P":
            play_silence(notes[current][1])
        else:
            volume(notes[current][2])
            play_note(notes[current][0], notes[current][1])
            
        current = current + 1

    _next_cb = next_note
    play_note(notes[0][0], notes[0][1])


def mute_sound():
    volume(0)
    
def test():
    import time

    init(26)
    volume(0.10)
    
    play_note("A6", 500)
    time.sleep(0.5)
    
    play_sound(450, 1000)
    time.sleep(1)
    
    play_tune(["E5","G5","A5","P","E5","G5","B5","A5","P","E5","G5","A5","P","G5","E5", "P", "P"], 200, 3)
    time.sleep(11)
    
    play_tune_with_volume([["G5", 80, 90/127], ["G5", 60, 100/127], ["C2", 150, 80/127], ["G3", 400, 40/127]])
    volume(0)
