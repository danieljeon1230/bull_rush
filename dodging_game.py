import pygame
import random
import sys

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

player = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)

font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

class Bull:
    def __init__(self, direction, size):
        self.direction = direction
        self.size = size
        speed = random.randint(200, 300)

        def clamp(value, min_val, max_val):
            return max(min_val, min(value, max_val))

        if direction == "horizontal":
            self.rect = pygame.Rect(
                0 if random.choice([True, False]) else WIDTH,
                int(clamp(random.gauss(HEIGHT // 2, HEIGHT // 6), 0, HEIGHT - size)),
                size, size)
            self.speed_x = speed if self.rect.x == 0 else -speed
            self.speed_y = 0
        else:
            self.rect = pygame.Rect(
                int(clamp(random.gauss(WIDTH // 2, WIDTH // 6), 0, WIDTH - size)),
                0 if random.choice([True, False]) else HEIGHT,
                size, size)
            self.speed_y = speed if self.rect.y == 0 else -speed
            self.speed_x = 0

    def move(self, delta_time):
        self.rect.x += self.speed_x * delta_time
        self.rect.y += self.speed_y * delta_time

    def off_screen(self):
        return (
            self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT
        )

bulls = []
spawn_timer = 0
level = 1
score = 0
spawn_interval = 800
level_message_timer = 0
game_over = False

while True:
    delta_time = clock.tick(FPS) / 1000
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_r:
                bulls.clear()
                score = 0
                level = 1
                spawn_interval = 800
                player.x, player.y = WIDTH // 2, HEIGHT // 2
                game_over = False


    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player.y -= PLAYER_SPEED * delta_time
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player.y += PLAYER_SPEED * delta_time
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player.x -= PLAYER_SPEED * delta_time
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player.x += PLAYER_SPEED * delta_time
        player.clamp_ip(screen.get_rect())

        spawn_timer += delta_time * 1000
        if spawn_timer > spawn_interval:
            direction = random.choice(["horizontal", "vertical"])
            size = min(INITIAL_BULL_SIZE + (level - 1) * BULL_SIZE_GROWTH, MAX_BULL_SIZE)
            bulls.append(Bull(direction, size))
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
