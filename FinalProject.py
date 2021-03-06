import random
import math

from collections import defaultdict

from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key
import pyglet.media as media
import pyglet.app

import cocos.layer
import cocos.sprite
import cocos.collision_model as cm
import cocos.euclid as eu
import cocos.actions as ac

import cocos.menu as menu




class Actor(cocos.sprite.Sprite):
    def __init__(self, x, y, img='ball.png'):
        super(Actor, self).__init__(img)
        self.position = pos = eu.Vector2(x, y)
        self.cshape = cm.AARectShape(self.position, self.width * 0.5, self.height * 0.5)
        self.w = 800
        self.h = 650


    def update(self,dt):
        pass




class PlayerCannon(Actor):
    KEYS_PRESSED = defaultdict(int)

    def __init__(self, x, y):
        self.seq = ImageGrid(load('SpaceShip.png'), 4, 1)
        super(PlayerCannon, self).__init__(x, y, self.seq[3])
        #self.x, self.y = self.position
        self.speed = 7
        self.timer =0
        self.subtimer = 0
        self.HP = 10

        self.sub =[]

        self.shoot = []
        self.vec = [0,1]
        self.shootPoint = [0,0]

        self.soundPlayer = media.Player()
        self.shoot_sound = media.load('shoot.wav')
        self.shootS_sound = media.load('shootS.mp3', streaming=False)
        self.shootR_sound = media.load('shootR.wav', streaming=False)
        self.BombS_sound = media.load('BombS.wav', streaming=False)
        self.BombR_sound = media.load('BombR.wav', streaming=False)


    def collide(self, other):
        self.HP -= 1
        self.do(ac.Blink(3,0.5))
        self.do(ac.FadeIn(1))
        self.color = (255,255,255)

        if self.HP<=0:
            for subC in self.sub:
                subC.kill()
            self.sub.clear()
            self.kill()

        other.kill()

 

    def update(self, elapsed):
        pressed = PlayerCannon.KEYS_PRESSED
        Q_pressed = pressed[key.Q] == 1
        E_pressed = pressed[key.E] == 1
        self.timer += elapsed
        self.subtimer += elapsed
        subLCharged = False
        subRCharged = False



        horizon = pressed[key.D] - pressed[key.A]
        virtical = pressed[key.W] - pressed[key.S]
    
        w = self.width * 0.5
        h = self.height*0.5

        shootX = pressed[key.RIGHT] - pressed[key.LEFT]
        shootY = pressed[key.UP] - pressed[key.DOWN]
        radian = 0
        SubLshootX = 0
        SubRshootX = 0
        SubLshootY = 0
        SubRshootY = 0


        if (shootX != 0 or shootY !=0) and self.timer > 0.7:
            if shootX != 0:
                shootY = 0


            if shootX == -1:
                self.image = self.seq[0]
                self.sub[0].position = [self.x, self.y -40]
                self.sub[1].position = [self.x, self.y +40]

                SubLshootX = 0
                SubRshootX = 0
                SubLshootY = -1
                SubRshootY = 1

            elif shootX == 1:
                self.image = self.seq[2]
                self.sub[0].position = [self.x, self.y +40]
                self.sub[1].position = [self.x, self.y -40]

                SubLshootX = 0
                SubRshootX = 0
                SubLshootY = 1
                SubRshootY = -1

            elif shootY == -1:
                self.image = self.seq[1]
                self.sub[0].position = [self.x+40, self.y]
                self.sub[1].position = [self.x-40, self.y]

                SubLshootX = 1
                SubRshootX = -1
                SubLshootY = 0
                SubRshootY = 0

            elif shootY == 1:
                self.image = self.seq[3]
                self.sub[0].position = [self.x-40, self.y]
                self.sub[1].position = [self.x+40, self.y]

                SubLshootX = -1
                SubRshootX = 1
                SubLshootY = 0
                SubRshootY = 0

            self.timer = 0
            PShoot = PlayerShoot(self.x + w*shootX, self.y+ h*shootY, [shootX, shootY])
            self.shoot.append(PShoot)
            self.parent.add(PShoot)

            self.soundPlayer.queue(self.shoot_sound)


            for subC in self.sub:
                if subC.charged:
                    if random.random() > 0.7:

                        if subC.number == 0:
                            subLCharged = subC.charged;
                            self.parent.add(reflectShoot(subC.x + w*SubLshootX, 
                                                        subC.y +h*SubLshootY, 
                                                        [SubLshootX, SubLshootY]))
                            self.shootS_sound.play()

                        elif subC.number == 1:
                            subRCharged = subC.charged;
                            self.parent.add(straightShoot(subC.x + w*SubRshootX, 
                                                        subC.y +h*SubRshootY, 
                                                        [SubRshootX, SubRshootY]))
                            self.shootR_sound.play()


            self.soundPlayer.play()
            pyglet.app.run()
            pyglet.app.exit()



 #reflectShoot        straightShoot


        if Q_pressed != 0 and self.sub[0].charged:
            self.sub[0].discharge()
            LBomb = []
            for i in range(0, 4):
                LBomb.append(reflectShoot(self.x + 40 + (40 * (-1)*math.cos(math.radians(0+90*i))), 
                                          self.y - 40 + (40 * (-1)*math.sin(math.radians(0+90*i))), 
                                          [math.sin(math.radians(0+90*i)), math.cos(math.radians(0+90*i))]))
                LBomb.append(reflectShoot(self.x - 40 + (40 * (-1)*math.cos(math.radians(0+90*i))), 
                                          self.y + 40 + (40 * (-1)*math.sin(math.radians(0+90*i))), 
                                          [math.sin(math.radians(0+90*i)), math.cos(math.radians(0+90*i))]))
            for LB in LBomb:
                self.parent.add(LB)
            self.BombS_sound.play()

        if E_pressed != 0 and self.sub[1].charged:
            self.sub[1].discharge()
            RBomb = []
            for i in range(0, 4):
                RBomb.append(straightShoot(self.x + 40 + (40 * (-1)*math.sin(math.radians(0+90*i))), 
                                          self.y - 40 + (40 * (-1)*math.cos(math.radians(0+90*i))), 
                                          [math.sin(math.radians(0+90*i)), math.cos(math.radians(0+90*i))]))
                RBomb.append(straightShoot(self.x - 40 + (40 * (-1)*math.sin(math.radians(0+90*i))), 
                                          self.y + 40 + (40 * (-1)*math.cos(math.radians(0+90*i))), 
                                          [math.sin(math.radians(0+90*i)), math.cos(math.radians(0+90*i))]))
            for RB in RBomb:
                self.parent.add(RB)
            self.BombR_sound.play()


            pyglet.app.run()
            pyglet.app.exit()
             

        if horizon != 0:
            if w > self.x and horizon == -1:
                horizon = 0
            if self.x > self.parent.width - w and horizon == 1:
                horizon = 0
            self.move(horizon,1)

            for subC in self.sub:
                subC.move(horizon,1)


        if virtical != 0:
            if h > self.y and virtical == -1:
                virtical = 0
            if self.y > self.parent.height - h and virtical == 1:
                virtical = 0
            self.move(virtical,-1)

            for subC in self.sub:
                subC.move(virtical,-1)



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


    def chargeSub(self, NPC):
        if NPC == 0:
            self.sub[0].charge()
        elif NPC == 1:
            self.sub[1].charge()



