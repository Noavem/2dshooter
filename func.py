import os, sys
import pygame
import math
import random
import time
from values import *
import classes
import los
pygame.init()
pygame.font.init()

agency = pygame.font.Font('texture/agencyb.ttf', round(70))
terminal = pygame.font.Font('texture/terminal.ttf', 20)
terminal2 = pygame.font.Font('texture/terminal.ttf', 30)
terminal3 = pygame.font.Font('texture/terminal.ttf', 10)

evade_skip_tick = 0
acceleration = 200/1.875
velocity_cap = 9/1.875
breaking = 0.9
walking_speed = 7/1.875
running_speed = 13/1.875
evade_speed = 30/1.875
camera_breaking = 0.1/1.875
evading = False
tick_count = 60

camera_offset = [size[0]/2 , size[1]/2]

def debug_render(text_str):
    text = agency.render(str(text_str), False, [255,255,0])
    render_cool(text, [1000,60],15,16,render = True, offset = 10)   ### IN GAME

def print_s(screen,text_str,slot, color = [255,255,255]):
    text = terminal.render(str(text_str), False, color)
    screen.blit(text, (size[0] - 10 - text.get_rect().size[0], slot*30)) #

def load_animation(directory, start_frame, frame_count):
    list = []
    for x in range(frame_count):
        x = x+start_frame
        im_dir = directory + "/" + (4-len(str(x)))*"0" + str(x) + ".png"
        print(im_dir)

        im = pygame.image.load(im_dir).convert_alpha()
        list.append(im)

    return list

def colorize(image, newColor):
    """
    Create a "colorized" copy of a surface (replaces RGB values with the given color, preserving the per-pixel alphas of
    original).
    :param image: Surface to create a colorized copy of
    :param newColor: RGB color to use (original alpha values are preserved)
    :return: New colorized Surface instance
    """
    image = image.copy()

    # zero out RGB values
    image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    # add in new RGB values
    image.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

    return image


def rgb_render(list, amount, pos, cam_delta, screen):

    #rect_pos = list[0].get_rect(center = list[0].get_rect(center = (pos[0], pos[1])).center)

    pos[1] = pos[1] + random.randint(-amount,amount)



    screen.blit(pick_random_from_list(list[1:]),[pos[0] + 20 + random.randint(-amount,amount) + cam_delta[0]*2, pos[1] + random.randint(-amount,amount) + cam_delta[1]*2])

    screen.blit(list[0], [pos[0] + 20 + cam_delta[0], pos[1] + cam_delta[1]])







def get_dist_points(point_1,point_2):
    return math.sqrt((point_2[0] - point_1[0])**2 + (point_2[1] - point_1[1])**2)

def render_cool(image,pos,tick,beat_tick_h,render = False, offset = 0, scale = 1,screen = screen , style = "default", alpha = 255):

    a = 1 - math.sin(offset+10*tick/(2*math.pi*beat_tick_h))*0.1 * scale
    b = 1 - math.sin(math.pi/2 +offset+10*tick/(2*math.pi*beat_tick_h))*0.1 * scale
    rotation = math.sin(math.pi/2 +offset+10*tick/(2*math.pi*beat_tick_h))*2 * scale
    if style == "default":
        image_size = image.get_rect().size
        image_size_2 = [round(image_size[0]*a),round(image_size[1]*b)]

        image_2 = pygame.transform.scale(image,image_size_2)

        pos = [pos[0] - a/4 * image_size_2[0], pos[1] - b/4 * image_size_2[1]]

        if render == True:
            image_2, image_2_rot = rot_center(image_2,rotation,pos[0],pos[1])

        screen.blit(image_2,pos)

def check_for_render(player_pos,pos,range = 3000):
    if range < math.sqrt((player_pos[0] - pos[0])**2 + (player_pos[1] - pos[1])**2):
        return True
    return False

def get_angle(pos1,pos2):
    myradians = math.atan2(pos2[1]-pos1[1], pos2[0]-pos1[0])
    mydegrees = math.degrees(myradians)
    return mydegrees

def minus(list1,list2):
    try:
        list_1 = list1.copy()
        list_2 = list2.copy()
    except:
        list_1 = list1
        list_2 = list2
    for x in range(len(list1)):
        list_1[x] += list_2[x]
    return list_1

