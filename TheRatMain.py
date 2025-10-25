# --- Full Script: Smarter Bot with Ping and Pathfinding (Enhanced Logic) ---
import random
import pygame as pg
import sys
import math
import numpy as np

# Constants
n = 30
ALPHA = 0.5
ship = [[0]*n for _ in range(n)]
openCells = []
canChange = []
botCell = []
ratCell = []
botTrail = []
beliefMatrix = [[0 for _ in range(n)] for _ in range(n)]
bot_target = None

# UI Colors
backgroundColor = pg.Color(235, 245, 255)
openColor = pg.Color(200, 200, 200)
closeColor = pg.Color(50, 50, 50)
botColor = pg.Color(50, 200, 50)
ratColor = pg.Color(50, 50, 255)
trailColor = pg.Color(100, 100, 255)

# Dimensions
HEIGHT = 120 + ((n + 2) * 16)
WIDTH = max(900, 50 + ((n + 2) * 16))

# Pygame Initialization
pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('Smart Bot with Ping and Pathfinding')
main_font = pg.font.Font(pg.font.get_default_font(), 10)

# Sound Generation
ping_sound = None
try:
    SAMPLE_RATE = 22050
    DURATION = 0.2
    FREQ = 880
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), False)
    wave = 0.8 * np.sin(2 * np.pi * FREQ * t)
    audio = np.array(wave * 32767, dtype=np.int16)
    stereo = np.stack([audio, audio], axis=-1)
    ping_sound = pg.sndarray.make_sound(stereo)
except Exception as e:
    print("⚠️ Could not load beep sound:", e)

# Button Definitions
button_width = 120
button_height = 45
button_gap = 30
num_buttons = 5
button_total_width = num_buttons * button_width + (num_buttons - 1) * button_gap
button_start_x = (WIDTH - button_total_width) // 2

def make_button(index, text, bg, hover, border, shadow):
    return {
        'pos': (button_start_x + index * (button_width + button_gap), 30), 'size': (button_width, button_height),
        'background_color': bg, 'hover_color': hover, 'border_color': border,
        'text_color': (255, 255, 255), 'text': text, 'font_size': 22,
        'font_style': 'italic', 'font_weight': 'bold', 'border_radius': 18,
        'shadow_offset': 3, 'shadow_color': shadow
    }

generate_button = make_button(0, 'GENERATE', (181, 168, 213), (200, 185, 230), (161, 148, 193), (150, 140, 180))
bot1_button = make_button(1, 'BOT 1 Stationary', (220, 80, 80), (240, 100, 100), (200, 60, 60), (180, 50, 50))
bot2_button = make_button(2, 'BOT 1 OnMove', (70, 130, 180), (100, 160, 210), (50, 110, 160), (40, 100, 140))
bot3_button = make_button(3, 'BOT 2 Stationary', (255, 165, 0), (255, 190, 60), (230, 140, 0), (200, 130, 0))
bot4_button = make_button(4, 'BOT 2 OnMove', (100, 100, 100), (130, 130, 130), (80, 80, 80), (70, 70, 70))

