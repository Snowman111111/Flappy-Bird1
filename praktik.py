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

# Цвета для ночи
NIGHT_SKY = (10, 10, 40)
MOON_COLOR = (230, 230, 210)
STAR_COLOR = (255, 255, 200)

BIRD_RADIUS = 20
GRAVITY = 0.5
JUMP_STRENGTH = -10

PIPE_WIDTH = 70
PIPE_GAP_START = 200
PIPE_GAP_MIN = 120
PIPE_SPEED_START = 3
PIPE_SPEED_MAX = 8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird with Moving Pipes and Coins")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)

bird_x = 100
bird_y = HEIGHT // 2
bird_velocity = 0

score = 0
frame_count = 0

menu = True
playing = False
game_over = False

pipe_gap = PIPE_GAP_START
pipe_speed = PIPE_SPEED_START

HIGHSCORE_FILE = "highscore.txt"

# Режим дня/ночи
is_night = False

# Звёзды — список координат и "яркости"
NUM_STARS = 50
stars = []
for _ in range(NUM_STARS):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT // 2)  # Звёзды на верхней половине экрана
    brightness = random.randint(150, 255)
    stars.append([x, y, brightness, random.choice([1, -1])])  # последний элемент — направление мерцания

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

def check_collision(bird_y, pipes):
    for pipe in pipes:
        if pipe.collides_with(bird_x, bird_y, BIRD_RADIUS):
            return True
    if bird_y - BIRD_RADIUS < 0 or bird_y + BIRD_RADIUS > HEIGHT:
        return True
    return False

