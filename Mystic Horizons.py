import pygame
import sys
import os
import random

# --- Setup ---
pygame.init()
clock = pygame.time.Clock()
worldx, worldy = 960, 720
fps = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
world = pygame.display.set_mode((worldx, worldy))
pygame.display.set_caption("Mystic Horizons")

# --- Fonts ---
title_font = pygame.font.SysFont("Arial", 80, bold=True)
button_font = pygame.font.SysFont("Arial", 40, bold=True)


# --- Background ---
class ParallaxBackground:
    def __init__(self):
        self.layers = []
        for i in range(1, 7):
            img = pygame.image.load(
                os.path.join("Images", f"Hills Layer 0{i}.png")
            ).convert_alpha()
            img = pygame.transform.scale(img, (worldx, worldy))
            self.layers.append(img)
        self.speeds = [0.1, 0.2, 0.4, 0.6, 0.8, 1.0]

    def draw_layers(self, surface, camera_x, start, end):
        for i in range(start, end):
            layer = self.layers[i]
            speed = self.speeds[i]
            offset = int((-camera_x * speed) % worldx)
            surface.blit(layer, (offset - worldx, 0))
            surface.blit(layer, (offset, 0))

    def draw_all(self, surface, camera_x=0):
        self.draw_layers(surface, camera_x, 0, len(self.layers))


background = ParallaxBackground()


