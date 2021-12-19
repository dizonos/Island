import pygame
import os

pygame.init()

size = width, height = 1920, 1080
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Island')


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


def main():
    print('Ura, vi nachali igru')


class Land(pygame.sprite.Sprite):
    image = load_image('задник для игры.png')

    def __init__(self, group):
        super().__init__(group)
        self.image = Land.image
        self.rect = self.image.get_rect()


class MenuButton(pygame.sprite.Sprite):
    # загрузка глав меню
    def __init__(self, x, y, group, name):
        super().__init__(all_sprites)
        self.image = load_image(name, -1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)
        self.add(group)

    def update(self, *args):
        global running
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):  # мб есть какой-то более лёгкий спсобо опредления нажата ли кнопка или нет, но я не искал dizonos
            if 300 <= args[0].pos[1] <= 400:
                main()
            elif 450 <= args[0].pos[1] <= 550:
                print('poka ne gotovo')
            else:
                running = False
                return


all_sprites = pygame.sprite.Group()
button_sprites = pygame.sprite.Group()

running = True

Land(all_sprites)
MenuButton(0, 200, button_sprites, 'new_game.png')
MenuButton(0, 400, button_sprites, 'load_game.png')
MenuButton(537, 662, button_sprites, 'exit.png')

# надо бы как-то текст подобрать, чтоб прям на кпопках писало, мб будет проще на текстуре написать

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            button_sprites.update(event)
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    pygame.display.flip()
pygame.quit()