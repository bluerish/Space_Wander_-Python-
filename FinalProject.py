import random

from collections import defaultdict

from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key

import cocos.layer
import cocos.sprite
import cocos.collision_model as cm
import cocos.euclid as eu
import cocos.actions as ac



class Actor(cocos.sprite.Sprite):
    def __init__(self, x, y, color, img='ball.png'):
        super(Actor, self).__init__(img, color=color)
        self.position = pos = eu.Vector2(x, y)
        self.cshape = cm.CircleShape(pos, self.width/2)

        self.w = 800
        self.h = 650


    def update(self,dt):
        pass





class PlayerCannon(Actor):
    KEYS_PRESSED = defaultdict(int)

    def __init__(self, x, y):
        super(PlayerCannon, self).__init__(x, y, (255,255,255))
        #self.x, self.y = self.position
        self.speed = 7
        self.timer =0
        self.HP = 10
        self.sub =[]


        self.shoot = []
        self.vec = [0,1]
        self.shootPoint = [0,0]
 

    def update(self, elapsed):
        pressed = PlayerCannon.KEYS_PRESSED
        space_pressed = pressed[key.SPACE] == 1
        self.timer += elapsed

        horizon = pressed[key.D] - pressed[key.A]
        virtical = pressed[key.W] - pressed[key.S]
    
        w = self.width * 0.5
        h = self.height*0.5

        shootX = pressed[key.RIGHT] - pressed[key.LEFT]
        shootY = pressed[key.UP] - pressed[key.DOWN]



        if (shootX != 0 or shootY !=0) and self.timer > 0.7:
            if shootX != 0:
                shootY = 0

            self.timer = 0
            PShoot = PlayerShoot(self.x + w*shootX, self.y+ h*shootY, [shootX, shootY])
            self.shoot.append(PShoot)
            self.parent.add(PShoot)

            #for subC in self.sub:
            #    if random.random() < 0.5:
            #        self.parent.add(PlayerShoot(subC.x, self.y + 50))

        



        if horizon != 0:
            if w > self.x and horizon == -1:
                horizon = 0
            if self.x > self.parent.width - w and horizon == 1:
                horizon = 0
            self.move(horizon,1)
            #for subC in self.sub:
            #    subC.move(self.speed * movement * elapsed)

        if virtical != 0:
            if w > self.y and virtical == -1:
                virtical = 0
            if self.y > self.parent.height - h and virtical == 1:
                virtical = 0
            self.move(virtical,-1)



    def move(self,dt, axis):
        pos = self.position

        if(axis == 1):
            new_x = pos[0] + self.speed * dt
            new_y = pos[1]
        if(axis == -1):
            new_x = pos[0]
            new_y = pos[1] + self.speed * dt
        
        self.position = eu.Vector2(new_x, new_y)
        self.cshape.center = self.position



class NPC(Actor):
    def __init__(self, x, y, color):
        super(NPC, self).__init__(x, y,color=color)
        self.speed = 400
        self.vec = [random.random()*2-1, random.random()*2-1]

    def move(self,dt):
        pos = self.position

        new_x = pos[0] + self.speed * self.vec[0] * dt
        new_y = pos[1] + self.speed * self.vec[1] * dt
        
        self.position = eu.Vector2(new_x, new_y)
        self.cshape.center = self.position


class reflectN(NPC):
    def __init__(self, x, y):
        super(reflectN, self).__init__(x, y, color=(0,255,0))
        self.speed = 200

    def update(self,dt):
        self.move(dt)
        self.move_reflect(self.position,self.vec)


    def move_reflect(self,pos,vec):
        x,y=pos
        if x < 0 or x > self.w:
            vec[0] *= -1
        elif y < 0 or y > self.h:
            vec[1] *= -1

        return vec

class straightN(NPC):
    def __init__(self, x, y):
        super(straightN, self).__init__(x, y,color=(0,0,255))
        self.speed = 300

    def update(self,dt):
        self.position = self.move_out(self.position)
        self.move(dt)


    def move_out(self,pos):
        x,y=pos

        if x < 0:
            x = self.w
        elif x > self.w:
            x = 0
        if y < 0:
            y = self.h
        elif y > self.h:
            y = 0

        return x,y

class chaseN(NPC):
    def __init__(self, x, y):
        super(straightN, self).__init__(x, y,color=(0,0,255))
        self.speed = 30
        

    def update(self,dt):
        self.move_chase(dt)


    def move_chase(self):

        if x < 0:
            x = self.w
        elif x > self.w:
            x = 0
        if y < 0:
            y = self.h
        elif y > self.h:
            y = 0

        return x,y


class Shoot(Actor):
    def __init__(self, x, y, vec, img='shoot.png'):
        super(Shoot, self).__init__(x, y, (255,255,255), img)
        self.speed = 24
        self.vec = [0,0]
        self.vec[0] = vec[0]
        self.vec[1] = vec[1]

    def update(self, elapsed):
        self.move(self.speed * elapsed)

    def move(self,dt):
        pos = self.position

        new_x = pos[0] + self.speed * self.vec[0] * dt
        new_y = pos[1] + self.speed * self.vec[1] * dt
        
        self.position = eu.Vector2(new_x, new_y)
        self.cshape.center = self.position