def pick_random_from_list(list):
    return list[random.randint(0,len(list)-1)]

def pick_random_from_dict(dict):
    print(dict)
    dict_keys = list(dict.keys())
    print(dict_keys)
    return dict[dict_keys[random.randint(0,len(dict_keys)-1)]]

def minus_list(list1,list2):
    list3 = list1.copy()
    for i in range(len(list1)):
        list3[i] = list1[i] - list2[i]

    return list3

def list_play(list):
    for y in list:
        y.stop()
    pick_random_from_list(list).play()

def load_image(image):
    im = pygame.image.load(image)
    size = im.get_rect().size
    size = [round(size[0] * r_w), round(size[1] * r_h)]
    return pygame.transform.scale(im,size)

def draw_pos(pos,cam_pos, x_off = 0, y_off = 0):
    return [pos[0] - cam_pos[0] + x_off, pos[1] - cam_pos[1] + y_off]

def get_closest_value(value, list):
    list_1 = {}
    for x in list:
        list_1[abs(value - x)] = x
    key_min = min(list_1)
    return list_1[key_min]

def get_closest_point(pos, list):
    dists = {}
    for point in list:
        dists[point] = get_dist_points(pos, point)

    key_min = min(dists.keys(), key=(lambda k: dists[k]))
    return dists[key_min]


def player_movement2(pressed, player_pos, x_vel, y_vel):
    global evading, evade_skip_tick

    if pressed[pygame.K_SPACE] and evading == False and evade_skip_tick == 0:
        if pressed[pygame.K_w]:
            y_vel = -evade_speed
        elif pressed[pygame.K_s]:
            y_vel = evade_speed
        else:
            y_vel = 0
        if pressed[pygame.K_d]:
            x_vel = evade_speed
        elif pressed[pygame.K_a]:
            x_vel = -evade_speed
        else:
            x_vel = 0



        if (x_vel, y_vel) != (0,0):
            evade_skip_tick = 30
            evading = True



    if evading == False:

        if pressed[pygame.K_LSHIFT]:
            sprinting = True
            velocity_cap = 9/1.875
        elif pressed[pygame.K_LCTRL]:
            crouching = True
            velocity_cap = 2.75/1.875
        else:
            sprinting = False
            velocity_cap = 5/1.875
        if pressed[pygame.K_w]:
            y_acc = -acceleration
        elif pressed[pygame.K_s]:
            y_acc = acceleration
        else:
            y_acc = 0
        if pressed[pygame.K_d]:
            x_acc = acceleration
        elif pressed[pygame.K_a]:
            x_acc = -acceleration
        else:
            x_acc = 0

    else:
        velocity_cap = 5/1.875
        x_acc, y_acc = 0,0

        if math.sqrt(x_vel**2 + y_vel**2) < velocity_cap:
            evading = False


    if abs(x_vel) < velocity_cap:
        x_vel += x_acc/tick_count
    if abs(y_vel) < velocity_cap:
        y_vel += y_acc/tick_count

    if abs(x_vel) > 0.1:
        x_vel *= breaking
    else:
        x_vel = 0
    if abs(y_vel) > 0.1:
        y_vel *= breaking
    else:
        y_vel = 0

    if evade_skip_tick != 0:
        evade_skip_tick -= 1
    else:
        evading = False


    player_pos[0] += x_vel
    player_pos[1] += y_vel

    return player_pos, x_vel, y_vel

