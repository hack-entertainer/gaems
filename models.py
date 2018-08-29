import random as rn

from datetime import datetime, timedelta
from math import sqrt, sin, cos, pi, inf

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

from utils import Point, Pen, Brush, Geometry
from colors import *


class GameObject:
  '''
  repository for generic object attributes
  '''

  def __init__(self, size, color, location=None):
    """
    size -- int
    color -- RGB tuple good for sdl
    location -- Point()
    """
    self.size = size
    self.color = color
    self.location = location

  def move(self):
    '''
    use velocity to calculate new location
    '''
    speed, angle = self.velocity

    # SOH CAH TOA

    # assume 0 <= angle <= 90; quadrant I
    x_dist = speed * cos(angle)  # CAH
    y_dist = speed * sin(angle)  # SOH

    # todo -- convert from degrees to radians here; works now but... it shouldn't >:/
    # compute aim returns aim in degrees which is why this
    # works for bullets but not for other objects
    # todo -- end

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

    self.calc_points()

  def _move(self):
    '''
    use velocity to calculate new location
    '''
    speed, angle = self.velocity

    # SOH CAH TOA
    x_dist = speed * cos(angle)  # CAH
    y_dist = speed * sin(angle)  # SOH

    self.location.x += x_dist
    self.location.y += y_dist

    self.calc_points()


class Square(GameObject):
  '''
  a square
  '''

  def __init__(self, size, color, location=None):
    """
    size -- int
    color -- RGB tuple good for sdl
    location -- Point()
    """
    super(Square, self).__init__(size, color, location=location)
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
  def __init__(self, size, color, location=None, x_velo=0, y_velo=0, max_velo=0):
    """
    size -- int
    color -- RGB tuple good for sdl
    location -- Point()
    """
    super(Triangle, self).__init__(size, color, location=location)

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


class Protagonist(Triangle):
  '''
  a triangle-shaped man

  '''

  def __init__(self, size, color, hp=1, location=None, x_velo=0, y_velo=0, max_velo=0):
    """
    size -- int
    color -- RGB tuple good for sdl
    location -- Point()
    """
    super(Protagonist, self).__init__(size, color, location=location)

    self.hp = hp

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
    # todo -- have man use base move method
    self.location.x += self.x_velo
    self.location.y += self.y_velo
    self.calc_points()


class Bullet(Triangle):
  '''
  a triangleman-like object

  '''

  def __init__(self, size, color, location=None, power=1, lifespan=timedelta(0, .25), velocity=(1, 90)):
    """
    brush -- Brush()
    size -- int
    color -- RGB tuple good for sdl
    location -- Point()
    velocity -- tuple(['speed', 'direction as degrees of a circle'])
    """
    super(Bullet, self).__init__(size, color, location=location)

    self.power = power
    self.lifespan = lifespan
    self.creation = datetime.now()
    self.velocity = velocity

    # define points, left, middle, right
    self.height = sqrt(size ** 2 - (size ** 2 / 4))
    self.calc_points()


class Frenemy(Square):
  def __init__(self, size, color, target, max_speed=1, location=None, power=0, hp=1):
    """
    size -- int
    color -- RGB tuple good for sdl
    location -- Point()
    velocity -- tuple(['speed', 'direction as degrees of a circle'])
    """
    super(Frenemy, self).__init__(size, color, location=location)

    self.hp = hp
    self.power = power
    self.max_speed = max_speed
    self.velocity = 0, 0

    self.target = target

  def act(self):
    '''
    decide what to do next
    '''

    # todo
    # shoot 'em if you got 'em

    # set new velocity based on position of mans
    self.set_velocity()

    super()._move()

  def set_velocity(self):
    direction = Geometry.angle_between(self.location, self.target.location)
    self.velocity = self.max_speed, direction


