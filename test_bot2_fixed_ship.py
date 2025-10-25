import random
import math
import csv

n = 30

ship = [[0]*n for _ in range(n)]
openCells = []
canChange = []
botCell = []
ratCell = []
beliefMatrix = [[0 for _ in range(n)] for _ in range(n)]

def generateOpenCells():
    openCells.clear()
    canChange.clear()
    for i in range(n):
        for j in range(n):
            ship[i][j] = 0
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

def placeSubjects():
    botCell.clear()
    ratCell.clear()
    samples = random.sample(openCells, 2) 
    botCell.append(samples[0])
    ratCell.append(samples[1])

def initialize_belief():
    total = len(openCells)
    for i, j in openCells:
        beliefMatrix[i][j] = 1 / total

def get_sensor(alpha):
    bx, by = botCell[0]
    rx, ry = ratCell[0]
    dist = abs(bx - rx) + abs(by - ry)
    if dist == 0:
        return "ping"
    prob = math.exp(-alpha * (dist - 1))
    return "ping" if random.random() < prob else "no ping"

def update_belief(sensor, alpha):
    bx, by = botCell[0]
    total = 0.0
    likelihoods = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if ship[i][j] == 0:
                continue
            d = abs(bx - i) + abs(by - j)
            P_S_given_R = math.exp(-alpha * (d - 1)) if d > 0 else 1.0
            likelihood = P_S_given_R if sensor == "ping" else (1 - P_S_given_R)
            likelihoods[i][j] = likelihood * beliefMatrix[i][j]
            total += likelihoods[i][j]
    if total == 0:
        initialize_belief()
    else:
        for i in range(n):
            for j in range(n):
                if ship[i][j] == 0:
                    continue
                beliefMatrix[i][j] = likelihoods[i][j] / total

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

def move_bot_utility(alpha):
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

def run_simulation(alpha, moving_rat=True):
    placeSubjects()
    initialize_belief()
    step = 0
    ping_count = 0
    while True:
        sensor = get_sensor(alpha)
        if sensor == "ping":
            ping_count += 1
        update_belief(sensor, alpha)
        botCell[0] = move_bot_utility(alpha)
        if moving_rat:
            move_rat()
        step += 1
        if is_rat_caught() or step > 100:
            return step, ping_count

# Main experiment
results = []
generateOpenCells()
alphas = [round(i * 0.05, 2) for i in range(21)]




for alpha in alphas:
    for trial in range(100):
        steps, pings = run_simulation(alpha, moving_rat=True)
        results.append([alpha, trial+1, steps, pings])

with open("bot2_ratMoving_fixedship_100runs.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Alpha", "Trial", "Steps", "Pings"])
    writer.writerows(results)