def player_movement(pressed, player_pos,x_vel, y_vel, angle):
    global evading, evade_skip_tick
    sprinting, crouching = False, False
    if pressed[pygame.K_LSHIFT]:
        sprinting = True
    elif pressed[pygame.K_LCTRL]:
        crouching = True




    if pressed[pygame.K_SPACE] and evading == False and evade_skip_tick == 0:
        evading = True
        hor_speed = 0
        vert_speed, hor_speed = 0,0
        if pressed[pygame.K_w]:
            vert_speed = evade_speed
        elif pressed[pygame.K_s]:
            vert_speed = -evade_speed
        if pressed[pygame.K_a]:
            hor_speed = -evade_speed
        elif pressed[pygame.K_d]:
            hor_speed = evade_speed

        try:
            scalar = (evade_speed/math.sqrt(vert_speed ** 2 + hor_speed **2))
        except:
            scalar = 1
        y_vel_target, x_vel_target = 0,0
        y_vel_target -= math.sin(math.radians(angle)) * vert_speed * scalar
        x_vel_target += math.cos(math.radians(angle)) * vert_speed * scalar

        y_vel_target += math.cos(math.radians(angle)) * hor_speed * scalar
        x_vel_target += math.sin(math.radians(angle)) * hor_speed * scalar



        x_vel += (x_vel_target)

        y_vel += (y_vel_target)

        print("EVADE SPEED:", x_vel, y_vel)







    speed, vert_speed, hor_speed = 0,0,0
    if evading == False:

        if pressed[pygame.K_w]:
            if sprinting:
                vert_speed = running_speed
            elif crouching:
                vert_speed = walking_speed*0.35
            else:
                vert_speed = walking_speed

        if pressed[pygame.K_a]:
            if sprinting:
                hor_speed = -running_speed
            elif crouching:
                hor_speed = -walking_speed*0.35
            else:
                hor_speed = -walking_speed

        if pressed[pygame.K_d]:
            if sprinting:
                hor_speed = running_speed
            elif crouching:
                hor_speed = walking_speed*0.35
            else:
                hor_speed = walking_speed


        if pressed[pygame.K_s]:
            if sprinting:
                vert_speed = -running_speed
            elif crouching:
                vert_speed = -walking_speed*0.35
            else:
                vert_speed = -walking_speed




    try:
        scalar = (running_speed/math.sqrt(vert_speed ** 2 + hor_speed **2) if sprinting else walking_speed/math.sqrt(vert_speed ** 2 + hor_speed **2))
    except:
        scalar = 1
    if scalar > 1:
        scalar = 1

    if evading == False:
        y_vel_target, x_vel_target = 0,0

        y_vel_target -= math.sin(math.radians(angle)) * vert_speed * scalar
        x_vel_target += math.cos(math.radians(angle)) * vert_speed * scalar

        y_vel_target += math.cos(math.radians(angle)) * hor_speed * scalar
        x_vel_target += math.sin(math.radians(angle)) * hor_speed * scalar

        x_vel += (x_vel_target-x_vel)*breaking

        y_vel += (y_vel_target-y_vel)*breaking

    if abs(x_vel) > 0.1:
        x_vel *= breaking
    else:
        x_vel = 0
    if abs(y_vel) > 0.1:
        y_vel *= breaking
    else:
        y_vel = 0

    if evading == True and math.sqrt(x_vel ** 2 + y_vel **2) < walking_speed:
        print("")
        pass
        evading = False
        evade_skip_tick = 30

    player_pos[0] += x_vel
    player_pos[1] += y_vel


    if evade_skip_tick != 0 and not pressed[pygame.K_SPACE]:
        evade_skip_tick -= 1



    return player_pos, x_vel, y_vel

def render_player(screen, mouse_pos, player, player_pos, camera_pos,firing_tick = False):

    player_pos = [player_pos[0] - camera_pos[0],player_pos[1] - camera_pos[1]]

    x_diff = mouse_pos[0]-player_pos[0]
    y_diff = mouse_pos[1]-player_pos[1]

    try:
        angle = math.atan(x_diff/y_diff) * 180/math.pi +90
        if (x_diff < 0 and y_diff > 0) or (x_diff > 0 and y_diff > 0):
            angle += 180
    except:
        angle = 0
    if firing_tick == False:
        player_rotated, player_rotated_rect = rot_center(player,angle,player_pos[0],player_pos[1])
    else:
        player_rotated, player_rotated_rect = rot_center(player_firing,angle,player_pos[0],player_pos[1])

    offset = [player_rotated_rect[0]-player_pos[0], player_rotated_rect[1]-player_pos[1]]
    player_pos_center = player_rotated.get_rect().center
    player_pos_center = [player_pos[0]-player_pos_center[0],player_pos[1]-player_pos_center[1]]

    screen.blit(player_rotated,[player_pos[0]+offset[0],player_pos[1]+offset[1]])
    return angle

def rot_center(image, angle, x, y):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image, new_rect

def camera_aling(camera_pos,target_pos):
    camera_pos = [camera_pos[0] + camera_offset[0], camera_pos[1] + camera_offset[1]]
    camera_pos = [camera_pos[0] + (-camera_pos[0] + target_pos[0])*camera_breaking - camera_offset[0], camera_pos[1] + (-camera_pos[1] + target_pos[1])*camera_breaking - camera_offset[1]]
    return camera_pos

