import pygame as pg
import random
from settings import *
from player import *
from sprites import *
from tilemap import collide_hit_rect
vec = pg.math.Vector2
import pytweening as tween
from itertools import chain

class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.current_frame = 0
        self.last_update = 0
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.health = MOB_HEALTH

        def wall_check(self, dir):
            if dir == 'down':
                self.rect.y += WALL_CHECK_DIST
                hits = pg.sprite.spritecollide(self, self.game.walls,False)
                self.rect.y -= WALL_CHECK_DIST
                if hits:
                    return True

            if dir == 'left':
                self.rect.x -= WALL_CHECK_DIST
                hits = pg.sprite.spritecollide(self, self.game.walls,False)
                self.rect.y += WALL_CHECK_DIST
                if hits:
                    return True

            if dir == 'right':
                self.rect.x += WALL_CHECK_DIST
                hits = pg.sprite.spritecollide(self, self.game.walls,False)
                self.rect.y -= WALL_CHECK_DIST
                if hits:
                    return True

        def collide_with_walls(self, dir):
            if dir == 'x':
                hits = pg.sprite.spritecollide(self, self.game.walls, False)
                if hits:
                    if self.vel.x > 0:  #right
                        self.pos.x = hits[0].rect.left - self.rect.width
                    if self.vel.x < 0:  #left
                        self.pos.x = hits[0].rect.right
                    self.vel.x *= 0.01
                    self.rect.x = self.pos.x

            if dir == 'y':
                hits = pg.sprite.spritecollide(self, self.game.walls, False)
                if hits:
                    if self.vel.y > 0:  #down
                        self.pos.y = hits[0].rect.top - self.rect.height
                    if self.vel.y < 0:  #up
                        self.pos.y = hits[0].rect.y + self.rect.width
                    self.vel.y = 0
                    self.rect.y = self.pos.y

        def knockback(self, dir):
            if self.game.player.pos.x < self.pos.x:
                self.vel.y += SKELE_KNOCKBACK_Y
                self.vel.x += -SKELE_KNOCKBACK_X
            if self.game.player.pos.x > self.pos.x:
                self.vel.y += SKELE_KNOCKBACK_Y
                self.vel.x += SKELE_KNOCKBACK_X


class Mob(Enemy):
    def __init__(self, game, x, y):
        # self._layer = MOB_LAYER
        #self.groups = game.all_sprites, game.mobs
        super(Mob, self).__init__(game, x, y)
        #self.game = game
        self.load_images()
        # self.current_frame = 0
        # self.last_update = 0
        self.image = self.mob_img_r[0]
        self.rect = self.image.get_rect()
        # self.pos = vec(x, y)
        # self.vel = vec(0, 0)
        # self.acc = vec(0, 0)
        self.rot = 0
        # self.health = MOB_HEALTH

    def load_images(self):
        self.mob_img_r = [
        self.game.eye_spritesheet.get_image(0,0,32,32),
        self.game.eye_spritesheet.get_image(32,0,32,32),
        self.game.eye_spritesheet.get_image(64,0,32,32)
        ]
        self.mob_img_l = []
        for img in self.mob_img_r:
            img.set_colorkey(BLACK)
            self.mob_img_l.append(pg.transform.flip(img, True, False))

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > EYE_ANIM:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.mob_img_r)
            bottom = self.rect.bottom
            if self.vel.x > 0:
                self.image = self.mob_img_r[self.current_frame]
            if self.vel.x < 0:
                self.image = self.mob_img_l[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom

#    def wall_check(self, dir):
        if dir == 'down':
            self.rect.y += WALL_CHECK_DIST
            hits = pg.sprite.spritecollide(self, self.game.walls,False)
            self.rect.y -= WALL_CHECK_DIST
            if hits:
                return True

        if dir == 'left':
            self.rect.x -= WALL_CHECK_DIST
            hits = pg.sprite.spritecollide(self, self.game.walls,False)
            self.rect.y += WALL_CHECK_DIST
            if hits:
                return True

        if dir == 'right':
            self.rect.x += WALL_CHECK_DIST
            hits = pg.sprite.spritecollide(self, self.game.walls,False)
            self.rect.y -= WALL_CHECK_DIST
            if hits:
                return True

#    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:  #right
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:  #left
                    self.pos.x = hits[0].rect.right
                self.vel.x *= 0.01
                self.rect.x = self.pos.x

        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:  #down
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:  #up
                    self.pos.y = hits[0].rect.y + self.rect.width
                self.vel.y = 0
                self.rect.y = self.pos.y

    def update(self):
        self.animate()
        self.rect = self.image.get_rect()
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        self.move()
        self.pos.x += self.vel.x
        if self.wall_check('down'):
            self.vel.y += 5
        self.pos.y += self.vel.y
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

        if self.health <= 0:
            if random.random() > HP_DROP_CHANCE:
                i = Item(self.game, self.pos, 'health')
                self.game.all_sprites.add(i)
                self.game.items.add(i)
            self.kill()

    def move(self):
        self.vel.x += random.randrange(-2,3) * self.game.dt

    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED

        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar_full = pg.Rect(0,0,MOB_HEALTH,5)
        self.health_bar = pg.Rect(0, 0, width, 5)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image,BLACK,self.health_bar_full)
            pg.draw.rect(self.image,col,self.health_bar)