class SubCannon(Actor):
    def __init__(self, x, y, num):
        super(SubCannon, self).__init__(x, y, 'Sub.png')
        self.speed = 7
        self.energe = 0
        self.number = num
        self.charged = False

    def update(self, elapsed):
        pass


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

    def charge(self):

        if self.number == 0:
            if self.energe < 15:
                self.energe += 1
                self.color = (255,255-9.2*self.energe, 255-17*self.energe)
                #ff8b00
            else:
                self.charged = True


        elif self.number == 1:
             if self.energe < 15:
                self.energe += 1
                self.color = (255-17*self.energe,255-12.3*self.energe, 255)
                #00b9ff
             else:
                self.charged = True

    def discharge(self):
        self.energe = 0
        self.charged = False
        self.color = (255,255, 255)




class NPC(Actor):
    def __init__(self, x, y, img):
        super(NPC, self).__init__(x, y, img)
        rand = random.random()

        self._set_scale(1+rand*0.7)
        self.speed = 200
        self.score = (15 + int(rand*10))
        self.vec = [random.random()*2-1, random.random()*2-1]

    def move(self,dt):
        pos = self.position

        new_x = pos[0] + self.speed * self.vec[0] * dt
        new_y = pos[1] + self.speed * self.vec[1] * dt
        
        self.position = eu.Vector2(new_x, new_y)
        self.cshape.center = self.position


