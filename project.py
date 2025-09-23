import pygame
import random
import sys
import os
import json
import math

# --- SETUP & CONSTANTS ---
pygame.init()
pygame.mixer.init()

# MODIFIED: Restored your custom screen and layout dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 450, 625
TOP_UI_AREA_HEIGHT = 225
BOARD_SIZE = 4

TILE_SIZE = (SCREEN_WIDTH * 0.8) / (BOARD_SIZE + (BOARD_SIZE + 1) * 0.05)
MARGIN = TILE_SIZE * 0.05
GAME_BOARD_SIZE = (TILE_SIZE * BOARD_SIZE) + (MARGIN * (BOARD_SIZE + 1))
BOARD_X = (SCREEN_WIDTH - GAME_BOARD_SIZE) / 2
BOARD_Y = TOP_UI_AREA_HEIGHT

BEST_SCORE_FILE = os.path.join(os.path.expanduser("~"), "2048_best_score.json")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2048")
clock = pygame.time.Clock()

try:
    move_sound = pygame.mixer.Sound("move.wav")
    click_sound = pygame.mixer.Sound("click.wav")
except (pygame.error, FileNotFoundError):
    print("Warning: Sound files 'move.wav' & 'click.wav' not found. Sounds are disabled.")
    class DummySound:
        def play(self): pass
    move_sound = DummySound()
    click_sound = DummySound()

TILE_COLORS = {
    0: (205, 193, 180), 2: (238, 228, 218), 4: (237, 224, 200),
    8: (242, 177, 121), 16: (245, 149, 99), 32: (246, 124, 95),
    64: (246, 94, 59), 128: (237, 207, 114), 256: (237, 204, 97),
    512: (237, 200, 80), 1024: (237, 197, 63), 2048: (237, 194, 46),
    4096: (60, 58, 50), 8192: (60, 58, 50),
}

THEMES = {
    "Default": {
        "background": (187, 173, 160), "board_background": (205, 193, 180, 150),
        "font_color": (119, 110, 101), "light_font_color": (249, 246, 242),
        "tile_colors": TILE_COLORS, "button_color": (143, 122, 102),
        "button_hover_color": (167, 143, 122), "button_font_color": (255, 255, 255)
    },
    "Ocean": {
        "background": (1, 22, 39), "board_background": (2, 45, 78, 200),
        "font_color": (230, 245, 255), "light_font_color": (255, 255, 255),
        "grid_color": (8, 55, 93),
        "tile_colors": {
            0: (2, 45, 78), 2: (173, 216, 230), 4: (135, 206, 250),
            8: (0, 191, 255), 16: (30, 144, 255), 32: (65, 105, 225),
            64: (70, 130, 180), 128: (0, 0, 255), 256: (0, 0, 205),
            512: (0, 0, 139), 1024: (25, 25, 112), 2048: (23, 32, 42),
        },
        "button_color": (8, 55, 93), "button_hover_color": (16, 93, 155),
        "button_font_color": (255, 255, 255)
    },
    "Retro": {
        "background": (0, 0, 0), "board_background": (20, 20, 20, 200),
        "font_color": (0, 255, 0), "light_font_color": (0, 255, 0),
        "tile_colors": {
            0: (20, 20, 20), 2: (40, 40, 40), 4: (60, 60, 60),
            8: (10, 50, 10), 16: (10, 70, 10), 32: (10, 90, 10),
            64: (10, 110, 10), 128: (10, 130, 10), 256: (10, 150, 10),
            512: (10, 170, 10), 1024: (10, 190, 10), 2048: (0, 255, 0),
        },
        "button_color": (0, 80, 0), "button_hover_color": (0, 120, 0),
        "button_font_color": (0, 255, 0)
    }
}
current_theme = THEMES["Default"]

