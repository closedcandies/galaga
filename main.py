import pygame
import random
import time
import os

SPEED = 2
ENEMY_SPEED = 1
BULLET_SPEED = 6
SIZE = WIDTH, HEIGHT = (600, 600)
PLAYER_POSITION = 530
HOLD_TIME = 2
PLAYER_LIVES = 3
START_IMAGE = 'data/start_image.png'
GMOVER_IMAGE = 'data/game_over.png'
PLAYER_MODEL = 'data/images/player_spaceship.png'
ENEMY_MODEL = 'data/images/enemy_shooter.png'
BLOW_MODELS = sorted(os.listdir('data/blow_images'), key=lambda x: int(list(x.split('.')[0])[-1]))
BLOW_PATH = 'data/blow_images/'
BULLET_MODEL = 'data/images/bullet.png'
ENEMY_BULLET_MODEL = 'data/images/enemy_bullet.png'
BEST_SCORE_PATH = 'data/score.txt'
PLAYER_HIT = 1
GAME_CONTINUE = 2
LEFT_BORDER = 3
RIGHT_BORDER = 4
LABELS_Y, LABELS_DELTA = 10, 80


def get_bscore():
    bscore = int(open(BEST_SCORE_PATH, 'r').read().strip())
    return bscore


def update_score(score, bscore):
    if score > bscore:
        with open(BEST_SCORE_PATH, 'w') as file:
            file.write(str(score))


def start(screen):
    running = True
    button = pygame.sprite.Sprite()
    button.add(main_group)
    button.image = pygame.image.load(START_IMAGE)
    button.rect = button.image.get_rect()
    button.rect.x, button.rect.y = int(WIDTH * 0.5 - button.rect.w * 0.5), int(
        HEIGHT * 0.5 - button.rect.h * 0.5)
    for i in range(50):
        Star(main_group)
    while running:
        pygame.draw.rect(screen, (255, 255, 255), (0, 0, 100, 100))
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] in range(button.rect.x, button.rect.x + button.rect.w):
                    if event.pos[1] in range(button.rect.y, button.rect.y + button.rect.h):
                        button.kill()
                        return True
            elif event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        main_group.update()
        main_group.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
    return False


def view_stats():
    gmover_sprite = pygame.sprite.Sprite()
    gmover_sprite.image = pygame.image.load(GMOVER_IMAGE)
    gmover_sprite.add(main_group)
    gmover_sprite.rect = gmover_sprite.image.get_rect()
    gmover_sprite.rect.x = int(WIDTH * 0.5 - gmover_sprite.rect.w * 0.5)
    gmover_sprite.rect.y = int(HEIGHT * 0.5 - gmover_sprite.rect.h * 0.5)
    text = 'Shots fired ' + str(shots) + '. Enemies killed ' + str(player.killed)
    text = font.render(text, True, (0, 0, 255))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
        screen.fill((0, 0, 0))
        screen.blit(text, (gmover_sprite.rect.x, gmover_sprite.rect.y + gmover_sprite.rect.w + 5))
        main_group.update()
        main_group.draw(screen)
        pygame.display.flip()
        clock.tick(fps)