def keypress_manager(pressed,c_weapon, player_inventory):
    if pressed[pygame.K_r] and c_weapon.reload_tick() == 0 and c_weapon.get_Ammo() != c_weapon.get_clip_size()+1:
        c_weapon.reload(player_inventory)


def weapon_fire(c_weapon, player_inventory, angle, player_pos, screen = screen, ai = False):
    firing_tick = False
    if ai:
        if c_weapon.get_semi_auto():

            click = pick_random_from_list([True,False,False,False,False,False,False,False,False,False,False,False,False])

        else:
            click = True
    else:
        click = pygame.mouse.get_pressed()[0]

    if c_weapon.get_semi_auto():
        if c_weapon.check_for_Fire(click) == True and c_weapon.reload_tick() == 0:
            reload.stop()
            c_weapon.fire(player_pos,angle,screen)
            firing_tick = True
        elif c_weapon.get_Ammo() == 0 and player_inventory.get_amount_of_type(c_weapon.__dict__["ammo"]):

            reload_tick = c_weapon.reload(player_inventory)

            for x in weapon_fire_Sounds:
                x.stop()

    else:
        if c_weapon.check_for_Fire(click) == True and  c_weapon.weapon_fire_Tick() <= 0 and c_weapon.reload_tick() == 0:##FIRE
            while c_weapon.weapon_fire_Tick() <= 0 and c_weapon.check_for_Fire(click) == True:
                reload.stop()
                c_weapon.fire(player_pos,angle,screen)
                firing_tick = True


        elif c_weapon.get_Ammo() == 0 and player_inventory.get_amount_of_type(c_weapon.__dict__["ammo"]) > 0:
            reload_tick = c_weapon.reload(player_inventory)

            for x in weapon_fire_Sounds:
                x.stop()



    c_weapon.spread_recoverial()
    c_weapon.weapon_tick()

    return firing_tick