# --- CLASS DEFINITIONS ---
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        font = get_font(30, bold=True)
        color = current_theme["button_color"]
        hover_color = current_theme["button_hover_color"]
        font_color = current_theme["button_font_color"]
        draw_color = hover_color if self.is_hovered else color
        pygame.draw.rect(surface, draw_color, self.rect, border_radius=8)
        text_surf = font.render(self.text, True, font_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            click_sound.play()
            if self.action:
                return self.action
        return None

class PowerUpButton:
    def __init__(self, x, y, size, action, count):
        self.rect = pygame.Rect(x, y, size, size)
        self.action = action
        self.count = count
        self.is_hovered = False
        self.is_active = False

    def draw(self, surface):
        color = current_theme["button_color"]
        hover_color = current_theme["button_hover_color"]
        draw_color = hover_color if self.is_hovered else color
        pygame.draw.circle(surface, draw_color, self.rect.center, self.rect.width // 2)
        self.draw_icon(surface)
        if self.count > 0:
            font = get_font(18, bold=True)
            count_pos = (self.rect.right - 12, self.rect.top + 12)
            pygame.draw.circle(surface, (200,0,0), count_pos, 12)
            text_surf = font.render(str(self.count), True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=count_pos)
            surface.blit(text_surf, text_rect)
        if self.is_active:
            pygame.draw.circle(surface, (255, 255, 0), self.rect.center, self.rect.width // 2 + 3, 3)

    def handle_event(self, event):
        if self.count <= 0: return None
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            click_sound.play()
            return self.action
        return None
    
    def draw_icon(self, surface):
        pass

class BombButton(PowerUpButton):
    def __init__(self, x, y, size, count):
        super().__init__(x, y, size, "bomb_toggle", count)
    def draw_icon(self, surface):
        bomb_color = (20, 20, 20)
        fuse_color = (200, 150, 0)
        pygame.draw.circle(surface, bomb_color, self.rect.center, self.rect.width // 3)
        fuse_rect = pygame.Rect(0,0, 4, self.rect.width//4)
        fuse_rect.center = (self.rect.centerx, self.rect.centery - self.rect.width//3)
        pygame.draw.rect(surface, fuse_color, fuse_rect)

class ShuffleButton(PowerUpButton):
    def __init__(self, x, y, size, count):
        super().__init__(x, y, size, "shuffle_activate", count)
    def draw_icon(self, surface):
        arrow_color = (249, 246, 242)
        center = self.rect.center
        radius = self.rect.width // 4
        pygame.draw.arc(surface, arrow_color, (center[0] - radius, center[1] - radius, radius*2, radius*2), math.pi / 2, math.pi * 2.2, 4)
        pygame.draw.polygon(surface, arrow_color, [(center[0], center[1] - radius - 6), (center[0], center[1] - radius + 6), (center[0] + 6, center[1] - radius)])

# --- FILE & GAME STATE ---
def load_best_score():
    if not os.path.exists(BEST_SCORE_FILE): return 0
    try:
        with open(BEST_SCORE_FILE, "r") as f: return json.load(f).get("best_score", 0)
    except (json.JSONDecodeError, IOError, OSError): return 0

def save_best_score(score):
    try:
        current_best = load_best_score()
        if score > current_best:
            with open(BEST_SCORE_FILE, "w") as f: json.dump({"best_score": score}, f)
    except (IOError, OSError): pass

def reset_best_score():
    try:
        with open(BEST_SCORE_FILE, "w") as f:
            json.dump({"best_score": 0}, f)
        print("Best score has been reset to 0.")
    except (IOError, OSError) as e:
        print(f"Warning: Unable to reset best score: {e}")

def initialize_game():
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    add_random_tile(board)
    add_random_tile(board)
    return board, 0

# --- CORE GAME LOGIC ---
def add_random_tile(board):
    empty = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == 0]
    if empty:
        r, c = random.choice(empty)
        board[r][c] = 2 if random.random() < 0.9 else 4

def move_left(board):
    new_board, score_add = [], 0
    for row in board:
        new_row = [i for i in row if i != 0]
        i = 0
        while i < len(new_row) - 1:
            if new_row[i] == new_row[i + 1]:
                new_row[i] *= 2
                score_add += new_row[i]
                new_row.pop(i + 1)
            i += 1
        new_board.append(new_row + [0] * (BOARD_SIZE - len(new_row)))
    return new_board, score_add

def rotate(board): return [list(row) for row in zip(*board[::-1])]

def move(board, direction):
    for _ in range(direction): board = rotate(board)
    board, score_add = move_left(board)
    for _ in range(4 - direction): board = rotate(board)
    return board, score_add

def check_game_over(board):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == 0: return False
            if r > 0 and board[r][c] == board[r-1][c]: return False
            if c > 0 and board[r][c] == board[r][c-1]: return False
    return True

# --- DRAWING & UI ---
def get_font(size, bold=False):
    font_name = "Consolas" if current_theme == THEMES["Retro"] else "Arial"
    return pygame.font.SysFont(font_name, size, bold=bold)

def draw_text(text, font, x, y, color):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)

def draw_background(score, best_score):
    screen.fill(current_theme["background"])
    draw_text("2048", get_font(70, bold=True), SCREEN_WIDTH / 2, 46, current_theme["font_color"])
    draw_score_box("SCORE", score, SCREEN_WIDTH / 2 - 80, 100)
    draw_score_box("BEST", best_score, SCREEN_WIDTH / 2 + 80, 100)

def draw_score_box(title, score, x, y):
    box_rect = pygame.Rect(0, 0, 150, 50)
    box_rect.center = (x, y)
    pygame.draw.rect(screen, current_theme["button_color"], box_rect, border_radius=5)
    draw_text(title, get_font(15, bold=True), x, y - 10, current_theme["light_font_color"])
    draw_text(str(score), get_font(25, bold=True), x, y + 10, current_theme["light_font_color"])

def draw_powerups_ui(bomb_button, shuffle_button, active_powerup):
    bomb_button.draw(screen)
    shuffle_button.draw(screen)
    if active_powerup == "bomb":
        draw_text("BOMB ACTIVE: Click a tile!", get_font(22, True), SCREEN_WIDTH/2, SCREEN_HEIGHT - 30, (255, 255, 0))

def get_tile_rect(r, c):
    x = BOARD_X + MARGIN + c * (TILE_SIZE + MARGIN)
    y = BOARD_Y + MARGIN + r * (TILE_SIZE + MARGIN)
    return pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

def get_tile_from_pos(pos):
    if not (BOARD_X <= pos[0] <= BOARD_X + GAME_BOARD_SIZE and BOARD_Y <= pos[1] <= BOARD_Y + GAME_BOARD_SIZE): return None
    col = int((pos[0] - BOARD_X - MARGIN) // (TILE_SIZE + MARGIN))
    row = int((pos[1] - BOARD_Y - MARGIN) // (TILE_SIZE + MARGIN))
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE: return row, col
    return None

def draw_board(board):
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, GAME_BOARD_SIZE, GAME_BOARD_SIZE)
    pygame.draw.rect(screen, current_theme["button_color"], board_rect, border_radius=10)

    if current_theme.get("grid_color"):
        grid_color = current_theme["grid_color"]
        for i in range(1, BOARD_SIZE):
            line_x = BOARD_X + i * (TILE_SIZE + MARGIN) - (MARGIN / 2)
            pygame.draw.line(screen, grid_color, (line_x, BOARD_Y), (line_x, BOARD_Y + GAME_BOARD_SIZE), int(MARGIN))
            line_y = BOARD_Y + i * (TILE_SIZE + MARGIN) - (MARGIN / 2)
            pygame.draw.line(screen, grid_color, (BOARD_X, line_y), (BOARD_X + GAME_BOARD_SIZE, line_y), int(MARGIN))

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            val = board[r][c]
            color = current_theme["tile_colors"].get(val, TILE_COLORS[8192])
            rect = get_tile_rect(r, c)
            tile_rect = rect.inflate(-MARGIN/2, -MARGIN/2) if current_theme.get("grid_color") else rect
            pygame.draw.rect(screen, color, tile_rect, border_radius=8)
            if val != 0:
                font_size = int(TILE_SIZE * 0.4) if val < 1000 else int(TILE_SIZE * 0.3)
                font_color = current_theme["light_font_color"] if val > 4 else current_theme["font_color"]
                draw_text(str(val), get_font(font_size, bold=True), rect.centerx, rect.centery, font_color)

# --- MENUS & GAME STATES ---
def main_menu():
    title_font = get_font(100, bold=True)
    buttons = [
        Button(SCREEN_WIDTH/2 - 150, 300, 300, 50, "Play Game", "play"),
        Button(SCREEN_WIDTH/2 - 150, 370, 300, 50, "Quit", "quit"),
    ]
    while True:
        screen.fill(current_theme["background"])
        draw_text("2048", title_font, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, current_theme["font_color"])
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            for button in buttons:
                action = button.handle_event(event)
                if action: return action
        for button in buttons: button.draw(screen)
        pygame.display.flip()

def show_overlay_menu(message, buttons):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(current_theme["board_background"])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            for button in buttons:
                action = button.handle_event(event)
                if action: return action
        screen.blit(overlay, (0, 0))
        draw_text(message, get_font(70, bold=True), SCREEN_WIDTH/2, 100, current_theme["font_color"])
        for button in buttons: button.draw(screen)
        pygame.display.flip()

def theme_menu():
    global current_theme
    theme_keys = list(THEMES.keys())
    buttons = []
    button_y = 180
    for theme_name in theme_keys:
        buttons.append(Button(SCREEN_WIDTH/2 - 150, button_y, 300, 50, theme_name, action=theme_name))
        button_y += 70
    buttons.append(Button(SCREEN_WIDTH/2 - 150, button_y, 300, 50, "Back", action="back"))
    action = show_overlay_menu("Select Theme", buttons)
    if action and action != "back" and action in THEMES:
        current_theme = THEMES[action]
    return

def game_loop():
    board, score = initialize_game()
    best_score = load_best_score()
    undo_board, undo_score = None, None
    bomb_count, shuffle_count = 1, 1
    active_powerup = None
    won = False

    bomb_button = BombButton(SCREEN_WIDTH / 4 - 25, TOP_UI_AREA_HEIGHT - 60, 50, bomb_count)
    shuffle_button = ShuffleButton(SCREEN_WIDTH * 3 / 4 - 25, TOP_UI_AREA_HEIGHT - 60, 50, shuffle_count)

    running = True
    while running:
        bomb_button.is_active = (active_powerup == "bomb")
        bomb_button.count = bomb_count
        shuffle_button.count = shuffle_count
        
        draw_background(score, best_score)
        draw_powerups_ui(bomb_button, shuffle_button, active_powerup)
        draw_board(board)
        
        if active_powerup == "bomb": pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        else: pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()

        if not won and any(2048 in row for row in board):
            won = True
            action = show_overlay_menu("You Win!", [
                Button(SCREEN_WIDTH/2-150, 300, 300, 50, "Continue", "continue"),
                Button(SCREEN_WIDTH/2-150, 370, 300, 50, "Main Menu", "main_menu")])
            if action == "main_menu": running = False

        if check_game_over(board):
            save_best_score(score)
            action = show_overlay_menu("Game Over!", [
                Button(SCREEN_WIDTH/2-150, 300, 300, 50, "Restart", "restart"),
                Button(SCREEN_WIDTH/2-150, 370, 300, 50, "Main Menu", "main_menu")])
            if action == "restart":
                board, score, bomb_count, shuffle_count, undo_board, undo_score, won = *initialize_game(), 1, 1, None, None, False
            else: running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_best_score(score)
                return "quit"
            
            bomb_action = bomb_button.handle_event(event)
            if bomb_action == "bomb_toggle":
                active_powerup = "bomb" if active_powerup != "bomb" else None

            shuffle_action = shuffle_button.handle_event(event)
            if shuffle_action == "shuffle_activate":
                if shuffle_count > 0:
                    active_powerup = None
                    tiles = [board[r][c] for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] != 0]
                    coords = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] != 0]
                    random.shuffle(tiles)
                    for r in range(BOARD_SIZE):
                        for c in range(BOARD_SIZE):
                            if (r,c) in coords: board[r][c] = tiles.pop()
                            else: board[r][c] = 0
                    shuffle_count -= 1
                    add_random_tile(board)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and active_powerup == "bomb":
                if not bomb_button.rect.collidepoint(event.pos) and not shuffle_button.rect.collidepoint(event.pos):
                    tile_pos = get_tile_from_pos(event.pos)
                    if tile_pos and board[tile_pos[0]][tile_pos[1]] != 0:
                        board[tile_pos[0]][tile_pos[1]] = 0
                        bomb_count -= 1
                        active_powerup = None
                        add_random_tile(board)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    active_powerup = None
                    pause_buttons = [
                        Button(SCREEN_WIDTH/2-150, 200, 300, 50, "Resume", "resume"),
                        Button(SCREEN_WIDTH/2-150, 270, 300, 50, "Change Theme", "theme"),
                        Button(SCREEN_WIDTH/2-150, 340, 300, 50, "Reset Best Score", "reset_score"),
                        Button(SCREEN_WIDTH/2-150, 410, 300, 50, "Main Menu", "main_menu")]
                    action = show_overlay_menu("Paused", pause_buttons)
                    if action == "main_menu": running = False
                    if action == "theme": theme_menu()
                    if action == "reset_score":
                        reset_best_score()
                        best_score = 0
                
                direction = {pygame.K_LEFT: 0, pygame.K_DOWN: 1, pygame.K_RIGHT: 2, pygame.K_UP: 3}.get(event.key)
                if direction is not None and active_powerup is None:
                    undo_board, undo_score = [row[:] for row in board], score
                    new_board, score_add = move(board, direction)
                    if new_board != board:
                        move_sound.play()
                        board, score = new_board, score + score_add
                        add_random_tile(board)
        
        if score > best_score:
            best_score = score
            save_best_score(best_score)
        
        clock.tick(60)
        if not running: return "main_menu"

# --- MAIN PROGRAM FLOW ---
if __name__ == "__main__":
    while True:
        action = main_menu()
        if action == "play":
            result = game_loop()
            if result == "quit": 
                break
        elif action == "quit":
            break
            
    pygame.quit()
    sys.exit()