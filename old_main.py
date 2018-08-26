import ctypes
import sys

from sdl2 import *

from colors import *
from models import *
from utils import Brush, Pen, Point

map_width, map_height = 900, 600


def main():
  # initialize surface and renderer
  SDL_Init(SDL_INIT_VIDEO)
  window = SDL_CreateWindow(b"Hello World",
                            SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                            map_width, map_height, SDL_WINDOW_SHOWN)
  renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED)

  # main_loop
  running = True
  event = SDL_Event()

  brush = Brush(renderer)
  # for text, TODO integrate into menu system
  pen = Pen(renderer)

  bottom = Point(round(map_width / 2), map_height - 125)
  map = TileMap(brush, 7, bottom, 30)

  # models
  mans = TriangleMan(brush, 15, HEATWAVE, location=map.bottom.center, position=map.bottom)
  map.bottom.occupant = mans

  BKGRND = NIGHTFALL
  while running:
    while SDL_PollEvent(ctypes.byref(event)):
      if event.type == SDL_QUIT:
        running = False
        break

      selected = None
      if event.type == SDL_KEYUP:
        if (event.key.keysym.sym == SDLK_UP):
          print('arriba')
        elif (event.key.keysym.sym == SDLK_DOWN):
          print('abajo')
        elif (event.key.keysym.sym == SDLK_LEFT):
          print('izquierda')
        elif (event.key.keysym.sym == SDLK_RIGHT):
          print('derecha')
      elif event.type == SDL_MOUSEBUTTONUP:
        # get position of click
        mouse_x, mouse_y = ctypes.c_int(), ctypes.c_int()
        SDL_GetMouseState(mouse_x, mouse_y)
        selected = map.get_tile(Point(mouse_x.value, mouse_y.value))

        # highlight it

      # select a position and highight it
      if selected and selected.occupant:
        # display menu
        pass

    # clear the screen
    SDL_SetRenderDrawColor(renderer, *BKGRND, SDL_ALPHA_OPAQUE)
    SDL_RenderClear(renderer)

    map.draw_game_objects(PARADISE)

    # draw mans
    mans.draw()

    # draw text
    pen.write()

    # draw all other assets
    SDL_RenderPresent(renderer)

  SDL_DestroyWindow(window)
  SDL_DestroyRenderer(renderer)
  SDL_Quit()


if __name__ == "__main__":
  sys.exit(main())
