from math import sqrt
from utils import Line, Point


class GameObject(object):
  '''
  repository for generic object attributes
  '''
  pass


class TriangleMan(GameObject):
  '''
  a triangle-shaped man

  brush -- Brush()
  size -- int
  color -- RGB tuple good for sdl
  location -- Point()
  '''

  def __init__(self, brush, size, color, location=None):
    '''

    :param size: int size
    :param location: Point() instance specifying center of triangle man
    '''
    self.brush = brush
    self.size = size
    self.color = color
    self.location = location

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

  def draw(self):
    '''
    draw an equilateral triangle
    '''
    # draw them using brush
    self.calc_points()
    self.brush.poly(self.points, self.color)
