import ctypes
import random as rn
import sys

from datetime import datetime, timedelta
from math import pi

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
  SDL_Quit,
  SDLK_w,
  SDLK_a,
  SDLK_s,
  SDLK_d,
  SDL_QUIT,
  SDL_KEYDOWN,
  SDL_KEYUP,
  SDLK_UP,
  SDLK_DOWN,
  SDLK_LEFT,
  SDLK_RIGHT,
  SDLK_SPACE,
)

from colors import *

from models import Game, Enemy, Bullet, Square, Protagonist
from utils import Point, Pen, Brush, Geometry


class Gauntlet(Game):

  def __init__(self, map_width, map_height, max_goals=1, goal_target=1, max_enemies=1):
    self.um = datetime.now()
    """

    :param renderer: 
    :param map_width: 
    :param map_height: 
    :param max_goals: 
    :param goal_target: 
    :param max_enemies: 
    """

    super(Gauntlet, self).__init__()

    # graephics
    # initialize surface and renderer
    SDL_Init(SDL_INIT_VIDEO)
    self.window = SDL_CreateWindow(b"Gauntlet",
                                   SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                                   map_width, map_height, SDL_WINDOW_SHOWN)
    self.renderer = SDL_CreateRenderer(self.window, -1, SDL_RENDERER_ACCELERATED)
    self.brush = Brush(self.renderer)
    self.pen = Pen(self.renderer)

    self.m_width, self.m_height = map_width, map_height
    self.map_center = Point(map_width / 2, map_height / 2)
    self.view_center = Point(self.map_center.x, self.map_center.y)
    self.max_distance_from_view_center = map_height / 4

    # keyboard state
    self.keyboard = {}

    # todo -- initial config starting to get big
    # protagonist
    mans = Protagonist(self.brush, 15, HEATWAVE, hp=5, location=Point(self.map_center.x, self.map_center.y))
    self.mans = mans

    # aiming; .2 second threshold
    self.diagonal_aim_threshold = timedelta(0, .2)

    # objects fired by player
    self.bullets = []

    # objectives
    self.goals = []
    self.max_goals = max_goals
    self.goals_achieved = 0
    self.goal_target = goal_target

    # villains
    self.max_enemies = max_enemies
    self.enemies = []

  def collisions(self):
    # todo -- convert into regions and do collisions on all items therein

    # mans and goals
    mans = self.mans
    goals = self.goals

    for t in reversed(range(len(goals))):
      if self.collision(mans, goals[t]):
        goals.pop(t)
        self.goals_achieved += 1

    if len(goals) is 0:
      self.ongoing = False

    # bullets and enemies
    enemies = self.enemies
    for enemy in enemies:
      for bullet in self.bullets:
        if self.collision(bullet, enemy):
          enemy.hp -= bullet.power

    # enemies and mans
    for enemy in enemies:
      if self.collision(enemy, mans):
        mans.hp -= enemy.power
        enemy.hp = 0

    if mans.hp < 1:
      self.ongoing = False

  def compute_aim(self):
    '''
    compute aim based on state of keys
    :return: aim, in radians
    '''
    keys = [SDLK_w, SDLK_a, SDLK_s, SDLK_d]
    keyboard = self.keyboard

    up = [key for key in keys if keyboard.setdefault(key, {'state': 'up', 'time': datetime.now()})['state'] is 'up']
    down = [key for key in keys if keyboard[key]['state'] is 'down']
    # yay, context
    up.sort(key=lambda button: keyboard[button]['time'], reverse=True)
    down.sort(key=lambda button: keyboard[button]['time'])

    # radians
    aim = self.mans.aim / pi

    aims = {
      SDLK_w: 1 / 2,
      SDLK_a: 1,
      SDLK_s: 3 / 2,
      SDLK_d: 0
    }
    diagonal_aims = {
      SDLK_w: {SDLK_a: 3 / 4, SDLK_d: 1 / 4},
      SDLK_a: {SDLK_w: 3 / 4, SDLK_s: 5 / 4},
      SDLK_s: {SDLK_a: 5 / 4, SDLK_d: 7 / 4},
      SDLK_d: {SDLK_w: 1 / 4, SDLK_s: 7 / 4}
    }

    diagonal_pairs = {
      SDLK_w: [SDLK_a, SDLK_d],
      SDLK_a: [SDLK_w, SDLK_s],
      SDLK_s: [SDLK_a, SDLK_d],
      SDLK_d: [SDLK_w, SDLK_s]
    }

    # if any keys down, aim based on those
    if len(down) > 0:
      # if 1 key down, aim that way
      last = down[0]
      aim = aims[last]

      # if 2 or more, aim according to last two horizontal, vertical keys pressed
      for second2last in down[1:]:
        if second2last in diagonal_pairs[last] and \
            keyboard[last]['time'] - keyboard[second2last]['time'] < self.diagonal_aim_threshold:
          aim = diagonal_aims[last][second2last]
          break
    else:
      # aim defaults to last key pressed, but if diagonal,
      # account for two keys recently released
      last = up[0]
      for second2last in up[1:]:
        if second2last in diagonal_pairs[last] and \
            keyboard[last]['time'] - keyboard[second2last]['time'] < self.diagonal_aim_threshold:
          aim = diagonal_aims[last][second2last]
          break
      pass

    return aim * pi

  def handle(self, event):
    if event.type == SDL_QUIT:
      self.ongoing = False

    # handle man updates
    mans = self.mans
    if event.type == SDL_KEYDOWN:

      # update man's movement and state
      if event.key.keysym.sym == SDLK_UP:
        if mans.y_velo > -1:
          mans.y_velo -= 1
      elif event.key.keysym.sym == SDLK_DOWN:
        if mans.y_velo < 1:
          mans.y_velo += 1
      elif event.key.keysym.sym == SDLK_LEFT:
        if mans.x_velo > -1:
          mans.x_velo -= 1
      elif event.key.keysym.sym == SDLK_RIGHT:
        if mans.x_velo < 1:
          mans.x_velo += 1
      elif event.key.keysym.sym == SDLK_SPACE:
        mans.firing = True
      elif event.key.keysym.sym in [SDLK_w, SDLK_a, SDLK_s, SDLK_d]:
        # aiming using w, a, s, d keys
        self.keyboard[event.key.keysym.sym] = {'state': 'down', 'time': datetime.now()}
        mans.aim = self.compute_aim()


    elif event.type == SDL_KEYUP:
      if event.key.keysym.sym == SDLK_UP:
        if mans.y_velo < 0:
          mans.y_velo += 1
      elif event.key.keysym.sym == SDLK_DOWN:
        if mans.y_velo > 0:
          mans.y_velo -= 1
      elif event.key.keysym.sym == SDLK_LEFT:
        if mans.x_velo < 0:
          mans.x_velo += 1
      elif event.key.keysym.sym == SDLK_RIGHT:
        if mans.x_velo > 0:
          mans.x_velo -= 1
      elif event.key.keysym.sym == SDLK_SPACE:
        mans.firing = False
      elif event.key.keysym.sym in [SDLK_w, SDLK_a, SDLK_s, SDLK_d]:
        # aiming using w, a, s, d keys
        self.keyboard[event.key.keysym.sym] = {'state': 'up', 'time': datetime.now()}
        mans.aim = self.compute_aim()

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

    # update list of game objects
    self.game_objects = [mans]
    self.game_objects.extend(missiles)
    self.game_objects.extend(villains)
    self.game_objects.extend(goals)

  def main(self):
    renderer = self.renderer
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

    SDL_DestroyWindow(self.window)
    SDL_DestroyRenderer(renderer)
    SDL_Quit()


if __name__ == "__main__":
  print(sys.exit(Gauntlet(map_height=600, map_width=600).main()))
