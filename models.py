from math import sqrt
from utils import Line, Point


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
    self.calc_radius()

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