class Player(pygame.sprite.Sprite):
    def __init__(self, enemy_group, groups):
        super().__init__()
        for group in groups:
            self.add(group)
        self.enemy_group, self.blow_images, self.blow_image = enemy_group, BLOW_MODELS, 0
        self.map_width, self.map_height = SIZE
        self.speed = SPEED
        self.blow_path = BLOW_PATH
        self.score, self.killed = 0, 0
        self.default_img = PLAYER_MODEL
        self.image = pygame.image.load(self.default_img)
        self.rect = self.image.get_rect()
        self.rect.x, self.bullet = 100, 0
        self.rect.y, self.lives = PLAYER_POSITION, PLAYER_LIVES

    def update(self, direction=0, score=0, killed=0):
        del_x = 0
        self.score += score
        self.killed += killed
        if (direction == -1 and self.rect.x > 0) or (direction == 1 and self.rect.x < self.map_width - self.rect.w):
            del_x = direction * self.speed
        self.rect = self.rect.move(del_x, 0)
        bullet = pygame.sprite.spritecollideany(self, self.enemy_group)
        if bullet or self.bullet:
            self.bullet = bullet if bullet else self.bullet
            self.blow()
            return PLAYER_HIT
        else:
            return GAME_CONTINUE

    def blow(self):
        self.image = pygame.image.load(self.blow_path + self.blow_images[int(self.blow_image)])
        self.blow_image += 0.5
        if self.blow_image == len(self.blow_images) - 1:
            self.lives -= 1
            pygame.draw.rect(self.image, (0, 0, 0), (0, 0, self.rect.w, self.rect.h))
            time.sleep(1)
            self.image = pygame.image.load(self.default_img)
            self.blow_image, self.bullet = 0, 0
            for enemy in enemy_group:
                enemy.kill()
        if self.lives == 0:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, host, groups, image):
        super().__init__()
        for group in groups:
            self.add(group)
        self.speed = BULLET_SPEED * 0.8 if host in enemy_group else -BULLET_SPEED
        self.host = host
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.host.rect.x + self.host.rect.w // 2 - self.rect.w // 2, self.host.rect.y

    def update(self, *args):
        self.rect = self.rect.move(0, self.speed)
        if self.rect.y > self.host.map_height or self.rect.y < 0:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_group, groups, seq_pos):
        super().__init__()
        for group in groups:
            self.add(group)
        self.player_group, self.speed, self.blow_path = player_group, ENEMY_SPEED, BLOW_PATH
        self.map_width, self.map_height = SIZE
        self.bullet_image, self.blow_images, self.blow_image = ENEMY_BULLET_MODEL, BLOW_MODELS, 0
        self.image = pygame.image.load(ENEMY_MODEL)
        self.hold_time = HOLD_TIME
        self.rect = self.image.get_rect()
        '''Выбираем, откуда появится враг'''
        if random.randint(0, 1):
            self.rect.x = -self.rect.w * seq_pos
            self.border = LEFT_BORDER
        else:
            self.rect.x = self.map_width + self.rect.w * seq_pos
            self.border = RIGHT_BORDER
        '''Выбираем точку на карте, где враг повиснет перед атакой'''
        self.const_x = random.randint(1, self.map_width // self.rect.w - 1) * self.rect.w
        self.const_y = random.randint(2, 4) * self.rect.h
        self.rect.y = self.const_y + 2 * self.rect.h
        self.perform_stage = 0
        self.timer = 0
        self.performing, self.bullet = True, False

    def update(self):
        bullet = pygame.sprite.spritecollideany(self, self.player_group)
        if bullet or self.bullet:
            self.bullet = bullet if bullet else self.bullet
            self.performing = False
            self.blow()
        elif self.performing:
            self.perform()
        else:
            if int(time.time()) - int(self.timer) >= self.hold_time:
                self.attack()
        if self.rect.y > self.map_height or self.rect.y < 0 and not self.performing:
            self.kill()

    def blow(self):
        self.image = pygame.image.load(self.blow_path + self.blow_images[int(self.blow_image)])
        self.blow_image += 0.5
        if self.blow_image == len(self.blow_images) - 1:
            self.player_group.update(0, 50, 1)
            self.kill()

    def perform(self):
        '''В оригинальной игре враги вылетали по спирали. Я долго думал, как анимировать такую спираль
        и не нашел ничего лучше, чем разбить полет на отрезки и в каждом выполнять часть пируэта'''
        del_x = self.speed if self.perform_stage in (0, 1, 4) else -self.speed
        del_x = -del_x if self.border == RIGHT_BORDER else del_x  # если враг появится справа, то инвертируем
        if self.perform_stage in (0, 4):
            delta_y = 0
        else:
            delta_y = self.speed if self.perform_stage == 3 else -self.speed
        self.rect = self.rect.move(del_x, delta_y)
        if self.rect.x == self.const_x and self.rect.y == self.const_y:
            self.timer = time.time()
            self.performing = False
        elif self.rect.x == self.const_x or self.rect.y == self.const_y:
            self.perform_stage += 1 if self.perform_stage != 4 else 0

    def attack(self):
        if random.randint(0, 30) == 1:
            Bullet(self, tuple(self.groups()), self.bullet_image)
        self.rect = self.rect.move(self.speed if self.rect.x < self.map_width // 2 else -self.speed, self.speed)


class Star(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = pygame.Surface((3, 3))
        self.map_width, self.map_height = SIZE
        self.rect = pygame.Rect(random.randint(1, self.map_width), random.randint(1, self.map_height - 1), 3, 3)
        pygame.draw.rect(self.image, (255, 255, 255), (0, 0, 3, 3))

    def update(self):
        self.rect = self.rect.move(0, 1)
        if self.rect.y == self.map_height:
            self.rect.y = -3


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    screen.fill((0, 0, 0))
    level = 0
    a_pressed = False
    d_pressed = False
    delta_x = 0
    fps, shots = 60, 0
    best_score = get_bscore()

    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    main_group = pygame.sprite.Group()

    clock = pygame.time.Clock()
    running = start(screen)
    player = Player(enemy_group, (main_group, player_group))
    font = pygame.font.Font(None, 20)
    while running:
        if len(enemy_group) == 0:
            pygame.time.delay(500)
            level += 1
            fps += 5
            for i in range(level):
                Enemy(player_group, (main_group, enemy_group), i + 1)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    delta_x = -1
                    a_pressed = True
                elif event.key == pygame.K_d:
                    delta_x = 1
                    d_pressed = True
                elif event.key == pygame.K_SPACE:
                    Bullet(player, (main_group, player_group), BULLET_MODEL)
                    shots += 1
                else:
                    continue
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    a_pressed = False
                    delta_x = 0 if not d_pressed else 1
                elif event.key == pygame.K_d:
                    d_pressed = False
                    delta_x = 0 if not a_pressed else -1
            elif event.type == pygame.QUIT:
                running = False
        response = player.update(delta_x)
        if not player.alive():
            print('player killed')
            running = False
            view_stats()
        if response == GAME_CONTINUE:
            main_group.update()
        else:
            player.update()
        screen.fill((0, 0, 0))
        texts = ['Level ' + str(level), 'Lives ' + str(player.lives), 'Score ' + str(player.score),
                 'Best ' + str(best_score)]
        for text in range(len(texts)):
            label = font.render(texts[text], True, (0, 0, 255))
            screen.blit(label, (5 + LABELS_DELTA * text, LABELS_Y))
        main_group.draw(screen)
        clock.tick(fps + level)
        pygame.display.flip()
    update_score(player.score, best_score)
    pygame.quit()
