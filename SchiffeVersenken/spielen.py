import abc
import argparse
import os
from multiprocessing import Process, Pipe
from copy import deepcopy
from msvcrt import getch
from time import time
from structures import *
import sys

terminal_clear = 'cls'  # Change to 'cls' if using windows         # um den terminal sauber zu machen


# Tastatur-Input bekommen
def key_getch():
    """
    ch: Eingabe des Nutzers
    Key vom User bekommen und returnen
    """
    while True:  # Jede Taste hat seinen eigenen code
        key = ord(getch())  # ord changes an object to unicode
        if key == 119:
            return 'w'
        elif key == 97:
            return 'a'
        elif key == 115:
            return 's'
        elif key == 100:
            return 'd'
        elif key == 112:
            return 'p'
        elif key == 27:
            return 'q'
        elif key == 114:
            return 'r'
        else:
            return '0'


## SPIEL KLASSE
class Game():

    def __init__(self):  # empty constructor, skeletton code
        ...

    @abc.abstractmethod  # pairing class
    def start_game(self):
        pass

    @staticmethod  # can use it outside the class
    def user_input_bekommen(width, height):
        """
        Methode dient dafür, die Koordinaten des Spielers zu bekommen
        :return: list =
                         0 index = Reihe
                         1 index = Spalte
        """

        board_letter = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10, 'K': 11,
                        'L': 12, 'M': 13, 'N': 14, 'O': 15, 'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20, 'U': 21,
                        'V': 22, 'W': 23, 'X': 24, 'Y': 25, 'Z': 26}
        while True:  # schleife umd zu wdh bei fslsche eingabe
            hit_position = input('Welche Stelle soll abgeschossen werden? (Spalte, Reihe): ')
            try:
                col, row = hit_position.split(',')
                col = str(col).upper()
                if col not in board_letter.keys() or len(col) != 1:
                    print('Falsche Eingabe, nochmal versuchen!')
                    continue

                if not row.isdigit() or int(row) > height or int(row) <= 0:
                    print('Falsche Eingabe, nochmal versuchen!')
                    continue

            except:
                print('Falsche Eingabe, nochmal versuchen!')
                continue

            hit_position = (int(row) - 1, board_letter[col] - 1)  # wenn kein error

            return hit_position

    @staticmethod
    def check_ob_ein_schiff_kaputt(ship_sign: str, Ocean):
        """
        Methode um zu sehen, ob ein Schiff vollständig zerstört ist
        :param ship_sign: Abkürzung der Schiffe, z.B. "CA"
        :param Ocean: ozean object
        :return: bool -> "False" wenn das Schiff nicht zerstört ist. Sonst "True"
        """
        for row in Ocean.board:  # board is the spielfeld mrkkk    row is horizontal standard looking mechanism
            for square in row:  # square = boxes
                if square.sign == ship_sign.upper():  # wenn schiff in square ist
                    return False
        return True

    @staticmethod
    def check_ob_alle_schiffe_kaputt(ocean: Ocean):  # ocean is object of Ocean class
        """
        Methode um zu sehen, ob bestimmte Schiffe zerstört sind
        :param Ocean: ozean object
        :return: bool -> "False" wenn das Schiff nicht zerstört ist. Sonst "True"
        """
        for row in ocean.board:
            for square in row:
                if isinstance(square, ShipSquare):  # falls in square schiff drin ist
                    return False
        return True  # also wenn alle schiffe ciao sind

    def platziere_schiffe_in_spielfeld(self, player, height, width):  # nicht static
        """
        Methode um alle Schiffe ins Spielfeld zu tun
        :param player: Spieler-Instanz
        """
        ships = ['Carrier', 'Battleship', 'Cruiser', 'Submarine', 'Destroyer']
        movement_keys = ['w', 's', 'a', 'd']
        decoy_ocean = Ocean(height, width)  # temporäre schiffe um sich zu bewegen
        decoy = Player('decoy', decoy_ocean, player.ocean)

        print('Platzier-Modus:\n' + str(player) + "'s Spielfeld")
        print(decoy.ocean)

        while ships:
            starting_position = 1, 1
            is_horizontal = True

            while True:
                user_input = input(
                    'Soll dein ' + ships[0] + ' horizontal oder vertikal platziert werden? (h or v) ').lower()
                if user_input == 'h':
                    break
                elif user_input == 'v':
                    is_horizontal = False
                    break
                else:
                    print('Falsche Eingabe! Nur horizontale and vertikale Platzierung erlaubt.')

            while True:  # schleife um objecte zu platzieren
                decoy.ocean.board = deepcopy(player.ocean.board)
                os.system(terminal_clear)  # terminal clear
                decoy.tu_schiff_aufs_brett(ships[0], is_horizontal, starting_position, True)  # decoy weil vor p nix
                print('Platzier-Modus: \n' + str(player) + "'s Spielfeld")
                print(decoy.ocean)

                print(
                    'Benutze W,A,S,D um das Schiff zu bewegen, dann P um es zu platzieren. Mit R kann man neustarten.')

                move_ship = key_getch()
                if move_ship in movement_keys:  # 132       check if wsad
                    starting_position = self.schiffe_bewegen(is_horizontal, starting_position, ships[0], move_ship,
                                                             height, width)
                    # change
                elif move_ship == 'p':  # ab dann real
                    try:
                        player.tu_schiff_aufs_brett(ships[0], is_horizontal, starting_position, False)
                        ships.pop(0)
                        break
                    except:
                        print('Hier kannst du dein Schiff nicht platzieren!')
                        continue

                elif move_ship == 'q':
                    quit()

                elif move_ship == 'r':
                    player.ocean = Ocean(height, width)
                    os.system(terminal_clear)
                    self.platziere_schiffe_in_spielfeld(player, height, width)

                else:
                    print('Falsche Eingabe!')

    @staticmethod
    def schiffe_bewegen(is_horizontal, position, ship_type, move_ship, height, width):
        """
        Methode dient dazu, die Schiffe auf dem Spielfeld zu bewegen (mit WSAD-Tasten)
        Method puts ships on board using WSAD buttons
        :param is_horizontal: bool - > ist unser Schiff horizontal?
        :param position: list -> liste die die startposition beschreibt
        :param ship_type: str -> Typ des Schiffs
        :param move_ship: str -> Richtung
        :return: None
        """
        position = list(position)  # tuple to list
        ships_lengths = {'Carrier': 5, 'Battleship': 4, 'Cruiser': 3, 'Submarine': 2, 'Destroyer': 1}
        ship_length = ships_lengths[ship_type]
        if is_horizontal:
            if move_ship == 'w':
                if position[1] > 1:  # 0 colum 1 row
                    position[1] -= 1

            elif move_ship == 's':
                if position[1] < (height - 2):
                    position[1] += 1

            elif move_ship == 'a':
                if position[0] > 1:
                    position[0] -= 1

            elif move_ship == 'd':
                if position[0] < (width - ship_length - 1):
                    position[0] += 1
        else:
            if move_ship == 'w':
                if position[1] > 1:
                    position[1] -= 1

            elif move_ship == 's':
                if position[1] < (height - ship_length - 1):
                    position[1] += 1

            elif move_ship == 'a':
                if position[0] > 1:
                    position[0] -= 1

            elif move_ship == 'd':
                if position[0] < (width - 2):
                    position[0] += 1

        position = tuple(position)  # list to tuple          cant change position later on

        return position

    @staticmethod
    def versteck_alle_schiffe(Ocean):
        """
        Methode um die Schiffe vom Spielfeld zu verstecken
        (Man soll ja nicht die Schiffe des Feindes sehen)
        Method hide all ships from ocean board
        :param Ocean:
        :return: None
        """
        board = Ocean.board  # temporary
        for row in board:
            for square in row:
                if isinstance(square, ShipSquare):
                    square.change_sign('~ ')

    @staticmethod
    def zeig_alle_schiffe(Ocean):
        """
        Eigene Schiffe anzeigen
        Method all hidden from ocean board
        :param Ocean:
        :return: None
        """
        board = Ocean.board
        for row in board:
            for square in row:
                if isinstance(square, ShipSquare):
                    square.change_sign(square.final_sign)