def reset_game():
    global bird_y, bird_velocity, score, frame_count, pipe_gap, pipe_speed
    bird_y = HEIGHT // 2
    bird_velocity = 0
    score = 0
    frame_count = 0
    pipe_gap = PIPE_GAP_START
    pipe_speed = PIPE_SPEED_START

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = PIPE_WIDTH
        self.color = random.choice([GREEN, DARK_GREEN, ORANGE])
        self.top_height = random.randint(50, HEIGHT - pipe_gap - 50)
        self.passed = False

        # 40% труб двигаются вверх-вниз
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
        # Ограничения по высоте
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
        max_attempts = 100
        for _ in range(max_attempts):
            y_candidate = random.randint(50, HEIGHT - 50)
            collide = False
            for pipe in pipes:
                pipe_top = pipe.current_top_height if hasattr(pipe, 'current_top_height') else pipe.top_height
                pipe_bottom = pipe_top + pipe_gap
                # Проверяем, чтобы монета не находилась в области трубы с отступом радиуса
                if (self.x + self.radius > pipe.x and self.x - self.radius < pipe.x + pipe.width):
                    # Проверяем вертикально с запасом радиуса, чтобы монета не перекрывалась
                    if pipe_top - self.radius < y_candidate < pipe_bottom + self.radius:
                        collide = True
                        break
            if not collide:
                return y_candidate
        # Если не нашли подходящее место, ставим посередине экрана (редко происходит)
        return HEIGHT // 2

    def update(self):
        self.x -= pipe_speed

    def draw(self, surface):
        # Рисуем монету с "блеском" - два круга
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x - self.radius//3), int(self.y - self.radius//3)), self.radius//3)

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
        # Рисуем облако из нескольких овалов для пушистости
        x, y, s = int(self.x), int(self.y), self.size
        # Основа
        pygame.draw.ellipse(surface, LIGHT_GRAY, (x, y + s//3, s * 2, s))
        # Верхние "пухлые" части облака
        pygame.draw.ellipse(surface, LIGHT_GRAY, (x + s//3, y, s, s))
        pygame.draw.ellipse(surface, LIGHT_GRAY, (x + s, y - s//3, s, s))
        pygame.draw.ellipse(surface, LIGHT_GRAY, (x + s + s//2, y + s//4, s, s))

clouds = [Cloud() for _ in range(5)]

bird_y = HEIGHT // 2
bird_velocity = 0

pipes = []
coins = []

def check_coin_collection():
    global score
    for coin in coins:
        if not coin.collected and coin.collides_with(bird_x, bird_y, BIRD_RADIUS):
            coin.collected = True
            score += 10

def main():
    global bird_y, bird_velocity, pipes, coins, score, frame_count
    global pipe_gap, pipe_speed, menu, playing, game_over, highscore, is_night

    running = True
    while running:
        clock.tick(FPS)

        # Фон и небо + солнце или луна и звёзды
        if is_night:
            screen.fill(NIGHT_SKY)

            # Рисуем звёзды с мерцанием
            for star in stars:
                x, y, brightness, direction = star
                color = (brightness, brightness, int(brightness * 0.8))
                pygame.draw.circle(screen, color, (x, y), 2)
                # Изменяем яркость для мерцания
                star[2] += direction * 2
                if star[2] >= 255:
                    star[2] = 255
                    star[3] = -1
                elif star[2] <= 150:
                    star[2] = 150
                    star[3] = 1

            # Рисуем луну (простой круг с "затенением")
            moon_x, moon_y = WIDTH - 70, 70
            pygame.draw.circle(screen, MOON_COLOR, (moon_x, moon_y), 40)
            pygame.draw.circle(screen, NIGHT_SKY, (moon_x + 15, moon_y - 10), 30)
        else:
            screen.fill(BLUE)
            # Рисуем солнце
            pygame.draw.circle(screen, YELLOW, (WIDTH - 70, 70), 40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Переключение день/ночь клавишей N
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    is_night = not is_night

            if menu:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if start_button.collidepoint(mx, my):
                        menu = False
                        playing = True
                        reset_game()
                        pipes.clear()
                        coins.clear()
            elif playing:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    bird_velocity = JUMP_STRENGTH
            elif game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    menu = True
                    game_over = False

        # Рисуем и двигаем облака
        # Можно не рисовать облака ночью, но я оставил их для атмосферы
        for cloud in clouds:
            cloud.move()
            cloud.draw(screen)

        if menu:
            title = font.render("Flappy Bird", True, BLACK)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            start_button = draw_button("Start Game", WIDTH//2 - 100, HEIGHT//2, 200, 50, GREEN, WHITE)
            info = small_font.render("Press N to toggle Day/Night anytime", True, BLACK)
            screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2 + 70))

        elif playing:
            bird_velocity += GRAVITY
            bird_y += bird_velocity

            # Создаём трубы
            if len(pipes) == 0 or pipes[-1].x < WIDTH - 200:
                pipes.append(Pipe(WIDTH))

            # Обновляем трубы
            for pipe in pipes:
                pipe.update()
            # Удаляем трубы, которые ушли за экран
            if pipes and pipes[0].x < -PIPE_WIDTH:
                pipes.pop(0)

            # Создаём монеты
            if len(coins) == 0 or (coins[-1].x < WIDTH - 250 and random.random() < 0.02):
                coins.append(Coin(pipes))

            # Обновляем монеты
            for coin in coins:
                coin.update()
            # Удаляем собранные или ушедшие монеты
            coins = [c for c in coins if c.x > -20 and not c.collected]

            check_coin_collection()

            # Проверка столкновений
            if check_collision(bird_y, pipes):
                playing = False
                game_over = True
                if score > highscore:
                    highscore = score
                    save_highscore(highscore)

            # Проверяем, прошла ли птица трубу, чтобы увеличить очки
            for pipe in pipes:
                if not pipe.passed and pipe.x + PIPE_WIDTH < bird_x:
                    pipe.passed = True
                    score += 1

                    # Сужаем разрыв и увеличиваем скорость постепенно, но не больше лимита
                    if pipe_gap > PIPE_GAP_MIN:
                        pipe_gap -= 1
                    if pipe_speed < PIPE_SPEED_MAX:
                        pipe_speed += 0.1

            # Рисуем трубы
            for pipe in pipes:
                pipe.draw(screen)

            # Рисуем монеты
            for coin in coins:
                if not coin.collected:
                    coin.draw(screen)

            # Рисуем птицу
            draw_bird(bird_x, bird_y)

            # Отображаем счет
            score_text = font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_text, (10, 10))

            highscore_text = small_font.render(f"Highscore: {highscore}", True, BLACK)
            screen.blit(highscore_text, (10, 50))

        elif game_over:
            game_over_text = font.render("Game Over", True, RED)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//3))
            score_text = small_font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//3 + 60))
            highscore_text = small_font.render(f"Highscore: {highscore}", True, BLACK)
            screen.blit(highscore_text, (WIDTH//2 - highscore_text.get_width()//2, HEIGHT//3 + 90))
            restart_text = small_font.render("Press SPACE to Restart", True, BLACK)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//3 + 140))

        pygame.display.flip()


if __name__ == "__main__":
    main()
