import ctypes
import sys

from sdl2 import *

from colors import *
from models import TriangleMan
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

  BKGRND = NIGHTFALL

  while running:
    while SDL_PollEvent(ctypes.byref(event)):
      if event.type == SDL_QUIT:
        running = False
        break

      selected = None
      if event.type == SDL_KEYDOWN:

        if (event.key.keysym.sym == SDLK_u):
          mans.location.x -=15
          mans.location.y -=15
        elif (event.key.keysym.sym == SDLK_i):
          mans.location.y -=15
        elif (event.key.keysym.sym == SDLK_o):
          mans.location.x +=15
          mans.location.y -=15
        elif (event.key.keysym.sym == SDLK_l):
          mans.location.x +=15
        elif (event.key.keysym.sym == SDLK_PERIOD):
          mans.location.x +=15
          mans.location.y +=15
        elif (event.key.keysym.sym == SDLK_COMMA):
          mans.location.y +=15
        elif (event.key.keysym.sym == SDLK_m):
          mans.location.x -=15
          mans.location.y +=15
        elif (event.key.keysym.sym == SDLK_j):
          mans.location.x -=15

      elif event.type == SDL_MOUSEBUTTONUP:
        # get position of click
        mouse_x, mouse_y = ctypes.c_int(), ctypes.c_int()
        SDL_GetMouseState(mouse_x, mouse_y)

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