class PlayerShoot(Shoot):
    INSTANCE = []

    def __init__(self, x, y, vec):
        super(PlayerShoot, self).__init__(x, y, vec, 'laser.png')
        PlayerShoot.INSTANCE.append(self)
        self.shootItem = False


    def collide(self, other):
        if isinstance(other, Alien):
            self.parent.update_score(other.score)
            if other.item == True:
                self.shootItem = True
            PlayerShoot.INSTANCE.remove(self)
            other.kill()
            self.kill()              

            return self.shootItem

    def on_exit(self):
        super(PlayerShoot, self).on_exit()
        if self in PlayerShoot.INSTANCE:
            PlayerShoot.INSTANCE.remove(self)
        
class ChaseShoot(Shoot): #총알이 player의 움직임에 따라 움직임
    INSTANCE = []

    def __init__(self, x, y, vec):
        super(PlayerShoot, self).__init__(x, y, vec, 'laser.png')
        self.speed *= -1
        PlayerShoot.INSTANCE.append(self)
        self.shootItem = False


    def collide(self, other):
        if isinstance(other, Alien):
            self.parent.update_score(other.score)
            if other.item == True:
                self.shootItem = True
            PlayerShoot.INSTANCE.remove(self)
            other.kill()
            self.kill()              

            return self.shootItem

    def on_exit(self):
        super(PlayerShoot, self).on_exit()
        if self in PlayerShoot.INSTANCE:
            PlayerShoot.INSTANCE.remove(self)



class GameLayer(cocos.layer.Layer):
    is_event_handler = True

    def on_key_press(self, k, _):
        PlayerCannon.KEYS_PRESSED[k] = 1

    def on_key_release(self, k, _):
        PlayerCannon.KEYS_PRESSED[k] = 0


    def __init__(self,hud):
        super(GameLayer, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.hud = hud
        self.width = w
        self.height = h

        self.player = PlayerCannon(300, 300)
        self.add(self.player)

        cell = self.player.width * 1.25
        self.collman = cm.CollisionManagerGrid(0, w, 0, h,
                                               cell, cell)



        self.schedule(self.update)


        
    def update(self, dt):

        self.collman.clear()
        for _, node in self.children:
            self.collman.add(node)
            if not self.collman.knows(node):
                self.remove(node)

        for _, node in self.children:
            node.update(dt)

        #for instance in PlayerShoot.INSTANCE:
        #    self.collide(instance)

        #for other in self.collman.iter_colliding(self.player):
        #    self.remove(other)

        #for instance in PlayerShoot.INSTANCE:
        #    self.collide(instance)

        self.create_NPC()


    def create_NPC(self):
        kind=0
        range=0
        pos = (0,0)

        if random.random() < 0.01:
            range = random.randrange(1,5)
            kind = random.randrange(1,3)
            
            if range == 1:
                pos = (1,random.randrange(1,self.height-1))
            elif range == 2:
                pos = (self.width-1,random.randrange(1,self.height-1))
            elif range == 3:
                pos = (random.randrange(1,self.width-1),1)
            elif range == 4:
                pos = (random.randrange(0,self.width),self.height)


            if kind == 1:
                self.add(straightN(pos[0], pos[1]))
            elif kind == 2:
                self.add(reflectN(pos[0], pos[1]))
            #elif kind == 3:
            #    self.add(chaseN(pos[0], pos[1]))



class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.score_text = cocos.text.Label('', font_size=18)
        self.score_text.position = (20, h - 40)
        self.level_text = cocos.text.Label('', font_size=18)
        self.level_text.position = (20, h - 70)
        self.lives_text = cocos.text.Label('', font_size=18)
        self.lives_text.position = (w - 100, h - 40)
        self.HP_text = cocos.text.Label('', font_size=18)
        self.HP_text.position = (w-190, h - 40)
        self.add(self.score_text)
        self.add(self.level_text)
        self.add(self.lives_text)
        self.add(self.HP_text)

    def update_score(self, score):
        self.score_text.element.text = 'Score: %s' % score

    def update_level(self, level):
        self.level_text.element.text = 'Level: %s' % level

    def update_lives(self, lives):
        self.lives_text.element.text = 'Lives: %s' % lives

    def update_HP(self, HP):
        self.HP_text.element.text = 'HP: %s' % HP



    def show_game_over(self):
        w, h = cocos.director.director.get_window_size()
        game_over = cocos.text.Label('Game Over', font_size=50,
                                     anchor_x='center',
                                     anchor_y='center')
        game_over.position = w * 0.5, h * 0.5
        self.add(game_over)
     
    def show_you_win(self):
        w, h = cocos.director.director.get_window_size()
        you_win = cocos.text.Label('You Win!', font_size=50,
                                     anchor_x='center',
                                     anchor_y='center')
        you_win.position = w * 0.5, h * 0.5
        self.add(you_win)


if __name__ == '__main__':
    cocos.director.director.init(caption='Space Wander', 
                                 width=800, height=650)
    main_scene = cocos.scene.Scene()
    hud_layer = HUD()
    main_scene.add(hud_layer, z=1)
    game_layer = GameLayer(hud_layer)
    main_scene.add(game_layer, z=0)
    cocos.director.director.run(main_scene)