class Skeleton(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.load_images()
        self.current_frame = 0
        self.last_update = 0
        self.last_movement = 0
        self.current_speed = 0
        self.last_dir = None
        self.image = self.mob_img_r[0]
        self.rect = self.image.get_rect()
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rot = 0
        self.health = MOB_HEALTH

    def load_images(self):
        self.mob_img_r = [
        self.game.skele_spritesheet.get_image(0,0,16,16),
        self.game.skele_spritesheet.get_image(16,0,16,16),
        self.game.skele_spritesheet.get_image(32,0,16,16),
        self.game.skele_spritesheet.get_image(48,0,16,16)

        ]
        self.mob_img_l = []
        for img in self.mob_img_r:
            img.set_colorkey(BLACK)
            self.mob_img_l.append(pg.transform.flip(img, True, False))

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > SKELE_ANIM:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.mob_img_r)
            bottom = self.rect.bottom
            if self.vel.x > 0 and self.wall_check('down'):
                self.image = self.mob_img_r[self.current_frame]
            if self.vel.x < 0 and self.wall_check('down'):
                self.image = self.mob_img_l[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom

    def wall_check(self, dir):
        if dir == 'down':
            self.rect.y += WALL_CHECK_DIST
            hits = pg.sprite.spritecollide(self, self.game.walls,False)
            self.rect.y -= WALL_CHECK_DIST
            if hits:
                return True

        if dir == 'left':
            self.rect.x -= WALL_CHECK_DIST
            hits = pg.sprite.spritecollide(self, self.game.walls,False)
            self.rect.y += WALL_CHECK_DIST
            if hits:
                return True

        if dir == 'right':
            self.rect.x += WALL_CHECK_DIST
            hits = pg.sprite.spritecollide(self, self.game.walls,False)
            self.rect.y -= WALL_CHECK_DIST
            if hits:
                return True

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:  #right
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:  #left
                    self.pos.x = hits[0].rect.right
                self.current_speed *= -1
                self.rect.x = self.pos.x

        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:  #down
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:  #up
                    self.pos.y = hits[0].rect.y + self.rect.width
                self.vel.y = 0
                self.rect.y = self.pos.y

    def knockback(self, dir):
        if self.game.player.pos.x < self.pos.x:
            self.vel.y += SKELE_KNOCKBACK_Y
            self.vel.x += -SKELE_KNOCKBACK_X
        if self.game.player.pos.x > self.pos.x:
            self.vel.y += SKELE_KNOCKBACK_Y
            self.vel.x += SKELE_KNOCKBACK_X

    def move(self):
        if self.health == MOB_HEALTH:
            #CHECK TIMER TO CHANGE DIRECTION
            now = pg.time.get_ticks()
            if now - self.last_movement > random.randrange(SKELE_MOVE_MIN,SKELE_MOVE_MAX):
                self.last_movement = now
                self.current_speed = random.choice(SKELE_SPEED)

        #CHASE PLAYER IF HURT
        elif self.health < MOB_HEALTH:
            #PLAYER RIGHT OF MOB
            if self.game.player.pos.x > self.pos.x:
                self.current_speed = SKELE_SPEED[1]
            #PLAYER LEFT OF MOB
            elif self.game.player.pos.x < self.pos.x:
                self.current_speed = SKELE_SPEED[2]
        # if self.vel.x > SKELE_MAX_SPEED:
        #     self.vel.x = SKELE_MAX_SPEED
        # elif self.vel.x < -SKELE_MAX_SPEED:
        #     self.vel.x = -SKELE_MAX_SPEED

    def update(self):
        self.animate()

        self.rect = self.image.get_rect()
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        #--MOVEMENT--
        self.acc.x = self.current_speed * self.game.dt
        self.move()



        self.acc.x += self.vel.x * SKELE_FRICTION
        self.vel += self.acc
        if abs(self.vel.x) < .1:
            self.vel.x = 0
        if abs(self.vel.y) < .1:
            self.vel.y = 0
        self.pos += (self.vel + 0.5 * self.acc)

        #self.pos.x += self.vel.x
        if not self.wall_check('down'):
            self.vel.y += 6
        if self.vel.y > 12:
            self.vel.y = 14

        if self.health <= 0:
            if random.random() > HP_DROP_CHANCE:
                i = Item(self.game, self.pos, 'health')
                self.game.all_sprites.add(i)
                self.game.items.add(i)
            self.kill()


        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

        if self.vel.x > 0:
            self.last_dir = 'right'
        elif self.vel.x > 0:
            self.last_dir = 'left'


    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED

        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar_full = pg.Rect(0,0,MOB_HEALTH,5)
        self.health_bar = pg.Rect(0, 0, width, 3)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image,BLACK,self.health_bar_full)
            pg.draw.rect(self.image,col,self.health_bar)


