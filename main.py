import pygame
import ctypes
import sys
import os
import time
import sqlite3
import datetime as dt
from random import choice

# получаем размер монитора и вводим константы
user32 = ctypes.windll.user32
SCREENSIZE = SCREEN_WIDTH, SCREEN_HEIGHT = user32.GetSystemMetrics(0), \
                                           user32.GetSystemMetrics(1) + 2

pygame.init()
pygame.display.set_caption("Island")

# если не произвести иниц. дисплея здесь, перестанет работать load_image()
screen = pygame.display.set_mode(SCREENSIZE)
HUNGER_EVENT = pygame.USEREVENT + 1
WALK_EVENT = pygame.USEREVENT + 2
FOOD_EVENT = pygame.USEREVENT + 3
final = False
clock = pygame.time.Clock()


def draw_num(screen, num, x, y, font_size, color=pygame.Color('white')):  # функция, чтоб показать увеличение предметов думаю, можно потом заменить
    font = pygame.font.Font(None, font_size)
    text = font.render(num, True, color)
    screen.blit(text, (x, y))


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


# функция завершения работы программы
def terminate():
    pygame.quit()
    sys.exit()


def load_level(filename):
    filename = "saves/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('#')
    return list(map(lambda x: x.ljust(max_width, '#'), level_map))


