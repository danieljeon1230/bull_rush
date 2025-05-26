import pygame
import random
import sys
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 30
PLAYER_SPEED = 300
FPS = 60
INITIAL_BULL_SIZE = 40
MAX_BULL_SIZE = 100
BULL_SIZE_GROWTH = 4

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐂 Bull Rush")
clock = pygame.time.Clock()

WHITE, RED, BLUE, BLACK = (255, 255, 255), (200, 0, 0), (0, 100, 255), (0, 0, 0)

confined_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 150, 400, 300)
player = pygame.Rect(confined_rect.centerx, confined_rect.centery, PLAYER_SIZE, PLAYER_SIZE)

font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

def normal_spawn_pos(max_val, size):
    center = max_val / 2
    std_dev = max_val / 6
    val = random.gauss(center, std_dev)
    return max(0, min(max_val - size, int(val)))

class Bull:
    def __init__(self, direction, size, min_speed, max_speed):
        self.direction = direction
        self.size = size
        speed = random.randint(min_speed, max_speed)

        if direction == "horizontal":
            y = normal_spawn_pos(HEIGHT, size)
            x = 0 - size if random.choice([True, False]) else WIDTH
            self.rect = pygame.Rect(x, y, size, size)
            self.speed_x = speed if x < WIDTH // 2 else -speed
            self.speed_y = 0
        else:
            x = normal_spawn_pos(WIDTH, size)
            y = 0 - size if random.choice([True, False]) else HEIGHT
            self.rect = pygame.Rect(x, y, size, size)
            self.speed_y = speed if y < HEIGHT // 2 else -speed
            self.speed_x = 0

    def move(self, delta_time):
        self.rect.x += self.speed_x * delta_time
        self.rect.y += self.speed_y * delta_time

    def off_screen(self):
        return (
            self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT
        )

    def will_enter_confined_area(self):
        future_rect = self.rect.move(self.speed_x, self.speed_y)
        return future_rect.colliderect(confined_rect)

bulls = []
spawn_timer = 0
level = 1
score = 0
spawn_interval = 800
level_message_timer = 0
game_over = False
paused = False

def reset_game():
    global bulls, spawn_timer, level, score, spawn_interval, level_message_timer, game_over, paused
    bulls = []
    spawn_timer = 0
    level = 1
    score = 0
    spawn_interval = 800
    level_message_timer = 0
    game_over = False
    paused = False
    player.x = confined_rect.centerx
    player.y = confined_rect.centery

while True:
    delta_time = clock.tick(FPS) / 1000
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, confined_rect, 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    reset_game()
            else:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if paused and event.key == pygame.K_r:
                    reset_game()

    if not game_over and not paused:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player.y -= PLAYER_SPEED * delta_time
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player.y += PLAYER_SPEED * delta_time
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player.x -= PLAYER_SPEED * delta_time
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player.x += PLAYER_SPEED * delta_time
        player.clamp_ip(confined_rect)

        spawn_timer += delta_time * 1000
        if spawn_timer > spawn_interval:
            direction = random.choice(["horizontal", "vertical"])
            bull_size = min(INITIAL_BULL_SIZE + BULL_SIZE_GROWTH * (level - 1), MAX_BULL_SIZE)
            min_speed = 150 + (level - 1) * 20
            max_speed = 250 + (level - 1) * 30
            temp_bull = Bull(direction, bull_size, min_speed, max_speed)
            if temp_bull.will_enter_confined_area():
                bulls.append(temp_bull)
                spawn_timer = 0

        for bull in bulls[:]:
            bull.move(delta_time)
            pygame.draw.rect(screen, RED, bull.rect)
            if bull.off_screen():
                bulls.remove(bull)
            elif bull.rect.colliderect(player):
                game_over = True

        pygame.draw.rect(screen, BLUE, player)

        score += 1
        if score % (FPS * 10) == 0:
            level += 1
            spawn_interval = max(400, spawn_interval - 100)
            level_message_timer = 2.0

    score_text = font.render(f"Score: {score // FPS}", True, WHITE)
    screen.blit(score_text, (10, 10))

    if level_message_timer > 0:
        level_message = font.render(f"Level Up! Level {level}", True, WHITE)
        screen.blit(level_message, (WIDTH - level_message.get_width() - 10, 10))
        level_message_timer -= delta_time

    pause_msg = font.render("Press P to Pause", True, WHITE)
    quit_msg = font.render("Press Q to Quit", True, WHITE)
    screen.blit(pause_msg, (WIDTH - pause_msg.get_width() - 10, HEIGHT - pause_msg.get_height() - 10))
    screen.blit(quit_msg, (10, HEIGHT - quit_msg.get_height() - 10))

    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        paused_text = big_font.render("PAUSED", True, WHITE)
        resume_msg = font.render("Press P again to Resume", True, WHITE)
        quit_msg_paused = font.render("Press Q to Quit", True, WHITE)
        restart_msg = font.render("Press R to Restart", True, WHITE)

        screen.blit(paused_text, (
            WIDTH // 2 - paused_text.get_width() // 2,
            HEIGHT // 2 - 100))
        screen.blit(resume_msg, (
            WIDTH // 2 - resume_msg.get_width() // 2,
            HEIGHT // 2 - 20))
        screen.blit(quit_msg_paused, (
            WIDTH // 2 - quit_msg_paused.get_width() // 2,
            HEIGHT // 2 + 20))
        screen.blit(restart_msg, (
            WIDTH // 2 - restart_msg.get_width() // 2,
            HEIGHT // 2 + 60))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        game_over_text = big_font.render("GAME OVER", True, RED)
        final_score_text = font.render(f"Final Score: {score // FPS}", True, WHITE)
        prompt_text = font.render("Press Q to Quit", True, WHITE)
        restart_text = font.render("Press R to Restart", True, WHITE)

        screen.blit(game_over_text, (
            WIDTH // 2 - game_over_text.get_width() // 2,
            HEIGHT // 2 - 100))
        screen.blit(final_score_text, (
            WIDTH // 2 - final_score_text.get_width() // 2,
            HEIGHT // 2 - 20))
        screen.blit(prompt_text, (
            WIDTH // 2 - prompt_text.get_width() // 2,
            HEIGHT // 2 + 40))
        screen.blit(restart_text, (
            WIDTH // 2 - restart_text.get_width() // 2,
            HEIGHT // 2 + 80))

    pygame.display.flip()
