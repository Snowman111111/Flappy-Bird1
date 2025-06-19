import pygame
import random
import sys
import os
import math

pygame.init()

WIDTH, HEIGHT = 400, 600
FPS = 60

WHITE = (255, 255, 255)
BLUE = (135, 206, 250)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 223, 0)
LIGHT_GRAY = (220, 220, 220)
ORANGE = (255, 165, 0)

NIGHT_SKY = (10, 10, 40)
MOON_COLOR = (230, 230, 210)
STAR_COLOR = (255, 255, 200)

BIRD_RADIUS = 20

PIPE_WIDTH = 70
PIPE_GAP_MIN = 120
PIPE_SPEED_MAX = 8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird with Moving Pipes and Coins")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 32)

bird_x = 100
bird_y = HEIGHT // 2
bird_velocity = 0

score = 0
frame_count = 0
lives = 3

menu = True
playing = False
game_over = False
difficulty_menu = True

pipe_gap = 200
pipe_speed = 3
GRAVITY = 0.5
JUMP_STRENGTH = -10

HIGHSCORE_FILE = "highscore.txt"

is_night = False

NUM_STARS = 50
stars = []
for _ in range(NUM_STARS):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT // 2)
    brightness = random.randint(150, 255)
    stars.append([x, y, brightness, random.choice([1, -1])])

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))

highscore = load_highscore()

def draw_button(text, x, y, w, h, color, text_color):
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)
    label = small_font.render(text, True, text_color)
    label_rect = label.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(label, label_rect)
    return pygame.Rect(x, y, w, h)

