import pygame
import ctypes
import sys
import os
import time

# получаем размер монитора и вводим константы
user32 = ctypes.windll.user32
SCREENSIZE = SCREEN_WIDTH, SCREEN_HEIGHT = user32.GetSystemMetrics(0), \
                                           user32.GetSystemMetrics(1) + 2

pygame.init()
pygame.display.set_caption("Island")

# если не произвести иниц. дисплея здесь, перестанет работать load_image()
screen = pygame.display.set_mode(SCREENSIZE)


# функция завершения работы программы
def terminate():
    pygame.quit()
    sys.exit()


# функция загрузки изображений
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
                tablet_sprites.empty()
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
                tablet_sprites.empty()
                screen.blit(background_picture, (0, 0))

                text = ["Эта кнопка должна загружать последнее сохранение"]
                print_text(text, 48, (10, SCREEN_HEIGHT // 2), "#251733")

                backbutton_sprite.add(BackButton())
                backbutton_sprite.draw(screen)


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
                tablet_sprites.empty()
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
                tablet_sprites.empty()
                screen.blit(background_picture, (0, 0))

                text = ["Пока не готово"]
                print_text(text, 48, (10, SCREEN_HEIGHT // 2), "#251733")

                backbutton_sprite.add(BackButton())
                backbutton_sprite.draw(screen)


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
                tablet_sprites.empty()
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
                tablet_sprites.empty()
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
            screen.fill('#99D9EA', self.rect)
            self.col_flag = True
            self.image = pygame.transform.scale(BackButton.active_image,
                                                (250, 70))
            backbutton_sprite.draw(screen)
        elif self.col_flag and not self.rect.collidepoint(args[0].pos):
            screen.fill('#99D9EA', self.rect)
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
                backbutton_sprite.empty()
                music_switch_sprite.empty()
                main_screen_init()


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
                exit_yesno_sprites.empty()
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
                new_game_yesno_sprites.empty()
                screen.blit(background_picture, (0, 0))

                text = ["Пока не готово"]
                print_text(text, 48, (10, SCREEN_HEIGHT // 2), "#251733", 40)

                backbutton_sprite.add(BackButton())
                backbutton_sprite.draw(screen)


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
                new_game_yesno_sprites.empty()
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

    # инициализация кнопок главного меню
    new_tablet = NewGameTablet(20, 200, tablet_sprites)
    continue_tablet = ContinueTablet(20, 280, tablet_sprites)
    load_tablet = LoadTablet(20, 360, tablet_sprites)
    settings_tablet = SettingsTablet(20, 440, tablet_sprites)
    help_tablet = HelpTablet(20, 520, tablet_sprites)
    exit_tablet = ExitTablet(20, 600, tablet_sprites)
    tablet_sprites.draw(screen)

    # выводим большую надпись ISLAND
    print_text(["ISLAND"], 200, (SCREEN_WIDTH // 4 + 150, 10), "#ffa97e")


if __name__ == '__main__':
    background_picture = pygame.transform.scale(load_image('test_image.png'),
                                                SCREENSIZE)

    tablet_sprites = pygame.sprite.Group()
    backbutton_sprite = pygame.sprite.Group()
    exit_yesno_sprites = pygame.sprite.Group()
    new_game_yesno_sprites = pygame.sprite.Group()
    music_switch_sprite = pygame.sprite.Group()

    main_screen_init()

    pygame.mixer.init()
    pygame.mixer.music.load('data/main_menu_sound.mp3')
    pygame.mixer.music.play(loops=-1)

    click_sound = pygame.mixer.Sound('data/click_sound.mp3')

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