class reflectN(NPC):
    def __init__(self, x, y):
        seq = ImageGrid(load('ReflectNPC.png'), 4, 1)
        self.img = Animation.from_image_sequence(seq, 0.2)
        super(reflectN, self).__init__(x, y, self.img)
        #self.speed = 200


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
        seq = ImageGrid(load('StraightNPC.png'), 4, 1)
        self.img = Animation.from_image_sequence(seq, 0.2)
        super(straightN, self).__init__(x, y,self.img)
        #self.speed = 300

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
        super(Shoot, self).__init__(x, y, img)
        self.speed = 24
        self.vec = [0,0]
        self.vec[0] = vec[0]
        self.vec[1] = vec[1]

    def update(self, elapsed):
        pass

    def move(self,dt):
        pos = self.position

        new_x = pos[0] + self.speed * self.vec[0] * dt
        new_y = pos[1] + self.speed * self.vec[1] * dt
        
        self.position = eu.Vector2(new_x, new_y)
        self.cshape.center = self.position

class PlayerShoot(Shoot):
    INSTANCE = []

    def __init__(self, x, y, vec):
        seq = ImageGrid(load('laser.png'), 2, 1)
        if vec[1] == 1 or vec[1] == -1:
            super(PlayerShoot, self).__init__(x, y, vec, seq[1])
        else:
            super(PlayerShoot, self).__init__(x, y, vec, seq[0])
        PlayerShoot.INSTANCE.append(self)
        self.shootItem = -1


    def collide(self, other):
        if isinstance(other, NPC):
            self.parent.update_score(other.score)
            if isinstance(other, reflectN):
                self.shootItem = 0
            elif isinstance(other, straightN):
                self.shootItem = 1

            PlayerShoot.INSTANCE.remove(self)
            other.kill()
            self.kill()              

            return self.shootItem

    def update(self, elapsed):
        self.move(self.speed * elapsed)


    def on_exit(self):
        super(PlayerShoot, self).on_exit()
        if self in PlayerShoot.INSTANCE:
            PlayerShoot.INSTANCE.remove(self)


class reflectShoot(Shoot):
    INSTANCE = []

    def __init__(self, x, y, vec):
        seq = ImageGrid(load('Rlaser.png'), 2, 1)
        if vec[1] == 1 or vec[1] == -1:
            super(reflectShoot, self).__init__(x, y, vec, seq[1])
        else:
            super(reflectShoot, self).__init__(x, y, vec, seq[0])
        reflectShoot.INSTANCE.append(self)



    def collide(self, other):
        if isinstance(other, NPC):
            self.parent.update_score(other.score)
            reflectShoot.INSTANCE.remove(self)
            other.kill()
            self.kill()              


    def update(self,dt):
        self.move(self.speed * dt)
        self.vec = self.move_reflect(self.position,self.vec)


    def move_reflect(self,pos,vec):
        x,y=pos
        if x < 0 or x > self.w:
            vec[0] *= -1
        elif y < 0 or y > self.h:
            vec[1] *= -1

        return vec


class straightShoot(Shoot):
    INSTANCE = []

    def __init__(self, x, y, vec):
        seq = ImageGrid(load('Slaser.png'), 2, 1)
        if vec[1] == 1 or vec[1] == -1:
            super(straightShoot, self).__init__(x, y, vec, seq[1])
        else:
            super(straightShoot, self).__init__(x, y, vec, seq[0])
        straightShoot.INSTANCE.append(self)



    def collide(self, other):
        if isinstance(other, NPC):
            self.parent.update_score(other.score)
            straightShoot.INSTANCE.remove(self)
            other.kill()
            self.kill()              


    def update(self,dt):
        self.position = self.move_out(self.position)
        self.move(self.speed * dt)


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



        



