import pygame
import ctypes
import sys
import os

# получаем размер монитора и вводим константы
user32 = ctypes.windll.user32
SCREENSIZE = SCREEN_WIDTH, SCREEN_HEIGHT = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1) + 2

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

    def get_x_pos(self):
        return self.pos_x

    def get_y_pos(self):
        return self.pos_y

    def tablet_moving(self, args):
        """чтобы анимация кнопки работала эффективно, я не обновляю экран,
        а закрашиваю область под новой отрисовкой в цвет фона
        поэтому, прежде чем вставлять другую картинку на фон, убедитесь, что
        область под кнопками однотонная и в screen.fill() указан этот цвет"""
        if not self.col_flag and self.rect.collidepoint(args[0].pos):
            screen.fill('#99D9EA', self.rect)
            self.rect.x = self.pos_x + 10
            self.col_flag = True
            tablet_sprites.draw(screen)
        elif self.col_flag and not self.rect.collidepoint(args[0].pos):
            screen.fill('#99D9EA', self.rect)
            self.rect.x = self.pos_x
            self.col_flag = False
            tablet_sprites.draw(screen)

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
                # следующий код посвечивает кнопку, если на неё нажать
                self.image = pygame.transform.scale(NewGameTablet.active_image, (250, 70))
                tablet_sprites.draw(screen)
                self.image = pygame.transform.scale(NewGameTablet.image, (250, 70))

                # далее стоит описывать функционал каждой отдельной кнопки
                tablet_sprites.empty()
                screen.blit(background_picture, (0, 0))

                text = ["Этот раздел должен обнулить игру (соотстветвенно, сохранения тоже)",
                        "Стоит выводить предупреждение об удалении предыдущих сохранений"]
                print_text(text, 48, (10, SCREEN_HEIGHT // 2), "#251733", 40)

                backbutton_sprite.add(BackButton())
                backbutton_sprite.draw(screen)


class ContinueTablet(NewGameTablet):
    image = load_image('continue_tablet.png')
    active_image = load_image('continue_active_tablet.png')

    def __init__(self, pos_x, pos_y, *group):
        super().__init__(pos_x, pos_y, *group)
        self.image = pygame.transform.scale(ContinueTablet.image, (250, 70))

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
                self.image = pygame.transform.scale(ContinueTablet.active_image, (250, 70))
                tablet_sprites.draw(screen)
                self.image = pygame.transform.scale(ContinueTablet.image, (250, 70))

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

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
                self.image = pygame.transform.scale(ExitTablet.active_image, (250, 70))
                tablet_sprites.draw(screen)
                terminate()


class LoadTablet(NewGameTablet):
    image = load_image('load_tablet.png')
    active_image = load_image('load_active_tablet.png')

    def __init__(self, pos_x, pos_y, *group):
        super().__init__(pos_x, pos_y, *group)
        self.image = pygame.transform.scale(LoadTablet.image, (250, 70))

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
                self.image = pygame.transform.scale(LoadTablet.active_image, (250, 70))
                tablet_sprites.draw(screen)
                self.image = pygame.transform.scale(LoadTablet.image, (250, 70))

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

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
                self.image = pygame.transform.scale(SettingsTablet.active_image, (250, 70))
                tablet_sprites.draw(screen)
                self.image = pygame.transform.scale(SettingsTablet.image, (250, 70))

                tablet_sprites.empty()
                screen.blit(background_picture, (0, 0))

                text = ["Здесь нужно сделать возможность убавить/прибавить/выключить музыку"]
                print_text(text, 48, (10, SCREEN_HEIGHT // 2), "#251733")

                backbutton_sprite.add(BackButton())
                backbutton_sprite.draw(screen)


class HelpTablet(NewGameTablet):
    image = load_image('help_tablet.png')
    active_image = load_image('help_active_tablet.png')

    def __init__(self, pos_x, pos_y, *group):
        super().__init__(pos_x, pos_y, *group)
        self.image = pygame.transform.scale(HelpTablet.image, (250, 70))

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEMOTION:
                self.tablet_moving(args)
            if args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
                self.image = pygame.transform.scale(HelpTablet.active_image, (250, 70))
                tablet_sprites.draw(screen)
                self.image = pygame.transform.scale(HelpTablet.image, (250, 70))

                tablet_sprites.empty()
                screen.blit(background_picture, (0, 0))

                text = ["Тут будет информация по управлению и мб квестам",
                        "Надо не забыть добавить y/n перед выходом из игры"]
                print_text(text, 48, (10, SCREEN_HEIGHT // 2), "#251733", 40)

                backbutton_sprite.add(BackButton())
                backbutton_sprite.draw(screen)


# используется в найстойках, помощи и загрузке для возврата на главный экран
class BackButton(pygame.sprite.Sprite):
    image = load_image('back_button.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.transform.scale(BackButton.image, (250, 70))
        self.rect = self.image.get_rect().move(SCREEN_WIDTH - 260, SCREEN_HEIGHT - 80)

    def update(self, *args):
        if args:
            if args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
                backbutton_sprite.empty()
                main_screen_init()


class YesButton(pygame.sprite.Sprite):
    image = None


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

    main_screen_init()

    # добавим в главное меню немного звуков
    pygame.mixer.init()
    pygame.mixer.music.load('data/main_menu_sound.mp3')
    pygame.mixer.music.play()

    while True:
        for event in pygame.event.get():
            # перед закрытием игры стоит предупредить игрока
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    terminate()
            elif event.type == pygame.QUIT:
                terminate()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                tablet_sprites.update(event)
                backbutton_sprite.update(event)
            elif event.type == pygame.MOUSEMOTION:
                tablet_sprites.update(event)
            pygame.display.flip()
