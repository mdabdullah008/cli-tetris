import curses
import random
import time

SHAPES = [
    [[1, 1, 1, 1]],                      # I
    [[1, 1], [1, 1]],                    # O
    [[0, 1, 0], [1, 1, 1]],              # T
    [[1, 1, 0], [0, 1, 1]],              # S
    [[0, 1, 1], [1, 1, 0]],              # Z
    [[1, 0, 0], [1, 1, 1]],              # J
    [[0, 0, 1], [1, 1, 1]]               # L
]

WIDTH = 10
HEIGHT = 20

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def check_collision(board, shape, offset):
    off_y, off_x = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            by = y + off_y
            bx = x + off_x
            if cell and (bx < 0 or bx >= WIDTH or by >= HEIGHT or (by >= 0 and board[by][bx])):
                return True
    return False

def merge(board, shape, offset):
    off_y, off_x = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            by = y + off_y
            bx = x + off_x
            if cell and 0 <= by < HEIGHT and 0 <= bx < WIDTH:
                board[by][bx] = 1

def remove_full_lines(board):
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    lines_cleared = HEIGHT - len(new_board)
    new_board = [[0]*WIDTH for _ in range(lines_cleared)] + new_board
    return new_board, lines_cleared

def draw_board(win, board, score, next_piece, current, offset):
    win.clear()
    height, width = win.getmaxyx()

    # grid position
    grid_x = max(2, (width - (WIDTH * 2)) // 2)
    grid_y = max(1, (height - HEIGHT) // 2)


    for y in range(HEIGHT + 2):
        for x in range(WIDTH * 2 + 2):
            char = " "
            if y == 0 or y == HEIGHT + 1:
                char = "-"
            elif x == 0 or x == WIDTH * 2 + 1:
                char = "|"
            win.addstr(grid_y + y, grid_x + x, char)

    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                win.addstr(grid_y + 1 + y, grid_x + 1 + x*2, "[]")

    for y, row in enumerate(current):
        for x, cell in enumerate(row):
            by = y + offset[0]
            bx = x + offset[1]
            if cell and 0 <= by < HEIGHT and 0 <= bx < WIDTH:
                win.addstr(grid_y + 1 + by, grid_x + 1 + bx*2, "[]")

    win.addstr(grid_y, grid_x + WIDTH*2 + 4, f"Score: {score}")
    win.addstr(grid_y + 2, grid_x + WIDTH*2 + 4, "Next:")
    for y, row in enumerate(next_piece):
        for x, cell in enumerate(row):
            if cell:
                win.addstr(grid_y + 3 + y, grid_x + WIDTH*2 + 4 + x*2, "[]")

    win.refresh()

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    board = [[0]*WIDTH for _ in range(HEIGHT)]
    current = random.choice(SHAPES)
    next_piece = random.choice(SHAPES)
    offset = [0, WIDTH//2 - len(current[0])//2]
    score = 0
    speed = 0.5
    next_drop = time.time() + speed

    while True:
        key = stdscr.getch()

        if key in [ord('q'), ord('Q')]:
            break
        elif key == curses.KEY_LEFT:
            new_offset = [offset[0], offset[1]-1]
            if not check_collision(board, current, new_offset):
                offset = new_offset
        elif key == curses.KEY_RIGHT:
            new_offset = [offset[0], offset[1]+1]
            if not check_collision(board, current, new_offset):
                offset = new_offset
        elif key == curses.KEY_UP:
            rotated = rotate(current)
            if not check_collision(board, rotated, offset):
                current = rotated
        elif key == curses.KEY_DOWN:
            new_offset = [offset[0]+1, offset[1]]
            if not check_collision(board, current, new_offset):
                offset = new_offset
            else:
                merge(board, current, offset)
                board, cleared = remove_full_lines(board)
                score += cleared * 100
                if cleared:
                    speed = max(0.1, speed - 0.02)

                current = next_piece
                next_piece = random.choice(SHAPES)
                offset = [0, WIDTH//2 - len(current[0])//2]

                if check_collision(board, current, offset):
                    stdscr.clear()
                    stdscr.addstr(10, 10, "GAME OVER!!!")
                    stdscr.addstr(12, 10, f"Final Score: {score}")
                    stdscr.refresh()
                    time.sleep(2)
                    break

        if time.time() > next_drop:
            next_drop = time.time() + speed
            new_offset = [offset[0]+1, offset[1]]
            if not check_collision(board, current, new_offset):
                offset = new_offset
            else:
                merge(board, current, offset)
                board, cleared = remove_full_lines(board)
                score += cleared * 100
                if cleared:
                    speed = max(0.1, speed - 0.02)

                current = next_piece
                next_piece = random.choice(SHAPES)
                offset = [0, WIDTH//2 - len(current[0])//2]

                if check_collision(board, current, offset):
                    stdscr.clear()
                    stdscr.addstr(10, 10, "GAME OVER!!!")
                    stdscr.addstr(12, 10, f"Final Score: {score}")
                    stdscr.refresh()
                    time.sleep(2)
                    break

        temp_board = [row[:] for row in board]
        for y, row in enumerate(current):
            for x, cell in enumerate(row):
                by = y + offset[0]
                bx = x + offset[1]
                if cell and 0 <= by < HEIGHT and 0 <= bx < WIDTH:
                    temp_board[by][bx] = 1

        draw_board(stdscr, temp_board, score, next_piece, current, offset)

curses.wrapper(main)
