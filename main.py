from venv import create

import pygame
from classes import *
import os

# Создание главной игровой поверхности
screen = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)
clock = pygame.time.Clock()
frame = 0

score = 0


menu = Menu(
    ['Новая игра', 'Загрузить', 'Выход'],
    'fonts/PF Stamps Pro Rough.ttf',
    'White',
    'DarkGray',
    'center'

)
level = 0
map = Map(level)
player = Player(map.playerPos)
bullets = []
player.health = 5



enemies = []
for item in map.enemyRects:
    enemies.append(Enemy(item, map.map, map.border_rect))

enemy_bullets = []

interface = Interface(level, 3, score)

def create_level(level):
    global bullets, enemies, enemy_bullets
    maps = os.listdir('maps')
    if f'{level}.txt' in maps:
        map.__init__(level)
        player.__init__(map.playerPos)
        bullets = []
        enemies = []
        for item in map.enemyRects:
            enemies.append(Enemy(item, map.map, map.border_rect))
        enemy_bullets = []
        interface.__init__(level, 3, score)


# Обработчик событий
def handler():
    global level
    # Получаем список событий и идём по этому списку


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(Bullet(player.rect.center, player.dir))
            elif event.key == pygame.K_SPACE:
                menu.mode = 'menu'
            elif event.key == pygame.K_n:
                level += 1
                create_level(level)

        if event.type == pygame.MOUSEBUTTONDOWN and menu.mode == 'menu':
            for item in range(len(menu.items)):
                if menu.rects[item].collidepoint(pygame.mouse.get_pos()):
                    if menu.items[item] == 'Новая игра':
                        menu.mode = 'game'
                        create_level(0)
                    elif menu.items[item] == 'Загрузить':
                        menu.mode = 'game'
                        with open('save.txt', 'r') as file:
                            level = int(file.read())
                            create_level(level)
                    elif menu.items[item] == 'Выход':
                        quit()


    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player.move = True
        player.dir = 'left'
    elif keys[pygame.K_d]:
        player.move = True
        player.dir = 'right'
    elif keys[pygame.K_w]:
        player.move = True
        player.dir = 'up'
    elif keys[pygame.K_s]:
        player.move = True
        player.dir = 'down'
    else:
        player.move = False

    moving(player.dir, player.move)

def collider():
    global score, level
    for item in map.map:
        block = item[0]

        for bullet in bullets:
            if bullet.rect.colliderect(block) and item[1] not in [3, 4, 5]:
                if item[1] in [1, 6]:
                    item[2] -= 1
                bullets.remove(bullet)
            elif bullet.rect.x < 0 or bullet.rect.x > map.size*13\
                    or bullet.rect.y < 0 or bullet.rect.y > map.size*13:
                bullets.remove(bullet)

            for enemy in enemies:
                if bullet.rect.colliderect(enemy.rect):
                    if bullet in bullets:
                        bullets.remove(bullet)
                    enemy.health -= 1
                    if enemy.health <= 0:
                        score += 1
                        enemies.remove(enemy)
                        interface.enemies_number -= 1
                        pos = random.choice(map.enemyRects)
                        enemies.append(Enemy(pos, map.map, map.border_rect))

                        if interface.enemies_number == 0:
                            level += 1
                            create_level(level)


        for bullet in enemy_bullets:
            if bullet.rect.colliderect(block) and item[1] not in [3, 4, 5]:
                if item[1] in [1, 6]:
                    item[2] -= 1
                if bullet in enemy_bullets:
                    enemy_bullets.remove(bullet)
            elif bullet.rect.x < 0 or bullet.rect.x > map.size * 13 \
                    or bullet.rect.y < 0 or bullet.rect.y > map.size * 13:
                if bullet in enemy_bullets:
                     enemy_bullets.remove(bullet)
            elif bullet.rect.colliderect(player.rect):
                if bullet in enemy_bullets:
                    enemy_bullets.remove(bullet)

                player.health -= 1
                if player.health == 0:
                    with open('save.txt', 'w') as file:
                        file.write(str(level))
                    menu.mode = 'menu'
            for i in bullets:
                if bullet.rect.colliderect(i.rect):
                    if bullet in enemy_bullets:
                        enemy_bullets.remove(bullet)
                    if i in bullets:
                        bullets.remove(item)

        if block.colliderect(player.rect) and item[1] != 3:
            if player.dir == 'up':
                player.rect.y += 1
            elif player.dir == 'down':
                player.rect.y -= 1
            elif player.dir == 'left':
                player.rect.x += 1
            elif player.dir == 'right':
                player.rect.x -= 1


def moving(dir, move):
    if move:
        margin = (H - map.size * 13) // 2
        if dir == 'up':
            if player.rect.top > margin:
                player.rect.y -= 1
        elif dir == 'down':
            if player.rect.bottom < H - margin:
                player.rect.y += 1
        elif dir == 'left':
            if player.rect.left > margin:
                player.rect.x -= 1
        elif dir == 'right':
            if player.rect.right < H - margin:
                player.rect.x += 1

    collider()

# Главный игрвой цикл
while True:
    handler()
    screen.fill('Black')


    if menu.mode == 'game':

        interface.draw(screen, score, player.health)

        if random.randint(0, 40) < 1:
            item = random.choice(enemies)
            enemy_bullets.append(Bullet(item.rect.center, item.dir))
        for item in bullets:
            item.draw(screen)

        player.draw(screen)
        for item in bullets:
            item.draw(screen)
        for item in enemy_bullets:
            item.draw(screen)

        for item in enemies:
            item.draw(screen)

        map.draw(screen)
    elif menu.mode == 'menu':
        menu.draw(screen)
    frame += 1
    clock.tick(120)
    pygame.display.update()