class Clayton(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.load_images()
        self.current_frame = 0
        self.last_update = 0
        self.last_dir = None
        self.image = self.mob_img_r[0]
        self.rect = self.image.get_rect()

        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center

        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rot = 0
        self.health = MOB_HEALTH



    def load_images(self):
        self.mob_img_l = [
        self.game.clayton_spritesheet.get_image(0,96, 48, 48),
        self.game.clayton_spritesheet.get_image(48,96, 48, 48),
        self.game.clayton_spritesheet.get_image(96,96, 48, 48),
        self.game.clayton_spritesheet.get_image(144,96, 48, 48),
        self.game.clayton_spritesheet.get_image(192,96, 48, 48),
        self.game.clayton_spritesheet.get_image(240,96, 48, 48),
        self.game.clayton_spritesheet.get_image(288,96, 48, 48),
        self.game.clayton_spritesheet.get_image(336,96, 48, 48),
        self.game.clayton_spritesheet.get_image(384,96, 48, 48),
        self.game.clayton_spritesheet.get_image(432,96, 48, 48),

        ]
        self.mob_img_r = []
        for img in self.mob_img_l:
            img.set_colorkey(BLACK)
            self.mob_img_r.append(pg.transform.flip(img, True, False))

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > SKELE_ANIM:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.mob_img_r)
            bottom = self.rect.bottom
            if self.vel.x > 0:
                self.image = self.mob_img_r[self.current_frame]
            if self.vel.x < 0:
                self.image = self.mob_img_l[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom

    def wall_check(self, dir):
        if dir == 'down':
            self.rect.y += WALL_CHECK_DIST
            hits = pg.sprite.spritecollide(self, self.game.walls,False)
            self.rect.y -= WALL_CHECK_DIST
            if hits:
                return True

        if dir == 'left':
            self.rect.x -= WALL_CHECK_DIST
            hits = pg.sprite.spritecollide(self, self.game.walls,False)
            self.rect.y += WALL_CHECK_DIST
            if hits:
                return True

        if dir == 'right':
            self.rect.x += WALL_CHECK_DIST
            hits = pg.sprite.spritecollide(self, self.game.walls,False)
            self.rect.y -= WALL_CHECK_DIST
            if hits:
                return True

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:  #right
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:  #left
                    self.pos.x = hits[0].rect.right
                self.vel.x *= 0.01
                self.rect.x = self.pos.x

        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:  #down
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:  #up
                    self.pos.y = hits[0].rect.y + self.rect.width
                self.vel.y = 0
                self.rect.y = self.pos.y

    def knockback(self, dir):
        if dir == 'right':
            self.rect.y = SKELE_KNOCKBACK_Y
            self.rect.x = -SKELE_KNOCKBACK_X
        if dir == 'left':
            self.rect.y = SKELE_KNOCKBACK_Y
            self.rect.x = SKELE_KNOCKBACK_X
        print('knockback')

    def move(self):
        if self.health == MOB_HEALTH:
            self.vel.x += random.randrange(-3,4) * self.game.dt
        #CHASE PLAYER
        elif self.health < MOB_HEALTH:
            if self.game.player.pos.x > self.pos.x:
                self.vel.x += random.randrange(0,3) * self.game.dt
            elif self.game.player.pos.x < self.pos.x:
                self.vel.x += random.randrange(-2,1) * self.game.dt
        if self.vel.x > SKELE_MAX_SPEED:
            self.vel.x = SKELE_MAX_SPEED
        elif self.vel.x < -SKELE_MAX_SPEED:
            self.vel.x = -SKELE_MAX_SPEED

    def update(self):
        self.animate()
        self.rect = self.image.get_rect()
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        self.move()

        self.pos.x += self.vel.x
        if self.wall_check('down'):
            self.vel.y += 6

        if self.health <= 0:
            if random.random() > HP_DROP_CHANCE:
                i = Item(self.game, self.pos, 'health')
                self.game.all_sprites.add(i)
                self.game.items.add(i)
            self.kill()

        self.pos.y += self.vel.y
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

        if self.vel.x > 0:
            self.last_dir = 'right'
        elif self.vel.x > 0:
            self.last_dir = 'left'



    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED

        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar_full = pg.Rect(0,0,MOB_HEALTH,5)
        self.health_bar = pg.Rect(0, 0, width, 3)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image,BLACK,self.health_bar_full)
            pg.draw.rect(self.image,col,self.health_bar)
