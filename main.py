import ctypes
import sys

from sdl2 import *

from colors import *
from models import TriangleMan, Square
from utils import Brush, Pen, Point

map_width, map_height = 900, 600


def main():
  # initialize surface and renderer
  SDL_Init(SDL_INIT_VIDEO)
  window = SDL_CreateWindow(b"Triangle Man",
                            SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                            map_width, map_height, SDL_WINDOW_SHOWN)
  renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED)

  # main_loop
  running = True
  event = SDL_Event()

  brush = Brush(renderer)
  pen = Pen(renderer)

  # object
  mans = TriangleMan(brush, 15, HEATWAVE, location=Point(25, 25))

  # game objects
  goal_square = Square(brush, 5, PARADISE, location=Point(round(map_width * .75), round(map_height * .75)))
  BKGRND = NIGHTFALL

  while running:
    while SDL_PollEvent(ctypes.byref(event)):
      if event.type == SDL_QUIT:
        running = False
        break

      if event.type == SDL_KEYDOWN:

        # move mans
        if (event.key.keysym.sym == SDLK_UP):
          if mans.y_velo > -1:
            mans.y_velo -= 1
        elif (event.key.keysym.sym == SDLK_DOWN):
          if mans.y_velo < 1:
            mans.y_velo += 1
        elif (event.key.keysym.sym == SDLK_LEFT):
          if mans.x_velo > -1:
            mans.x_velo -= 1
        elif (event.key.keysym.sym == SDLK_RIGHT):
          if mans.y_velo < 1:
            mans.x_velo += 1

      elif event.type == SDL_KEYUP:
        if (event.key.keysym.sym == SDLK_UP):
          mans.y_velo += 1
        elif (event.key.keysym.sym == SDLK_DOWN):
          mans.y_velo -= 1
        elif (event.key.keysym.sym == SDLK_LEFT):
          mans.x_velo += 1
        elif (event.key.keysym.sym == SDLK_RIGHT):
          mans.x_velo -= 1



      elif event.type == SDL_MOUSEBUTTONUP:
        # get position of click
        mouse_x, mouse_y = ctypes.c_int(), ctypes.c_int()
        SDL_GetMouseState(mouse_x, mouse_y)

    # movement
    mans.location.x += mans.x_velo
    mans.location.y += mans.y_velo

    # "goals"

    # #1: touch white square
    
    # clear the screen
    SDL_SetRenderDrawColor(renderer, *BKGRND, SDL_ALPHA_OPAQUE)
    SDL_RenderClear(renderer)

    mans.draw()
    # draw all other assets
    SDL_RenderPresent(renderer)

  SDL_DestroyWindow(window)
  SDL_DestroyRenderer(renderer)
  SDL_Quit()


if __name__ == "__main__":
  sys.exit(main())
