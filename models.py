import random as rn

from datetime import datetime, timedelta
from math import sqrt, sin, cos, pi

from sdl2 import (
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

from utils import Point, Pen, Brush
from colors import *


class GameObject(object):
  '''
  repository for generic object attributes
  '''

  def __init__(self, brush, size, color, location=None):
    """
    brush -- Brush()
    size -- int
    color -- RGB tuple good for sdl
    location -- Point()
    """
    self.brush = brush
    self.size = size
    self.color = color
    self.location = location

  def draw(self):
    '''
    draw myself
    '''
    # draw them using brush
    self.calc_points()
    self.brush.poly(self.points, self.color)

  def move(self):
    '''
    use velocity to calculate new location
    '''
    speed, angle = self.velocity

    # SOH CAH TOA

    # assume 0 <= angle <= 90; quadrant I
    x_dist = speed * cos(angle)  # CAH
    y_dist = speed * sin(angle)  # SOH

    # use reflection for quadrants II-IV
    # todo -- convert from degrees to radians here; works now but... it shouldn't >:/
    if 90 <= angle <= 180:
      x_dist *= -1
    elif 180 <= angle <= 270:
      x_dist *= -1
      y_dist *= -1
    else:
      # 270 <= angle <= 360
      y_dist *= -1

    self.location.x += x_dist
    self.location.y += y_dist


class Square(GameObject):
  '''
  a square
  '''

  def __init__(self, brush, size, color, location=None):
    """
    brush -- Brush()
    size -- int
    color -- RGB tuple good for sdl
    location -- Point()
    """
    super(Square, self).__init__(brush, size, color, location=location)
    self.calc_points()

  def calc_points(self):
    """
    determine location of all points
    :return:
    """
    self.points = [
      Point(self.location.x - round(self.size / 2), self.location.y - round(self.size / 2)),
      Point(self.location.x + round(self.size / 2), self.location.y - round(self.size / 2)),
      Point(self.location.x + round(self.size / 2), self.location.y + round(self.size / 2)),
      Point(self.location.x - round(self.size / 2), self.location.y + round(self.size / 2))

    ]


class Triangle(GameObject):
  def __init__(self, brush, size, color, location=None, x_velo=0, y_velo=0, max_velo=0):
    """
    brush -- Brush()
    size -- int
    color -- RGB tuple good for sdl
    location -- Point()
    """
    super(Triangle, self).__init__(brush, size, color, location=location)

    # for movement
    self.x_velo = x_velo
    self.y_velo = y_velo
    self.max_velo = max_velo

    # read, fire, aim
    self.fire_rate = timedelta(0, .125)
    self.last_fire = datetime.now()
    self.firing = False
    self.aim = 3 / 2 * pi

    # define points, left, middle, right
    self.height = sqrt(size ** 2 - (size ** 2 / 4))
    self.calc_points()

  def calc_points(self):
    '''
    draw points
    :return:
    '''
    location, size, height = self.location, self.size, self.height
    self.points = [
      Point(location.x - size / 2, round(location.y + 1 / 3 * height)),
      Point(location.x, round(location.y - (2 / 3 * height))),
      Point(location.x + size / 2, round(location.y + 1 / 3 * height))
    ]


class TriangleMan(Triangle):
  '''
  a triangle-shaped man

  '''

  def __init__(self, brush, size, color, location=None, x_velo=0, y_velo=0, max_velo=0):
    """
    brush -- Brush()
    size -- int
    color -- RGB tuple good for sdl
    location -- Point()
    """
    super(TriangleMan, self).__init__(brush, size, color, location=location)

    # for movement
    self.x_velo = x_velo
    self.y_velo = y_velo
    self.max_velo = max_velo

    # read, fire, aim
    self.fire_rate = timedelta(0, .125)
    self.last_fire = datetime.now()
    self.firing = False
    self.aim = 3 / 2 * pi

    # define points, left, middle, right
    self.height = sqrt(size ** 2 - (size ** 2 / 4))
    self.calc_points()

  def move(self):
    self.location.x += self.x_velo
    self.location.y += self.y_velo


class Bullet(Triangle):
  '''
  a triangleman-like object

  '''

  def __init__(self, brush, size, color, location=None, lifespan=timedelta(0, .25), velocity=(1, 90)):
    """
    brush -- Brush()
    size -- int
    color -- RGB tuple good for sdl
    location -- Point()
    velocity -- tuple(['speed', 'direction as degrees of a circle'])
    """
    super(Bullet, self).__init__(brush, size, color, location=location)

    self.lifespan = lifespan
    self.creation = datetime.now()
    self.velocity = velocity

    # define points, left, middle, right
    self.height = sqrt(size ** 2 - (size ** 2 / 4))
    self.calc_points()


class Villain(Square):
  def __init__(self, brush, size, color, location=None, hp=1):
    """
    brush -- Brush()
    size -- int
    color -- RGB tuple good for sdl
    location -- Point()
    velocity -- tuple(['speed', 'direction as degrees of a circle'])
    """
    super(Villain, self).__init__(brush, size, color, location=location)

    self.hp = hp
    self.velocity = 0, 0

  def act(self):
    '''
    decide what to do next
    '''

    # shoot 'em if you got 'em
    # todo

    # set new velocity based on position of mans
    # todo

    self.move()


class Game:
  """
  encompases (eventually) all assets and activities within a game such as collision detection, state management,
  and win conditions
  """

  def __init__(self, renderer, map_width, map_height):
    self.ongoing = True
    self.brush = Brush(renderer)
    self.pen = Pen(renderer)

    self.m_width, self.m_height = map_width, map_height

    # keyboard state
    self.keyboard = {}

    mans = TriangleMan(self.brush, 15, HEATWAVE, location=Point(25, 25))
    self.mans = mans

    # aiming; .2 seconds
    self.diagonal_aim_threshold = timedelta(0, .2)

    # objects fired by player
    self.missiles = []

    self.goal_square = Square(self.brush, 8, HEATWAVE, location=Point(round(map_width * .75), round(map_height * .75)))

    # villains
    self.villains = []

  def collisions(self):
    # mans and goals

    # bullets and enemies

    # enemies and mans

    # todo -- convert into regions and do collisions on all items therein
    pass

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

  @classmethod
  def collision(cls, o1, o2):
    '''

    :param o1: a game object
    :param o2: another game object
    :return: True if they collide

    For now, just use Euclidean distance between spheres to determine collision.
    TODO -- implement SAT but mayyyybe bake your own simple one based on testing each side
    TODO -- move into Geometry class -- eventually implement/import physics and *gasp* chemistry!!?
    '''

    return o1.size + o2.size >= sqrt(
      (o1.location.x - o2.location.x) ** 2 + (o1.location.y - o2.location.y) ** 2
    )

  def draw(self):
    '''
    draw game assets
    '''
    self.mans.draw()
    self.goal_square.draw()

    for missile in self.missiles:
      missile.draw()

    for v in self.villains:
      v.draw()

  def update(self):
    '''
    update game asset states
    '''

    ## VILLAIN CREW ##
    villains = self.villains

    # spawn
    while len(self.villains) < 5:
      villains.append(
        Villain(
          self.brush, 18, GREEN,
          location=Point(rn.randint(0, self.m_width), rn.randint(0, self.m_height)))
      )

    for v in villains:
      v.act()
    ## END VILLAIN ##

    # move missiles
    missiles = self.missiles
    for missile in missiles:
      missile.move()

    mans = self.mans
    mans.move()
    if mans.firing:
      # fire bullet at correct frequency
      if datetime.now() - mans.last_fire >= mans.fire_rate:
        missiles.append(Bullet(
          self.brush, 25, RED, lifespan=timedelta(0, .5), location=Point(mans.location.x, mans.location.y),
          velocity=(1.5, mans.aim)
        ))
        mans.last_fire = datetime.now()

    # delete pxpired missiles
    for i in reversed(range(len(missiles))):
      if datetime.now() - missiles[i].creation > missiles[i].lifespan:
        missiles.pop(i)

    self.collision()
