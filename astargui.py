from queue import PriorityQueue

import pygame as pg

PINKISH_WHITE = (255, 226, 216)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (150, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (0, 209, 209)
BLUE = (0, 0, 255)
LIGHT_BLUE = (0, 255, 255)
ORANGE = (255, 161, 0)


class Node:
    def __init__(self, row, col, node_width, window):
        self.node_width = node_width
        self.row = row
        self.col = col
        self.window = window
        self.x = col * node_width
        self.y = row * node_width
        self.width = node_width
        self.color = PINKISH_WHITE
        self.neighbours = []

    def is_start(self):
        return self.color == BLUE

    def is_barrier(self):
        return self.color == BLACK

    def is_end(self):
        return self.color == DARK_RED

    def is_explored(self):
        return self.color == RED

    def reset(self):
        self.color = PINKISH_WHITE

    def make_start(self):
        self.color = BLUE

    def make_end(self):
        self.color = DARK_RED

    def make_barrier(self):
        self.color = BLACK

    def make_explored(self):
        self.color = RED

    def make_active(self):
        self.color = ORANGE

    def make_path(self):
        self.color = GREEN

    def get_pos(self):
        return self.x, self.y

    def draw_node(self):
        pg.draw.rect(self.window, self.color, (self.x, self.y, self.node_width, self.node_width))

    def update_neighbours(self, grid):
        total_rows = len(grid)
        self.neighbours = []

        # for down neighbour
        if self.row < total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbours.append(grid[self.row + 1][self.col])

        # for up neighbour
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbours.append(grid[self.row - 1][self.col])

        # for right neighbour
        if self.col < total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbours.append(grid[self.row][self.col + 1])

        # for left neighbour
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbours.append(grid[self.row][self.col - 1])

    # Resolves tie breakers by comparing two Node objects
    def __lt__(self, other):
        return False


def draw_window(window, rows, width, grid):
    window.fill(PINKISH_WHITE)
    node_width = width // rows

    # draw Nodes
    for row in grid:
        for node in row:
            node.draw_node()

    # draw grid lines
    for i in range(rows + 1):
        pg.draw.line(window, BLACK, (0, i * node_width), (width, i * node_width))
        pg.draw.line(window, BLACK, (i * node_width, 0), (i * node_width, width))

    pg.time.delay(20)
    pg.display.update()


def make_grid(window, rows, node_width):
    grid = []
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, node_width, window)
            grid[i].append(node)
    return grid


def get_clicked_pos(position, node_width):
    return position[1] // node_width, position[0] // node_width


def heuristic_function(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x1 - x2) + abs(y1 - y2)


def run_pf_algorithm(grid, start, end, draw):
    # creating priority Queue
    algo_queue = PriorityQueue()

    # initializing g_score and f_score with infinity
    g_score = {node: float("inf") for row in grid for node in row}
    f_score = {node: float("inf") for row in grid for node in row}

    # data for start
    g_score[start] = 0
    f_score[start] = heuristic_function(start.get_pos(), end.get_pos())
    algo_seek_queue = {start}

    # adding start in the queue
    algo_queue.put((f_score[start], start))
    previous_node = {}

    while not algo_queue.empty():
        # quit event
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return False

        node = algo_queue.get()
        active_node = node[1]
        algo_seek_queue.remove(active_node)

        # if path found trace path and return
        if active_node == end:
            retrace_path(start, end, previous_node, draw)
            end.make_end()
            start.make_start()
            return True

        # if path not found go and try to find in its neighbours
        for neighbour in active_node.neighbours:
            possible_g_score = g_score[active_node] + 1
            if g_score[neighbour] > possible_g_score:
                g_score[neighbour] = possible_g_score
                previous_node[neighbour] = active_node
                f_score[neighbour] = g_score[neighbour] + heuristic_function(neighbour.get_pos(), end.get_pos())

                # neighbours are revisited so only add them if not already in the queue
                if neighbour not in algo_seek_queue:
                    algo_queue.put((f_score[neighbour], neighbour))
                    algo_seek_queue.add(neighbour)
                    neighbour.make_active()

        draw()
        # current node is not end and the neighbours are in queue, hence the node is fully explored
        if active_node != start:
            active_node.make_explored()
    return False


def retrace_path(start, end, previous_node, draw):
    active_node = previous_node[end]
    active_node.make_path()
    while active_node != start:
        active_node = previous_node[active_node]
        active_node.make_path()
        draw()


def main():
    # basic structure of gui
    width = 600
    rows = 30
    node_width = width // rows
    fps = 60

    window = pg.display.set_mode((width, width))
    pg.display.set_caption("A* Path Finding Algorithm Visualizer")
    grid = make_grid(window, rows, node_width)
    clock = pg.time.Clock()

    # initializing variables
    running = True
    start = None
    end = None

    # the infinite loop of game
    while running:

        clock.tick(fps)
        for event in pg.event.get():

            # handle quit
            if event.type == pg.QUIT:
                running = False

            # handle keyboard
            if event.type == pg.KEYDOWN:
                if start and end and (event.key == pg.K_SPACE or event.key == pg.K_RETURN):
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)
                            # in case of rerun without reset reset the nodes except start end and barriers
                            if not node.is_end() and not node.is_start() and not node.is_barrier():
                                node.reset()

                    run_pf_algorithm(grid, start, end, lambda: draw_window(window, rows, width, grid))

                # reset the board on specific keypress
                if event.key == pg.K_ESCAPE or event.key == pg.K_DELETE or event.key == pg.K_c:
                    for row in grid:
                        for node in row:
                            node.reset()
                            start = None
                            end = None

            # handle left mouse click
            if pg.mouse.get_pressed(3)[0]:
                position = pg.mouse.get_pos()
                row, col = get_clicked_pos(position, node_width)
                node = grid[row][col]
                if not start and not node.is_end():
                    start = node
                    start.make_start()
                elif not end and not node.is_start():
                    end = node
                    end.make_end()
                elif not node.is_start() and not node.is_end():
                    node.make_barrier()

            # handle right mouse click for resetting Nodes
            if pg.mouse.get_pressed(3)[2]:
                position = pg.mouse.get_pos()
                row, col = get_clicked_pos(position, node_width)
                node = grid[row][col]
                if node.is_end():
                    node.reset()
                    end = None
                elif node.is_start():
                    node.reset()
                    start = None
                else:
                    node.reset()

        draw_window(window, rows, width, grid)

    pg.quit()


if __name__ == '__main__':
    main()
