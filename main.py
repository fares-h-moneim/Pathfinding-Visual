import pygame, sys
import PIL
from PIL import Image
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement


class Pathfinder:
    def __init__(self, matrix):
        self.matrix = matrix
        self.grid = Grid(matrix=matrix)
        self.select_surf = pygame.image.load('selection.png').convert_alpha()

        self.path = []

        self.roomba = pygame.sprite.GroupSingle(Roomba(self.clear_path))

    def draw_active_cell(self):
        mouse_pos = pygame.mouse.get_pos()
        row = mouse_pos[1] // 32
        col = mouse_pos[0] // 32
        rect = pygame.Rect((col * 32, row * 32), (32, 32))
        if matrix[row][col] == 1:
            screen.blit(self.select_surf, rect)

    def create_path(self):
        startX, startY = self.roomba.sprite.get_pos()
        start = self.grid.node(startX, startY)

        mouse_pos = pygame.mouse.get_pos()
        endX, endY = mouse_pos[0] // 32, mouse_pos[1] // 32
        end = self.grid.node(endX, endY)

        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        self.path, _ = finder.find_path(start, end, self.grid)
        self.grid.cleanup()
        self.roomba.sprite.set_path(self.path)

    def clear_path(self):
        self.path = []

    def draw_path(self):
        if self.path:
            points = []
            for point in self.path:
                x = point[0] * 32 + 16
                y = point[1] * 32 + 16
                points.append((x, y))
                pygame.draw.circle(screen, '#4a4a4a', (x, y), 5)
            pygame.draw.lines(screen, '#4a4a4a', False, points, 5)

    def update(self):
        self.draw_active_cell()
        self.draw_path()

        self.roomba.update()
        self.roomba.draw(screen)


class Roomba(pygame.sprite.Sprite):
    def __init__(self, clear_path):
        super().__init__()
        self.image = pygame.image.load('roomba.png').convert_alpha()
        self.rect = self.image.get_rect(center=(60, 60))

        self.pos = self.rect.center
        self.speed = 2
        self.direction = pygame.math.Vector2(0, 0)

        self.path = []
        self.collision_rect = []

        self.clear_path = clear_path

    def get_pos(self):
        col = self.rect.centerx // 32
        row = self.rect.centery // 32
        return (col, row)

    def set_path(self, path):
        self.path = path
        self.create_collision_rects()
        self.get_direction()

    def create_collision_rects(self):
        if self.path:
            self.collision_rect = []
            for point in self.path:
                x = point[0] * 32 + 16
                y = point[1] * 32 + 16
                rect = pygame.Rect((x - 2, y - 2), (4, 4))
                self.collision_rect.append(rect)

    def get_direction(self):
        if self.collision_rect:
            start = pygame.math.Vector2(self.pos)
            end = pygame.math.Vector2(self.collision_rect[0].center)
            self.direction = (end - start).normalize()
        else:
            self.direction = pygame.math.Vector2(0, 0)
            self.path = []

    def check_coll(self):
        if self.collision_rect:
            for rect in self.collision_rect:
                if rect.collidepoint(self.pos):
                    del self.collision_rect[0]
                    self.get_direction()
        else:
            self.clear_path()

    def update(self):
        self.pos += self.direction * self.speed
        self.check_coll()
        self.rect.center = self.pos


def pixels_to_text(image):
    pixels = image.getdata()
    mat = []
    print(pixels);
    for i in range(0, 23):
        col = []
        for j in range(0, 40):
            pixel = image.getpixel((j, i))
            if pixel[0] + pixel[1] + pixel[2] == 0:
                col.append(0)
            else:
                col.append(1)
        mat.append(col)
    return mat

pygame.init()
screen = pygame.display.set_mode((1280, 736))
clock = pygame.time.Clock()
bg = pygame.image.load('map.png').convert()
image = PIL.Image.open('matrix.png')
matrix = pixels_to_text(image)

pathfinder = Pathfinder(matrix)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pathfinder.create_path()

    screen.blit(bg, (0, 0))
    pathfinder.update()
    pygame.display.update()
    clock.tick(60)
