# forked from https://github.com/christian-oudard/blokus/blob/master/poly.py

from constants import BOARD_SIZE, MAX_SIZE


class Piece:
    def __init__(self, points):
        # Give points a predictable order.
        self._points = tuple(sorted(points))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self._points)

    _block_char = '#'

    def __str__(self):
        max_x = max(x for x, y in self)
        max_y = max(y for x, y in self)
        grid = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]
        for x, y in self:
            grid[y][x] = self._block_char
        return '\n'.join(''.join(line).rstrip() for line in grid)

    def __len__(self):
        return len(self._points)

    def __getitem__(self, indices):
        return self._points[indices]

    def __iter__(self):
        return iter(self._points)

    def __eq__(self, other):
        return isinstance(other, Piece) and self._points == other._points

    def __hash__(self):
        return hash((self.__class__, self._points))

    def __lt__(self, other):
        return ((len(self), self._points) < (len(other), other._points))

    def min(self):
        xmin = min(x for x, y in self)
        ymin = min(y for x, y in self)
        return (xmin, ymin)

    def max(self):
        xmax = max(x for x, y in self)
        ymax = max(y for x, y in self)
        return (xmax, ymax)

    def translate_origin(self):
        min_x = min(x for x, y in self)
        min_y = min(y for x, y in self)
        return self.translated(-min_x, -min_y)

    def translated(self, tx, ty):
        return Piece((x + tx, y + ty) for x, y in self)

    def canonical(self):
        cached = piece_to_canonical.get(self)
        if cached:
            return cached
        return self._canonical()

    #O(n) time
    def collides(self, other):
        i, j = 0, 0
        while i < len(other) and j < len(self):
            if other[i] == self[j]:
                return True
            elif other[i] < self[j]:
                i += 1
            else:
                j += 1
        return False

    def _canonical(self):
        return min(self.orientations())

    def orientations(self):
        clone = Piece(self)
        rotations = [clone]
        for _ in range(3):
            rotations.append(Piece((y, -x) for x, y in rotations[-1]))
        mirrors = []
        for r in rotations:
            mirrors.append(Piece((x, -y) for x, y in r))
        orientations = rotations + mirrors
        orientations = set(p.translate_origin() for p in orientations)
        return orientations

    def adjacencies(self, use_cache=True):
        if use_cache:
            cached = piece_to_adjacencies.get(self)
            if cached:
                return cached
        points = set(self)
        ret = []
        for x, y in list(points):
            for adj in adjacent((x, y)):
                if adj not in points:
                    ret.append(adj)
                    points.add(adj)
        return ret

    def corner_adjacencies(self, use_cache=True):
        if use_cache:
            cached = piece_to_corner_adjacencies.get(self)
            if cached:
                return cached
        adjs = set(self.adjacencies())
        points = set(self)
        ret = []
        for x, y in self:
            for adj in [
                (x - 1, y - 1),
                (x - 1, y + 1),
                (x + 1, y - 1),
                (x + 1, y + 1),
            ]:
                if adj not in points and \
                        adj not in adjs:
                    ret.append(adj)
                    points.add(adj)
        return ret

def on_board(point):
    x,y = point
    return x >= 0 and x < BOARD_SIZE and y >= 0 and y < BOARD_SIZE



def gen_polys(generation):
    if generation == 1:
        return {Piece([(0, 0)])}

    new_polys = set()
    for poly in gen_polys(generation - 1):
        for adj in poly.adjacencies(use_cache=False):
            new_poly = Piece(poly._points + (adj,))
            new_polys.add(new_poly._canonical())
    return new_polys


def adjacent(point):
    x, y = point
    return [
        (x - 1, y),
        (x + 1, y),
        (x, y - 1),
        (x, y + 1),
    ]


one = Piece([(0, 0), ])
two = Piece([(0, 0), (0, 1)])
three_i = Piece([(0, 0), (0, 1), (0, 2)])
three_l = Piece([(0, 0), (0, 1), (1, 0)])
four_i = Piece([(0, 0), (0, 1), (0, 2), (0, 3)])
four_l = Piece([(0, 0), (0, 1), (0, 2), (1, 0)])
four_t = Piece([(0, 0), (0, 1), (0, 2), (1, 1)])
four_o = Piece([(0, 0), (0, 1), (1, 0), (1, 1)])
four_s = Piece([(0, 0), (0, 1), (1, 1), (1, 2)])
five_i = Piece([(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)])
five_l = Piece([(0, 0), (0, 1), (0, 2), (0, 3), (1, 0)])
five_y = Piece([(0, 0), (0, 1), (0, 2), (0, 3), (1, 1)])
five_p = Piece([(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)])
five_u = Piece([(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)])
five_v = Piece([(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)])
five_t = Piece([(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)])
five_j = Piece([(0, 0), (0, 1), (0, 2), (1, 2), (1, 3)])
five_f = Piece([(0, 0), (0, 1), (1, 1), (1, 2), (2, 1)])
five_w = Piece([(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)])
five_z = Piece([(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)])
five_x = Piece([(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)])

# Put them in an index dictionary too.
piece_to_name = {}
for k, v in dict(locals()).items():
    if isinstance(v, Piece):
        piece_to_name[v] = k


# Pieces
all_pieces = []
for size in range(1, MAX_SIZE + 1):
    all_pieces.extend(gen_polys(size))
all_pieces.sort()

if MAX_SIZE == 5:
    assert len(piece_to_name) == len(all_pieces)


# Generate the canonical cache
# key is the piece in a given orientation. value is the canonical piece.
piece_to_canonical = {}
piece_to_adjacencies = {}
piece_to_corner_adjacencies = {}
for poly in all_pieces:
    for o in poly.orientations():
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                t_piece = o.translated(x, y)
                include = True
                for p in t_piece:
                    if not on_board(p):
                        include = False
                if include:
                    piece_to_canonical[t_piece] = poly
                    piece_to_adjacencies[t_piece] = list(t_piece.adjacencies(use_cache=False))
                    piece_to_corner_adjacencies[t_piece] = list(t_piece.corner_adjacencies(use_cache=False))