class GameLayer(cocos.layer.Layer):
    is_event_handler = True

    def on_key_press(self, k, _):
        PlayerCannon.KEYS_PRESSED[k] = 1

    def on_key_release(self, k, _):
        PlayerCannon.KEYS_PRESSED[k] = 0


    def __init__(self, difficulty,hud):
        super(GameLayer, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.hud = hud
        self.width = w
        self.height = h

        self.difficulty = difficulty
        self.lives = 2

        self.second = 0
        self.timer = 0
        self.score = 0


        #self.hud.tutorial()

        self.update_score()
        self.create_player()
        self.hud.update_timer(self.timer)

        cell = self.player.width * 1.25
        self.collman = cm.CollisionManagerGrid(0, w, 0, h,
                                               cell, cell)


        self.schedule(self.update)


    def create_player(self):
        self.player = PlayerCannon(self.width * 0.5, self.height*0.5)
        SCLeft = SubCannon(self.width * 0.5 - 40, self.height*0.5, 0)
        SCRight = SubCannon(self.width * 0.5 + 40, self.height*0.5, 1)

        self.player.sub.append(SCLeft)
        self.player.sub.append(SCRight)

        self.add(SCLeft)
        self.add(SCRight)
        self.add(self.player)
        self.hud.update_HP(self.player.HP)
        self.hud.update_lives(self.lives)

    def respawn_player(self):
        self.lives -= 1
        if self.lives < 0:
            self.unschedule(self.update)
            self.hud.show_game_over(self.score, self.timer)
        else:
            for _, node in self.children:
                self.remove(node)
            self.create_player()


    def update_score(self, score=0):
        self.score += score
        self.hud.update_score(self.score)


        
    def update(self, dt):

        self.collman.clear()
        for _, node in self.children:
            self.collman.add(node)
            if not self.collman.knows(node):
                self.remove(node)

        for _, node in self.children:
            node.update(dt)


        for other in self.collman.iter_colliding(self.player):
            if isinstance(other, NPC):
                self.player.collide(other)
                self.hud.update_HP(self.player.HP)
                if self.player.HP <= 0:
                    self.respawn_player()


        for instance in PlayerShoot.INSTANCE:
            self.collide(instance)
        for instance in reflectShoot.INSTANCE:
            self.collide(instance)
        for instance in straightShoot.INSTANCE:
            self.collide(instance)


        self.create_NPC()

        self.second += dt
        if self.second>=1:
            self.update_score(int(self.second) * 10)
            self.timer += int(self.second)
            self.hud.update_timer(self.timer)
            self.second = 0



    def collide(self, node):
        if node is not None:
            for other in self.collman.iter_colliding(node):
                item = node.collide(other)
                self.player.chargeSub(item)
                return True
        return False


    def create_NPC(self):
        kind=0
        range=0
        pos = (0,0)

        if random.random() < (0.012+0.003*self.difficulty +self.timer/7000):
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



class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.score_text = cocos.text.Label('', font_size=18)
        self.score_text.position = (20, h - 40)
        self.timer_text = cocos.text.Label('', font_size=18)
        self.timer_text.position = (20, h - 80)
        self.lives_text = cocos.text.Label('', font_size=18)
        self.lives_text.position = (w - 100, h - 40)
        self.HP_text = cocos.text.Label('', font_size=18)
        self.HP_text.position = (w-190, h - 40)
        self.add(self.score_text)
        self.add(self.timer_text)
        self.add(self.lives_text)
        self.add(self.HP_text)

        move = cocos.text.Label('Move: WASD', font_size=18, position = (w/2, h - 40), anchor_x = 'center')
        shoot = cocos.text.Label('Shoot: Up, Down, Left, Right', font_size=18, position = (w/2, h - 60), anchor_x = 'center')
        bomb = cocos.text.Label('Bomb: Left - Q, Right - E', font_size=18, position = (w/2, h - 80), anchor_x = 'center')
        self.add(move)
        self.add(shoot)
        self.add(bomb)

    def update_score(self, score):
        self.score_text.element.text = 'Score: %s' % score

    def update_timer(self, timer):
        self.timer_text.element.text = 'Timer: %s' % timer

    def update_lives(self, lives):
        self.lives_text.element.text = 'Lives: %s' % lives

    def update_HP(self, HP):
        self.HP_text.element.text = 'HP: %s' % HP



    def show_game_over(self,score, timer):
        w, h = cocos.director.director.get_window_size()

        game_over = cocos.text.Label('Game Over', font_size=50,
                                     anchor_x='center',
                                     anchor_y='center')
        game_over.position = w * 0.5, h * 0.7
        self.add(game_over)

        score_final = cocos.text.Label('Your Score: '+ str(score), font_size=30,
                                     anchor_x='center',
                                     anchor_y='center')
        score_final.position = w * 0.5, h * 0.5
        self.add(score_final)

        timer_final = cocos.text.Label('Total Playtime: '+ str(timer), font_size=30,
                                     anchor_x='center',
                                     anchor_y='center')
        timer_final.position = w * 0.5, h * 0.35
        self.add(timer_final)



class MainMenu(menu.Menu):
    def __init__(self):
        super(MainMenu, self).__init__('Space Wander')
        self.font_title['font_name'] = 'Times New Roman'
        self.font_title['font_size'] = 60
        self.font_title['bold'] = True
        self.font_item['font_name'] = 'Times New Roman'
        self.font_item_selected['font_name'] = 'Times New Roman'

        self.difficulty = ['Easy', 'Normal', 'Hard']
        self.selDifficulty = 0

        m1 = menu.MenuItem('New Game', self.new_game)
        m2 = menu.MultipleMenuItem('Difficulty: ', self.set_difficulty, self.difficulty)
        m3 = menu.MenuItem('Quit', pyglet.app.exit)
        self.create_menu([m1, m2, m3], menu.shake(), menu.shake_back())
        # selected effect, unselected effect
        # zoom_in(), zoom_out()


    def new_menu(): # create menu
        scene = cocos.scene.Scene()
        color_layer = cocos.layer.ColorLayer(0,0,0, 255)
        scene.add(MainMenu(), z=1)
        scene.add(color_layer, z=0)
        return scene

    def set_difficulty(self, index):
        self.selDifficulty = index
        print('Difficulty set to', self.selDifficulty)




    def tutorial(self):
        w, h = cocos.director.director.get_window_size()
        move = cocos.text.Label('Move: WASD', font_size=18, position = (w/2, h - 40))
        shoot = cocos.text.Label('Shoot: Up, Down, Left, Right', font_size=18, position = (w/2, h - 60))
        bomb = cocos.text.Label('Bomb: Left - Q, Right - E', font_size=18, position = (w/2, h - 80))


        layer = cocos.layer.Layer()
        layer.add(move, shoot, bomb)

        tutorial_scene = cocos.scene.Scene()
        tutorial_scene.add(layer, z=2)

        start = menu.MenuItem('Start', self.new_game)
        tutorial_scene.add(start, z=1)

        color_layer = cocos.layer.ColorLayer(0,0,0, 255)
        tutorial_scene.add(color_layer, z=0)

        cocos.director.director.run(tutorial_scene)


    def new_game(self): # gamelayer.py

        main_scene = cocos.scene.Scene()
        hud_layer = HUD()
        main_scene.add(hud_layer, z=1)
        game_layer = GameLayer(self.selDifficulty, hud_layer)
        main_scene.add(game_layer, z=0)

        cocos.director.director.run(main_scene)
        #return cocos.scene.Scene(main_scene)

        # cocos.scene.Scene(*children)

    def game_over(): 
        w, h = director.get_window_size()
        layer = cocos.layer.Layer()
        text = cocos.text.Label('Game Over', position=(w*0.5, h*0.5),
        font_name='Times New Roman', font_size=72,
        anchor_x='center', anchor_y='center')
        layer.add(text)
        scene = cocos.scene.Scene(layer)
        new_scene = FadeTransition(mainmenu.new_menu())

        # replace: replaces running scene with new scene
        func = lambda: director.replace(new_scene)
        scene.do(ac.Delay(3) + ac.CallFunc(func))
        return scene


if __name__ == '__main__':
    cocos.director.director.init(caption='Space Wander', 
                                 width=800, height=650)

    cocos.director.director.run(MainMenu.new_menu())