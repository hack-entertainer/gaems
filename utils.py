import os

from math import atan, pi
from os import path

from sdl2 import *
from sdl2 import ext


class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __repr__(self):
    return ''.join(['Point(', str(self.x), ',', str(self.y), ')'])


class Brush:
  '''
  wrap the SDL objects and methods
  '''

  def __init__(self, renderer):
    '''

    renderer -- result of SDL_CreateRenderer()
    '''
    self.renderer = renderer

  def poly(self, points, COLOR, OPACITY=SDL_ALPHA_OPAQUE):
    '''
    sdl draw points
    '''
    renderer = self.renderer

    # draw line for each pair of points
    SDL_SetRenderDrawColor(renderer, *COLOR, OPACITY)
    for i in range(len(points) - 1):
      p1, p2 = points[i], points[i + 1]
      SDL_RenderDrawLine(renderer, int(p1.x), int(p1.y), int(p2.x), int(p2.y))

    # link last pair
    p1, p2 = points[-1], points[0]
    SDL_RenderDrawLine(renderer, int(p1.x), int(p1.y), int(p2.x), int(p2.y))


class Pen:
  '''
  draws text
  '''

  def __init__(self, renderer):
    self.renderer = renderer

  def write(self, message, position=Point(0, 0), height=20):
    renderer = self.renderer

    fpath = path.join(os.path.abspath(os.path.dirname(__file__)), 'roboto/RobotoCondensed-Bold.ttf')

    f_mngr = ext.FontManager(fpath, 'roboto')

    surface = f_mngr.render(message)
    texture = SDL_CreateTextureFromSurface(renderer, surface)

    recta = SDL_Rect(x=position.x, y=position.y, w=len(message) * round(height / 2.8), h=height)

    SDL_RenderCopy(renderer, texture, recta, recta)


class Line:
  def __init__(self, p1, p2):
    self.slope = (p2.y - p1.y) / (p2.x - p1.x)
    self.intercept = p1.y - p1.x * self.slope

  def y_value(self, x):
    return self.slope * x + self.intercept


class Geometry:
  '''
  geometry functions for polygons and kin
  '''

  @classmethod
  def distance(cls, p1, p2):
    pass

  @classmethod
  def angle_between(cls, p1, p2):
    """
    return angle, in radians, between p1 and p2

    p1, p2 -- Point(), Point()
    """
    x = p2.x - p1.x
    y = p2.y - p1.y

    # todo account for x == 0 || y == 0 when the exception occurs

    # assume quadrant I
    # SOH CAH *TOA*
    angle = atan(abs(y / x))

    # for reflection
    arc2y_axis = pi / 2 - angle
    arc2x_axis = angle

    # quadrants II-IV
    if x < 0 and y >= 0:
      # II
      angle += 2 * arc2y_axis
    elif x < 0 and y < 0:
      # III
      angle += 2 * arc2y_axis + 2 * arc2x_axis
    elif x >= 0 and y < 0:
      # IV
      angle += 4 * arc2y_axis + 2 * arc2x_axis

    return angle
