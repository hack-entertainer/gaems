import ctypes
import sys

from sdl2 import (
  SDL_Init,
  SDL_INIT_VIDEO,
  SDL_CreateWindow,
  SDL_WINDOWPOS_CENTERED,
  SDL_WINDOW_SHOWN,
  SDL_CreateRenderer,
  SDL_RENDERER_ACCELERATED,
  SDL_Event,
  SDL_PollEvent,
  SDL_SetRenderDrawColor,
  SDL_ALPHA_OPAQUE,
  SDL_RenderClear,
  SDL_RenderPresent,
  SDL_DestroyWindow,
  SDL_DestroyRenderer,
  SDL_Quit
)

from colors import *
from models import TriangleMan


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

  game = TriangleMan(renderer, map_width, map_height, max_enemies=1, max_goals=2, goal_target=5)

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
    game.draw_game_objects()

    SDL_RenderPresent(renderer)

  SDL_DestroyWindow(window)
  SDL_DestroyRenderer(renderer)
  SDL_Quit()


if __name__ == "__main__":
  sys.exit(main())