def win():
    global clock
    time = clock.tick() // 1000
    while True:
        screen.fill(pygame.Color('black'))
        lastsave = LoadLastSaveButton()
        return_to_menu = ReturnToMainMenuButton(
            SCREEN_WIDTH // 2 + 5,
            SCREEN_HEIGHT // 2 + 20,
            die_dialog_sprites)
        die_init_flag = True
        print_text(['ВЫ ПОБЕДИЛИ'], 114,
                   (SCREEN_WIDTH // 2 - 255,
                    SCREEN_HEIGHT // 2 - 200), pygame.Color('white')
                   )
        print_text([f'Итоговое время: {time} секунд'.rjust(2, ' ')], 72,
                   (SCREEN_WIDTH // 2 - 255,
                    SCREEN_HEIGHT // 2 - 50), pygame.Color('white'))
        die_dialog_sprites.draw(screen)
        pygame.display.flip()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('water', x, y)
            elif level[y][x] == '1':
                Tile('huge_sand', x, y)
            elif level[y][x] == 'r':
                ObjectNotSpecial('rock', x, y)
                Tile('huge_sand', x, y)
            elif level[y][x] == 'b':
                ObjectNotSpecial('branch', x, y)
                Tile('huge_sand', x, y)
            elif level[y][x] == '@':
                Tile('huge_sand', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '2':
                Tile('poor_sand', x, y)
            elif level[y][x] == 'c':
                ObjectNotSpecial('coconut', x, y)
                Tile('poor_sand', x, y)
            elif level[y][x] == 'p':
                SpecialObject('palm', x, y)
                if choice([1, 2]) == 1:
                    if map_list[y][x - 1].isdigit():
                        ObjectNotSpecial('coconut', x - 1, y)
                else:
                    if map_list[y][x + 1].isdigit():
                        ObjectNotSpecial('coconut', x + 1, y)
                Tile('huge_sand', x, y)
            elif level[y][x] == 'a':
                ObjectNotSpecial('axe', x, y)
                Tile('huge_sand', x, y)
            elif level[y][x] == 'x':
                ObjectNotSpecial('pickaxe', x, y)
                Tile('huge_sand', x, y)
            elif level[y][x] == 's':
                SpecialObject('cobblestone', x, y)
                Tile('poor_sand', x, y)
            elif level[y][x] == '!':
                Boat(x, y)
                Tile('poor_sand', x, y)

    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def load_game(num): # загрузка сейвоф из бд
    global list_of_item, hp, hunger
    con = sqlite3.connect('saves/saves.db')
    cur = con.cursor()
    content = cur.execute(f"""SELECT * from saves
    WHERE id = {num}""").fetchall()
    map_name = content[0][1] + '.txt'
    list_of_item1 = content[0][2] # если нет предметов, то и мысла дальше нет
    hp = content[0][4]
    hunger = content[0][5]
    if list_of_item1:
        list_of_item1 = [i for i in list_of_item1.split(';')]
        list_of_item_num = content[0][3]
        list_of_item_num = [int(i) for i in list_of_item_num.split(';')]
        for i in range(len(list_of_item1)):
            list_of_item[list_of_item1[i]] = list_of_item_num[i]
    con.close()
    start_game(map_name)


def final_window():
    global list_of_item, final
    run_final = True
    while run_final:
        window_group = pygame.sprite.Group()
        button_group = pygame.sprite.Group()
        ExitGameScreen(window_group)
        ArriveButton(739, 645, button_group)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                button_group.update(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                button_group.update(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    run_final = False
        window_group.draw(screen)
        button_group.draw(screen)
        pygame.display.flip()
        if final:
            window_group.empty()
            button_group.empty()
            run_final = False
            win()


def save_game():
    con = sqlite3.connect('saves/saves.db')
    cur = con.cursor()
    num = cur.execute(f"""SELECT id FROM saves""").fetchall()
    if not num:
        num = 1
    else:
        num = num[-1][0] + 1
    if num > 5:
        con.close()
        print('nado dobavit uvedomlenie')
        return
    now = dt.datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    with open(f'saves/map_save{num}.txt', 'w', encoding='utf-8') as file: # нужно для переписывания карты
        for i in range(len(map_list)):
            for j in map_list[i]:
                file.write(j)
            if i != len(map_list) - 1:
                file.write('\n')
        file.close()
    inventory = ';'.join(i for i in list_of_item.keys())
    num_of_things = ';'.join(str(i) for i in list_of_item.values())
    cur.execute(f"""INSERT INTO saves VALUES(?, ?, ?, ?, ?, ?, ?)""",
                (num, f'map_save{num}', inventory, num_of_things, hp, hunger, dt_string)).fetchall()
    con.commit()
    con.close()


def start_game(map_name):
    global list_of_item, hp, hunger
    reserve = tiles_group
    player, level_x, level_y = generate_level(load_level(map_name))
    start_x, start_y = player.pos_x, player.pos_y
    stats, inventory = Stats(), Inventory()
    stats.hp, stats.hunger = hp, hunger
    stats.update(0)
    list_of_item = dict()
    inventory_group.update()
    HE_speed = 2000
    pygame.time.set_timer(HUNGER_EVENT, HE_speed)
    pygame.time.set_timer(WALK_EVENT, 200)
    player_group.draw(screen)

    go = False
    craft_init_flag = False
    die_init_flag = False
    pause_init_flag = False
    game_is_running = True
    while_is_true = True
    camera = Camera()

    # изменяем ракурс камеры
    for sprite in tiles_group:
        camera.apply_y(sprite)
    for sprite in object_group:
        camera.apply_x(sprite)
    while while_is_true:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                die_dialog_sprites.update(event)
                pause_menu_sprites.update(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                die_dialog_sprites.update(event)
                pause_menu_sprites.update(event)
                craft_sprites.update(event)
                if event.button == 3:
                    inventory_group.update(event.pos)
                if pause_init_flag and save_game_button.is_clicked():
                    hp, hunger = stats.hp, stats.hunger
                    map_list[start_y][start_x] = f'{choice([1, 2])}'
                    map_list[player.pos_y][player.pos_x] = '@'
                    save_game()
                    print_text(["Игра успешно сохранена"], 32, (5, 5), (0, 0, 255))
                if (die_init_flag or pause_init_flag) and return_to_menu.is_clicked():
                    while_is_true = False
                    tiles_group.empty()
                    all_sprites.empty()
                    player_group.empty()
                    object_group.empty()
                    interface_group.empty()
                    inventory_group.empty()
                    die_dialog_sprites.empty()
                    pause_menu_sprites.empty()
                    main_screen_init()
                if pause_init_flag and return_to_game.is_clicked():
                    pygame.time.set_timer(HUNGER_EVENT, HE_speed)
                    pygame.time.set_timer(WALK_EVENT, 200)
                    pause_init_flag = False
                    game_is_running = True
                    pause_menu_sprites.empty()
                if craft_init_flag and pickaxe.is_clicked():
                    can_make = all([(elem[:-2] in list(list_of_item.keys()) and int(elem[-1]) <= list_of_item.get(elem[:-2])) for elem in crafting.get('pickaxe')])
                    if can_make:
                        print_text(["Предмет успешно создан: кирка"], 32, (5, 5), (0, 0, 255))
                        for elem in crafting.get('pickaxe'):
                            name, quantity = elem.split(':')
                            list_of_item[name] -= int(quantity)
                        inventory_group.update()
                        list_of_item['pickaxe'] = 10 if 'pickaxe' not in list(list_of_item.keys()) else list_of_item['pickaxe'] + 10
                    else:
                        print_text(["Недостаточно ресурсов!", "Нужно: 2 ветки, 2 камня"], 32, (5, 5), (255, 0, 0), 40)
                if craft_init_flag and axe.is_clicked():
                    can_make = all([(elem[:-2] in list(list_of_item.keys()) and int(elem[-1]) <= list_of_item.get(elem[:-2])) for elem in crafting.get('axe')])
                    if can_make:
                        print_text(["Предмет успешно создан: топор"], 32, (5, 5), (0, 0, 255))
                        for elem in crafting.get('axe'):
                            name, quantity = elem.split(':')
                            list_of_item[name] -= int(quantity)
                        inventory_group.update()
                        list_of_item['axe'] = 10 if 'axe' not in list(list_of_item.keys()) else list_of_item['axe'] + 10
                    else:
                        print_text(["Недостаточно ресурсов!", "Нужно: 2 ветки, 1 камень"], 32, (5, 5), (255, 0, 0), 40)
                if craft_init_flag and paddle.is_clicked():
                    can_make = all([(elem[:-2] in list(list_of_item.keys()) and int(elem[-1]) <= list_of_item.get(elem[:-2])) for elem in crafting.get('paddle')])
                    if can_make:
                        print_text(["Предмет успешно создан: весло"], 32, (5, 5), (0, 0, 255))
                        for elem in crafting.get('paddle'):
                            name, quantity = elem.split(':')
                            list_of_item[name] -= int(quantity)
                        inventory_group.update()
                        list_of_item['paddle'] = 10 if 'paddle' not in list(list_of_item.keys()) else list_of_item['paddle'] + 10
                    else:
                        print_text(["Недостаточно ресурсов!", "Нужно: 2 ветки, 2 бревна"], 32, (5, 5), (255, 0, 0), 40)

            if event.type == HUNGER_EVENT:
                stats.update(-1)
                # код ниже запускает диалог, если персонаж умирает
                if stats.current_hp() <= 0:
                    die_init_flag = True
                    game_is_running = False
                    pygame.time.set_timer(HUNGER_EVENT, 0)
                    pygame.time.set_timer(WALK_EVENT, 0)

                    screen.fill('#4e1818')
                    load_last_save = LoadLastSaveButton()
                    return_to_menu = ReturnToMainMenuButton()
                    print_text(["Вы погибли"], 38, (SCREEN_WIDTH // 2 - 255, SCREEN_HEIGHT // 2 - 50), '#efdfbb')
                    die_dialog_sprites.draw(screen)
            if event.type == WALK_EVENT:
                go = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    terminate()
                # код ниже запускает меню паузы
                if event.key == pygame.K_ESCAPE and not die_init_flag and not craft_init_flag and not pause_init_flag:
                    pause_init_flag = True
                    game_is_running = False
                    pygame.time.set_timer(HUNGER_EVENT, 0)
                    pygame.time.set_timer(WALK_EVENT, 0)

                    screen.fill('#7a0c72', (SCREEN_WIDTH // 2 - 270, SCREEN_HEIGHT // 2 - 105, 540, 310))
                    screen.fill('#8c92ac', (SCREEN_WIDTH // 2 - 265, SCREEN_HEIGHT // 2 - 100, 530, 300))

                    return_to_game = ReturnToGameButton()
                    return_to_menu = ReturnToMainMenuButton()
                    save_game_button = SaveGameButton()

                    print_text(["ПАУЗА".rjust(25, ' ')], 52, (SCREEN_WIDTH // 2 - 255, SCREEN_HEIGHT // 2 - 50), '#efdfbb')
                    pause_menu_sprites.draw(screen)
                if event.key == pygame.K_SPACE:
                    object_group_not_special.update(player.pos_x, player.pos_y)
                    special_object_group.update(player.pos_x, player.pos_y)
                if event.key == pygame.K_b:
                    if player.pos_x == 30 and player.pos_y == 23:
                        print(1)
                        final_window()
                if event.key == pygame.K_9:  # кнопка сохранения
                    hp, hunger = stats.hp, stats.hunger
                    map_list[start_y][start_x] = f'{choice([1, 2])}'
                    map_list[player.pos_y][player.pos_x] = '@'
                    save_game()
                if event.key == pygame.K_e and not die_init_flag and not pause_init_flag:
                    if not craft_init_flag:
                        pygame.time.set_timer(HUNGER_EVENT, 0)
                        pygame.time.set_timer(WALK_EVENT, 0)
                        game_is_running = False
                        craft_init_flag = True

                        screen.blit(load_image('craft.png', -1), (0, 0))

                        pickaxe = CraftingSprite('pickaxe')
                        axe = CraftingSprite('axe')
                        paddle = CraftingSprite('paddle')

                        craft_sprites.draw(screen)
                    else:
                        pygame.time.set_timer(HUNGER_EVENT, HE_speed)
                        pygame.time.set_timer(WALK_EVENT, 200)
                        game_is_running = True
                        craft_init_flag = False
                        craft_sprites.empty()
        if go:
            if pygame.key.get_pressed()[pygame.K_w]:
                if map_list[player.pos_y - 1][player.pos_x] != '#':
                    player.rect.y -= 50
                    player.pos_y -= 1
                    player.update('w')
            if pygame.key.get_pressed()[pygame.K_s]:
                if map_list[player.pos_y + 1][player.pos_x] != '#':
                    player.pos_y += 1
                    player.rect.y += 50
                    player.update('s')
            if pygame.key.get_pressed()[pygame.K_a]:
                if map_list[player.pos_y][player.pos_x - 1] != '#':
                    player.rect.x -= 50
                    player.pos_x -= 1
                    player.update('a')
            if pygame.key.get_pressed()[pygame.K_d]:
                if map_list[player.pos_y][player.pos_x + 1] != '#':
                    player.rect.x += 50
                    player.pos_x += 1
                    player.update('d')
            go = False
        camera.update(player)
        for sprite in all_sprites:
            camera.apply_x(sprite)
            camera.apply_y(sprite)
        camera.dx = 0
        camera.dy = 0
        if game_is_running:
            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            all_sprites.draw(screen)
            player_group.draw(screen)
            object_group.draw(screen)
            interface_group.draw(screen)
            inventory_group.draw(screen)
        pygame.display.flip()


"""--------------------------ВНУТРЕННОСТИ--ИГРЫ-----------------------------"""


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply_x(self, obj):
        obj.rect.x += self.dx

    def apply_y(self, obj):
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - SCREEN_WIDTH // 2) + 30
        self.dy = -(target.rect.y + target.rect.h // 2 - SCREEN_HEIGHT // 2) + 189


class Boat(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, object_group)
        self.image = load_image('boat.png', -1)
        self.image = pygame.transform.scale(self.image, (250, 150))
        self.pos_x = x
        self.pos_y = y
        print(x, y)
        self.rect = self.image.get_rect().move(
            tile_width * self.pos_x, tile_height * self.pos_y)


class Stats(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(interface_group)
        self.image = load_image('stat.png', -1)
        self.hp, self.hunger = 1, 1
        draw_num(self.image, str(self.hp), 1673, 160, 30)
        draw_num(self.image, str(self.hunger), 1823, 160, 30)
        self.rect = self.image.get_rect()

    def current_hp(self):
        return self.hp

    def update(self, num):
        self.image = load_image('stat.png', -1)
        self.hunger += num
        if self.hunger > 100:
            self.hp += self.hunger - 100
            if self.hp > 100:
                self.hp = 100
            self.hunger = 100
        elif self.hunger < 0:
            self.hp += self.hunger
            self.hunger = 0
        if self.hp <= 25:
            draw_num(self.image, str(self.hp), 1639, 140, 35,
                     pygame.Color('red'))
        else:
            draw_num(self.image, str(self.hp), 1639, 140, 35)
        if self.hunger <= 25:
            draw_num(self.image, str(self.hunger), 1789, 140, 35,
                     pygame.Color('red'))
        else:
            draw_num(self.image, str(self.hunger), 1789, 140, 35)
        self.image = pygame.transform.scale(self.image,
                                            (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.rect = self.image.get_rect()


class Palma(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites, special_object_group, palm_group, object_group)
        self.image = tile_images[tile_type]
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = self.image.get_rect().move(
            tile_width * self.pos_x, tile_height * self.pos_y)


class SpecialObject(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(special_object_group, object_group, all_sprites)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def update(self, *args):
        for i in Hand.keys():
            if i == 'axe' and self.tile_type == 'palm':
                if self.pos_x == args[0] and self.pos_y == args[1] - 1:
                    map_list[self.pos_y][self.pos_x] = '2'
                    if 'wood' in list_of_item.keys():  # добавление предмета идёт с проверкой есть ли он в списке
                        list_of_item['wood'] += 3
                    else:
                        list_of_item['wood'] = 3
                    Hand[i] -= 3
                    self.kill()
                    if Hand[i] <= 0:
                        del Hand[i]
                        break

            elif i == 'pickaxe' and self.tile_type == 'cobblestone':
                if self.pos_x == args[0] and self.pos_y == args[1]:
                    map_list[self.pos_y][self.pos_x] = '2'
                    if 'stone' in list_of_item.keys():  # добавление предмета идёт с проверкой есть ли он в списке
                        list_of_item['stone'] += 3
                    else:
                        list_of_item['stone'] = 3
                    Hand[i] -= 3
                    self.kill()
                    if Hand[i] <= 0:
                        del Hand[i]
                        break

        inventory_group.update()


class Inventory(pygame.sprite.Sprite):  # класс инвентаря( нижней полоски)
    """ классе инвенторя будут в словаре храниться предметы
    при получении нового предмета просто будет перерисовываться инвентарь
    добавить синхнонизацию по размеру экрана"""
    image = load_image('inventory.png', -1)

    def __init__(self):
        super().__init__(inventory_group)
        self.image = Inventory.image
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.rect = self.image.get_rect()
        self.inventory = list_of_item
        self.hand = Hand

    def update(self, *args):
        global Hand, list_of_item
        self.image = load_image('inventory.png', -1)
        self.inventory = list_of_item
        self.hand = Hand
        n = 0
        for i in self.hand.keys():
            item_image = load_image(i + '.png', -1)
            item_image = pygame.transform.scale(item_image, (50, 50))
            draw_num(item_image, str(self.hand[i]), 35, 35, 25)
            self.image.blit(item_image, (1134, 1022))
        for i in self.inventory.keys():
            item_image = load_image(i + '.png', -1)
            item_image = pygame.transform.scale(item_image, (50, 50))
            draw_num(item_image, str(self.inventory[i]), 35, 35, 25)
            self.image.blit(item_image, (255 + 90 * n, 1022))
            n += 1
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.rect = self.image.get_rect()
        if args:
            if self.rect.collidepoint(args[0][0] * (1920 // SCREEN_HEIGHT), args[0][1] * (1080 // SCREEN_WIDTH)):
                x = args[0][0] * (1920 // SCREEN_HEIGHT)
                y = args[0][1] # * (1080 // SCREEN_WIDTH)
                c = 0
                for i in self.inventory.keys():
                    if 254 + 90 * c <= x <= 304 + 90 * c and 1022 <= y <= 1072:
                        if i == 'coconut':
                            interface_group.update(5)
                            list_of_item[i] -= 1
                            if list_of_item[i] == 0:
                                del list_of_item[i]
                                inventory_group.update()
                                break
                        if i == 'axe':
                            if self.hand:
                                list_of_item['pickaxe'] = Hand['pickaxe']
                                del Hand['pickaxe']
                            Hand['axe'] = list_of_item['axe']
                            del list_of_item[i]
                            break
                        if i == 'pickaxe':
                            if self.hand:
                                list_of_item['axe'] = Hand['axe']
                                del Hand['axe']
                            Hand['pickaxe'] = list_of_item['pickaxe']
                            del list_of_item[i]
                            break
                    c += 1
                inventory_group.update()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.pos_x = pos_x
        self.pos_y = pos_y


class ObjectNotSpecial(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(object_group_not_special, object_group, all_sprites)
        self.image = tile_images[tile_type]
        if tile_type == 'pickaxe' or tile_type == 'axe':
            self.image = pygame.transform.rotate(self.image, choice(range(181)))
            self.image = pygame.transform.scale(self.image, (35, 35))
        self.tile_type = tile_type
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def update(self, *args):
        if self.pos_x == args[0] and self.pos_y == args[1]:
            map_list[self.pos_y][self.pos_x] = '1'
            if self.tile_type in list_of_item.keys():  # добавление предмета идёт с проверкой есть ли он в списке
                list_of_item[self.tile_type] += 1
            else:
                if self.tile_type == 'axe' or self.tile_type == 'pickaxe':
                    list_of_item[self.tile_type] = 10
                else:
                    list_of_item[self.tile_type] = 1
            inventory_group.update()
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image['s']
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y - 10)
        self.pos_x = pos_x
        self.pos_y = pos_y

    def update(self, *args):
        self.image = player_image[args[0]]


"""-------------------------------------------------------------------------"""

"""------------------------------КНОПКИ-------------------------------------"""


class ExitGameScreen(pygame.sprite.Sprite):
    image = load_image('end_screen.png', -1)

    def __init__(self, *group):
        super().__init__(*group)
        self.image = ExitGameScreen.image
        self.rect = self.image.get_rect()


class ArriveButton(pygame.sprite.Sprite):
    image = load_image('arrive.png')
    active_image = load_image('arrive_active.png')

    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = pygame.transform.scale(ArriveButton.image, (250, 70))
        self.rect = self.image.get_rect().move(x, y)
        self.pos_x, self.pos_y = x, y
        self.needs = {
            'coconut': 10,
            'rock': 15,
            'branch': 10,
            'wood': 20,
            'stone': 15,
            'axe': 1
        }

    def update(self, *args):
        global list_of_item, final
        if args and args[0].type == pygame.MOUSEMOTION and \
                self.rect.collidepoint(args[0].pos):
            self.image = self.active_image
        elif args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            self.image = pygame.transform.scale(self.image, (250, 70))
            for i in self.needs.keys():
                if i in list_of_item.keys():
                    if list_of_item[i] < self.needs[i]:
                        break
            screen.fill((0, 0, 0))
            final = True
        self.image = pygame.transform.scale(self.image, (250, 70))


# материнский класс для кнопок в главном меню (и кнопка "Новая игра")
class NewGameTablet(pygame.sprite.Sprite):
    image = load_image('new_game_tablet.png')
    active_image = load_image('new_game_active_tablet.png')

    def __init__(self, pos_x, pos_y):
        super().__init__(tablet_sprites)
        self.image = pygame.transform.scale(NewGameTablet.image, (280, 100))
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.col_flag = False

    def tablet_moving(self, args):
        if not self.col_flag and self.rect.collidepoint(args[0].pos):
            screen.fill('#99D9EA', self.rect)
            self.rect.x = self.pos_x + 10
            self.col_flag = True
            self.image = pygame.transform.scale(NewGameTablet.active_image,
                                                (280, 100))
            tablet_sprites.draw(screen)
        elif self.col_flag and not self.rect.collidepoint(args[0].pos):
            screen.fill('#99D9EA', self.rect)
            self.rect.x = self.pos_x
            self.col_flag = False
            self.image = pygame.transform.scale(NewGameTablet.image, (280, 100))
            tablet_sprites.draw(screen)

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                tablet_sprites.empty()
                music_switch_sprite.empty()
                new_game_dialog_init()


class ContinueTablet(pygame.sprite.Sprite):
    image = load_image('continue_tablet.png')
    active_image = load_image('continue_active_tablet.png')

    def __init__(self, pos_x, pos_y):
        super().__init__(tablet_sprites)
        self.image = pygame.transform.scale(ContinueTablet.image, (280, 100))
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.col_flag = False

    def tablet_moving(self, args):
        if not self.col_flag and self.rect.collidepoint(args[0].pos):
            screen.fill('#99D9EA', self.rect)
            self.rect.x = self.pos_x + 10
            self.col_flag = True
            self.image = pygame.transform.scale(ContinueTablet.active_image,
                                                (280, 100))
            tablet_sprites.draw(screen)
        elif self.col_flag and not self.rect.collidepoint(args[0].pos):
            screen.fill('#99D9EA', self.rect)
            self.rect.x = self.pos_x
            self.col_flag = False
            self.image = pygame.transform.scale(ContinueTablet.image,
                                                (280, 100))
            tablet_sprites.draw(screen)

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                tablet_sprites.empty()
                loading_screen()
                con = sqlite3.connect('saves/saves.db')
                cur = con.cursor()
                num = cur.execute("""SELECT id FROM saves""").fetchall()
                if not num:
                    start_game('map.txt')
                else:
                    num = num[-1][0]
                    load_game(num)


class ExitTablet(pygame.sprite.Sprite):
    image = load_image('exit_tablet.png')
    active_image = load_image('exit_active_tablet.png')

    def __init__(self, pos_x, pos_y):
        super().__init__(tablet_sprites)
        self.image = pygame.transform.scale(ExitTablet.image, (280, 100))
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.col_flag = False

    def tablet_moving(self, args):
        if not self.col_flag and self.rect.collidepoint(args[0].pos):
            screen.fill('#99D9EA', self.rect)
            self.rect.x = self.pos_x + 10
            self.col_flag = True
            self.image = pygame.transform.scale(ExitTablet.active_image,
                                                (280, 100))
            tablet_sprites.draw(screen)
        elif self.col_flag and not self.rect.collidepoint(args[0].pos):
            screen.fill('#99D9EA', self.rect)
            self.rect.x = self.pos_x
            self.col_flag = False
            self.image = pygame.transform.scale(ExitTablet.image, (280, 100))
            tablet_sprites.draw(screen)

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                tablet_sprites.empty()
                music_switch_sprite.empty()
                exit_dialog_init()


"""-------------------------------------------------------------------------"""

"""-----------------------КНОПКИ--МЕНЮ--ПАУЗЫ-------------------------------"""


class ReturnToGameButton(pygame.sprite.Sprite):
    image = load_image('return_to_game_button.png')
    active_image = load_image('return_to_game_active_button.png')

    def __init__(self):
        super().__init__(pause_menu_sprites)
        self.image = pygame.transform.scale(ReturnToGameButton.image,
                                            (250, 70))
        self.rect = self.image.get_rect().move(SCREEN_WIDTH // 2 - 255,
                                               SCREEN_HEIGHT // 2 + 20)
        self.col_flag = False
        self.clicked_flag = False

    def tablet_moving(self, args):
        if not self.col_flag and self.rect.collidepoint(args[0].pos):
            self.col_flag = True
            self.image = pygame.transform.scale(ReturnToGameButton.active_image, (250, 70))
            pause_menu_sprites.draw(screen)
        elif self.col_flag and not self.rect.collidepoint(args[0].pos):
            self.col_flag = False
            self.image = pygame.transform.scale(ReturnToGameButton.image, (250, 70))
            pause_menu_sprites.draw(screen)

    def is_clicked(self):
        return self.clicked_flag

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                pause_menu_sprites.empty()
                self.clicked_flag = True


# после смерти кнопка "выйти в главное меню"
class ReturnToMainMenuButton(pygame.sprite.Sprite):
    image = load_image('return_to_main_menu_button.png')
    active_image = load_image('return_to_main_menu_active_button.png')

    def __init__(self):
        super().__init__(pause_menu_sprites, die_dialog_sprites)
        self.image = pygame.transform.scale(ReturnToMainMenuButton.image,
                                            (250, 70))
        self.rect = self.image.get_rect().move(SCREEN_WIDTH // 2 + 5,
                                               SCREEN_HEIGHT // 2 + 20)
        self.col_flag = False
        self.clicked_flag = False

    def tablet_moving(self, args):
        if not self.col_flag and self.rect.collidepoint(args[0].pos):
            self.col_flag = True
            self.image = pygame.transform.scale(ReturnToMainMenuButton.active_image, (250, 70))
            pause_menu_sprites.draw(screen)
        elif self.col_flag and not self.rect.collidepoint(args[0].pos):
            self.col_flag = False
            self.image = pygame.transform.scale(ReturnToMainMenuButton.image, (250, 70))
            pause_menu_sprites.draw(screen)

    def is_clicked(self):
        return self.clicked_flag

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                self.clicked_flag = True
                pause_menu_sprites.empty()


class SaveGameButton(pygame.sprite.Sprite):
    image = load_image('save_game_button.png')
    active_image = load_image('save_game_active_button.png')

    def __init__(self):
        super().__init__(pause_menu_sprites)
        self.image = pygame.transform.scale(SaveGameButton.image, (250, 70))
        self.rect = self.image.get_rect().move(SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2 + 100)
        self.col_flag = False
        self.clicked_flag = False

    def is_clicked(self):
        return self.clicked_flag

    def tablet_moving(self, args):
        if not self.col_flag and self.rect.collidepoint(args[0].pos):
            self.col_flag = True
            self.image = pygame.transform.scale(SaveGameButton.active_image, (250, 70))
            pause_menu_sprites.draw(screen)
        elif self.col_flag and not self.rect.collidepoint(args[0].pos):
            self.col_flag = False
            self.image = pygame.transform.scale(SaveGameButton.image,
                                                (250, 70))
            pause_menu_sprites.draw(screen)

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                self.clicked_flag = True


# после смерти кнопка "загрузить последнее сохранение"
class LoadLastSaveButton(pygame.sprite.Sprite):
    image = load_image('load_last_save_button.png')
    active_image = load_image('load_last_save_active_button.png')

    def __init__(self):
        super().__init__(die_dialog_sprites)
        self.image = pygame.transform.scale(LoadLastSaveButton.image, (250, 70))
        self.rect = self.image.get_rect().move(SCREEN_WIDTH // 2 - 255,
                                               SCREEN_HEIGHT // 2 + 20)
        self.col_flag = False

    def tablet_moving(self, args):
        if not self.col_flag and self.rect.collidepoint(args[0].pos):
            self.col_flag = True
            self.image = pygame.transform.scale(LoadLastSaveButton.active_image,
                                                (250, 70))
            die_dialog_sprites.draw(screen)
        elif self.col_flag and not self.rect.collidepoint(args[0].pos):
            self.col_flag = False
            self.image = pygame.transform.scale(LoadLastSaveButton.image,
                                                (250, 70))
            die_dialog_sprites.draw(screen)

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                die_dialog_sprites.empty()
                loading_screen()
                con = sqlite3.connect('saves/saves.db')
                cur = con.cursor()
                num = cur.execute("""SELECT id FROM saves""").fetchall()
                if not num:
                    start_game('map.txt')
                else:
                    num = num[-1][0]
                    load_game(num)


"""-------------------------------------------------------------------------"""

"""---------------------------КНОПКИ-ДИАЛОГОВ-------------------------------"""


# эта кнопка нужна в диалоговом окне перед выходом, чтобы подтвердить выход
class YesExitButton(pygame.sprite.Sprite):
    image = load_image('yes_button.png')
    active_image = load_image('yes_active_button.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.transform.scale(YesExitButton.image, (250, 70))
        self.rect = self.image.get_rect().move(SCREEN_WIDTH // 2 - 255,
                                               SCREEN_HEIGHT // 2 + 20)
        self.col_flag = False

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                if self.rect.collidepoint(args[0].pos) and not self.col_flag:
                    self.col_flag = True
                    self.image = pygame.transform.scale(
                        YesExitButton.active_image, (250, 70))
                    exit_yesno_sprites.draw(screen)
                elif not self.rect.collidepoint(args[0].pos) and self.col_flag:
                    self.col_flag = False
                    self.image = pygame.transform.scale(YesExitButton.image,
                                                        (250, 70))
                    exit_yesno_sprites.draw(screen)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                time.sleep(0.5)
                terminate()


# эта кнопка нужна в диалоговом окне перед выходом, чтобы отменить выход
class NoExitButton(pygame.sprite.Sprite):
    image = load_image('no_button.png')
    active_image = load_image('no_active_button.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.transform.scale(NoExitButton.image, (250, 70))
        self.rect = self.image.get_rect().move(SCREEN_WIDTH // 2 + 5,
                                               SCREEN_HEIGHT // 2 + 20)
        self.col_flag = False

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                if self.rect.collidepoint(args[0].pos) and not self.col_flag:
                    self.col_flag = True
                    self.image = pygame.transform.scale(
                        NoExitButton.active_image, (250, 70))
                    exit_yesno_sprites.draw(screen)
                elif not self.rect.collidepoint(args[0].pos) and self.col_flag:
                    self.col_flag = False
                    self.image = pygame.transform.scale(NoExitButton.image,
                                                        (250, 70))
                    exit_yesno_sprites.draw(screen)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                for elem in self.groups():
                    elem.empty()
                main_screen_init()


class YesNewGameButton(pygame.sprite.Sprite):
    image = load_image('yes_button.png')
    active_image = load_image('yes_active_button.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.transform.scale(YesNewGameButton.image, (250, 70))
        self.rect = self.image.get_rect().move(SCREEN_WIDTH // 2 - 255,
                                               SCREEN_HEIGHT // 2 + 20)
        self.col_flag = False

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                if self.rect.collidepoint(args[0].pos) and not self.col_flag:
                    self.col_flag = True
                    self.image = pygame.transform.scale(
                        YesNewGameButton.active_image, (250, 70))
                    new_game_yesno_sprites.draw(screen)
                elif not self.rect.collidepoint(args[0].pos) and self.col_flag:
                    self.col_flag = False
                    self.image = pygame.transform.scale(YesNewGameButton.image,
                                                        (250, 70))
                    new_game_yesno_sprites.draw(screen)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                for elem in self.groups():
                    elem.empty()
                loading_screen()
                start_game('map.txt')


class NoNewGameButton(pygame.sprite.Sprite):
    image = load_image('no_button.png')
    active_image = load_image('no_active_button.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.transform.scale(NoNewGameButton.image, (250, 70))
        self.rect = self.image.get_rect().move(SCREEN_WIDTH // 2 + 5,
                                               SCREEN_HEIGHT // 2 + 20)
        self.col_flag = False

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                if self.rect.collidepoint(args[0].pos) and not self.col_flag:
                    self.col_flag = True
                    self.image = pygame.transform.scale(
                        NoNewGameButton.active_image, (250, 70))
                    new_game_yesno_sprites.draw(screen)
                elif not self.rect.collidepoint(args[0].pos) and self.col_flag:
                    self.col_flag = False
                    self.image = pygame.transform.scale(NoNewGameButton.image,
                                                        (250, 70))
                    new_game_yesno_sprites.draw(screen)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                for elem in self.groups():
                    elem.empty()
                main_screen_init()


# выключатель музыки главного меню в разделе "настройки"
class MusicSwitchButton(pygame.sprite.Sprite):
    musicOn = load_image('music_on_button.png')
    musicOff = load_image('music_off_button.png')

    def __init__(self, *group):
        super().__init__(*group)
        if pygame.mixer.music.get_busy():
            self.image = pygame.transform.scale(MusicSwitchButton.musicOn,
                                                (50, 50))
        else:
            self.image = pygame.transform.scale(MusicSwitchButton.musicOff,
                                                (50, 50))
        self.rect = self.image.get_rect().move((20, SCREEN_HEIGHT // 3 + 400))
        print_text(["Включить/выключить шум моря"], 52, (80, SCREEN_HEIGHT // 3 + 400), (0, 0, 0))

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                if pygame.mixer.music.get_busy():
                    self.image = pygame.transform.scale(
                        MusicSwitchButton.musicOff, (50, 50))
                    music_switch_sprite.draw(screen)
                    pygame.mixer.music.pause()
                elif not pygame.mixer.music.get_busy():
                    self.image = pygame.transform.scale(
                        MusicSwitchButton.musicOn, (50, 50))
                    music_switch_sprite.draw(screen)
                    pygame.mixer.music.unpause()


class CraftingSprite(pygame.sprite.Sprite):
    image = load_image('img.png')

    def __init__(self, type):
        super().__init__(craft_sprites)
        self.clicked_flag = False
        if type == 'pickaxe':
            self.image = pygame.transform.scale(load_image('pickaxe.png', -1), (250, 250))
            self.rect = self.image.get_rect().move((366, 449))
        elif type == 'axe':
            self.image = pygame.transform.scale(load_image('axe.png', -1), (250, 250))
            self.rect = self.image.get_rect().move((837, 449))
        elif type == 'paddle':
            self.image = pygame.transform.scale(load_image('paddle.png', -1), (250, 250))
            self.rect = self.image.get_rect().move((1306, 449))

    def is_clicked(self):
        return self.clicked_flag

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                self.clicked_flag = True


"""-------------------------------------------------------------------------"""


# функция для выведения текста на экран
def print_text(text, font_point, first_line_pos, text_color, line_space=0):
    font = pygame.font.Font(None, font_point)
    temp = first_line_pos[1]
    for line in text:
        line_rendered = font.render(line, True, text_color)
        line_rect = line_rendered.get_rect()
        line_rect.x = first_line_pos[0]
        temp += line_space
        line_rect.top = temp
        screen.blit(line_rendered, line_rect)


# эта функция загружает диалоговое окно перед выходом из игры
def exit_dialog_init():
    screen.blit(background_picture, (0, 0))
    screen.fill('#7a0c72', (SCREEN_WIDTH // 2 - 270, SCREEN_HEIGHT // 2 - 105,
                            540, 210))
    screen.fill('#8c92ac', (SCREEN_WIDTH // 2 - 265, SCREEN_HEIGHT // 2 - 100,
                            530, 200))
    exit_yesno_sprites.add(YesExitButton())
    exit_yesno_sprites.add(NoExitButton())
    print_text(["Вы уверены, что хотите покинуть игру?"], 38,
               (SCREEN_WIDTH // 2 - 255, SCREEN_HEIGHT // 2 - 50), '#efdfbb')
    exit_yesno_sprites.draw(screen)


# эта функция загружает диалоговое окно перед началом новой игры
def new_game_dialog_init():
    screen.blit(background_picture, (0, 0))
    screen.fill('#7a0c72', (SCREEN_WIDTH // 2 - 270, SCREEN_HEIGHT // 2 - 105,
                            540, 210))
    screen.fill('#8c92ac', (SCREEN_WIDTH // 2 - 265, SCREEN_HEIGHT // 2 - 100,
                            530, 200))
    new_game_yesno_sprites.add(YesNewGameButton())
    new_game_yesno_sprites.add(NoNewGameButton())
    print_text(["Вы уверены, что хотите начать".rjust(37, ' '),
                "новую игру?".rjust(37, ' ')], 38,
               (SCREEN_WIDTH // 2 - 255, SCREEN_HEIGHT // 2 - 110), '#efdfbb',
               40)
    new_game_yesno_sprites.draw(screen)


# эта функция загружает главный экран
def main_screen_init():
    screen.blit(background_picture, (0, 0))
    screen.blit(load_image('title.png', -1), (0, -40))

    # инициализация кнопок главного меню
    start_point = SCREEN_HEIGHT // 3
    new_tablet = NewGameTablet(20, start_point)
    continue_tablet = ContinueTablet(20, start_point + 110)
    exit_tablet = ExitTablet(20, start_point + 220)
    music_switch_sprite.add(MusicSwitchButton())
    music_switch_sprite.draw(screen)
    tablet_sprites.draw(screen)


def loading_screen():
    screen.blit(load_image('loading_screen.png'), (0, 1))
    pygame.display.flip()
    time.sleep(1)


if __name__ == '__main__':
    background_picture = pygame.transform.scale(load_image(
        'background_image.png'), SCREENSIZE)

    tile_images = {
        # 'huge_sand': load_image('sand.png'),
        'huge_sand': pygame.transform.scale(load_image('test_sand1.png'), (50, 50)),
        # 'water': load_image('ocean.png'),
        'water': pygame.transform.scale(load_image('test_water.png'), (50, 50)),
        'rock': load_image('rock.png', -1),
        'branch': load_image('branch.png', -1),
        # 'poor_sand': load_image('poor_sand.png'),
        'poor_sand': pygame.transform.scale(load_image('test_sand2.png'), (50, 50)),
        'coconut': load_image('coconut.png', -1),
        'palm': load_image('palm.png', -1),
        'ship': load_image('boat.png', -1),
        'axe': load_image('axe.png', -1),
        'pickaxe': load_image('pickaxe.png', -1),
        'cobblestone': load_image('cobblestone.png', -1)
    }

    player_image = {
        'd': load_image('hero_d.png', -1),
        'a': load_image('hero_a.png', -1),
        's': load_image('hero_s.png', -1),
        'w': load_image('hero_w.png', -1)
    }
    boat = pygame.image.load('data/boat.png').convert_alpha()
    tile_width = tile_height = 50

    crafting = {
        'pickaxe': ['branch:2', 'stone:2'],
        'axe': ['branch:2', 'stone:1'],
        'paddle': ['branch:2', 'wood:1']
    }

    player = None
    map_list = load_level('map.txt')
    map_list = [list(i) for i in map_list]
    Hand = dict()
    list_of_item = dict()  # список всех предметов в инвентаря
    hp, hunger = 100, 100

    # группы спрайтов Паши
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()  # группа для песка и воды
    player_group = pygame.sprite.Group()  # игрок
    object_group_not_special = pygame.sprite.Group()  # объекты для которых не нужен предмет
    interface_group = pygame.sprite.Group()  # чтоб было удобнее группа интерфейсов
    inventory_group = pygame.sprite.Group()  # группа отвечающая за инвентарь
    object_group = pygame.sprite.Group()  # здесь хранятся объекты, с которыми можно будет взаимдейстовать
    palm_group = pygame.sprite.Group()
    special_object_group = pygame.sprite.Group()
    # группы спрайтов Даши
    tablet_sprites = pygame.sprite.Group()  # кнопки в меню
    exit_yesno_sprites = pygame.sprite.Group()  # да/нет при выходе из игры
    new_game_yesno_sprites = pygame.sprite.Group()  # да/нет при начале новой игры
    music_switch_sprite = pygame.sprite.Group()  # выключатель музыки
    die_dialog_sprites = pygame.sprite.Group()  # кнопки для диалога загрузки после смерти
    pause_menu_sprites = pygame.sprite.Group()  # кнопки в меню паузы
    craft_sprites = pygame.sprite.Group()  # кнопки в меню крафта

    pygame.mixer.init()
    pygame.mixer.music.load('data/main_menu_sound.mp3')
    pygame.mixer.music.play(loops=-1)
    click_sound = pygame.mixer.Sound('data/click_sound.mp3')

    main_screen_init()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    terminate()
            elif event.type == pygame.QUIT:
                terminate()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                tablet_sprites.update(event)
                exit_yesno_sprites.update(event)
                new_game_yesno_sprites.update(event)
                music_switch_sprite.update(event)

            elif event.type == pygame.MOUSEMOTION:
                tablet_sprites.update(event)
                exit_yesno_sprites.update(event)
                new_game_yesno_sprites.update(event)

            pygame.display.flip()