def draw_HUD(screen, player_inventory, cam_delta, camera_pos, weapon, player_actor, mouse_pos, clicked, r_click_tick):
    x_d, y_d =cam_delta
    x_d = -x_d
    y_d = -y_d
    clip_size = weapon.get_clip_size()
    clip = weapon.get_Ammo()
    pl_pos = minus_list(player_actor.get_pos(),camera_pos)
    pl_angl = player_actor.get_angle()

    pl_dist = los.get_dist_points(pl_pos, mouse_pos)
    # if pl_dist < 100:
    #     pl_dist = 100

    pl_dist_mult = pl_dist/25

    spread = weapon.__dict__["_Weapon__c_bullet_spread"] + weapon.__dict__["_Weapon__spread"]


    if not pygame.mouse.get_visible():
        pos2 = line = [pl_pos[0] + math.cos(math.radians(pl_angl-spread)) * (pl_dist+pl_dist_mult), pl_pos[1] - math.sin(math.radians(pl_angl-spread)) * (pl_dist+pl_dist_mult)]
        pos3 = line = [pl_pos[0] + math.cos(math.radians(pl_angl+spread)) * (pl_dist+pl_dist_mult), pl_pos[1] - math.sin(math.radians(pl_angl+spread)) * (pl_dist+pl_dist_mult)]

        pos1 = line = [pl_pos[0] + math.cos(math.radians(pl_angl-spread)) * (pl_dist-pl_dist_mult), pl_pos[1] - math.sin(math.radians(pl_angl-spread)) * (pl_dist-pl_dist_mult)]
        pos4 = line = [pl_pos[0] + math.cos(math.radians(pl_angl+spread)) * (pl_dist-pl_dist_mult), pl_pos[1] - math.sin(math.radians(pl_angl+spread)) * (pl_dist-pl_dist_mult)]

        pos5 = line = [pl_pos[0] + math.cos(math.radians(pl_angl)) * (pl_dist-pl_dist_mult*2), pl_pos[1] - math.sin(math.radians(pl_angl)) * (pl_dist-pl_dist_mult*2)]
        pos6 = line = [pl_pos[0] + math.cos(math.radians(pl_angl)) * (pl_dist+pl_dist_mult), pl_pos[1] - math.sin(math.radians(pl_angl)) * (pl_dist+pl_dist_mult)]

        pygame.draw.line(screen, [255,255,255], pos1, pos2,2)
        pygame.draw.line(screen, [255,255,255], pos4, pos3,2)
        pygame.draw.line(screen, [255,255,255], pos5, pos6,3)



    try:
        im = weapon.get_image()
        im.set_alpha(100)
        screen.blit(im,[5+x_d, 5+y_d])
    except:
        pass
    if weapon.__dict__["_Weapon__reload_tick"] == 0:
        if clip == clip_size + 1:
            text = terminal.render(str(clip-1) + "+1/" + str(clip_size), False, [255,255,255])
            screen.blit(text, (15+x_d, 45+y_d)) #
        else:
            if clip == 0:
                color = [255,0,0]
            else:
                color = [255,255,255]


            text = terminal.render(str(clip) + "/" + str(clip_size), False, color)
            screen.blit(text, (15+x_d, 45+y_d)) #

        if player_inventory.get_amount_of_type(weapon.__dict__["ammo"]) < clip_size:
            color = [255,0,0]
        else:
            color = [255,255,255]

        text = terminal.render("+" + str(player_inventory.get_amount_of_type(weapon.__dict__["ammo"])) + " res.", False, color)
        screen.blit(text, (110+x_d, 45+y_d)) #

    else:
        text = terminal.render("reloading...", False, [255,255,255])
        screen.blit(text, (15+x_d, 45+y_d)) #

    if weapon.get_semi_auto():
        text = terminal3.render("Semi-Automatic", False, [255,255,255])
        screen.blit(text, (15+x_d, 65+y_d)) #

        text = terminal3.render(str(weapon.__dict__["ammo"]), False, [255,255,255])
        screen.blit(text, (110+x_d, 65+y_d)) #
    else:
        text = terminal3.render("Automatic", False, [255,255,255])
        screen.blit(text, (15+x_d, 65+y_d)) #

        text = terminal3.render(str(weapon.__dict__["ammo"]), False, [255,255,255])
        screen.blit(text, (80+x_d, 65+y_d)) #




        text = terminal3.render(str(weapon.__dict__["_Weapon__bullet_per_min"]) + "RPM", False, [255,255,255])
        screen.blit(text, (150+x_d, 65+y_d)) #



    hp = player_actor.__dict__["hp"]
    bars = round((hp-5)/10)


    sanity = player_actor.__dict__["sanity"]
    bars_s = round((sanity)/10)

    amount, tick = player_actor.get_sanity_change()
    if amount != False:

        if tick >= 60:

            bars_s = round((sanity - (amount*(tick-60)/30))/10)
            print(bars_s)

        text = terminal3.render(str(amount) + "% SANITY REGAINED", False, [255,255,255])
        if 1 < tick <= 10:
            screen.blit(text, (844+x_d + (400/tick) - text.get_rect().size[0], 400 +y_d)) #
        elif 10 < tick <= 60:
            screen.blit(text, (844+x_d - text.get_rect().size[0], 400+y_d)) #
        else:
            screen.blit(text, (844 + 150 - 300/(tick-59)+x_d - text.get_rect().size[0], 400+y_d))



    text = terminal2.render("SANITY", False, [255,255,255])
    screen.blit(text, (844+x_d - text.get_rect().size[0], 412+y_d)) #

    pygame.draw.rect(screen, [255,255,255], [631+x_d,440+y_d,210,30],3)
    for i in range(bars_s):
        pygame.draw.rect(screen, [255,255,255], [818 - i*20+x_d,446+y_d,16,18])


    text = terminal2.render("HP", False, [255,255,255])
    screen.blit(text, (12+x_d, 412+y_d)) #

    pygame.draw.rect(screen, [255,255,255], [15+x_d,440+y_d,210,30],3)
    for i in range(bars):
        pygame.draw.rect(screen, [255,255,255], [22 + i*20+x_d,446+y_d,16,18])



    text = terminal2.render(str(weapon.__dict__["_Weapon__name"]), False, [255,255,255])
    screen.blit(text, (15+x_d, 15+y_d)) #

    player_inventory.draw_inventory(screen, x_d, y_d, mouse_pos, clicked, player_actor.get_pos(), r_click_tick, player_actor)
