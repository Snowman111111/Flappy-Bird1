import pygame
import random
import sys
import os
import math

pygame.init()

WIDTH, HEIGHT = 400, 600
FPS = 60

WHITE = (255, 255, 255)
BLUE = (135, 206, 250)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 223, 0)
LIGHT_GRAY = (220, 220, 220)
ORANGE = (255, 165, 0)

BIRD_RADIUS = 20
GRAVITY = 0.5
JUMP_STRENGTH = -10

PIPE_WIDTH = 70
PIPE_GAP_START = 200
PIPE_GAP_MIN = 120
PIPE_SPEED_START = 3
PIPE_SPEED_MAX = 8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird with Moving Pipes and Coins")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)
