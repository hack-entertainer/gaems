import ctypes
import sys

from sdl2 import *

from colors import *
from models import Game

def main():
  map_width, map_height = 1000, 750

  # initialize surface and renderer
  SDL_Init(SDL_INIT_VIDEO)
  window = SDL_CreateWindow(b"Triangle Man",
                            SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                            map_width, map_height, SDL_WINDOW_SHOWN)
  renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED)

  # main_loop
  event = SDL_Event()

  game = Game(renderer, map_width, map_height)

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
    game.draw()

    SDL_RenderPresent(renderer)

  SDL_DestroyWindow(window)
  SDL_DestroyRenderer(renderer)
  SDL_Quit()


if __name__ == "__main__":
  sys.exit(main())