## PLAYER KLASSE
class Player():
    """
    Klasse, die den Spieler repräsentiert (mit seinem Feld und dem Feld seines Gegners als Attribute)
    Class representing a player with his board and opponent board as attributes
    """

    def __init__(self, name, ocean, opponent_ocean):  # init:     constructor of class
        """
        :param name: String -> Name des Spielers
        :param is_human: bool -> True wenn er ein Mensch ist, sonst False
        :param ocean: Ocean -> Ozean des Spielers
        :param opponent_ocean: Ocean -> Ozean des Gegenspielers
        """
        self.name = name  # of the player
        self.ocean = ocean
        self.opponent_ocean = opponent_ocean
        #  self.name = name
        self.fired = 0
        self.ships_alive = 5
        self.opp_ships_alive = 5

    def tu_schiff_aufs_brett(self, ship_name, is_horizontal, starting_point, is_decoy=False):
        """
        Schiff Objekt generieren und auf dem Spielfeld platzieren
        :param ship_name: String -> Name eines Schiffs
        :param is_horizontal: bool -> True wenn das Schiff horizontal ist, sonst False
        :param starting_point: int, int -> Tuple mit Startpunkt eines Schiffs (Reihe, Spalte)
        :param is_decoy: bool -> True wenn das Schiff [...] , sonst False
        """
        eval(ship_name)(self.ocean, is_horizontal, starting_point, is_decoy)

    def player_turn(self, player_name):
        """
        Spielfelder abbilden (von beiden Spielern)
        :param player_name: String -> Name eines Spieler Objekts
        Print table with both boards for player turn
        :param player_name: String -> Name of a Player object
        """
        ocean_lines = self.ocean.__str__().split('\n')
        Game.versteck_alle_schiffe(self.opponent_ocean)
        ocean2_lines = self.opponent_ocean.__str__().split('\n')
        Game.zeig_alle_schiffe(self.opponent_ocean)
        width = (self.ocean.board_width - 1) * 3
        table_names = 'Dein Ozean: ' + ' ' * width + 'Ozean des Gegners:'

        print('[ Dran ist: ', player_name, ']', '\n', table_names)
        print("Spielstand: Deine Schiffe - ", self.ships_alive, "           Gegner-Schiffe - ", self.opp_ships_alive)
        print()
        for i in range(0, len(ocean_lines)):
            print(ocean_lines[i] + '     ' + ocean2_lines[i])

    def schuss_ergebnis(self, positions):
        """
        Bei einem Fehlschuss wird die Stelle als '0' markiert
        Bei einem Treffer wird 'ShipSquare' zu 'OceanSquare'
        :param positions: int, int -> Tuple mit abgeschossener Position
        Change the sign of a square to '0' if you miss or change the ShipSquare to OceanSquare if you hit.
        :param positions: int, int -> Tuple with shooted position
        """  # reverse weil looks good
        # row           column
        if not isinstance(self.opponent_ocean.board[positions[0]][positions[1]],
                          ShipSquare):  # if not shipsquare dann 0
            self.opponent_ocean.board[positions[0]][positions[1]].change_sign('0 ')
            self.fired += 1
            print('Schuss verfehlt!')
            return False
        else:
            self.opponent_ocean.board[positions[0]][positions[1]] = OceanSquare('X ')  # hitbox change
            self.fired += 1
            print('Treffer! :)')
            return True  # because hit

    def __str__(self):  # definen damit name geprintet wird, sonst unnoetige sachen
        return self.name


