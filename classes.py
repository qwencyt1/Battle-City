import random

import pygame



pygame.init()
H  = pygame.display.Info().current_h
W = pygame.display.Info().current_w

class Map:
    def __init__(self, level):
        self.health = 4
        self.image = pygame.image.load('images/map.png').convert_alpha()
        self.sprites = [None]
        for i in range(7):
            sprite = self.image.subsurface([32*i, 0, 32, 32])
            self.size = H//13
            self.margin = (H - self.size*13)//2
            sprite = pygame.transform.scale(sprite, [self.size, self.size])
            self.sprites.append(sprite)


        self.draft = []
        with open(f'maps/{level}.txt', mode = 'r') as file:
            for line in file.readlines():
                self.draft.append(line.split())

        self.enemyRects = []
        self.map = []
        for y in range(len(self.draft)):
            for x in range(len(self.draft[y])):

                rect = self.sprites[1].get_rect(topleft=[self.margin+x*self.size,self.margin+y*self.size])
                index = int(self.draft[y][x])
                if index in [1, 2, 3, 4, 5, 6, 7]:
                    self.map.append([rect, index, self.health])
                elif index == 8:
                    self.playerPos = [self.margin+x*self.size,self.margin+y*self.size]
                elif index == 9:
                    self.enemyRects.append(rect)
        self.border_rect = pygame.Rect([self.margin, self.margin, self.size*13 + 2*self.margin, self.size*13 + 2*self.margin])

    def draw(self, screen):
        pygame.draw.rect(screen, 'DarkGray',self.border_rect, width=5)
        for item in self.map:
            if item[1] != 0:
                screen.blit(self.sprites[item[1]], item[0])
            if item[2] == 0:
                if item[1] != 6:
                    self.map.remove(item)
                else:
                    item[2] = -1
                    item[1] = 7