# --- Player ---
class Player(pygame.sprite.Sprite):
    def __init__(self, scale=2):
        super().__init__()
        self.scale = scale
        self.animations = {"idle": [], "walk": [], "jump": [], "attack": []}
        self.state = "idle"
        self.prev_state = None
        self.frame = 0
        self.direction = "right"
        self.movex = 0
        self.on_ground = True
        self.attacking = False
        self.max_health = 100
        self.health = self.max_health

        # Load animations
        self.load_animation("IDLE.png", "idle", 4)
        self.load_animation("WALK.png", "walk", 4)
        self.load_animation("JUMP.png", "jump", 2)
        self.load_animation("ATTACK.png", "attack", 4)

        base_image = self.animations["idle"][0]
        self.image = base_image
        self.rect = base_image.get_rect()
        self.rect.width -= 20  # thinner hitbox (optional)
        self.rect.height -= 35  # shorter to match feet area
        self.rect.midbottom = (worldx // 2, worldy - 15)
        self.pos_x = float(self.rect.x)

        self.gravity = 0.2  # 0.2
        self.jump_strength = -6
        self.velocity_y = 0

    def load_animation(
        self, filename, state, frame_count, frame_w=64, frame_h=64, scale=None
    ):
        if scale is None:
            scale = self.scale
        path = os.path.join("Images", filename)
        sheet = pygame.image.load(path).convert_alpha()
        scaled_w = int(frame_w * scale)
        scaled_h = int(frame_h * scale)
        for i in range(frame_count):
            rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
            frame = sheet.subsurface(rect).copy()
            frame = pygame.transform.scale(frame, (scaled_w, scaled_h))
            base_surf = pygame.Surface((scaled_w, scaled_h), pygame.SRCALPHA)
            frame_rect = frame.get_rect(center=(scaled_w // 2, scaled_h // 2))
            base_surf.blit(frame, frame_rect)
            self.animations[state].append(base_surf)

    def control(self, x):
        self.movex = x
        if x < 0:
            self.direction = "left"
        elif x > 0:
            self.direction = "right"

    def jump(self):
        if self.on_ground:
            self.velocity_y = self.jump_strength
            self.on_ground = False
            self.state = "jump"

    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.frame = 0

    def update(self):
        # Gravity
        if self.velocity_y < 0:  # rising
            self.velocity_y += self.gravity * 0.5
        else:  # falling
            self.velocity_y += self.gravity * 0.5
        self.rect.y += self.velocity_y
        ground_y = worldy - 15
        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.velocity_y = 0
            self.on_ground = True

        # Movement
        self.pos_x += self.movex
        self.rect.x = int(self.pos_x)

        # Determine state
        if self.attacking:
            self.state = "attack"
        elif not self.on_ground:
            self.state = "jump"
        elif self.movex != 0:
            self.state = "walk"
        else:
            self.state = "idle"

        # Reset animation frame if state changed
        if self.state != self.prev_state:
            self.frame = 0
            self.prev_state = self.state

        # Animate
        self.frame += 1
        frame_speed = 40
        current_animation = self.animations[self.state]
        frame_index = (self.frame // frame_speed) % len(current_animation)
        frame_image = current_animation[frame_index]

        # End attack after last frame
        if self.state == "attack" and frame_index == len(current_animation) - 1:
            self.attacking = False

        # Flip image
        if self.direction == "left":
            frame_image = pygame.transform.flip(frame_image, True, False)

        self.image = frame_image

    def draw_healthbar(self, surface):
        bar_width = 200
        bar_height = 20
        x = 20
        y = 20
        fill = (self.health / self.max_health) * bar_width
        pygame.draw.rect(surface, RED, (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (x, y, fill, bar_height))
        pygame.draw.rect(surface, BLACK, (x, y, bar_width, bar_height), 2)


player = Player(scale=2)
player_group = pygame.sprite.Group(player)
steps = 1.5


class CollisionBlock(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)


# --- PLATFORM CLASS ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        path = os.path.join("Images", "platform.png")
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        # Place the platform rect at the bottom-left aligned to your desired y
        self.rect.bottomleft = (x, y + height)


platforms = pygame.sprite.Group()
platform_list = [
    Platform(100, worldy - 150, 150, 40),
    Platform(350, worldy - 250, 150, 40),
    Platform(650, worldy - 200, 150, 40),
    Platform(150, worldy - 400, 150, 40),
    Platform(450, worldy - 500, 150, 40),
    Platform(750, worldy - 450, 150, 40),
]

for p in platform_list:
    platforms.add(p)

tile_size = 64
tile_map = [
    "......................",
    ".......###............",
    "......................",
    ".###.......##.........",
    "......................",
    "......................",
]

for y, row in enumerate(tile_map):
    for x, tile in enumerate(row):
        if tile == "#":
            p = Platform(x * tile_size, worldy - 400 + y * 40, tile_size, 40)
            platforms.add(p)


def player_platform_collision(player, platforms):
    player.on_ground = False
    for platform in platforms:
        # Moving downward
        if player.velocity_y >= 0:
            # Check if player's feet are overlapping top of platform
            if (
                player.rect.bottom + player.velocity_y > platform.rect.top
                and player.rect.bottom <= platform.rect.top
                and player.rect.right > platform.rect.left + 10
                and player.rect.left < platform.rect.right - 10
            ):
                # Land on platform
                player.rect.bottom = platform.rect.top
                player.velocity_y = 0
                player.on_ground = True
                break

    # If not on any platform, check for ground
    if not player.on_ground:
        if player.rect.bottom >= worldy - 15:
            player.rect.bottom = worldy - 15
            player.velocity_y = 0
            player.on_ground = True


# --- Enemy Crow ---
class EnemyCrow(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=2):
        super().__init__()
        self.scale = scale
        self.animations = {
            "idle": [],
            "walk": [],
            "attack": [],
            "damage": [],
            "death": [],
        }
        self.state = "idle"
        self.prev_state = None
        self.frame = 0
        self.direction = 1
        self.speed = 2
        self.rect = pygame.Rect(x, y, 64 * scale, 64 * scale)
        self.health = 50
        self.max_health = 50
        self.alive = True
        self.attack_range = 50
        self.attack_damage = 10

        # Load animations
        self.load_animation("crow_idle.png", "idle", 4)
        self.load_animation("crow_walk.png", "walk", 4)
        self.load_animation("crow_attack.png", "attack", 4)
        self.load_animation("crow_damage.png", "damage", 2)
        self.load_animation("crow_death2.png", "death", 4)

        self.image = self.animations["idle"][0]

    def load_animation(
        self, filename, state, frame_count, frame_w=64, frame_h=64, scale=None
    ):
        if scale is None:
            scale = self.scale
        path = os.path.join("Images", filename)
        sheet = pygame.image.load(path).convert_alpha()
        scaled_w = int(frame_w * scale)
        scaled_h = int(frame_h * scale)
        for i in range(frame_count):
            rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
            frame = sheet.subsurface(rect).copy()
            frame = pygame.transform.scale(frame, (scaled_w, scaled_h))
            base_surf = pygame.Surface((scaled_w, scaled_h), pygame.SRCALPHA)
            frame_rect = frame.get_rect(center=(scaled_w // 2, scaled_h // 2))
            base_surf.blit(frame, frame_rect)
            self.animations[state].append(base_surf)

    def update(self):
        frame_speed = 50

        if self.health <= 0 and self.alive:
            self.alive = False
            self.state = "death"
            self.frame = 0

        if not self.alive:
            # Death animation
            current_animation = self.animations["death"]
            frame_index = min(self.frame // frame_speed, len(current_animation) - 1)
            frame_image = current_animation[frame_index]

            if self.direction == -1:
                frame_image = pygame.transform.flip(frame_image, True, False)
            self.image = frame_image

            # Remove sprite after death animation finishes
            if frame_index == len(current_animation) - 1:
                self.kill()

        else:
            # Patrol left-right
            self.rect.x += self.speed * self.direction
            if self.rect.right >= worldx - 50:
                self.direction = -1
            elif self.rect.left <= 50:
                self.direction = 1

            # Attack if player is close
            if abs(player.rect.centerx - self.rect.centerx) < self.attack_range:
                self.state = "attack"
                player.health -= self.attack_damage / fps
            else:
                self.state = "walk"

            # Choose animation
            current_animation = self.animations[self.state]
            frame_index = (self.frame // frame_speed) % len(current_animation)
            frame_image = current_animation[frame_index]

            if self.direction == -1:
                frame_image = pygame.transform.flip(frame_image, True, False)
            self.image = frame_image

        # Advance frame counter
        self.frame += 1

        # Animate
        self.frame += 1
        frame_speed = 50
        current_animation = self.animations[self.state]
        frame_index = (self.frame // frame_speed) % len(current_animation)
        frame_image = current_animation[frame_index]

        if self.direction == -1:
            frame_image = pygame.transform.flip(frame_image, True, False)
        self.image = frame_image

    def draw_healthbar(self, surface):
        bar_width = 30 * self.scale
        bar_height = 10
        x = self.rect.centerx - bar_width // 2  # center the bar
        y = self.rect.top - 1
        fill = (self.health / self.max_health) * bar_width
        pygame.draw.rect(surface, RED, (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (x, y, fill, bar_height))
        pygame.draw.rect(surface, BLACK, (x, y, bar_width, bar_height), 2)


enemy = EnemyCrow(300, worldy - 110)
enemy_group = pygame.sprite.Group(enemy)


# --- Coin class ---
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        path = os.path.join("Images", "coin.png")
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=(x, y))


coin_group = pygame.sprite.Group()


def spawn_coin():
    x = random.randint(100, worldx - 100)
    y = random.randint(200, worldy - 200)
    coin = Coin(x, y)
    coin_group.empty()
    coin_group.add(coin)


spawn_coin()

level = 1


# --- Buttons ---
def draw_fancy_button(surface, text, rect, color, hover_color, border_color=(0, 0, 0)):
    mouse_pos = pygame.mouse.get_pos()
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(surface, hover_color, rect, border_radius=15)
        pygame.draw.rect(surface, border_color, rect, 3, border_radius=15)
    else:
        pygame.draw.rect(surface, color, rect, border_radius=15)
        pygame.draw.rect(surface, border_color, rect, 3, border_radius=15)
    text_surf = button_font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)


play_button = pygame.Rect(worldx // 2 - 120, worldy // 2, 240, 70)
exit_button = pygame.Rect(worldx // 2 - 120, worldy // 2 + 120, 240, 70)


def draw_title(
    surface, text, font, pos, color, outline_color=(0, 0, 0), outline_width=3
):
    base = font.render(text, True, color)
    x, y = pos
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                surf = font.render(text, True, outline_color)
                surface.blit(
                    surf,
                    (x - surf.get_width() // 2 + dx, y - surf.get_height() // 2 + dy),
                )
    surface.blit(base, (x - base.get_width() // 2, y - base.get_height() // 2))


def main_menu():
    menu_scroll = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_button.collidepoint(event.pos):
                        return
                    if exit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
        menu_scroll += 0.2
        background.draw_all(world, menu_scroll)
        draw_title(
            world, "Mystic Horizons", title_font, (worldx // 2, worldy // 4), WHITE
        )
        draw_fancy_button(world, "Play", play_button, WHITE, (200, 200, 200))
        draw_fancy_button(world, "Exit", exit_button, WHITE, (200, 200, 200))
        pygame.display.flip()
        clock.tick(fps)


def game_over_screen():
    over_font = pygame.font.SysFont("Arial", 80, bold=True)
    small_font = pygame.font.SysFont("Arial", 40, bold=True)
    timer = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # grįžtam į main_menu()

        world.fill((0, 0, 0))
        text = over_font.render("GAME OVER", True, RED)
        subtext = small_font.render("Press any key to return to menu", True, WHITE)
        world.blit(
            text,
            (worldx // 2 - text.get_width() // 2, worldy // 2 - 100),
        )
        world.blit(
            subtext,
            (worldx // 2 - subtext.get_width() // 2, worldy // 2),
        )
        pygame.display.flip()
        clock.tick(fps)
        timer += 1
        if timer > 300:  # auto-return po ~5 sekundžių
            return


# --- Run Main Menu ---
main_menu()

# --- Game Loop ---
camera_x = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                player.control(-steps)
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                player.control(steps)
            if event.key == pygame.K_SPACE:
                player.jump()
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                player.control(0)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player.attack()
                # Damage enemy if close
                if abs(player.rect.centerx - enemy.rect.centerx) < 80:
                    enemy.health -= 5

    # Update
    player.update()
    enemy_group.update()

    # --- Coin surinkimas ---
    for coin in coin_group:
        if player.rect.colliderect(coin.rect.inflate(-30, -30)):
            coin.kill()
            level += 1
            world.fill((0, 0, 0))
            font = pygame.font.SysFont("Arial", 80, bold=True)
            text = font.render(f"LYGIS {level}", True, (255, 215, 0))
            world.blit(text, (worldx // 2 - text.get_width() // 2, worldy // 2 - 50))
            pygame.display.flip()
            pygame.time.delay(2000)
            # Resetinam player ir spawninam naują coin
            player.rect.midbottom = (worldx // 2, worldy - 15)
            player.pos_x = float(player.rect.x)
            spawn_coin()
            # Respawninam enemy (jei reikia)
            if not enemy.alive:
                enemy.alive = True
                enemy.health = enemy.max_health
                enemy.rect.x = random.randint(100, worldx - 100)
                enemy.rect.y = worldy - 110
                enemy_group.add(enemy)

    camera_x = 0
    player_platform_collision(player, platforms)

    # Draw background layers 0-4
    background.draw_layers(world, camera_x, 0, 5)

    # Draw enemy and healthbar
    enemy_group.draw(world)
    coin_group.draw(world)
    for e in enemy_group:
        e.draw_healthbar(world)

    platforms.draw(world)

    # Draw player
    player_group.draw(world)
    player.draw_healthbar(world)

    # Draw front layer
    background.draw_layers(world, camera_x, 5, 6)

    if player.health <= 0:
        game_over_screen()
        main_menu()
        # Reset player gyvybes ir poziciją
        player.health = player.max_health
        player.rect.midbottom = (worldx // 2, worldy - 15)
        player.pos_x = float(player.rect.x)

    font = pygame.font.SysFont("Arial", 40, bold=True)
    level_text = font.render(f"Lygis: {level}", True, WHITE)
    world.blit(level_text, (worldx - 200, 20))

    if "show_level_text" in locals() and show_level_text:
        big_font = pygame.font.SysFont("Arial", 80, bold=True)
        text = big_font.render(f"LYGIS {level}", True, (255, 215, 0))
        world.blit(text, (worldx // 2 - text.get_width() // 2, worldy // 2 - 50))
        level_display_timer -= 1
        if level_display_timer <= 0:
            show_level_text = False

    pygame.display.flip()