## Mehrspieler Klasse, welche die Spielklasse vererbt bekommt
#
# MULTIPLAYER GAME CLASS INHERITED FROM GAME CLASS
class MultiPlayerGame(Game):  # childclass

    def __init__(self, player_name_1, player_name_2, ocean_width, ocean_height):

        self.board_width = ocean_width
        self.board_height = ocean_height
        self.ocean_player_1 = Ocean(self.board_height, self.board_width)
        self.ocean_player_2 = Ocean(self.board_height, self.board_width)
        self.player1 = Player(player_name_1, self.ocean_player_1, self.ocean_player_2)
        self.player2 = Player(player_name_2, self.ocean_player_2, self.ocean_player_1)
        self.ship_signs_player_1 = ["CA", "BS", "CR", "SU", "DE"]
        self.ship_signs_player_2 = ["CA", "BS", "CR", "SU", "DE"]

    def set_configuarations(self):
        os.system(terminal_clear)
        self.platziere_schiffe_in_spielfeld(self.player1, self.board_height, self.board_width)
        os.system(terminal_clear)
        self.platziere_schiffe_in_spielfeld(self.player2, self.board_height, self.board_width)
        os.system(terminal_clear)

    def player1_move(self, pipe_conn):
        turn = '-1'
        p_output, p_input = pipe_conn #pipe
        while True:
            if turn != '0':
                turn = p_output.recv() #get input from pipe
            if turn == '0': # if pipe has 0, it means its player 1's turn
                self.player1.player_turn(self.player1.name)
                hit_position = self.user_input_bekommen(self.board_width, self.board_height)
                os.system(terminal_clear)
                print('In Process 1 for Player 1 moves')
                is_hit = self.player1.schuss_ergebnis(hit_position)

                # for each ship
                for sign in self.ship_signs_player_2:
                    if self.check_ob_ein_schiff_kaputt(sign, self.ocean_player_2):
                        self.ship_signs_player_2.remove(sign)
                        self.player1.opp_ships_alive -= 1
                        self.player2.ships_alive -= 1
                        print("Feindschiff: " + sign + " ist gesunken!")

                if not is_hit:
                    input('Computer an Spieler 2 übergeben und Enter drücken')
                    os.system(terminal_clear)

                is_win = self.check_ob_alle_schiffe_kaputt(self.ocean_player_2)

                if is_win is True:
                    win = str(
                        "\n\n" + '----------------------------------' + "\n" + self.player1.name + ' gewinnt das Spiel! Glückwunsch! :)' + "\n" + '----------------------------------' + "\n\n")
                    print(win)
                    input('Enter drücken, um fortzufahren.')
                    p_input.send('Terminate') #tell child to end as well using pipe
                    break #end process

                if is_hit is True:
                    continue
                else:
                    p_input.send('1') #send 1 on pipe to tell that its player 2's turn now
                    turn = '-1'

            elif turn == 'Terminate':
                break #end process

    def player2_move(self, pipe_conn):
        turn = '-1'
        sys.stdin = open(0) #opening a standard input stream for child process
        p_output, p_input = pipe_conn # pipe
        p_input.send('0') # sending 0 on pipe, telling it that the first turn is parent's or player 1's
        while True:
            if turn != '1':
                turn = p_output.recv() #get input from piple
            if turn == '1': # if pipe has 1, it means its player 2's turn
                self.player2.player_turn(self.player2.name)
                hit_position = self.user_input_bekommen(self.board_width, self.board_height)
                os.system(terminal_clear)
                print('In Process 2 for Player 2 moves')
                is_hit = self.player2.schuss_ergebnis(hit_position)

                for sign in self.ship_signs_player_1:
                    if self.check_ob_ein_schiff_kaputt(sign, self.ocean_player_1):
                        self.ship_signs_player_1.remove(sign)
                        self.player1.ships_alive -= 1
                        self.player2.opp_ships_alive -= 1
                        print("Feindschiff: " + sign + " ist gesunken!")

                if not is_hit:
                    input('Computer an Spieler 1 übergeben und Enter drücken')
                    os.system(terminal_clear)
                is_win = self.check_ob_alle_schiffe_kaputt(self.ocean_player_1)

                if is_win is True:
                    win = str(
                        "\n\n" + '----------------------------------' + "\n" + self.player2.name + ' gewinnt das Spiel! Glückwunsch! :)' + "\n" + '----------------------------------' + "\n\n")
                    print(win)
                    input('Enter drücken, um fortzufahren.')
                    p_input.send('Terminate') #tell parent to end as well using pipe
                    break # end process

                if is_hit is True:
                    continue
                else:
                    p_input.send('0') #send 0 on pipe to tell that its player 1's turn now
                    turn = '-1'

            elif turn == 'Terminate':
                break #end process