class Player:
    def __init__(self, playerPos):
        self.image = pygame.image.load('images/General-Sprites.png').convert_alpha()

        self.size = H//16
        self.sprites = {
            0: {'left': [], 'right': [], 'up': [], 'down': []},
            1: {'left': [], 'right': [], 'up': [], 'down': []},
            2: {'left': [], 'right': [], 'up': [], 'down': []},
            3: {'left': [], 'right': [], 'up': [], 'down': []},
        }
        for l in range (4):
            for dir in enumerate(['up', 'left', 'down', 'right']):
                for i in range(2):
                    sprite = self.image.subsurface([dir[0]*32 + i*16,l*16,16,16])
                    sprite = pygame.transform.scale(sprite, [self.size, self.size])
                    self.sprites[l][dir[1]].append(sprite)

        self.rect = self.sprites[0]['up'][0].get_rect(center=[playerPos[0] + self.size//2,
                                                              playerPos[1] + self.size//2])
        self.frame = 0
        self.level = 0
        self.dir = 'up'
        self.move = False

    def draw(self,screen):
        if self.move:
            cur = int(self.frame % 2)
        else:
            cur = 0
        screen.blit(self.sprites[self.level][self.dir][cur],self.rect)
        self.frame += 0.1

class Bullet:
    def __init__(self, pos, dir):
        self.pos = pos
        self.dir = dir
        self.image = pygame.image.load('images/General-Sprites.png').convert_alpha()
        self.sprite = self.image.subsurface([262, 102, 3, 3])
        self.sprite = pygame.transform.scale(self.sprite, [12, 12])
        self.rect = self.sprite.get_rect(center = self.pos)
    def draw(self, screen):
        self.move = {
            'up': [0, -10], 'down': [0, 10], 'left': [-10, 0], 'right': [10, 0]
        }
        screen.blit(self.sprite,self.rect)
        self.rect.x += self.move[self.dir][0]
        self.rect.y += self.move[self.dir][1]


class Menu:
    def __init__(self, items:list,font_path:str,
                 active_color:str,passive_color:str, pos:str):
        self.mode = 'menu'
        self.font = pygame.font.Font(font_path, 48)
        self.items = items
        self.active_color = active_color
        self.passive_color = passive_color
        self.pos = pos
        self.renders = {'active' : [], 'passive' : []}
        for item in self.items:
            render = self.font.render(item, True, self.passive_color)
            self.renders['passive'].append(render)
            render = self.font.render(item, True, self.active_color)
            self.renders['active'].append(render)

        H = pygame.display.Info().current_h
        W = pygame.display.Info().current_w
        self.margin = 25
        Hm = 0
        for item in self.renders['passive']:

            Hm += item.get_height()
        Hm += self.margin * (len(self.items) - 1)
        Y0 = H//2 - Hm//2 + self.renders['passive'][0].get_height()//2


        self.rects = []
        for item in self.renders['passive']:
            if self.pos == 'center':
                self.rects.append(item.get_rect(center=[W//2, Y0]))
            elif self.pos == 'left':
                self.rects.append(item.get_rect(midleft=[W//7, Y0]))
            elif self.pos == 'right':
                self.rects.append(item.get_rect(midright=[(W//7)*6, Y0]))

            Y0 += item.get_height() + self.margin


    def draw(self, screen):
        for item in range(len(self.items)):
            if self.rects[item].collidepoint(pygame.mouse.get_pos()):
                screen.blit(self.renders['active'][item], self.rects[item])
            else:
                screen.blit(self.renders['passive'][item], self.rects[item])
class Enemy:
    def __init__(self, playerPos, map, border_rect):
        self.border_rect = border_rect
        self.image = pygame.image.load('images/General-Sprites.png').convert_alpha()
        self.health = 5
        self.map = map
        self.size = H//16
        self.sprites = {
            0: {'left': [], 'right': [], 'up': [], 'down': []}
        }
        for dir in enumerate(['up', 'left', 'down', 'right']):
            for i in range(2):
                sprite = self.image.subsurface([128 + dir[0]*32 + 0*16,0*16,16,16])
                sprite = pygame.transform.scale(sprite, [self.size, self.size])
                self.sprites[0][dir[1]].append(sprite)

        self.rect = self.sprites[0]['up'][0].get_rect(center=[playerPos[0] + self.size//2,
                                                              playerPos[1] + self.size//2])
        self.frame = 0
        self.dir = 'down'
        self.speed = {
            'right': {'x':1, 'y': 0},
            'left': {'x': -1,'y': 0},
            'down': {'x': 0, 'y': 1},
            'up': {'x': 0, 'y': -1},
        }
    def draw(self,screen):
        cur = int(self.frame % 2)
        screen.blit(self.sprites[0][self.dir][cur],self.rect)
        self.frame += 0.1

        self.rect.x += self.speed[self.dir]['x']
        self.rect.y += self.speed[self.dir]['y']

        for item in self.map:
            if item[0].colliderect(self.rect) and item[1] != 3 :
                self.rect.x -= self.speed[self.dir]['x']
                self.rect.y -= self.speed[self.dir]['y']
                self.dir = random.choice(['up','down','left','right'])
        collide_border = self.border_rect.top >= self.rect.top and self.dir == 'up' or \
                         self.border_rect.bottom <= self.rect.bottom and self.dir == 'down' or \
                         self.border_rect.left >= self.rect.left and self.dir == 'left' or \
                         self.border_rect.right <= self.rect.right and self.dir == 'right'
        if collide_border:
            self.rect.x -= self.speed[self.dir]['x']
            self.rect.y -= self.speed[self.dir]['y']
            self.dir = random.choice(['up','down','left','right'])
        if random.randint(0, 300) < 1:
            self.dir = random.choice(['up','down','left','right'])



class Interface:
    def __init__(self, level, health, score):
        self.font = pygame.font.Font('fonts/PF Stamps Pro Rough.ttf', 48)
        self.enemies_number = 10 + 5*level
        self.health = health
        self.score = score
        self.image = pygame.image.load('images/General-Sprites.png').convert_alpha()
        self.sprite = self.image.subsurface([128, 0, 16, 16])
        self.sprite = pygame.transform.scale(self.sprite, [60, 60])

    def draw(self, screen, score, health):
        self.score = score
        self.health = health
        self.render_score = self.font.render(f'СЧЕТ {self.score}', True, 'White')
        self.render_health = self.font.render(f'ЖИЗНИ {self.health}', True, 'White')
        screen.blit(self.render_health, [1200, 940])
        screen.blit(self.render_score, [1500, 940])
        x = 1200
        y = 100
        for i in range(self.enemies_number):
            screen.blit(self.sprite, [x, y])
            x += 75
            if (i+1)%8 == 0 and i != 0:
                y += 75
                x = 1200