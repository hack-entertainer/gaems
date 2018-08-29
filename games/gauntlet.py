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

from models import Game

class Gauntlet(Game):

  def update(self):
    '''
    update game asset states
    '''
    # sugar
    mans = self.mans

    ## VILLAIN CREW ##

    villains = [enemy for enemy in self.enemies if enemy.hp > 0]

    # spawn
    while len(villains) < self.max_enemies:
      villains.append(
        Enemy(
          self.brush, 18, GREEN, target=mans, power=0,
          location=Point(rn.randint(0, self.m_width), rn.randint(0, self.m_height)))
      )

    for v in villains:
      v.act()

    self.enemies = villains
    ## END VILLAIN ##

    # move missiles
    missiles = self.bullets
    for missile in self.bullets:
      missile.move()

    if datetime.now() - self.um > timedelta(0, .5):
      self.um = datetime.now()

    mans.move()

    self.adjust_view()

    # have the action follow the man
    # todo -- continue here
    if mans.firing:
      # fire bullet at correct frequency
      if datetime.now() - mans.last_fire >= mans.fire_rate:
        missiles.append(Bullet(
          self.brush, 25, RED, lifespan=timedelta(0, .5), location=Point(mans.location.x, mans.location.y),
          velocity=(1.5, mans.aim)
        ))
        mans.last_fire = datetime.now()

    # delet exppired missiles
    for i in reversed(range(len(missiles))):
      if datetime.now() - missiles[i].creation > missiles[i].lifespan:
        missiles.pop(i)

    goals = self.goals
    while len(goals) < self.max_goals and self.goals_achieved < self.goal_target:
      goals.append(
        Square(self.brush, 18, HEATWAVE,
               location=Point(
                 rn.randint(0, self.m_width),
                 rn.randint(0, self.m_height)))
      )

    self.collisions()

  def main(self):
    map_width, map_height = 700, 700

    # initialize surface and renderer
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(b"Triangle Man",
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              map_width, map_height, SDL_WINDOW_SHOWN)
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED)

    # main_loop
    event = SDL_Event()

    BKGRND = NIGHTFALL

    while self.ongoing:
      while SDL_PollEvent(ctypes.byref(event)):
        self.handle(event)

      # update game assets
      self.update()

      # clear the screen
      SDL_SetRenderDrawColor(renderer, *BKGRND, SDL_ALPHA_OPAQUE)
      SDL_RenderClear(renderer)

      # draw my stuff
      self.draw_game_objects()

      SDL_RenderPresent(renderer)

    SDL_DestroyWindow(window)
    SDL_DestroyRenderer(renderer)
    SDL_Quit()

if __name__ == "__main__":
  print(sys.exit(Gauntlet().main()))