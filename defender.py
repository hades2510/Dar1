import time
import random
import math
import vec

from constants import *
from init import display, read_input
from audio import play_tune_with_volume, mute_sound

BULLET_SPEED = 3

ROT_SPEED = 5
FRAME_MS = 40
BARREL_LENGTH = 6
ENEMY_SPEED = 0.2
ENEMY_SPAWN_RATE = 1.5
ENEMY_SIZE = 2

SHOW_DEBUG = True
ENABLE_SOUNDS = False

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

def draw():
    for obj in objects:
        if obj['type'] == 'rect':
            display.rect(obj['x'] - 3, obj['y'] - 3, 6, 6, OUTLINE_COLOR)
        if obj['type'] == 'line':
            display.line(obj['x'], obj['y'], obj['xe'], obj['ye'], OUTLINE_COLOR)
        if obj['type'] == 'circle':
            display.ellipse(round(obj['x']), round(obj['y']), obj['r'], obj['r'], OUTLINE_COLOR)
    for bullet in bullets:
        display.ellipse(round(bullet['x']), round(bullet['y']), 1, 1, OUTLINE_COLOR, True)

def physics():
    global bullets
    global is_game_over
    global score
    global objects

    for bullet in bullets:
        bullet['x'] = bullet['x'] + bullet['xs']
        bullet['y'] = bullet['y'] + bullet['ys']

    for obj in objects:
        if obj['type'] == 'circle':
            obj['x'] = obj['x'] + obj['xs']
            obj['y'] = obj['y'] + obj['ys']
            
            # check for game over
            if obj['x'] >= HALF_WIDTH - 3 and obj['x'] <= HALF_WIDTH + 3 and obj['y'] >= HALF_HEIGHT - 3 and obj['y'] <= HALF_HEIGHT + 3:
                is_game_over = True
                play_tune_with_volume(GAME_OVER_TUNE)

    bullets = [bullet for bullet in bullets if bullet['x'] >= 0 and bullet['y'] >=0 and bullet['x'] <= WIDTH and bullet['y'] <= HEIGHT]
    
    # check if we have a hit
    for bullet in bullets:
        for obj in objects:
            if obj['type'] == 'circle':
                travelVec={'x': bullet['xs'], 'y': bullet['ys']}
                prevPos = vec.sub(bullet, travelVec)
                proj = vec.add(vec.proj(vec.sub(obj, prevPos), vec.sub(bullet, prevPos)), prevPos)
                #	need to see if the proj is inside the line seg
                distToPrev = vec.dist(proj, prevPos)
                distToCurrent = vec.dist(proj, bullet)
                if math.fabs( vec.magnitude(travelVec) - distToPrev - distToCurrent ) < 0.1:
                    dist = vec.dist(proj, obj)
                    if dist <= obj['r']:
                        bullet['remove'] = True
                        obj['remove'] = True
                        score = score + 1
                        
                        play_tune_with_volume([["C3", 150, 100/127], ["C4", 80, 90/127], ["FS3", 200, 80/127]])

    
    # clean up objects
    bullets = [bullet for bullet in bullets if bullet.get('remove', False) == False]
    objects = [obj for obj in objects if obj.get('remove', False) == False]
        
def adjust_barrel(rot):
    global barrel
    angle = rot * 3.1415 / 180
    
    barrel['xe'] = barrel['x'] + int(math.cos(angle) * BARREL_LENGTH)
    barrel['ye'] = barrel['y'] + int(math.sin(angle) * BARREL_LENGTH)

def do_ai():
    r = random.random() * 100
    if r < ENEMY_SPAWN_RATE:
        pos = random.randrange(2 * WIDTH + 2 * HEIGHT)
        x = 0
        y = 0
        
        if pos <= WIDTH:
            x = pos
        if pos > WIDTH and pos <= WIDTH + HEIGHT:
            x = WIDTH
            y = pos - WIDTH
        if pos > WIDTH + HEIGHT and pos <= 2 * WIDTH + HEIGHT:
            x = pos - WIDTH + HEIGHT
            y = HEIGHT
        if pos > 2 * WIDTH + HEIGHT:
            y = pos - (2 * WIDTH + HEIGHT)
            
        dist = math.sqrt( (x-HALF_WIDTH)*(x-HALF_WIDTH) + (y-HALF_HEIGHT)*(y-HALF_HEIGHT))
            
        xs = (HALF_WIDTH-x)/dist * ENEMY_SPEED
        ys = (HALF_HEIGHT-y)/dist * ENEMY_SPEED

        objects.append({
            'type': 'circle',
            'x': x,
            'y': y,
            'r': 2,
            'xs': xs,
            'ys': ys
        })
    pass

def show_hud():
    display.text(f'S:{score: >3}', WIDTH-40, 0)

def show_debug():
    display.text(f'fps: {debug["fps"]:.0f}', 0, 0)
    display.text(f'rot: {debug["rot"]}', 0, 10)

def render_thread(id):
    #display_lock.acquire()

    display.fill(0)

    draw()
    show_hud()

    if SHOW_DEBUG == True:
        show_debug()

    display.show()
    
    #display_lock.release()
    
    return
    

barrel = {
    'type': 'line',
    'x': HALF_WIDTH,
    'y': HALF_HEIGHT,
    'xe': HALF_WIDTH + BARREL_LENGTH,
    'ye': HALF_HEIGHT
}
objects = [{'x': HALF_WIDTH, 'y': HALF_HEIGHT, 'type': 'rect'}, barrel]
bullets = []

was_button_pressed = False

render_frame = False

current_rot = 0

score = 0
is_game_over = False

debug = {
    'fps': 0,
    'rot': 0
}

#display_lock = _thread.allocate_lock()

while True:
    #display_lock.acquire()
    start_time = time.ticks_ms()

    rot, is_pressed = read_input()

    if is_game_over == True:
        display.fill(0)
        display.text('GAME OVER', HALF_WIDTH - 30, HALF_HEIGHT - 10)
        display.text(f'SCORE:{score: >2}', HALF_WIDTH - 25, HALF_HEIGHT)
        display.show()
        
        mute_sound()
        break

    adjust_barrel(rot)
        
    if is_pressed:
        if was_button_pressed == False:
            was_button_pressed = True
            angle = rot * 3.1415 / 180
            bullets.append({
                'x': HALF_WIDTH,
                'y': HALF_HEIGHT,
                'xs': BULLET_SPEED * math.cos(angle),
                'ys': BULLET_SPEED * math.sin(angle),
            })
            play_tune_with_volume([["G5", 60, 100/127], ["G5", 50, 110/127], ["C2", 120, 90/127]])
    else:
        was_button_pressed = False
        
    
    do_ai()
    physics()

    end_time = time.ticks_ms()

    msec_frame = end_time-start_time
    if msec_frame != 0:
        debug['fps'] = 1000/(msec_frame)
    else:
        debug['fps'] = 1234
    debug['rot'] = rot
    
    #display_lock.release()
    #_thread.start_new_thread(render_thread, (2,))
    render_thread(2)
    
    time.sleep((FRAME_MS - msec_frame)/1000)
