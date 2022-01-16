import pygame
import ctypes
import sys
import os
import time
import sqlite3
import datetime as dt

# получаем размер монитора и вводим константы
user32 = ctypes.windll.user32
SCREENSIZE = SCREEN_WIDTH, SCREEN_HEIGHT = user32.GetSystemMetrics(0), \
                                           user32.GetSystemMetrics(1) + 2
"""SCREENSIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600"""

pygame.init()
pygame.display.set_caption("Island")

pygame.mixer.init()
pygame.mixer.music.load('data/main_menu_sound.mp3')
pygame.mixer.music.play(loops=-1)
pygame.mixer.music.stop()

click_sound = pygame.mixer.Sound('data/click_sound.mp3')

# если не произвести иниц. дисплея здесь, перестанет работать load_image()
screen = pygame.display.set_mode(SCREENSIZE)
HUNGER_EVENT = pygame.USEREVENT + 1
WALK_EVENT = pygame.USEREVENT + 2


def draw_num(screen, num, x, y, color, font_size): # функция, чтоб показать увеличение предметов думаю, можно потом заменить
    font = pygame.font.Font(None, font_size)
    text = font.render(num, True, color)
    text_x = x - text.get_width()
    text_y = y - text.get_height()
    screen.blit(text, (text_x, text_y))


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


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('water', x, y)
            elif level[y][x] == '.':
                Tile('sand', x, y)
            elif level[y][x] == 'r':
                ObjectNotSpecial('rock', x, y)
                Tile('sand', x, y)
            elif level[y][x] == 'b':
                ObjectNotSpecial('branch', x, y)
                Tile('sand', x, y)
            elif level[y][x] == '@':
                Tile('sand', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def load_game(num):  # загрузка сейвоф из бд
    global list_of_item, list_of_item_num, hp, hunger
    con = sqlite3.connect('saves/saves.db')
    cur = con.cursor()
    content = cur.execute(f"""SELECT * from saves
    WHERE id = {num}""").fetchall()
    map_name = content[0][1] + '.txt'
    list_of_item = content[0][2]  # если нет предметов, то и мысла дальше нет
    hp, hunger = content[0][4], content[0][5]
    if list_of_item:
        list_of_item = [i for i in list_of_item.split(';')]
        list_of_item_num = content[0][3]
        list_of_item_num = [int(i) for i in list_of_item_num.split(';')]
        for i in range(len(list_of_item)):
            sup = InventoryItem(list_of_item[i])
            sup.num = list_of_item_num[i]
            sup.update('add', list_of_item[i], 0)
    con.close()
    start_game(map_name)


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
    inventory = ';'.join(i for i in list_of_item)
    num_of_things = ';'.join(str(i) for i in list_of_item_num)
    cur.execute(f"""INSERT INTO saves VALUES(?, ?, ?, ?, ?, ?, ?)""",
                (num, f'map_save{num}', inventory, num_of_things, hp, hunger, dt_string)).fetchall()
    con.commit()
    con.close()


def start_game(map_name):
    global list_of_item, list_of_item_num, hp, hunger

    player, level_x, level_y = generate_level(load_level(map_name))
    start_x, start_y = player.pos_x, player.pos_y
    camera = Camera()  # нужно сделать
    inventory, stats = Inventory(), Stats()
    stats.hp, stats.hunger = hp, hunger
    stats.update(0)

    pygame.time.set_timer(HUNGER_EVENT, 100)  # , 7000)
    pygame.time.set_timer(WALK_EVENT, 200)

    game_is_running = True
    go = False

    while_is_true = True
    while while_is_true:
        """Тут будет обработка нажатий клавиш, уже есть движение"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                die_dialog_sprites.update(event)
                pause_menu_sprites.update(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                die_dialog_sprites.update(event)
                pause_menu_sprites.update(event)
                if returnto.is_clicked():
                    while_is_true = False
            if event.type == HUNGER_EVENT:
                stats.update(-1)
                if stats.current_hp() <= 0:
                    game_is_running = False
                    pygame.time.set_timer(HUNGER_EVENT, 0)
                    pygame.time.set_timer(WALK_EVENT, 0)

                    tiles_group.empty()
                    player_group.empty()
                    object_group_not_special.empty()
                    interface_group.empty()
                    list_of_item_group.empty()
                    object_group.empty()

                    screen.fill('#4e1818')
                    loadsave = LoadLastSave(die_dialog_sprites)
                    returnto = ReturnToMainMenuButton(die_dialog_sprites)
                    print_text(["Вы погибли".rjust(8, " ")], 72,
                               (SCREEN_WIDTH // 2 - 255,
                                SCREEN_HEIGHT // 2 - 50), '#efdfbb')
                    die_dialog_sprites.draw(screen)
            if event.type == WALK_EVENT:
                go = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                if event.key == pygame.K_t:
                    game_is_running = False
                    player_group.empty()
                    object_group_not_special.empty()
                    interface_group.empty()
                    list_of_item_group.empty()
                    object_group.empty()

                    '''screen.fill('#7a0c72', (SCREEN_WIDTH // 2 - 270, 
                                            SCREEN_HEIGHT // 2 - 105,
                                            540, 210))
                    screen.fill('#8c92ac', (SCREEN_WIDTH // 2 - 265, 
                                            SCREEN_HEIGHT // 2 - 100,
                                            530, 200))'''
                    screen.fill('#3aebca')
                    pause_menu_sprites.add(ContinueTablet(10, 50))
                    pause_menu_sprites.add(SettingsTablet(10, 110))
                    pause_menu_sprites.add(HelpTablet(10, 170))
                    pause_menu_sprites.add(ExitTablet(10, 230))
                    print_text(["ПАУЗА"], 72, (SCREEN_WIDTH // 2 - 255,
                                               SCREEN_HEIGHT // 2 - 110),
                               '#efdfbb')
                    pause_menu_sprites.draw(screen)
                if event.key == pygame.K_SPACE:
                    object_group_not_special.update(player.pos_x, player.pos_y)
                if event.key == pygame.K_9:  # кнопка сохранения
                    hp, hunger = stats.hp, stats.hunger
                    map_list[start_y][start_x] = '.'
                    map_list[player.pos_y][player.pos_x] = '@'
                    save_game()
        if go:
            if pygame.key.get_pressed()[pygame.K_w]:
                if map_list[player.pos_y - 1][player.pos_x] != '#':
                    player.pos_y -= 1
            if pygame.key.get_pressed()[pygame.K_s]:
                if map_list[player.pos_y + 1][player.pos_x] != '#':
                    player.pos_y += 1
            if pygame.key.get_pressed()[pygame.K_a]:
                if map_list[player.pos_y][player.pos_x - 1] != '#':
                    player.pos_x -= 1
            if pygame.key.get_pressed()[pygame.K_d]:
                if map_list[player.pos_y][player.pos_x + 1] != '#':
                    player.pos_x += 1
            go = False

        if game_is_running:
            screen.fill((0, 0, 0))
            player_group.update()
            tiles_group.draw(screen)
            object_group.draw(screen)
            player_group.draw(screen)
            interface_group.draw(screen)
            list_of_item_group.draw(screen)
        pygame.display.flip()


"""--------------------------ВНУТРЕННОСТИ--ИГРЫ-----------------------------"""


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - SCREEN_WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - SCREEN_HEIGHT // 2)


class Stats(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(interface_group)
        self.image = load_image('stat.png', -1)
        self.hp, self.hunger = 1, 1
        draw_num(self.image, str(self.hp), 1673, 160, pygame.Color('white'), 35)
        draw_num(self.image, str(self.hunger), 1823, 160, pygame.Color('white'), 35)
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
        elif self.hunger < 0:
            self.hp += self.hunger
            self.hunger = 0
        if self.hp <= 25:
            draw_num(self.image, str(self.hp), 1673, 160, pygame.Color('red'), 35)
        else:
            draw_num(self.image, str(self.hp), 1673, 160, pygame.Color('white'), 35)
        if self.hunger <= 25:
            draw_num(self.image, str(self.hunger), 1823, 160, pygame.Color('red'), 35)
        else:
            draw_num(self.image, str(self.hunger), 1823, 160, pygame.Color('white'), 35)
        self.rect = self.image.get_rect()


class Inventory(pygame.sprite.Sprite):  # класс инвентаря (нижней полоски)
    image = load_image('inventory.png', -1)

    def __init__(self):
        super().__init__(interface_group)
        self.image = Inventory.image
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.rect = self.image.get_rect()


class InventoryItem(pygame.sprite.Sprite):  # предметы в инвентаре
    def __init__(self, tile_type):
        super().__init__(list_of_item_group)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.image = pygame.transform.scale(self.image, (72, 72))
        self.num = 1
        draw_num(self.image, str(self.num), 72, 72, pygame.Color('white'), 40)
        self.rect = self.image.get_rect().move(
            186 + 130 * len(list_of_item), 1000)

    def update(self, fl, tile_type, num):
        if fl == 'add':
            if self.tile_type == tile_type:
                self.image = tile_images[tile_type]
                self.image = pygame.transform.scale(self.image, (72, 72))
                self.rect = self.image.get_rect().move(
                    186 + 130 * list_of_item.index(tile_type), 1000)
                self.num += num
                draw_num(self.image, str(self.num), 72, 72, pygame.Color('white'), 40)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class ObjectNotSpecial(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(object_group_not_special,object_group)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def update(self, *args):
        if self.pos_x == args[0] and self.pos_y == args[1]:
            map_list[self.pos_y][self.pos_x] = '.'
            if self.tile_type in list_of_item:  # добавление предмета идёт с проверкой есть ли он в списке
                list_of_item_group.update('add', self.tile_type, 1)
                list_of_item_num[list_of_item.index(self.tile_type)] += 1
            else:
                InventoryItem(self.tile_type)
                list_of_item.append(self.tile_type)
                list_of_item_num.append(1)
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos_x = pos_x
        self.pos_y = pos_y

    def update(self):
        self.rect = self.image.get_rect().move(
            tile_width * self.pos_x, tile_height * self.pos_y - 5)


"""-------------------------------------------------------------------------"""
"""------------------------------КНОПКИ-------------------------------------"""


# материнский класс для кнопок в главном меню (и кнопка "Новая игра")
class NewGameTablet(pygame.sprite.Sprite):
    image = load_image('new_game_tablet.png')
    active_image = load_image('new_game_active_tablet.png')

    def __init__(self, pos_x, pos_y, *group):
        super().__init__(*group)
        self.image = pygame.transform.scale(NewGameTablet.image, (250, 70))
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.pos_x, self.pos_y = pos_x, pos_y
        """флаг ниже нужен, чтобы программа не проводила отрисовку каждую 
        секунду, пока курсор наведён на кнопку, а отрисовало один раз и 
        больше ничего не делало, пока курсор с кнопки не слетит 
        (см. self.tablet_moving())"""
        self.col_flag = False

    """я решила вынести функцию замены картинки при наведении на кнопку в 
    отдельную функцию, чтобы в дочерних классах менялись только строчки про
    картинки и не приходилось перееопределять полностью self.tablet_moving()"""
    def is_active(self, boolian=False):
        if boolian:
            self.image = pygame.transform.scale(NewGameTablet.active_image,
                                                (250, 70))
        else:
            self.image = pygame.transform.scale(NewGameTablet.image, (250, 70))

    def tablet_moving(self, args):
        """чтобы анимация кнопки работала эффективно, я не обновляю экран,
        а закрашиваю область под новой отрисовкой в цвет фона
        поэтому, прежде чем вставлять другую картинку на фон, убедитесь, что
        область под кнопками однотонная и в screen.fill() указан этот цвет"""
        if not self.col_flag and self.rect.collidepoint(args[0].pos):
            screen.fill('#99D9EA', self.rect)
            self.rect.x = self.pos_x + 10
            self.col_flag = True
            self.is_active(True)
            tablet_sprites.draw(screen)
        elif self.col_flag and not self.rect.collidepoint(args[0].pos):
            screen.fill('#99D9EA', self.rect)
            self.rect.x = self.pos_x
            self.col_flag = False
            self.is_active(False)
            tablet_sprites.draw(screen)

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()  # звук нажатия на кнопку
                """tablet_sprites нужно очищать, так как иначе кнопки этой 
                группы будут невидимыми, но активными"""
                for elem in self.groups():
                    elem.empty()
                new_game_dialog_init()


class ContinueTablet(NewGameTablet):
    image = load_image('continue_tablet.png')
    active_image = load_image('continue_active_tablet.png')

    def __init__(self, pos_x, pos_y, *group):
        super().__init__(pos_x, pos_y, *group)
        self.image = pygame.transform.scale(ContinueTablet.image, (250, 70))

    def is_active(self, boolian=False):
        if boolian:
            self.image = pygame.transform.scale(ContinueTablet.active_image,
                                                (250, 70))
        else:
            self.image = pygame.transform.scale(ContinueTablet.image,
                                                (250, 70))

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                for elem in self.groups():
                    elem.empty()
                loading_screen()
                con = sqlite3.connect('saves/saves.db')
                cur = con.cursor()
                num = cur.execute("""SELECT id FROM saves""").fetchall()
                if not num:
                    start_game('map.txt')
                else:
                    num = num[-1][0]
                    load_game(num)


class ExitTablet(NewGameTablet):
    image = load_image('exit_tablet.png')
    active_image = load_image('exit_active_tablet.png')

    def __init__(self, pos_x, pos_y, *group):
        super().__init__(pos_x, pos_y, *group)
        self.image = pygame.transform.scale(ExitTablet.image, (250, 70))

    def is_active(self, boolian=False):
        if boolian:
            self.image = pygame.transform.scale(ExitTablet.active_image,
                                                (250, 70))
        else:
            self.image = pygame.transform.scale(ExitTablet.image, (250, 70))

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                for elem in self.groups():
                    elem.empty()
                exit_dialog_init()


class LoadTablet(NewGameTablet):
    image = load_image('load_tablet.png')
    active_image = load_image('load_active_tablet.png')

    def __init__(self, pos_x, pos_y, *group):
        super().__init__(pos_x, pos_y, *group)
        self.image = pygame.transform.scale(LoadTablet.image, (250, 70))

    def is_active(self, boolian=False):
        if boolian:
            self.image = pygame.transform.scale(LoadTablet.active_image,
                                                (250, 70))
        else:
            self.image = pygame.transform.scale(LoadTablet.image, (250, 70))

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                for elem in self.groups():
                    elem.empty()
                screen.blit(background_picture, (0, 0))
                load_game(2)
                # text = ["Пока не готово"]
                # print_text(text, 48, (10, SCREEN_HEIGHT // 2), "#251733")
                #
                # backbutton_sprite.add(BackButton())
                # backbutton_sprite.draw(screen)


class SettingsTablet(NewGameTablet):
    image = load_image('settings_tablet.png')
    active_image = load_image('settings_active_tablet.png')

    def __init__(self, pos_x, pos_y, *group):
        super().__init__(pos_x, pos_y, *group)
        self.image = pygame.transform.scale(SettingsTablet.image, (250, 70))

    def is_active(self, boolian=False):
        if boolian:
            self.image = pygame.transform.scale(SettingsTablet.active_image,
                                                (250, 70))
        else:
            self.image = pygame.transform.scale(SettingsTablet.image,
                                                (250, 70))

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                for elem in self.groups():
                    elem.empty()
                screen.blit(background_picture, (0, 0))

                print_text(["НАСТРОЙКИ".rjust(36, ' ')], 100, (20, 10),
                           "#251733")
                text = ["Пока что здесь ничего нет, но вы можете выключить "
                        "музыку главного меню!".rjust(82, ' ')]
                print_text(text, 48, (20, 100), "#251733")
                print_text(["Выключить/включить музыку"], 48, (80, 210),
                           '#251733')

                backbutton_sprite.add(BackButton())
                music_switch_sprite.add(MusicSwitchButton())
                backbutton_sprite.draw(screen)
                music_switch_sprite.draw(screen)


class HelpTablet(NewGameTablet):
    image = load_image('help_tablet.png')
    active_image = load_image('help_active_tablet.png')

    def __init__(self, pos_x, pos_y, *group):
        super().__init__(pos_x, pos_y, *group)
        self.image = pygame.transform.scale(HelpTablet.image, (250, 70))

    def is_active(self, boolian=False):
        if boolian:
            self.image = pygame.transform.scale(HelpTablet.active_image,
                                                (250, 70))
        else:
            self.image = pygame.transform.scale(HelpTablet.image, (250, 70))

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                for elem in self.groups():
                    elem.empty()
                screen.blit(background_picture, (0, 0))

                print_text(["ПОМОЩЬ".rjust(39, ' ')], 100, (20, 10),
                           "#251733")
                text = ["Тут будет информация по управлению и мб квестам"]
                print_text(text, 48, (10, SCREEN_HEIGHT // 2), "#251733")

                backbutton_sprite.add(BackButton())
                backbutton_sprite.draw(screen)


# используется в найстойках, помощи и загрузке для возврата на главный экран
class BackButton(pygame.sprite.Sprite):
    image = load_image('back_button.png')
    active_image = load_image('back_button_active.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.transform.scale(BackButton.image, (250, 70))
        self.rect = self.image.get_rect().move(SCREEN_WIDTH - 260,
                                               SCREEN_HEIGHT - 80)
        self.col_flag = False

    def tablet_moving(self, args):
        if not self.col_flag and self.rect.collidepoint(args[0].pos):
            self.col_flag = True
            self.image = pygame.transform.scale(BackButton.active_image,
                                                (250, 70))
            backbutton_sprite.draw(screen)
        elif self.col_flag and not self.rect.collidepoint(args[0].pos):
            self.col_flag = False
            self.image = pygame.transform.scale(BackButton.image,
                                                (250, 70))
            backbutton_sprite.draw(screen)

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                for elem in self.groups():
                    elem.empty()
                music_switch_sprite.empty()
                main_screen_init()


# после смерти кнопка "выйти в главное меню"
class ReturnToMainMenuButton(BackButton):
    image = load_image('return_to_main_menu_button.png')
    active_image = load_image('return_to_main_menu_active_button.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.transform.scale(ReturnToMainMenuButton.image,
                                            (250, 70))
        self.rect = self.image.get_rect().move(SCREEN_WIDTH // 2 + 5,
                                               SCREEN_HEIGHT // 2 + 20)
        self.clicked_flag = False

    def tablet_moving(self, args):
        if not self.col_flag and self.rect.collidepoint(args[0].pos):
            self.col_flag = True
            self.image = pygame.transform.scale(
                ReturnToMainMenuButton.active_image,
                (250, 70))
            die_dialog_sprites.draw(screen)
        elif self.col_flag and not self.rect.collidepoint(args[0].pos):
            self.col_flag = False
            self.image = pygame.transform.scale(ReturnToMainMenuButton.image,
                                                (250, 70))
            die_dialog_sprites.draw(screen)

    def is_clicked(self):
        return self.clicked_flag

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and \
                    self.rect.collidepoint(args[0].pos):
                click_sound.play()
                for elem in self.groups():
                    elem.empty()
                main_screen_init()
                self.clicked_flag = True


# после смерти кнопка "загрузить последнее сохранение"
class LoadLastSave(ContinueTablet):
    image = load_image('load_last_save_button.png')
    active_image = load_image('load_last_save_active_button.png')

    def __init__(self, * group):
        super().__init__(SCREEN_WIDTH // 2 - 255, SCREEN_HEIGHT // 2 + 20, *group)
        self.image = pygame.transform.scale(LoadLastSave.image, (250, 70))

    def tablet_moving(self, args):
        if not self.col_flag and self.rect.collidepoint(args[0].pos):
            self.col_flag = True
            self.image = pygame.transform.scale(LoadLastSave.active_image,
                                                (250, 70))
            die_dialog_sprites.draw(screen)
        elif self.col_flag and not self.rect.collidepoint(args[0].pos):
            self.col_flag = False
            self.image = pygame.transform.scale(LoadLastSave.image, (250, 70))
            die_dialog_sprites.draw(screen)


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
        self.rect = self.image.get_rect().move((20, 200))

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


def craft_menu_init():
    pass


# эта функция загружает главный экран
def main_screen_init():
    screen.blit(background_picture, (0, 0))

    # инициализация кнопок главного меню
    start_point = SCREEN_HEIGHT // 3
    new_tablet = NewGameTablet(20, start_point - 80, tablet_sprites)
    continue_tablet = ContinueTablet(20, start_point, tablet_sprites)
    load_tablet = LoadTablet(20, start_point + 80, tablet_sprites)
    settings_tablet = SettingsTablet(20, start_point + 80 * 2, tablet_sprites)
    help_tablet = HelpTablet(20, start_point + 80 * 3, tablet_sprites)
    exit_tablet = ExitTablet(20, start_point + 80 * 4, tablet_sprites)
    tablet_sprites.draw(screen)

    # выводим большую надпись ISLAND
    print_text(["ISLAND"], 200, (SCREEN_WIDTH // 4 + SCREEN_WIDTH // 12, 10), "#ffa97e")


def loading_screen():
    screen.blit(load_image('loading_screen.png'), (0, 0))
    pygame.display.flip()
    time.sleep(1.5)


if __name__ == '__main__':
    background_picture = pygame.transform.scale(load_image(
        'background_image.png'), SCREENSIZE)

    tile_images = {
        'sand': load_image('sand.png'),
        'water': load_image('ocean.png'),
        'rock': load_image('rock.png', -1),
        'branch': load_image('branch.png', -1)
    }
    player_image = load_image('hero.png', -1)
    tile_width = tile_height = 50
    player = None
    hp, hunger = 100, 100
    map_list = load_level('map.txt')
    map_list = [list(i) for i in map_list]

    list_of_item = list()  # список всех предметов в инвентаря
    list_of_item_num = list()  # количество предметов в инвентаре больше нужно для загрзки
    # группы спрайтов Паши
    tiles_group = pygame.sprite.Group()  # группа для песка и воды
    player_group = pygame.sprite.Group()  # игрок
    object_group_not_special = pygame.sprite.Group()  # объекты для которых не нужен предмет
    interface_group = pygame.sprite.Group()  # чтоб было удобнее группа интерфейсов
    list_of_item_group = pygame.sprite.Group()  # группа отвечающая за инвентарь
    object_group = pygame.sprite.Group()  # здесь хранятся объекты, с которыми можно будет взаимдейстовать
    # группы спрайтов Даши
    tablet_sprites = pygame.sprite.Group()  # кнопки в меню
    backbutton_sprite = pygame.sprite.Group()  # кнопка "назад"
    exit_yesno_sprites = pygame.sprite.Group()  # да/нет при выходе из игры
    new_game_yesno_sprites = pygame.sprite.Group()  # да/нет при начале новой игры
    music_switch_sprite = pygame.sprite.Group()  # выключатель музыки
    die_dialog_sprites = pygame.sprite.Group()  # кнопки для диалога загрузки после смерти
    pause_menu_sprites = pygame.sprite.Group()  # кнопки в меню паузы

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
                backbutton_sprite.update(event)
                exit_yesno_sprites.update(event)
                new_game_yesno_sprites.update(event)
                music_switch_sprite.update(event)
                
            elif event.type == pygame.MOUSEMOTION:
                tablet_sprites.update(event)
                backbutton_sprite.update(event)
                exit_yesno_sprites.update(event)
                new_game_yesno_sprites.update(event)
                
            pygame.display.flip()