def draw_bird(x, y):
    pygame.draw.circle(screen, RED, (int(x), int(y)), BIRD_RADIUS)
    eye_radius = 5
    pupil_radius = 2
    eye_x = int(x + BIRD_RADIUS // 2)
    eye_y = int(y - BIRD_RADIUS // 2)
    pygame.draw.circle(screen, WHITE, (eye_x, eye_y), eye_radius)
    pygame.draw.circle(screen, BLACK, (eye_x, eye_y), pupil_radius)

    wing_width = 16
    wing_height = 10
    wing_x = int(x - BIRD_RADIUS // 2)
    wing_y = int(y)
    pygame.draw.ellipse(screen, (200, 0, 0), (wing_x, wing_y, wing_width, wing_height))

    beak_length = 8
    beak_height = 6
    beak_x = int(x + BIRD_RADIUS)
    beak_y = int(y)
    points = [
        (beak_x, beak_y),
        (beak_x - beak_length, beak_y - beak_height // 2),
        (beak_x - beak_length, beak_y + beak_height // 2)
    ]
    pygame.draw.polygon(screen, BLACK, points)

def draw_heart(surface, x, y, size=20):
    radius = size // 4
    pygame.draw.circle(surface, RED, (x - radius, y), radius)
    pygame.draw.circle(surface, RED, (x + radius, y), radius)
    points = [(x - size // 2, y), (x + size // 2, y), (x, y + size // 1.3)]
    pygame.draw.polygon(surface, RED, points)

def draw_ground():
    ground_height = 60
    grass_height = 20
    ground_y = HEIGHT - ground_height

    # Почва
    pygame.draw.rect(screen, (139, 69, 19), (0, ground_y, WIDTH, ground_height))  # Коричневая почва

    # Трава
    pygame.draw.rect(screen, (34, 139, 34), (0, ground_y, WIDTH, grass_height))   # Зеленая трава

    # Немного деталей: травинки
    for i in range(0, WIDTH, 15):
        pygame.draw.line(screen, (0, 100, 0), (i, ground_y), (i, ground_y - 5), 2)

def check_collision(bird_y, pipes):
    for pipe in pipes:
        if pipe.collides_with(bird_x, bird_y, BIRD_RADIUS):
            return True
    if bird_y - BIRD_RADIUS < 0 or bird_y + BIRD_RADIUS > HEIGHT:
        return True
    return False

def reset_game():
    global bird_y, bird_velocity, score, frame_count
    global pipe_gap, pipe_speed, GRAVITY, JUMP_STRENGTH
    global lives
    bird_y = HEIGHT // 2
    bird_velocity = 0
    score = 0
    frame_count = 0
    lives = 3

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = PIPE_WIDTH
        self.color = random.choice([GREEN, DARK_GREEN, ORANGE])
        self.top_height = random.randint(50, HEIGHT - pipe_gap - 50)
        self.passed = False
        self.is_moving = random.random() < 0.4
        self.move_amplitude = random.randint(10, 30) if self.is_moving else 0
        self.move_speed = random.uniform(0.01, 0.03) if self.is_moving else 0
        self.move_offset = random.uniform(0, 2*math.pi) if self.is_moving else 0
        self.current_top_height = self.top_height

    def update(self):
        self.x -= pipe_speed
        if self.is_moving:
            offset = math.sin(pygame.time.get_ticks() * self.move_speed + self.move_offset) * self.move_amplitude
        else:
            offset = 0
        self.current_top_height = self.top_height + offset
        if self.current_top_height < 40:
            self.current_top_height = 40
        if self.current_top_height > HEIGHT - pipe_gap - 40:
            self.current_top_height = HEIGHT - pipe_gap - 40

    def draw(self, surface):
        bottom_y = self.current_top_height + pipe_gap
        pygame.draw.rect(surface, self.color, (self.x, 0, self.width, int(self.current_top_height)))
        pygame.draw.rect(surface, self.color, (self.x, int(bottom_y), self.width, HEIGHT - int(bottom_y)))

    def collides_with(self, bx, by, br):
        bottom_y = self.current_top_height + pipe_gap
        if bx + br > self.x and bx - br < self.x + self.width:
            if by - br < self.current_top_height or by + br > bottom_y:
                return True
        return False

class Coin:
    def __init__(self, pipes):
        self.radius = 10
        self.x = WIDTH + 20
        self.y = self.find_position(pipes)
        self.collected = False

    def find_position(self, pipes):
        # Найти ближайшую трубу справа (где будет монета)
        nearest_pipe = None
        for pipe in pipes:
            if pipe.x + pipe.width > WIDTH and (nearest_pipe is None or pipe.x < nearest_pipe.x):
                nearest_pipe = pipe

        if nearest_pipe:
            pipe_top = nearest_pipe.current_top_height
            pipe_bottom = pipe_top + pipe_gap
            # Размещаем монету в пределах зазора
            return random.randint(int(pipe_top + self.radius), int(pipe_bottom - self.radius))

        # Если подходящей трубы нет — центр экрана
        return HEIGHT // 2

    def update(self):
        self.x -= pipe_speed

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x - self.radius//3), int(self.y - self.radius//3)), self.radius//3)

    def collides_with(self, bx, by, br):
        dist = ((bx - self.x) ** 2 + (by - self.y) ** 2) ** 0.5
        return dist < br + self.radius

class Heart:
    def __init__(self, pipes):
        self.radius = 12
        self.x = WIDTH + 30
        self.y = self.find_position(pipes)
        self.collected = False

    def find_position(self, pipes):
        nearest_pipe = None
        for pipe in pipes:
            if pipe.x + pipe.width > WIDTH and (nearest_pipe is None or pipe.x < nearest_pipe.x):
                nearest_pipe = pipe

        if nearest_pipe:
            pipe_top = nearest_pipe.current_top_height
            pipe_bottom = pipe_top + pipe_gap
            return random.randint(int(pipe_top + self.radius), int(pipe_bottom - self.radius))

        return HEIGHT // 2

    def update(self):
        self.x -= pipe_speed

    def draw(self, surface):
        draw_heart(surface, int(self.x), int(self.y), size=24)

    def collides_with(self, bx, by, br):
        dist = ((bx - self.x) ** 2 + (by - self.y) ** 2) ** 0.5
        return dist < br + self.radius

class Cloud:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(20, 100)
        self.speed = random.uniform(0.2, 0.5)
        self.size = random.randint(30, 60)

    def move(self):
        self.x -= self.speed
        if self.x < -self.size * 3:
            self.x = WIDTH + random.randint(50, 150)
            self.y = random.randint(20, 100)
            self.speed = random.uniform(0.2, 0.5)
            self.size = random.randint(30, 60)

    def draw(self, surface):
        x, y, s = int(self.x), int(self.y), self.size
        pygame.draw.ellipse(surface, LIGHT_GRAY, (x, y + s//3, s * 2, s))
        pygame.draw.ellipse(surface, LIGHT_GRAY, (x + s//3, y, s, s))
        pygame.draw.ellipse(surface, LIGHT_GRAY, (x + s, y - s//3, s, s))
        pygame.draw.ellipse(surface, LIGHT_GRAY, (x + s + s//2, y + s//4, s, s))

clouds = [Cloud() for _ in range(5)]

class FallingStar:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)  # стартует выше экрана
        self.length = random.randint(5, 15)
        self.speed = random.uniform(2, 5)
        self.color = STAR_COLOR

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(-HEIGHT, 0)
            self.speed = random.uniform(2, 5)
            self.length = random.randint(5, 15)

    def draw(self, surface):
        end_y = self.y + self.length
        pygame.draw.line(surface, self.color, (self.x, self.y), (self.x, end_y), 2)
falling_stars = [FallingStar() for _ in range(20)]  # 20 падающих звезд

bird_y = HEIGHT // 2
bird_velocity = 0

hearts = []
pipes = []
coins = []

def check_coin_collection():
    global score
    for coin in coins:
        if not coin.collected and coin.collides_with(bird_x, bird_y, BIRD_RADIUS):
            coin.collected = True
            score += 10
def check_heart_collection():
    global lives
    for heart in hearts:
        if not heart.collected and heart.collides_with(bird_x, bird_y, BIRD_RADIUS):
            heart.collected = True
            if lives < 3:
                lives += 1

def main():
    global hearts
    global lives
    global bird_y, bird_velocity, pipes, coins, score, frame_count
    global pipe_gap, pipe_speed, menu, playing, game_over, highscore, is_night, difficulty_menu
    global GRAVITY, JUMP_STRENGTH

    running = True

    while running:
        clock.tick(FPS)

        if is_night:
            screen.fill(NIGHT_SKY)
            for star in stars:
                x, y, brightness, direction = star
                color = (brightness, brightness, int(brightness * 0.8))
                pygame.draw.circle(screen, color, (x, y), 2)
                star[2] += direction * 2
                if star[2] >= 255:
                    star[2] = 255
                    star[3] = -1
                elif star[2] <= 150:
                    star[2] = 150
                    star[3] = 1
            moon_x, moon_y = WIDTH - 70, 70
            pygame.draw.circle(screen, MOON_COLOR, (moon_x, moon_y), 40)
            pygame.draw.circle(screen, NIGHT_SKY, (moon_x + 15, moon_y - 10), 30)
            for fstar in falling_stars:
                fstar.update()
                fstar.draw(screen)

        else:
            screen.fill(BLUE)
            pygame.draw.circle(screen, YELLOW, (WIDTH - 70, 70), 40)
            draw_ground()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    is_night = not is_night

            if difficulty_menu:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if easy_button.collidepoint(mx, my):
                        pipe_speed = 2.5
                        pipe_gap = 250
                        GRAVITY = 0.4
                        JUMP_STRENGTH = -9
                        difficulty_menu = False
                        menu = False
                        playing = True
                        reset_game()
                        pipes.clear()
                        coins.clear()
                        hearts.clear()
                    elif normal_button.collidepoint(mx, my):
                        pipe_speed = 3
                        pipe_gap = 200
                        GRAVITY = 0.5
                        JUMP_STRENGTH = -10
                        difficulty_menu = False
                        menu = False
                        playing = True
                        reset_game()
                        pipes.clear()
                        coins.clear()
                        hearts.clear()
                    elif hard_button.collidepoint(mx, my):
                        pipe_speed = 4.5
                        pipe_gap = 160
                        GRAVITY = 0.6
                        JUMP_STRENGTH = -11
                        difficulty_menu = False
                        menu = False
                        playing = True
                        reset_game()
                        pipes.clear()
                        coins.clear()
                        hearts.clear()

            elif menu:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if start_button.collidepoint(mx, my):
                        difficulty_menu = True
                        menu = False

            elif playing:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    bird_velocity = JUMP_STRENGTH

            elif game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    difficulty_menu = True
                    game_over = False

        for cloud in clouds:
            cloud.move()
            cloud.draw(screen)

        if difficulty_menu:
            title = font.render("Выберите уровень сложности", True, BLACK)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            easy_button = draw_button("Простой", WIDTH//2 - 195, HEIGHT//2, 120, 50, GREEN, WHITE)
            normal_button = draw_button("Нормальный", WIDTH//2 - 70, HEIGHT//2, 140, 50, ORANGE, WHITE)
            hard_button = draw_button("Сложный", WIDTH//2 + 75, HEIGHT//2, 120, 50, RED, WHITE)
            info = small_font.render("Нажмите N для смены День/Ночь", True, BLACK)
            screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2 + 70))

        elif menu:
            title = font.render("Flappy Bird", True, BLACK)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            start_button = draw_button("Start Game", WIDTH//2 - 100, HEIGHT//2, 200, 50, GREEN, WHITE)
            info = small_font.render("Нажмите N для смены День/Ночь", True, BLACK)
            screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2 + 70))

        elif playing:
            bird_velocity += GRAVITY
            bird_y += bird_velocity

            if len(pipes) == 0 or pipes[-1].x < WIDTH - 200:
                pipes.append(Pipe(WIDTH))

            for pipe in pipes:
                pipe.update()
                pipe.draw(screen)

            pipes = [p for p in pipes if p.x + p.width > 0]

            if len(coins) == 0 or coins[-1].x < WIDTH - 150:
                coins.append(Coin(pipes))

            if len(hearts) == 0 or (hearts[-1].x < WIDTH - 400 and random.random() < 0.01):
                hearts.append(Heart(pipes))

            for heart in hearts:
                if not heart.collected:
                    heart.update()
                    heart.draw(screen)

            hearts = [h for h in hearts if h.x + h.radius > 0 and not h.collected]
            check_heart_collection()

            for coin in coins:
                if not coin.collected:
                    coin.update()
                    coin.draw(screen)

            coins = [c for c in coins if c.x + c.radius > 0 and not c.collected]

            check_coin_collection()

            draw_bird(bird_x, bird_y)

            score_label = font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_label, (10, 10))

            for i in range(lives):
                draw_heart(screen, 10 + i * 30, 50, 20)

            if check_collision(bird_y, pipes):
                lives -= 1
                if lives <= 0:
                    playing = False
                    game_over = True
                    if score > highscore:
                        highscore = score
                        save_highscore(highscore)
                else:
                    bird_y = HEIGHT // 2
                    bird_velocity = 0

            for pipe in pipes:
                if not pipe.passed and pipe.x + pipe.width < bird_x:
                    pipe.passed = True
                    score += 1

        elif game_over:
            over_label = font.render("Game Over", True, RED)
            screen.blit(over_label, (WIDTH//2 - over_label.get_width()//2, HEIGHT//3))
            score_label = small_font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_label, (WIDTH//2 - score_label.get_width()//2, HEIGHT//3 + 60))
            highscore_label = small_font.render(f"Highscore: {highscore}", True, BLACK)
            screen.blit(highscore_label, (WIDTH//2 - highscore_label.get_width()//2, HEIGHT//3 + 90))
            restart_label = small_font.render("Press SPACE to restart", True, BLACK)
            screen.blit(restart_label, (WIDTH//2 - restart_label.get_width()//2, HEIGHT//3 + 140))

        pygame.display.update()

if __name__ == "__main__":
    main()
