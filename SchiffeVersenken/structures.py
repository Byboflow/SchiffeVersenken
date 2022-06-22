class Square:
    """
    Class for representation of a single Square on board
    """

    def __init__(self, sign):
        """
        :param sign: str -> String representation of square
        """
        self.sign = sign
        self.final_sign = sign

    def change_sign(self, sign):
        """
        Change the sign of a Square object
        :param sign: str -> String representation of square
        """
        self.sign = sign

    def __repr__(self):
        """
        Return string representation of a Square
        """
        return self.sign

    def __str__(self):
        """
        Return string representation of a Square
        """
        return self.sign


class OceanSquare(Square):
    """
    Concrete class representing the playable Ocean
    """

    def __init__(self, ShipReference=None):
        """
        :param ShipReference: str -> String representation of OceanSquare
        """
        if (ShipReference is None):
            super().__init__("~ ")
        else:
            super().__init__(ShipReference)


class ShipSquare(Square):
    """
    Concrete class representing the Ship
    """

    def __init__(self, sign):
        """
        :param sign: str -> String representation of square
        """
        super().__init__(sign)


class Ocean():
    """
    Class representing one board with list of lists attribute
    """

    def __init__(self, height, width):
        self.board = []

        self.board_width = width
        self.board_height = height

        self.create_board(height, width)

    def create_board(self, height, width):
        """
        Create board with list of lists containing Square objects.
        :param height: int -> Height of board, default: 10
        :param width: int -> Width of board, default: 10
        """
        if self.board:
            self.board = []
        for c in range(0, height):
            self.board.append([OceanSquare() for i in range(width)])

    def __str__(self):
        """
        Print board
        """
        res = "    "
        for i in range(self.board_width):
            if i != self.board_width - 1:
                res += chr(i + 65) + "  "  ## ehrenlos
            else:
                res += chr(i + 65)
        res += " \n"

        for i in range(self.board_height):
            if (len(str(i + 1)) == 1):
                temp = str(i + 1) + "  "
            else:
                temp = str(i + 1) + " "

            for x in self.board[i]:
                temp += " " + x.__str__()

            res += temp + "\n"

        return res


class Ship():
    """
    Class representing Ship object on board
    """

    def __init__(self, space: int, sign: str, ocean: Ocean,
                 is_horizontal: bool, starting_point, is_decoy=False):
        """
        :param space: int -> Length of a ship
        :param sign: str -> String representation of a ship
        :param ocean: Ocean -> Ocean where the ship is placed
        :param is_horizontal: bool -> True if ship is placed horizontal, False if it is placed vertical
        :param starting_point: int, int -> Tuple with starting point of a ship (row, line)
        :param is_decoy: bool -> True if you are placing ship on additional temp board default: False
        """
        self.space = space
        self.sign = sign
        self.ocean = ocean
        self.is_horizontal = is_horizontal
        if not is_decoy:
            self.create_ship_by_user(starting_point)
        else:
            self.create_ship_by_decoy(starting_point)

    def create_ship_by_user(self, starting_point):
        """
        Check if ship can be placed here and add ship on board:
        The ships can only be placed vertically or horizontally.
        No part of a ship may hang off the edge of the board.
        Ships may not overlap each other.
        No ships may be placed on another ship. Ships may not touch each other.
        :param starting_point: int, int -> Tuple with starting point of a ship (row, line)
        """
        x = starting_point[0]  # reudig
        y = starting_point[1]

        if self.is_horizontal:
            if x <= 0 or x + self.space > self.ocean.board_width - 1 or y <= 0 or y > self.ocean.board_height - 1:
                raise ValueError('Your ship is hanging off the border!')
        else:
            if y <= 0 or y + self.space > self.ocean.board_height - 1 or x <= 0 or x > self.ocean.board_width - 1:
                raise ValueError('Your ship is hanging off the border!')

        if self.is_another_ship_near(x, y):
            raise ValueError('You cant put ship near another ship!')

        if self.is_horizontal:
            self.ocean.board[y][x: x + self.space] = [ShipSquare(self.sign) for i in range(self.space)]
        else:
            for i in self.ocean.board[y:y + self.space]:
                i[x] = ShipSquare(self.sign)

    def create_ship_by_decoy(self, position):
        """
        Used for moving ship while placing it, to do it we create temporary additional ocean
        :param position: int, int -> Tuple with starting point of a ship (row, line)
        """
        x = position[0]
        y = position[1]
        if self.is_horizontal:
            self.ocean.board[y][x: x + self.space] = [ShipSquare(self.sign) for i in range(self.space)]
        else:
            for i in self.ocean.board[y:y + self.space]:
                i[x] = ShipSquare(self.sign)

    def is_another_ship_near(self, x, y):
        """
        Chceck if there is another ship around ship with given position
        :param x: int -> Row
        :param y: int -> Line
        """
        BUFFER = 1
        surrounding = []

        if self.is_horizontal:
            surrounding += self.ocean.board[y + BUFFER][x - BUFFER: x + BUFFER + self.space]  ## auch ehrenlos
            surrounding += self.ocean.board[y][x - BUFFER: x + BUFFER + self.space]
            surrounding += self.ocean.board[y - BUFFER][x - BUFFER: x + BUFFER + self.space]
        else:
            surrounding += [i[x - BUFFER] for i in self.ocean.board[y - BUFFER: y + BUFFER + self.space]]
            surrounding += [i[x] for i in self.ocean.board[y - BUFFER: y + BUFFER + self.space]]
            surrounding += [i[x + BUFFER] for i in self.ocean.board[y - BUFFER: y + BUFFER + self.space]]
        return any(isinstance(i, ShipSquare) for i in surrounding)

    def __str__(self):
        return self.sign


class Carrier(Ship):

    def __init__(self, ocean: Ocean,
                 is_horizontal: bool, starting_point, is_decoy=False):
        super().__init__(5, "CA", ocean, is_horizontal, starting_point, is_decoy)


class Battleship(Ship):
    def __init__(self, ocean: Ocean,
                 is_horizontal: bool, starting_point, is_decoy=False):
        super().__init__(4, "BS", ocean, is_horizontal, starting_point, is_decoy)


class Cruiser(Ship):

    def __init__(self, ocean: Ocean,
                 is_horizontal: bool, starting_point, is_decoy=False):
        super().__init__(3, "CR", ocean, is_horizontal, starting_point, is_decoy)


class Submarine(Ship):

    def __init__(self, ocean: Ocean,
                 is_horizontal: bool, starting_point, is_decoy=False):
        super().__init__(2, "SU", ocean, is_horizontal, starting_point, is_decoy)


class Destroyer(Ship):
    def __init__(self, ocean: Ocean,
                 is_horizontal: bool, starting_point, is_decoy=False):
        super().__init__(1, "DE", ocean, is_horizontal, starting_point, is_decoy)