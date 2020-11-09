

import cocos
import cocos.collision_model as cm
import cocos.euclid as eu
import random

from collections import defaultdict
from pyglet.window import key

class Actor(cocos.sprite.Sprite):
    def __init__(self, x, y, color):
        super(Actor, self).__init__('ball.png', color=color)
        self.position = pos = eu.Vector2(x, y)
        self.cshape = cm.CircleShape(pos, self.width/2)

    def update(self,dt):
        pass



class NPC(Actor):
    def __init__(self, x, y, color):
        super(NPC, self).__init__(x, y,color=color)
        self.speed = 400
        self.vec = [random.random()*2-1, random.random()*2-1]

    def move(self,dt):
        pos = self.position

        new_x = pos[0] + self.speed * self.vec[0] * dt
        new_y = pos[1] + self.speed * self.vec[1] * dt
        
        self.position = (new_x,new_y)
        self.cshape.center = self.position


class reflectN(NPC):
    def __init__(self, x, y):
        super(reflectN, self).__init__(x, y,color=(0,255,0))
        self.speed = 200

    def update(self,dt):
        self.move(dt)
        self.move_reflect(self.position,self.vec)
        #self.vec = self.move_reflect(new_x,new_y,vec)


    def move_reflect(self,pos,vec):
        x,y=pos
        if x < 0 or x >640:
            vec[0] *= -1

        elif y < 0 or y > 480:
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
            x = 640
        elif x >640:
            x = 0
        if y < 0:
            y = 480
        elif y > 480:
            y = 0

        return x,y


class MainLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(MainLayer, self).__init__()
        self.player = Actor(320, 240, (255, 255, 255))
        self.add(self.player)

        for pos in [(100,100), (540,380), (540,100), (100,380)]:
            self.add(reflectN(pos[0], pos[1], (255, 0, 0)))

        #cell = self.player.width * 1.25
        #self.collman = cm.CollisionManagerGrid(0, 640, 0, 480,
        #                                       cell, cell)
        #self.speed = 300.0
        #self.pressed = defaultdict(int)
        self.schedule(self.update)

    def on_key_press(self, k, m):
        self.pressed[k] = 1

    def on_key_release(self, k, m):
        self.pressed[k] = 0
        
    def update(self, dt):
        #self.collman.clear()


        #for _, node in self.children:
        #    self.collman.add(node)

        for _, node in self.children:
            node.update(dt)

        #for other in self.collman.iter_colliding(self.player):
        #    self.remove(other)
        #    self.add(NPC(random.randrange(0,640), random.randrange(0,480), (255, 0, 0)))

        #x = self.pressed[key.RIGHT] - self.pressed[key.LEFT]
        #y = self.pressed[key.UP] - self.pressed[key.DOWN]
        #if x != 0 or y != 0:
        #    pos = self.player.position
        #    new_x = pos[0] + self.speed * x * dt
        #    new_y = pos[1] + self.speed * y * dt
        #    self.player.position = self.player.move_out(new_x,new_y)
        #    self.player.cshape.center = eu.Vector2(new_x, new_y)



if __name__ == '__main__':
    cocos.director.director.init(caption='Hello, Cocos')
    layer = MainLayer()
    scene = cocos.scene.Scene(layer)
    cocos.director.director.run(scene)
