import pygame, sys, math, heapq, random
import pygame_gui

pygame.init()
WIDTH, HEIGHT, GRID_SIZE = 1200, 700, 20
CIRCLE_RADIUS, OBSTACLE_SIZE = 25, (100, 60)
BACKGROUND_COLOR, BUTTON_COLOR, CIRCLE_COLOR, PATH_COLOR, OBSTACLE_COLOR, LINE_COLOR = (240, 240, 240), (51, 51, 51), (60, 60, 60), (60, 60, 60), (66, 100, 244), (200, 200, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Interactive Path-Finder")

manager = pygame_gui.UIManager((WIDTH, HEIGHT))

font = pygame.font.SysFont('Arial', 24)
highlight_font = pygame.font.SysFont('Arial', 28, bold=True)
clock = pygame.time.Clock()

# Dynamic animation variables
circle_animation_speeds = {}
path_animation_speeds = {}

button_rect_obstacle = pygame.Rect(WIDTH - 150, 20, 130, 50)
button_rect_new_path = pygame.Rect(WIDTH - 150, 80, 130, 50)

button_obstacle = pygame_gui.elements.UIButton(relative_rect=button_rect_obstacle, text='Add Obstacle', manager=manager)
button_new_path = pygame_gui.elements.UIButton(relative_rect=button_rect_new_path, text='New Path', manager=manager)

start_end_points, obstacles, dragging, resizing = [], [], None, None

def add_path():
    start_circle = [random.randint(50, WIDTH // 2 - 100), random.randint(50, HEIGHT - 50)]
    end_circle = [random.randint(WIDTH // 2 + 100, WIDTH - 50), random.randint(50, HEIGHT - 50)]
    start_end_points.append([start_circle, end_circle])
    circle_animation_speeds[tuple(start_circle)] = random.uniform(1.2, 2.5)
    circle_animation_speeds[tuple(end_circle)] = random.uniform(1.2, 2.5)

def add_obstacle():
    x, y = random.randint(50, WIDTH - OBSTACLE_SIZE[0] - 50), random.randint(50, HEIGHT - OBSTACLE_SIZE[1] - 50)
    obstacles.append(pygame.Rect(x, y, *OBSTACLE_SIZE))

def heuristic(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(start, goal, avoid_obstacles):
    open_set, came_from, g_score, f_score = [(0, start)], {}, {start: 0}, {start: heuristic(start, goal)}
    while open_set:
        current = heapq.heappop(open_set)[1]
        if distance(current, goal) < CIRCLE_RADIUS:
            path = []
            while current in came_from: path.append(current); current = came_from[current]
            return path[::-1]
        for neighbor in get_neighbors(current):
            if not is_point_in_obstacles(neighbor, avoid_obstacles):
                tentative_g = g_score[current] + distance(current, neighbor)
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor], g_score[neighbor], f_score[neighbor] = current, tentative_g, tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []

def get_neighbors(pos):
    return [(pos[0] + dx, pos[1] + dy) for dx, dy in [(GRID_SIZE, 0), (-GRID_SIZE, 0), (0, GRID_SIZE), (0, -GRID_SIZE)] if 0 <= pos[0] + dx < WIDTH and 0 <= pos[1] + dy < HEIGHT]

def is_point_in_obstacles(point, avoid_obstacles):
    return any(obstacle.collidepoint(point) for obstacle in obstacles) or any(distance(point, avoid_point) < CIRCLE_RADIUS for avoid_point in avoid_obstacles)

def distance(p1, p2): return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def smooth_transition(pos, target, speed):
    return [pos[0] + (target[0] - pos[0]) * speed, pos[1] + (target[1] - pos[1]) * speed]

def draw_circle_with_animation(surface, color, center, radius, speed_factor=0.1):
    radius += math.sin(pygame.time.get_ticks() / 100.0 * speed_factor) * 2
    pygame.draw.circle(surface, color, center, int(radius))

while True:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect_obstacle.collidepoint(event.pos): add_obstacle()
            elif button_rect_new_path.collidepoint(event.pos): add_path()
            else:
                for path_points in start_end_points:
                    if distance(event.pos, path_points[0]) <= CIRCLE_RADIUS: dragging = ("start", path_points, [path_points[0][0] - event.pos[0], path_points[0][1] - event.pos[1]]); break
                    elif distance(event.pos, path_points[1]) <= CIRCLE_RADIUS: dragging = ("end", path_points, [path_points[1][0] - event.pos[0], path_points[1][1] - event.pos[1]]); break
                for obstacle in obstacles:
                    if abs(obstacle.right - event.pos[0]) < 10 and abs(obstacle.bottom - event.pos[1]) < 10: resizing = obstacle; break
                    elif obstacle.collidepoint(event.pos): dragging = ("obstacle", obstacle, [obstacle.x - event.pos[0], obstacle.y - event.pos[1]]); break
        if event.type == pygame.MOUSEBUTTONUP: dragging, resizing = None, None
        if event.type == pygame.MOUSEMOTION:
            if dragging:
                if dragging[0] == "start": dragging[1][0] = [event.pos[0] + dragging[2][0], event.pos[1] + dragging[2][1]]
                elif dragging[0] == "end": dragging[1][1] = [event.pos[0] + dragging[2][0], event.pos[1] + dragging[2][1]]
                elif dragging[0] == "obstacle": dragging[1].x, dragging[1].y = event.pos[0] + dragging[2][0], event.pos[1] + dragging[2][1]
            elif resizing: resizing.width, resizing.height = max(20, event.pos[0] - resizing.x), max(20, event.pos[1] - resizing.y)

        manager.process_events(event)

    screen.fill(BACKGROUND_COLOR)
    for x in range(0, WIDTH, GRID_SIZE): pygame.draw.line(screen, LINE_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE): pygame.draw.line(screen, LINE_COLOR, (0, y), (WIDTH, y))

    manager.update(time_delta)
    manager.draw_ui(screen)

    for obstacle in obstacles: pygame.draw.rect(screen, OBSTACLE_COLOR, obstacle)

    avoid_points = []
    for start_circle, end_circle in start_end_points:
        circle_speed = circle_animation_speeds.setdefault(tuple(start_circle), random.uniform(1.2, 2.5))
        draw_circle_with_animation(screen, CIRCLE_COLOR, start_circle, CIRCLE_RADIUS, circle_speed)

        circle_speed = circle_animation_speeds.setdefault(tuple(end_circle), random.uniform(1.2, 2.5))
        draw_circle_with_animation(screen, CIRCLE_COLOR, end_circle, CIRCLE_RADIUS, circle_speed)

        path = astar(tuple(start_circle), tuple(end_circle), avoid_points)
        if path: pygame.draw.lines(screen, PATH_COLOR, False, path, 5)
        avoid_points.extend(path)

    pygame.display.flip()
