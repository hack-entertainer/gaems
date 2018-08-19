import ctypes
import sys

from sdl2 import *

from colors import *
from models import TriangleMan, Square, Game
from utils import Brush, Pen, Point

map_width, map_height = 1000, 750


def main():
  # initialize surface and renderer
  SDL_Init(SDL_INIT_VIDEO)
  window = SDL_CreateWindow(b"Triangle Man",
                            SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                            map_width, map_height, SDL_WINDOW_SHOWN)
  renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED)

  # main_loop
  event = SDL_Event()

  brush = Brush(renderer)
  pen = Pen(renderer)
  # todo -- eventually move all game assets into game

  game = Game(renderer)

  # todo -- move
  # game objects
  goal_square = Square(brush, 8, HEATWAVE, location=Point(round(map_width * .75), round(map_height * .75)))

  BKGRND = NIGHTFALL

  while game.ongoing:
    while SDL_PollEvent(ctypes.byref(event)):
      game.handle(event)

    # update game assets
    game.update()

    # clear the screen
    SDL_SetRenderDrawColor(renderer, *BKGRND, SDL_ALPHA_OPAQUE)
    SDL_RenderClear(renderer)

    # draw my stuff

    # todo -- move
    # "goals"
    # goal_square.draw()
    # #1: touch white square

    game.draw()

    SDL_RenderPresent(renderer)

    # todo -- move
    # collision
    # if game.collision(mans, goal_square):
    #   running = False

  SDL_DestroyWindow(window)
  SDL_DestroyRenderer(renderer)
  SDL_Quit()


if __name__ == "__main__":
  sys.exit(main())
