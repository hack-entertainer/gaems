import math
import os
from os import path

from sdl2 import *
from sdl2 import ext


class Game:
  """
  encompases (eventually) all assets and activities within a game such as collision detection, state management,
  and win conditions
  """

  def __init__(self, renderer):
    self.ongoing = True
    self.brush = Brush(renderer)
    self.pen = Pen(renderer)

  def handle(self, event):
    if event.type == SDL_QUIT:
      self.ongoing = False

  def collision(self, o1, o2):
    '''

    :param o1: a game object
    :param o2: another game object
    :return: True if they collide

    For now, just use Euclidean distance between spheres to determine collision.
    TODO -- implement SAT but mayyyybe bake your own simple one based on testing each side
    TODO -- move into Geometry class
    '''

    return o1.size + o2.size >= math.sqrt(
      (o1.location.x - o2.location.x) ** 2 + (o1.location.y - o2.location.y) ** 2
    )


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
