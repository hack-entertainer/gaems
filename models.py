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

    def __init__(self, brush, size, color, center=None, position=None):
        '''

        :param size: int size
        :param center: Point() instance specifying center of triangle man
        '''
        self.brush = brush
        self.size = size
        self.color = color
        self.location = center

        # define points, left, middle, right
        height = sqrt(size ** 2 - (size ** 2 / 4))
        self.points = [
            Point(center.x - size / 2, round(center.y + 1 / 3 * height)),
            Point(center.x, round(center.y - (2 / 3 * height))),
            Point(center.x + size / 2, round(center.y + 1 / 3 * height))
        ]

    def draw(self):
        '''
        draw an equilateral triangle
        '''
        # draw them using brush
        self.brush.poly(self.points, self.color)


class Tile(GameObject):
    def __init__(self, center, side):
        '''

        :param self:
        :param center: x, y coordinates as instance of Point()
        :param side: length of the side
        :return:
        '''
        self.center = center
        self.side = side
        self.occupant = None
        # bottom left, left, top left, top right, right, bottom right
        self.bleft, self.left, self.tleft, self.tright, self.right, self.bright = self.corners = self._corner_points()

    def _corner_points(self):
        '''
        :param center: el medio, como un punto i.e. Point()
        :param side: el lado
        :return: los lados i.e. botton left, left, etc...
        '''
        center, side = self.center, self.side
        height = sqrt(side ** 2 - (side ** 2) / 4)

        bl = Point(round(center.x - side / 2), round(center.y - height))
        l = Point(round(center.x - side), round(center.y))
        tl = Point(round(bl.x), round(bl.y + 2 * height))
        tr = Point(round(tl.x + side), round(tl.y))
        r = Point(round(center.x + side), round(center.y))
        br = Point(round(bl.x + side), round(bl.y))

        return [bl, l, tl, tr, r, br]

    def next_hex(self, direction):
        '''
        new hexagon in given direction from this one
        :param direction:
        :return:
        '''
        center = self.next_center(direction)
        return Tile(center, self.side)

    def next_center(self, direction):
        '''

        :param center:
        :param side:
        :param direction:
        :return: return center of hexagon in the given direction from one centered at point
        '''
        center, side = self.center, self.side

        height = sqrt(side ** 2 - (side ** 2) / 4)
        width = 2 * side

        x, y = center.x, center.y
        if direction == 'top_left':
            return Point(round(x - width + side / 2), round(y - height))
        elif direction == 'top':
            return Point(x, round(y - 2 * height))
        elif direction == 'top_right':
            return Point(round(x + width - side / 2), round(y - height))
        elif direction == 'bottom_right':
            return Point(round(x + width - side / 2), round(y + height))
        elif direction == 'bottom':
            return Point(x, round(y + 2 * height))
        elif direction == 'bottom_left':
            return Point(round(x - width + side / 2), round(y + height))
        else:
            raise Exception('improper direction given')


class TileMap(object):
    '''
    a linked mesh of hexagonal areas
    '''

    def __init__(self, brush, size, bottom, hex_size):
        '''
        bottom -- bottom, in form of Point()
        size -- how many rings in this hex map, including center
        side -- length of a side
        brush -- instance of Brush
        '''
        self.brush = brush
        self.size = size
        self.bottom = Tile(bottom, hex_size)

        # for click detection
        tiles = self.tiles = []

        # start w/ very bottom hex, spawning new rows up and to the left for the bottom half/middle-row,
        # and straight up for the top half
        # convert hex to point
        anchor = self.bottom
        row_length = size
        for row_num in range(2 * size - 1):
            tiles.append(anchor)

            self.create_row(anchor, row_length, merge_down=row_num > 0)

            # nix that extra next_hex/slight kludge
            if row_num == 2 * size - 2:
                break

            # determine direction of next hex
            if row_num < size - 1:
                next_hex = anchor.next_hex('top_left')
                # link them
                anchor.top_left = next_hex
                next_hex.bottom_right = anchor

                anchor = next_hex

            else:
                next_hex = anchor.next_hex('top')
                # link
                anchor.top = next_hex
                next_hex.bottom = anchor
                next_hex.bottom_right = anchor.top_right

                anchor = next_hex

            if row_num < size - 1:
                row_length += 1
            else:
                row_length -= 1

    def create_row(self, base_node, length, merge_down):
        '''
        create a row starting at base-node and going up, and to the right

        base_node -- instance of Hex(), assumed to have already been stitched down if merge_down == True
        length -- how long to make the row
        merge_down -- whether to link nodes in this row to a row below i.e. that row exists
        merge_last -- whether the last node should link the bottom_right edge to the row below
        '''
        previous = base_node
        for count in range(length - 1):
            # for selection purposes
            self.tiles.append(previous)

            next_hex = previous.next_hex('top_right')
            # link 'em
            previous.top_right = next_hex
            next_hex.bottom_left = previous

            if merge_down:
                next_hex.bottom = previous.bottom_right
                previous.bottom_right.top = next_hex

                # merge bottom right if exists
                # if next_hex.bottom.__hasattr__('top_right'):
                #     next_hex.bottom_right = next_hex.bottom.top_right
                #     next_hex.bottom.top_right.top_left = next_hex

                try:
                    bottom_right = next_hex.bottom.top_right
                    next_hex.bottom_right = bottom_right
                    bottom_right.top_left = next_hex
                except:
                    # print('I owe my soul to the company store.')
                    pass

            previous = next_hex

    def draw(self, COLOR):
        '''
        draw the map
        '''
        # TODO -- genericise color and background
        # starting with bottom, draw rows
        row_head = self.bottom
        try:
            while True:
                self.draw_row(row_head, COLOR)
                row_head = row_head.top_left
        except:
            pass

        try:
            while True:
                self.draw_row(row_head, COLOR)
                row_head = row_head.top
        except:
            pass

    def draw_row(self, row_head, COLOR):
        '''
        draw a row starting with row_head
        '''
        next_hex = row_head
        try:
            while True:
                self.brush.poly(next_hex.corners, COLOR)
                next_hex = next_hex.top_right
        except:


            # print('Is this exception abuse?')
            pass

    def get_tile(self, point):
        '''

        :param point: Point() instance
        :return: tile that overlaps point, or None
        '''
        # sort tiles according to distance from point
        distance_from_point = lambda tile: sqrt(
            (tile.center.x - point.x) ** 2 + (tile.center.y - point.y) ** 2
        )
        self.tiles.sort(key=distance_from_point)

        # determine if first result overlaps point
        closest = self.tiles[0]

        # return if overlap, else return None

        # do 3-region check
        # left region; between left x of left point and x of bottom-left point
        top_line, bottom_line = None, None
        if closest.left.x <= point.x < closest.bleft.x:
            # if point below top line and above bottom line
            top_line, bottom_line = Line(closest.left, closest.tleft), Line(closest.left, closest.bleft)
        elif closest.bleft.x <= point.x < closest.bright.x:
            # middle region
            top_line, bottom_line = Line(closest.tleft, closest.tright), Line(closest.bleft, closest.bright)
        elif closest.bright.x <= point.x <= closest.right.x:
            # right region
            top_line, bottom_line = Line(closest.tright, closest.right), Line(closest.bright, closest.right)

        # is point between top and bottom line?
        if top_line and point.y <= top_line.y_value(point.x) and point.y >= bottom_line.y_value(point.x):
            return closest

        # no result
        return None

class Menu(object):
    def __init__(self):
        self.displayed = False