# Button Helpers
def preload_button(button):
    button['text_render'] = main_font.render(button['text'], True, button['text_color'])
    text_rect = button['text_render'].get_rect()
    x, y = button['pos']
    w, h = button['size']
    button['text_pos'] = (x + (w - text_rect.width)//2, y + (h - text_rect.height)//2)

def draw_buttons():
    for button in [generate_button, bot1_button, bot2_button, bot3_button, bot4_button]:
        pg.draw.rect(screen, button['background_color'], (*button['pos'], *button['size']))
        screen.blit(button['text_render'], button['text_pos'])

# Ship Grid Drawing
def generateShip():
    screen.fill(backgroundColor)
    grid_pixel_width = (n + 2) * 16
    grid_start_x = (WIDTH - grid_pixel_width) // 2
    for i in range(n + 2):
        for j in range(n + 2):
            if i == 0 or i == n + 1 or j == 0 or j == n + 1:
                color = closeColor
            else:
                val = ship[i - 1][j - 1]
                color = closeColor if val == 0 else openColor
                if [i - 1, j - 1] in botTrail:
                    color = trailColor
                if botCell and [i - 1, j - 1] == botCell[0]:
                    color = botColor
                elif ratCell and [i - 1, j - 1] == ratCell[0]:
                    color = ratColor
            rect = pg.Rect(grid_start_x + (j * 16), 100 + (i * 16), 16, 16)
            pg.draw.rect(screen, color, rect)
            pg.draw.rect(screen, (180, 180, 180), rect, 1)
    draw_buttons()
    pg.display.flip()

def move_bot_utility():
    global bot_target
    bx, by = botCell[0]
    min_utility = float('inf')
    best_target = botCell[0]

    for i in range(n):
        for j in range(n):
            if ship[i][j] == 0:
                continue
            dist = abs(bx - i) + abs(by - j)
            prob = beliefMatrix[i][j]
            if prob == 0:
                continue
            # Expected cost = movement cost + 1 (sensing) + expected future cost
            expected_cost = dist + 1 + (1 - prob) * 10  # Assuming cost of 10 if sensing fails
            if expected_cost < min_utility:
                min_utility = expected_cost
                best_target = [i, j]

    bot_target = best_target
    path = bfs_path(botCell[0], bot_target)
    return path[0] if path else botCell[0]


# Ship Generation Logic
def checkValidChoices():
    i = 0
    while i < len(canChange):
        x, y = canChange[i]
        openNeighbours = 0
        if x > 0: openNeighbours += ship[x - 1][y]
        if y < n - 1: openNeighbours += ship[x][y + 1]
        if y > 0: openNeighbours += ship[x][y - 1]
        if x < n - 1: openNeighbours += ship[x + 1][y]
        if openNeighbours > 1: canChange.pop(i)
        else: i += 1

def generateOpenCells():
    x = random.randrange(n)
    y = random.randrange(n)
    ship[x][y] = 1
    openCells.append([x, y])
    if x > 0: canChange.append([x - 1, y])
    if x < n - 1: canChange.append([x + 1, y])
    if y > 0: canChange.append([x, y - 1])
    if y < n - 1: canChange.append([x, y + 1])
    while canChange:
        cx, cy = canChange.pop(random.randrange(len(canChange)))
        ship[cx][cy] = 1
        openCells.append([cx, cy])
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < n and 0 <= ny < n and ship[nx][ny] == 0 and [nx, ny] not in canChange:
                canChange.append([nx, ny])
        checkValidChoices()

# Subject Setup and Belief Initialization
def placeSubjects():
    botCell.clear()
    ratCell.clear()
    beliefMatrix[:] = [[0 for _ in range(n)] for _ in range(n)]
    samples = random.sample(openCells, 2)
    botCell.append(samples[0])
    ratCell.append(samples[1])

def initialize_belief():
    total = len(openCells)
    for i, j in openCells:
        beliefMatrix[i][j] = 1 / total

# def get_rat_sensor():
#     bx, by = botCell[0]
#     rx, ry = ratCell[0]
#     dist = abs(bx - rx) + abs(by - ry)
#     if dist == 0:
#         if ping_sound:
#             ping_sound.play()
#         return "ping"
#     prob = math.exp(-ALPHA * (dist - 1))
#     print(f"Sensor Check | Distance: {dist}, Probability: {prob:.4f}")
#     if random.random() < prob:
#         if ping_sound:
#             ping_sound.play()
#         return "ping"
#     return "no ping"


def get_rat_sensor():
    bx, by = botCell[0]
    rx, ry = ratCell[0]
    dist = abs(bx - rx) + abs(by - ry)
    if dist == 0:
        if ping_sound:
            ping_sound.set_volume(1.0)
            ping_sound.play()
        return "ping"
    prob = math.exp(-ALPHA * (dist - 1))
    if random.random() < prob:
        if ping_sound:
            ping_sound.set_volume(1.0)
            ping_sound.play()
        return "ping"
    return "no ping"


def update_belief(sensor):
    bx, by = botCell[0]
    total = 0.0
    likelihoods = [[0 for _ in range(n)] for _ in range(n)]

    # Step 1: Calculate P(S | R_ij) * P(R_ij)
    for i in range(n):
        for j in range(n):
            if ship[i][j] == 0:
                continue

            d = abs(bx - i) + abs(by - j)
            P_S_given_R = math.exp(-ALPHA * (d - 1)) if d > 0 else 1.0  # perfect if same cell
            if sensor == "ping":
                likelihood = P_S_given_R
            else:
                likelihood = 1 - P_S_given_R

            likelihoods[i][j] = likelihood * beliefMatrix[i][j]
            total += likelihoods[i][j]

    # Step 2: Normalize
    if total == 0:
        initialize_belief()
        return

    for i in range(n):
        for j in range(n):
            if ship[i][j] == 0:
                continue
            beliefMatrix[i][j] = likelihoods[i][j] / total


# def update_belief(sensor):
#     bx, by = botCell[0]
#     new_belief = [[0 for _ in range(n)] for _ in range(n)]
#     total = 0
#     for i in range(n):
#         for j in range(n):
#             if ship[i][j] == 0:
#                 continue
#             d = abs(bx - i) + abs(by - j)
#             p = math.exp(-ALPHA * (d - 1)) if d > 0 else 1.0
#             likelihood = p if sensor == "ping" else (1 - p)
#             new_belief[i][j] = beliefMatrix[i][j] * likelihood
#             total += new_belief[i][j]
#     if total == 0:
#         initialize_belief()
#     else:
#         for i in range(n):
#             for j in range(n):
#                 beliefMatrix[i][j] = new_belief[i][j] / total

def find_highest_belief_cell():
    max_val = -1
    target = botCell[0]
    for i in range(n):
        for j in range(n):
            if beliefMatrix[i][j] > max_val and ship[i][j] == 1:
                max_val = beliefMatrix[i][j]
                target = [i, j]
    return target

def bfs_path(start, goal):
    queue = [(start, [])]
    visited = set()
    while queue:
        (x, y), path = queue.pop(0)
        if [x, y] == goal:
            return path
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n and ship[nx][ny] == 1 and (nx, ny) not in visited:
                queue.append(((nx, ny), path + [[nx, ny]]))
    return []


def move_bot():
    bx, by = botCell[0]
    best_score = -1
    best_cell = botCell[0]

    for i in range(n):
        for j in range(n):
            if ship[i][j] == 0:
                continue
            belief = beliefMatrix[i][j]
            dist = abs(bx - i) + abs(by - j)
            score = belief / ((1 + dist) ** 2)
            if score > best_score:
                best_score = score
                best_cell = [i, j]
            elif score == best_score:
                if dist < abs(bx - best_cell[0]) + abs(by - best_cell[1]):
                    best_cell = [i, j]

    # Optional: if belief > 0.8 in any one cell, rush to it
    for i in range(n):
        for j in range(n):
            if beliefMatrix[i][j] > 0.8 and ship[i][j] == 1:
                best_cell = [i, j]
                break

    path = bfs_path(botCell[0], best_cell)
    return path[0] if path else botCell[0]


def move_rat():
    rx, ry = ratCell[0]
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = rx + dx, ry + dy
        if 0 <= nx < n and 0 <= ny < n and ship[nx][ny] == 1:
            ratCell[0] = [nx, ny]
            return

def is_rat_caught():
    bx, by = botCell[0]
    rx, ry = ratCell[0]
    return abs(bx - rx) + abs(by - ry) <= 1

# Preload buttons
for btn in [generate_button, bot1_button, bot2_button, bot3_button, bot4_button]:
    preload_button(btn)

generateShip()
def run_bot1_stationary():
    step = 0
    global bot_target
    bot_target = None
    while True:
        generateShip()
        sensor = get_rat_sensor()
        update_belief(sensor)
        botTrail.append(botCell[0][:])
        botCell[0] = move_bot()
        print(f"Step {step} | Sensor: {sensor} | Bot moved to: {botCell[0]}")
        if is_rat_caught():
            print(f"🎯 Bot caught the rat near {ratCell[0]} at step {step}")
            break
        step += 1
        pg.time.wait(300)

def run_bot1_moving():
    step = 0
    global bot_target
    bot_target = None
    while True:
        generateShip()
        sensor = get_rat_sensor()
        update_belief(sensor)
        botTrail.append(botCell[0][:])
        botCell[0] = move_bot()
        move_rat()
        print(f"Step {step} | Sensor: {sensor} | Bot: {botCell[0]}, Rat: {ratCell[0]}")
        if is_rat_caught():
            print(f"🎯 Bot caught the moving rat at {ratCell[0]} (step {step})")
            break
        step += 1
        pg.time.wait(300)

def run_bot2_stationary():
    step = 0
    global bot_target
    bot_target = None
    while True:
        generateShip()
        sensor = get_rat_sensor()
        update_belief(sensor)
        botTrail.append(botCell[0][:])
        botCell[0] = move_bot_utility()
        print(f"[BOT 2 | Static Rat] Step {step} | Sensor: {sensor} | Bot: {botCell[0]}")
        if is_rat_caught():
            print(f"🎯 BOT 2 caught the rat at {ratCell[0]} (step {step})")
            break
        step += 1
        pg.time.wait(300)

def run_bot2_moving():
    step = 0
    global bot_target
    bot_target = None
    while True:
        generateShip()
        sensor = get_rat_sensor()
        update_belief(sensor)
        botTrail.append(botCell[0][:])
        botCell[0] = move_bot_utility()
        move_rat()
        print(f"[BOT 2 | Moving Rat] Step {step} | Sensor: {sensor} | Bot: {botCell[0]}, Rat: {ratCell[0]}")
        if is_rat_caught():
            print(f"🎯 BOT 2 caught the moving rat at {ratCell[0]} (step {step})")
            break
        step += 1
        pg.time.wait(300)


# Main Loop
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            pg.quit()
            sys.exit()

        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_pos = pg.mouse.get_pos()

            def clicked(button):
                x, y = button['pos']
                w, h = button['size']
                return x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h
            
            if clicked(generate_button):
                openCells.clear()
                canChange.clear()
                botTrail.clear()
                bot_target = None

                for i in range(n):
                    for j in range(n):
                        ship[i][j] = 0

                generateOpenCells()
                placeSubjects()
                initialize_belief()
                generateShip()  # Redraw after generation


            if clicked(bot1_button) and len(botCell):
                run_bot1_stationary()

            if clicked(bot2_button) and len(botCell):
                run_bot1_moving()

            if clicked(bot3_button) and len(botCell):
                run_bot2_stationary()

            if clicked(bot4_button) and len(botCell):
                run_bot2_moving()


