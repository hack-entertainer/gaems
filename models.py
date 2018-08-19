import ctypes
import datetime

from math import sqrt, sin, cos, tan
from utils import Point, Brush

from sdl2 import *

from colors import *

from utils import Brush, Pen


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


class TriangleMan(GameObject):
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

  def move(self):
    self.location.x += self.x_velo
    self.location.y += self.y_velo


class Bullet(GameObject):
  '''
  a triangle-shaped man

  '''

  def __init__(self, brush, size, color, location=None, lifespan=1, velocity=(0, 0)):
    """
    brush -- Brush()
    size -- int
    color -- RGB tuple good for sdl
    location -- Point()
    velocity -- tuple(['speed', 'direction as degrees of a circle'])
    """
    super(Bullet, self).__init__(brush, size, color, location=location)

    self.lifespan = datetime.timedelta(0, .35)
    self.creation = datetime.datetime.now()
    self.velocity = velocity

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

    self.mans = TriangleMan(self.brush, 15, HEATWAVE, location=Point(25, 25))
    self.mans.fire_rate = datetime.timedelta(0, .01)
    self.mans.firing = False
    self.mans.last_fire = datetime.datetime.now()

    # objects fired by player
    self.missiles = []

    self.goal_square = Square(self.brush, 8, HEATWAVE, location=Point(round(map_width * .75), round(map_height * .75)))

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


    elif event.type == SDL_MOUSEBUTTONUP:
      # get position of click
      mouse_x, mouse_y = ctypes.c_int(), ctypes.c_int()
      SDL_GetMouseState(mouse_x, mouse_y)

  def collision(self, o1, o2):
    '''

    :param o1: a game object
    :param o2: another game object
    :return: True if they collide

    For now, just use Euclidean distance between spheres to determine collision.
    TODO -- implement SAT but mayyyybe bake your own simple one based on testing each side
    TODO -- move into Geometry class
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

  def update(self):
    '''
    update game asset states
    '''
    mans = self.mans
    mans.move()

    # delete expired missiles
    missiles = self.missiles
    for i in reversed(range(len(missiles))):
      if datetime.datetime.now() - missiles[i].creation > missiles[i].lifespan:
        missiles.pop(i)

    if mans.firing:
      # fire bullet if fire rate has passed
      if datetime.datetime.now() - mans.last_fire >= mans.fire_rate:
        missiles.append(Bullet(self.brush, 5, BLUE, lifespan=datetime.timedelta(0, .0001),
                               location=Point(mans.location.x, mans.location.y), velocity=(1.5, 360)))
        mans.last_fire = datetime.datetime.now()

    for missile in missiles:
      missile.move()

    if self.collision(mans, self.goal_square):
      self.ongoing = False
