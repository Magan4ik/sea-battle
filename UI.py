import pyglet
import math
import random
from copy import copy, deepcopy
from pyglet import shapes
from itertools import cycle


# import main

class Main_menu:
    def __init__(self, font_name):
        self.start = False
        self.game = False
        self.font_name = font_name
        self.button_list = []
        self.batch = pyglet.graphics.Batch()

    def add_button(self, name, x, y, font_size):
        self.button_list.append(Button(name, x, y, font_size, self.font_name, batch=self.batch))

    def on_button(self, x, y):
        for button in self.button_list:
            if x >= button.x - button.label.font_size * len(button.name) // 3 and \
                    x <= button.x + button.label.font_size * len(button.name) // 3 and \
                    y >= button.y - button.label.font_size // 2 and y <= button.y + button.label.font_size // 2:
                button.select(1.2)
                return True, button
            else:
                button.label.font_size = button.font_size
        else:
            return False, button


class Button:
    def __init__(self, name, x, y, font_size, font_name, batch=None):
        self.font_name = font_name
        self.name = name
        self.x = x
        self.y = y
        self.font_size = font_size
        self.batch = batch
        self.label = pyglet.text.Label(
            name,
            font_name=self.font_name,
            font_size=font_size,
            x=x, y=y,
            anchor_x='center', anchor_y='center', batch=self.batch)

    def on_button(self, x=-1, y=-1):
        if x in range(self.x - self.width, self.x + self.width) and y in range(self.y - self.height,
                                                                               self.y + self.height):
            return True
        else:
            return False

    def select(self, scale=1.2):
        self.label.font_size = self.font_size * scale

    @property
    def width(self):
        return int(self.label.font_size * len(self.name) // 3)

    @property
    def height(self):
        return int(self.label.font_size // 2)


class Game_field:
    def __init__(self):
        self.batch = pyglet.graphics.Batch()  # UI batch
        self.game_batch = pyglet.graphics.Batch()  # game field batch
        self.ship_batch = pyglet.graphics.Batch()  # batch of all ships
        self.ship_list = []  # general list of ships
        self.ship_net = []  # ships on net
        self.net_list = []
        self.select_ship = [False, None]  # [selected-ship<class:Ship>, pick<bool>]
        self.first_ships = []  # first player ships
        self.first_batch = pyglet.graphics.Batch()  # first player batch
        self.second_ships = []  # second player ships
        self.second_batch = pyglet.graphics.Batch()  # second player batch
        self.turn = cycle([1, 2])
        self.mover = 2  #
        self.shot_list = []  # position of shot list
        self.shots = []  # shot sprite list
        self.labels = []
        self.winner = 0

    def add_ship(self, x, y, decks, size, images=None):
        self.ship_list.append(Ship(x, y, decks, size, batch=self.ship_batch, images=images))

    def add_net(self, x, y, size, columns, rows, batch=None):
        self.size = size
        net = Game_net(x, y, size, columns, rows, batch=batch)
        self.net_list.append(net)
        return net

    def on_ship(self, x, y, list=None):
        list = self.ship_list if list == None else list
        for ship in list:
            size_x = ship.width
            size_y = ship.height
            sx = int(ship.ship.x - ship.anchor[0]) if ship.ship.rotation == 0 else int(ship.ship.x)
            if x in range(sx, sx + size_x) and \
                    y in range(ship.ship.y - ship.anchor[1], ship.ship.y + size_y - ship.anchor[1]):
                return True, ship
        else:
            return False, ship

    def ship_on_net(self):
        ship = self.select_ship[1]
        if ship not in self.ship_net:
            self.ship_net.append(ship)

    def ship_out_net(self):
        ship = self.select_ship[1]
        if ship in self.ship_net:
            self.ship_net.remove(ship)

    def check_ships(self):
        ship = self.select_ship[1]
        if len(self.ship_net) == 0: return True
        for sh in self.ship_net:
            if sh == ship: continue
            ship_w = ship.size
            if sh.X in range(ship.X - sh.width, ship.X + ship.width + 1) and \
                    sh.Y in range(ship.Y - sh.height, ship.Y + ship.height + 1):
                return False
        else:
            return True

    def done_button(self, name, x, y, font_size, font_name):
        self.done_button = Button(name, x, y, font_size, font_name)

    def reset_pos(self, ship):
        ship.anchor = (0, 0)
        ship.ship.x = ship.x
        ship.ship.y = ship.y
        ship.ship.rotation = 0
        ship.ship.scale_x = 1

    def on_done(self, x, y, click=False):
        if self.done_button.on_button(x, y):
            if click:
                self.done_button.select(1.2)
                for ship in self.ship_net:
                    if len(self.first_ships) < 10:
                        self.first_ships.append(ship.copy(new_batch=self.first_batch))
                    else:
                        ship.ship.x += 500
                        self.second_ships.append(ship.copy(new_batch=self.second_batch))
                for ship in self.ship_list:
                    self.reset_pos(ship)
                self.ship_net = []
            else:
                self.done_button.select(1.2)
        else:
            self.done_button.select(1)

    def strike(self, x, y, hit_list=None, miss_list=None):
        net = self.net_list[self.mover]
        check, cell_x, cell_y = net.on_net(x, y)
        if check:
            if (cell_x, cell_y) not in self.shot_list:
                list = self.first_ships if self.mover == 1 else self.second_ships
                check_ship, ship = self.on_ship(x, y, list)
                if check_ship:  #### HIT ####
                    self.labels[self.mover - 1].text = str(int(self.labels[self.mover - 1].text) + 1)
                    ship.dead += 1
                    if hit_list == None:
                        self.shots.append(shapes.Rectangle(cell_x, cell_y, width=self.size, height=self.size,
                                                           color=(217, 54, 62), batch=self.game_batch))
                    else:
                        sprite_hit = random.choice(hit_list)
                        sp = pyglet.sprite.Sprite(sprite_hit, cell_x + 2, cell_y + 2, batch=self.game_batch)
                        sp.update(scale=0.08)
                        self.shots.append(sp)
                    self.shot_list.append((cell_x, cell_y))
                    if ship.dead == ship.decks:  #### KILL ####
                        for i in range(ship.X - ship.size, ship.X + ship.width + ship.size, ship.size):
                            for j in range(ship.Y - ship.size, ship.Y + ship.height + ship.size, ship.size):
                                if (i, j) not in self.shot_list and i in range(net.x, net.right) and j in range(net.y,
                                                                                                                net.top):
                                    if miss_list == None:
                                        self.shots.append(shapes.Rectangle(i, j, width=self.size, height=self.size,
                                                                           color=(37, 77, 219), batch=self.game_batch))
                                    else:
                                        sprite_miss = random.choice(miss_list)
                                        sp = pyglet.sprite.Sprite(sprite_miss, i + 0, j + 0, batch=self.game_batch)
                                        sp.update(scale=0.08)
                                        self.shots.append(sp)
                                    self.shot_list.append((i, j))
                    if self.labels[self.mover - 1].text == 20:
                        self.win(self.mover)
                else:  #### MISS ####
                    if miss_list == None:
                        self.shots.append(shapes.Rectangle(cell_x, cell_y, width=self.size, height=self.size,
                                                           color=(37, 77, 219), batch=self.game_batch))
                    else:
                        sprite_miss = random.choice(miss_list)
                        sp = pyglet.sprite.Sprite(sprite_miss, cell_x + 0, cell_y + 0, batch=self.game_batch)
                        sp.update(scale=0.08)
                        self.shots.append(sp)
                    self.shot_list.append((cell_x, cell_y))
                    self.mover = next(self.turn)

    def add_label(self, name, x, y, size, batch=None):
        lab = pyglet.text.Label(
            name,
            font_name='Arial',
            font_size=size,
            x=x, y=y,
            anchor_x='center', anchor_y='center', batch=batch)
        self.labels.append(lab)
        return lab

    def win(self, winner):
        pass


class Ship:
    def __init__(self, x, y, decks, size, batch, images=None):
        self.images = images
        self.x = x
        self.y = y
        self.dead = 0
        self.anchor_x = 0
        self.anchor_y = 0
        self.size = size
        self.__batch = batch
        if images == None:
            self.ship = shapes.Rectangle(x, y, width=size, height=size * decks, color=(37, 114, 196),
                                         batch=self.__batch)
        else:
            self.ship = pyglet.sprite.Sprite(images[decks - 1], x, y, batch=batch)
            self.ship.update(scale=0.08)

        self.__decks = decks

    def copy(self, new_batch=pyglet.graphics.Batch()):
        obj = Ship(self.x, self.y, self.__decks, self.size, new_batch)
        obj.anchor_x = self.anchor_x
        obj.anchor_y = self.anchor_y
        obj.__batch = new_batch
        if self.images == None:
            obj.ship = shapes.Rectangle(self.X, self.Y, width=self.size, height=self.size * self.decks,
                                        color=(100, 100, 100), batch=obj.__batch)
        else:
            obj.ship = pyglet.sprite.Sprite(self.images[self.decks - 1], self.X, self.Y, batch=obj.__batch)
            obj.ship.update(scale=0.08)
        obj.ship.scale_x = self.ship.scale_x
        obj.anchor = self.anchor
        obj.ship.rotation = self.ship.rotation
        return obj

    @property
    def decks(self):
        return self.__decks

    @property
    def width(self):
        width_ = int(self.size * self.decks * math.sin(math.radians(self.ship.rotation)))
        if width_ == 0: width_ = self.size
        return width_

    @property
    def height(self):
        height_ = int(self.size * self.decks * math.cos(math.radians(self.ship.rotation)))
        if height_ == 0: height_ = self.size
        return height_

    @property
    def X(self):
        return self.ship.x

    @property
    def Y(self):
        return self.ship.y

    @X.setter
    def X(self, X):
        if self.images == None:
            self.ship.x = X
        else:
            if self.ship.rotation == 0:
                self.ship.x = X - self.ship.image.anchor_x
            else:
                self.ship.x = X

    @Y.setter
    def Y(self, Y):
        if self.images == None:
            self.ship.y = Y
        else:
            if self.ship.rotation == 0:
                self.ship.y = Y - self.ship.image.anchor_y
            else:
                self.ship.y = Y

    @property
    def batch(self):
        return self.__batch

    @batch.setter
    def batch(self, batch):
        self.__batch = batch
        self.ship.batch = batch

    @property
    def anchor(self):
        if self.images == None:
            return self.ship.anchor_position
        else:
            return (self.anchor_x, self.anchor_y)

    @anchor.setter
    def anchor(self, pos):
        if self.images == None:
            self.ship.anchor_position = pos
            # print((self.ship.anchor_x, self.ship.anchor_y), pos)
        else:
            self.ship.image.anchor_x = pos[0]
            self.ship.image.anchor_y = pos[1]
            # print(self.ship.image.anchor_x, self.ship.image.anchor_y)
            # x = self.ship.x + self.anchor_x
            # y = self.ship.y + self.anchor_y
            # self.ship.x = x - pos[0]
            # self.ship.y = y - pos[1]
        self.anchor_x = pos[0]
        self.anchor_y = pos[1]


class Game_net:
    def __init__(self, x, y, size, columns, rows, batch=None):
        self.size = size
        self.batch = batch
        self.net_list = []
        self.x = x
        self.y = y
        self.columns = columns
        self.rows = rows
        for i in range(columns + 1):
            self.net_list.append(
                shapes.Line(x + size * i, y, x + size * i, y + size * rows, width=1, color=(225, 225, 225),
                            batch=batch))
        for j in range(rows + 1):
            self.net_list.append(
                shapes.Line(x, y + size * j, x + size * columns, y + size * j, width=1, color=(225, 225, 225),
                            batch=batch))

    def on_net(self, x, y):
        left_x = self.x
        self.right = self.x + self.columns * self.size
        lower_y = self.y
        self.top = self.y + self.rows * self.size
        cell_x = math.floor((x - left_x) / self.size) * self.size + left_x
        cell_y = math.floor((y - lower_y) / self.size) * self.size + lower_y
        self.rec1 = shapes.Rectangle(cell_x, lower_y, width=self.size,
                                     height=self.top - lower_y, color=(255, 255, 255),
                                     batch=self.batch)
        self.rec2 = shapes.Rectangle(left_x, cell_y, width=self.right - left_x,
                                     height=self.size, color=(255, 255, 255),
                                     batch=self.batch)
        if x in range(left_x, self.right) and y in range(lower_y, self.top):
            self.rec1.opacity = 50
            self.rec2.opacity = 50
            return True, cell_x, cell_y
        else:
            self.rec1.opacity = 0
            self.rec2.opacity = 0
            return False, 0, 0
