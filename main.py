import pygame
import random
import math
import time
from queue import PriorityQueue

pygame.init()

SCREEN_HEIGHT = 700
INFO_HEIGHT = 180
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
PURPLE = (128,0,128)
ORANGE = (255,165,0)
GREY = (200,200,200)

FONT = pygame.font.SysFont("Arial", 18)


class Node:
    def __init__(self, row, col, size, total_rows):
        self.row = row
        self.col = col
        self.x = col * size
        self.y = row * size
        self.size = size
        self.total_rows = total_rows
        self.color = WHITE
        self.neighbors = []
        self.reset_costs()

    def reset_costs(self):
        self.g = float("inf")
        self.h = 0
        self.f = float("inf")
        self.parent = None

    def get_pos(self):
        return self.row, self.col

    def is_wall(self):
        return self.color == BLACK

    def reset(self):
        self.color = WHITE
        self.reset_costs()

    def make_start(self):
        self.color = ORANGE

    def make_goal(self):
        self.color = PURPLE

    def make_wall(self):
        self.color = BLACK

    def make_visited(self):
        self.color = BLUE

    def make_frontier(self):
        self.color = YELLOW

    def make_path(self):
        self.color = GREEN

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))

    def update_neighbors(self, grid):
        self.neighbors = []

        if self.row < self.total_rows - 1 and not grid[self.row+1][self.col].is_wall():
            self.neighbors.append(grid[self.row+1][self.col])
        if self.row > 0 and not grid[self.row-1][self.col].is_wall():
            self.neighbors.append(grid[self.row-1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col+1].is_wall():
            self.neighbors.append(grid[self.row][self.col+1])
        if self.col > 0 and not grid[self.row][self.col-1].is_wall():
            self.neighbors.append(grid[self.row][self.col-1])
    def __eq__(self, other):
        return isinstance(other, Node) and self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))


def heuristic(a, b, mode):
    if mode == "manhattan":
        return abs(a.row - b.row) + abs(a.col - b.col)
    else:
        return math.sqrt((a.row - b.row)**2 + (a.col - b.col)**2)


def reconstruct_path(end):
    path = []
    while end.parent:
        path.append(end)
        end = end.parent
    return path


def search_generator(grid, start, goal, algo, heuristic_mode):
    count = 0
    open_set = PriorityQueue()
    open_hash = set()
    closed_set = set()

    start.reset_costs()
    start.g = 0
    start.h = heuristic(start, goal, heuristic_mode)
    start.f = start.h if algo == "GBFS" else start.g + start.h

    open_set.put((start.f, count, start))
    open_hash.add(start)

    nodes_visited = 0
    start_time = time.time()

    while not open_set.empty():
       
        current = open_set.get()[2]
        open_hash.remove(current)

        if current == goal:
            end_time = time.time()
            yield ("DONE", reconstruct_path(goal), nodes_visited,
                   (end_time - start_time) * 1000)
            return

        closed_set.add(current)

        for neighbor in current.neighbors:

            if neighbor in closed_set:
                continue

            if algo == "A*":
                temp_g = current.g + 1

                if temp_g < neighbor.g:
                    neighbor.parent = current
                    neighbor.g = temp_g
                    neighbor.h = heuristic(neighbor, goal, heuristic_mode)
                    neighbor.f = neighbor.g + neighbor.h

                    if neighbor not in open_hash:
                        count += 1
                        open_set.put((neighbor.f, count, neighbor))
                        open_hash.add(neighbor)
                        neighbor.make_frontier()

            else:  
                if neighbor not in open_hash:
                    neighbor.parent = current
                    neighbor.h = heuristic(neighbor, goal, heuristic_mode)
                    neighbor.f = neighbor.h
                    count += 1
                    open_set.put((neighbor.f, count, neighbor))
                    open_hash.add(neighbor)
                    neighbor.make_frontier()

        if current != start:
            current.make_visited()

        nodes_visited += 1

        yield ("SEARCHING", None, nodes_visited, 0)

    yield ("FAILED", None, nodes_visited, 0)


def make_grid(rows, size):
    grid = []
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, size, rows)
            grid[i].append(node)
    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))


def draw(win, grid, rows, width, metrics):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)

    y_offset = width + 10
    for text in metrics:
        label = FONT.render(text, 1, (0,0,0))
        win.blit(label, (10, y_offset))
        y_offset += 30

    pygame.display.update()


def main():
    searching = False
    search_gen = None
    rows = int(input("Enter grid size: "))
    CELL_SIZE = (SCREEN_HEIGHT - INFO_HEIGHT) // rows
    WIDTH = CELL_SIZE * rows

    WIN = pygame.display.set_mode((WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dynamic Pathfinding Agent")

    grid = make_grid(rows, CELL_SIZE)

    start = grid[0][0]
    goal = grid[rows-1][rows-1]
    start.make_start()
    goal.make_goal()

    algo = "A*"
    heuristic_mode = "manhattan"
    dynamic = False
    density = 0.25

    clock = pygame.time.Clock()
    path = []
    nodes = 0
    exec_time = 0
    run = True

    while run:
        clock.tick(30)

        metrics = [
            f"Algorithm: {algo}",
            f"Heuristic: {heuristic_mode}",
            f"Nodes Visited: {nodes}",
            f"Path Cost: {len(path) if path else 0}",
            f"Execution Time: {exec_time:.2f} ms",
            f"Dynamic Mode: {dynamic}"
        ]

        draw(WIN, grid, rows, WIDTH, metrics)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                col = pos[0] // CELL_SIZE
                row = pos[1] // CELL_SIZE
                if row < rows and col < rows:
                    node = grid[row][col]
                    if node != start and node != goal:
                        node.make_wall()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    grid = make_grid(rows, CELL_SIZE)
                    start = grid[0][0]
                    goal = grid[rows-1][rows-1]
                    start.make_start()
                    goal.make_goal()
                    path = []
                    nodes = 0

                if event.key == pygame.K_m:
                    for row in grid:
                        for node in row:
                            if node != start and node != goal:
                                if random.random() < density:
                                    node.make_wall()

                if event.key == pygame.K_SPACE:

                   for row in grid:
                       for node in row:
                            if node.color not in [BLACK, ORANGE, PURPLE]:
                                node.reset()

                   for row in grid:
                       for node in row:
                           node.update_neighbors(grid)

                   search_gen = search_generator(grid, start, goal, algo, heuristic_mode)
                   searching = True

                if event.key == pygame.K_1:
                    algo = "A*"

                if event.key == pygame.K_2:
                    algo = "GBFS"

                if event.key == pygame.K_h:
                    heuristic_mode = "euclidean" if heuristic_mode == "manhattan" else "manhattan"
        if searching and search_gen:
            try:
               status, path, nodes, exec_time = next(search_gen)

               if status == "DONE":
                  searching = False
                  for node in path:
                       if node != start and node != goal:
                          node.make_path()

               elif status == "FAILED":
                   searching = False

            except StopIteration:
              searching = False
    pygame.quit()


if __name__ == "__main__":
    main()