# Main-Funktion
def main():
    """
    Es geht um die Menu-Optionen
    Handle menu options
    """
    os.system(terminal_clear)

    while True:
        os.system(terminal_clear)

        option = input('''
                 | ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~  Schiffe-Versenken  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ |  

                                         ,__                 ,__
                                         |__|>               |__|>
                                         |                   |
                                         |                   |
                    _______              |                   |              _______             
                    \-_-_-_\_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_/_-_-_-/ 
                        \=====================================================/          
                                \====================================/
                                         \==================/

Option auswählen:
(1) Multiplayer (P vs P)
(2) Spiel verlassen
''')

        if option == '1':
            os.system(terminal_clear)

            player_name1 = input('Name des 1. Spielers eingeben:  ')
            player_name2 = input('Name des 2. Spielers eingeben:  ')

            multiplayer_game = MultiPlayerGame(player_name1, player_name2, args.x, args.y)
            multiplayer_game.set_configuarations()

            start_time = time()
            p_output, p_input = Pipe() #creating a new pipe

            process_player2 = Process(target=multiplayer_game.player2_move, args=((p_output, p_input),)) #child process, will run player 2 turns
            process_player2.start() # starting child process

            multiplayer_game.player1_move((p_output, p_input)) # parent process, will run player 1 turns

            process_player2.join() #process 2 finished
            p_output.close()
            p_input.close()
            end_time = time() - start_time

            print('Game run time is: ', end_time)

        elif option == '2':
            os.system(terminal_clear)
            exit("Danke für's spielen.")


if __name__ == "__main__":  # für arguments in terminal

    parser = argparse.ArgumentParser()
    parser.add_argument("-x", required=True, type=int)
    parser.add_argument("-y", required=True, type=int)

    args = parser.parse_args()
    main()