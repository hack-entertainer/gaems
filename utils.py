import os

from os import path

from sdl2 import *
from sdl2 import ext


class Brush(object):
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


class Pen(object):
  '''
  draws text
  '''

  def __init__(self, renderer):
    self.renderer = renderer

  def write(self):
    renderer = self.renderer

    fpath = path.join(os.path.abspath(os.path.dirname(__file__)), 'roboto/RobotoCondensed-Bold.ttf')

    f_mngr = ext.FontManager(fpath, 'roboto')

    surface = f_mngr.render('Menu coming soon.')
    texture = SDL_CreateTextureFromSurface(renderer, surface)
    recta, rectb = SDL_Rect(x=0, y=0, w=200, h=20), SDL_Rect(x=350, y=350, w=200, h=20)
    SDL_RenderCopy(renderer, texture, recta, rectb)


class Line(object):
  def __init__(self, p1, p2):
    self.slope = (p2.y - p1.y) / (p2.x - p1.x)
    self.intercept = p1.y - p1.x * self.slope

  def y_value(self, x):
    return self.slope * x + self.intercept


class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __repr__(self):
    return ''.join(['Point(', str(self.x), ',', str(self.y), ')'])