class EnemySpigot(Square):

  def __init__(self, size, color, location, hp, spawn_type, spawn_rate, spawn_args, max_spawnable=inf):
    """

    :param size:
    :param color:
    :param location: Point()
    :param hp: int
    :param spawn_type: what type to spawn
    :param spawn_args: parameters of spawn type
    :param spawn_rate: how fast to spawn
    :param max_spawnable: how many to spawn
    """
    self.size = size
    self.color = color
    self.location = location
    self.hp = hp
    self.spawn_rate = spawn_rate
    self.spawn_type = spawn_type
    self.spawn_args = spawn_args
    self.spawn_loc = self.spawn_args['location']
    self.max_spawnable = max_spawnable
    self.last_spawn = datetime.now()

    self.total_spawned = 0

    self.calc_points()

  def can_spawn(self):
    return datetime.now() - self.last_spawn > self.spawn_rate and \
           self.total_spawned <= self.max_spawnable

  def spawn(self):
    self.total_spawned += 1
    self.last_spawn = datetime.now()
    self.spawn_args['location'] = Point(self.spawn_loc[0], self.spawn_loc[1])
    return self.spawn_type(**self.spawn_args)


class Game:
  def __init__(self):
    # game on
    self.ongoing = True

  def __repr__(self):
    return "It's a meee! WaAAAAaAAaAAaaa!"

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

  def adjust_view(self):
    # adjust view center
    v_center = self.view_center
    mans = self.mans
    max_distance = self.max_distance_from_view_center

    # horizontal
    if abs(mans.location.x - v_center.x) > max_distance:
      if mans.location.x < v_center.x:
        # mans to right
        v_center.x = mans.location.x + max_distance
      else:
        # mans to left of view center
        v_center.x = mans.location.x - max_distance

    # vertical
    if abs(mans.location.y - v_center.y) > max_distance:
      if mans.location.y < v_center.y:
        # mans to right
        v_center.y = mans.location.y + max_distance
      else:
        # mans to left of view center
        v_center.y = mans.location.y - max_distance

  def draw_game_objects(self):
    '''
    draw game assets
    '''
    mc = self.map_center
    vc = self.view_center
    for o in self.game_objects:
      # adjust drawing position to account or viewport position
      points = [Point(p.x + (mc.x - vc.x), p.y + (mc.y - vc.y)) for p in o.points]
      self.brush.poly(points, o.color)


class TriangleMan(Game):
  """
  encompases (eventually) all assets and activities within a game such as collision detection, state management,
  and win conditions
  """

  def __init__(self, renderer, map_width, map_height, max_goals=1, goal_target=1, max_enemies=1):
    self.um = datetime.now()
    """
    
    :param renderer: 
    :param map_width: 
    :param map_height: 
    :param max_goals: 
    :param goal_target: 
    :param max_enemies: 
    """

    super(TriangleMan, self).__init__()

    # graephics
    self.brush = Brush(renderer)
    self.pen = Pen(renderer)

    self.m_width, self.m_height = map_width, map_height
    self.map_center = Point(map_width / 2, map_height / 2)
    self.view_center = Point(self.map_center.x, self.map_center.y)
    self.max_distance_from_view_center = map_height / 4

    # keyboard state
    self.keyboard = {}

    # todo -- initial config starting to get big
    # protagonist
    mans = Protagonist(15, HEATWAVE, hp=5, location=Point(self.map_center.x, self.map_center.y))
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

    self.game_objects = [mans]

  def adjust_view(self):
    # adjust view center
    v_center = self.view_center
    mans = self.mans
    max_distance = self.max_distance_from_view_center

    # horizontal
    if abs(mans.location.x - v_center.x) > max_distance:
      if mans.location.x < v_center.x:
        # mans to right
        v_center.x = mans.location.x + max_distance
      else:
        # mans to left of view center
        v_center.x = mans.location.x - max_distance

    # vertical
    if abs(mans.location.y - v_center.y) > max_distance:
      if mans.location.y < v_center.y:
        # mans to right
        v_center.y = mans.location.y + max_distance
      else:
        # mans to left of view center
        v_center.y = mans.location.y - max_distance

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
        Frenemy(18, GREEN, target=mans, power=0,
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
          25, RED, lifespan=timedelta(0, .5), location=Point(mans.location.x, mans.location.y),
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
        Square(18, HEATWAVE,
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
