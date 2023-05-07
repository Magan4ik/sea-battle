from math import *
import pyglet
from pyglet.window import key, mouse, FPSDisplay
from pyglet import shapes
import random
import UI

if __name__ == '__main__':
    width, height = (1000, 500)
    win = pyglet.window.Window(width, height, style = pyglet.window.Window.WINDOW_STYLE_DEFAULT, caption = 'Fight in sea')
    w, h = win.width, win.height
    visible = False
    fps_dis = FPSDisplay(win)
    label = pyglet.text.Label(
                        '(x, y)',
                        font_name = 'Arial',
                        font_size = 10,
                        x = 950, y = 10,
                        anchor_x = 'center', anchor_y = 'center')

    #images
    exit_full_screen = pyglet.image.load('ex.png')
    full_screen = pyglet.image.load('fscr.png')
    back_arrow = pyglet.image.load('back.png')
    textures = {
    'hit_list' : [pyglet.image.load('textures\hit1.png'), pyglet.image.load('textures\hit2.png'), pyglet.image.load('textures\hit3.png')],
    'miss_list' : [pyglet.image.load('textures\miss1.png'), pyglet.image.load('textures\miss2.png'), pyglet.image.load('textures\miss3.png')],
    'ship_list' : [pyglet.image.load('textures\ship1.png'), pyglet.image.load('textures\ship2.png'), pyglet.image.load('textures\ship3.png'), pyglet.image.load('textures\ship4.png')]
    }
    #objects
    menu = UI.Main_menu('Arial')
    menu.add_button('Start Game', w // 2, h // 2 + 50, 20)
    menu.add_button('Exit', w // 2, h // 2, 20)
    field = UI.Game_field()
    player_net = field.add_net(50, 50, 40, 10, 10, batch = field.batch)
    game_net_1 = field.add_net(50, 50, 40, 10, 10, batch = field.game_batch)
    game_net_2 = field.add_net(550, 50, 40, 10, 10, batch = field.game_batch)
    score1 = field.add_label('0', 250, 475, 30, batch = field.game_batch)
    score2 = field.add_label('0', 750, 475, 30, batch = field.game_batch)
    #textures['ship_list'] = None
    for i in range(4):
        field.add_ship(600 + 50*i, 400, 1, field.size, textures['ship_list'])
    for i in range(3):
        field.add_ship(600 + 50*i, 300, 2, field.size, textures['ship_list'])
    for i in range(2):
        field.add_ship(800 + 50*i, 300, 3, field.size, textures['ship_list'])
    for i in range(1):
        field.add_ship(900 + 50*i, 300, 4, field.size, textures['ship_list'])
    field.done_button('done', 225, 25, 20, 'Arial')


@win.event
def on_mouse_motion(x, y, dx, dy):
    global label
    label.text = f'{x}, {y}'
    if menu.start and not menu.game:
        player_net.on_net(x, y)
        field.on_done(x, y)
    elif not menu.start and not menu.game:
        menu.on_button(x, y)
    elif menu.start and menu.game:
        on_net, cell_x, cell_y = game_net_1.on_net(x, y)
        on_net, cell_x, cell_y = game_net_2.on_net(x, y)
        check, ship = field.on_ship(x, y, field.first_ships)
@win.event
def on_mouse_press(x, y, but, mod):
    if not menu.start:
        check, button = menu.on_button(x, y)
        match check, button.name:
            case True, 'Start Game':
                menu.start = True
            case True, 'Exit':
                pyglet.app.exit()
            case _:
                pass
    elif not menu.game:
        on_ship, ship = field.on_ship(x, y)
        if on_ship:
            on_net, cell_x, cell_y = player_net.on_net(x, y)
            if not on_net:
                ship.anchor = (x - ship.ship.x, y - ship.ship.y)
                #ship.X = ship.x + ship.anchor[0]
                #ship.Y = ship.y + ship.anchor[1]
            else:
                #ship.anchor = (ship.size*sin(radians(ship.ship.rotation)), 0)
                pass
            field.select_ship[0] = True
            field.select_ship[1] = ship
        if len(field.ship_net) == len(field.ship_list):
            field.on_done(x, y, click = True)
            if len(field.second_ships) == 10:
                if field.done_button.on_button(x, y):
                    menu.game = True
    else:
        on_net, cell_x, cell_y = player_net.on_net(x, y)
        field.strike(x, y, hit_list = textures['hit_list'], miss_list = textures['miss_list'])

@win.event
def on_mouse_drag(mx, my, dx, dy, but, mod):
    if menu.start and not menu.game:
        if field.select_ship[0]:
            on_net, cell_x, cell_y = player_net.on_net(mx, my)
            ship = field.select_ship[1]
            if on_net:
                ship.anchor = (0, 0)#(ship.size*int(sin(radians(ship.ship.rotation))), 0)
                #print((ship.X, ship.Y), ship.anchor)
                ship.X, ship.Y = (cell_x, cell_y)
                #if ship.ship.rotation == 90: ship.ship.y += ship.size
            else:
                ship.X = mx
                ship.Y = my

@win.event
def on_mouse_release(mx, my, but, mod):
    if field.select_ship[0]:
        field.select_ship[0] = False
        on_net, cell_x, cell_y = player_net.on_net(mx, my)
        ship = field.select_ship[1]
        if on_net:
            if field.check_ships():
                field.ship_on_net()
            else:
                field.reset_pos(ship)
                field.ship_out_net()
            if ship.ship.rotation == 0:
                top_net = player_net.y + player_net.rows*field.size
                if ship.ship.y + ship.decks*ship.size > top_net:
                    field.reset_pos(ship)
                    field.ship_out_net()
                else:
                    field.ship_on_net()
            else:
                right_net = player_net.x + player_net.columns*field.size
                if ship.ship.x + ship.decks*ship.size > right_net:
                    field.reset_pos(ship)
                    field.ship_out_net()
                else:
                    field.ship_on_net()
        else:
            field.reset_pos(ship)
            field.ship_out_net()

@win.event
def on_key_press(sym, modif):
    global visible
    if sym == key.R and menu.start and field.select_ship[0]:
        ship = field.select_ship[1]
        if ship.ship.rotation != 0:
            ship.anchor = (0, 0)
            ship.ship.scale_x = 1
        else:
            ship.anchor = (0, 0)
            ship.ship.scale_x = -1
        ship.ship.rotation += 90
        if ship.ship.rotation > 90:
            ship.ship.rotation = 0
    elif sym == key.F:
        visible = True
    elif sym == key.G:
        visible = False

@win.event
def on_draw():
    global label, visible
    win.clear()
    shapes.Rectangle(0, 0, width = w, height = h, color = (31, 51, 130)).draw()
    if not menu.start:
        menu.batch.draw()
    elif not menu.game:
        field.batch.draw()
        field.ship_batch.draw()
        #field.first_batch.draw()
        #field.second_batch.draw()
    else:
        field.game_batch.draw()
    fps_dis.draw()
    if len(field.ship_net) == len(field.ship_list):
        field.done_button.label.draw()
    label.draw()
    if visible:
        field.first_batch.draw()
        field.second_batch.draw()

pyglet.app.run()
