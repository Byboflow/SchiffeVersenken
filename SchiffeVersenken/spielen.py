import abc
import argparse
import os
from multiprocessing import Process, Pipe       # interprozess kommunikation
from copy import deepcopy
from msvcrt import getch
from time import time
from structures import *
import sys

terminal_clear = 'cls'       # um den terminal zu saeubern


# Tastatur-Input bekommen
def key_getch():
    """
    ch: Eingabe des Nutzers
    Key vom User bekommen und returnen
    """
    while True:  # jede taste hat seinen eigenen ASCII-Code
        key = ord(getch())  # ord aendert ein object zu unicode
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
        elif key == 113:
            return 'q'
        elif key == 114:
            return 'r'
        else:
            return '0'


## SPIEL KLASSE
class Spiel():

    def __init__(self):  # leerer constructor, skeletton code
        ...

    @abc.abstractmethod  # pairing klasse
    def start_game(self):
        pass

    @staticmethod  # static. es kann ausserhalb der klasse benutzt werden
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
        while True:  # schleife umd zu wdh bei falscher Eingabe
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
        :param Ocean: Ozean Object
        :return: bool -> "False" wenn das Schiff nicht zerstört ist. Sonst "True"
        """
        for row in Ocean.board:  # board = spielfeld
            for square in row:  # square = ein feld
                if square.sign == ship_sign.upper():  # wenn das schiff im square ist
                    return False
        return True

    @staticmethod
    def check_ob_alle_schiffe_kaputt(ocean: Ocean):  # ocean ist das object der ocean klasse (in structures.py)
        """
        Methode um zu sehen, ob bestimmte Schiffe zerstört sind
        :param Ocean: Ozean Object
        :return: bool -> "False" wenn das Schiff nicht zerstört ist. Sonst "True"
        """
        for row in ocean.board:
            for square in row:
                if isinstance(square, ShipSquare):  # falls sich im square ein schiff befindet
                    return False
        return True  # wenn alle schiffe zerstört sind

    def platziere_schiffe_in_spielfeld(self, player, height, width):  # nicht static
        """
        Methode um alle Schiffe ins Spielfeld zu plazieren
        :param player: Spieler-Instanz
        """
        ships = ['Carrier', 'Battleship', 'Cruiser', 'Submarine', 'Destroyer']
        movement_keys = ['w', 's', 'a', 'd']
        decoy_ocean = Ocean(height, width)  # temporäre schiffe, um sich zu bewegen
        decoy = Player('decoy', decoy_ocean, player.ocean)

        print('Platzier-Modus:\n' + str(player) + "'s Spielfeld")
        print(decoy.ocean)

        reset = 0
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

            while True:  # schleife, um objekte zu platzieren
                decoy.ocean.board = deepcopy(player.ocean.board)
                os.system(terminal_clear)  # terminal saeubern
                decoy.tu_schiff_aufs_brett(ships[0], is_horizontal, starting_position, True)  # decoy, weil vor 'p' nichts sicher ist
                print('Platzier-Modus: \n' + str(player) + "'s Spielfeld")
                print(decoy.ocean)

                print(
                    'Benutze W,A,S,D um das Schiff zu bewegen, dann P um es zu platzieren. Mit R kann neu gestartet werden. Mit Q kann abgebrochen werden.')

                move_ship = key_getch()
                if move_ship in movement_keys:      #  checken, ob die wsad tasten benutzt werden
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
                    reset = 1
                    player.ocean = Ocean(height, width)     # neuer ozean
                    os.system(terminal_clear)
                    self.platziere_schiffe_in_spielfeld(player, height, width)
                    break

                else:
                    print('Falsche Eingabe!')
            
            if reset == 1:
                break           # wenn das nicht geschieht, dann platziert man fehlerhafterweise mehr als 5 Schiffe
        
        print("Fertig!!!")

    @staticmethod
    def schiffe_bewegen(is_horizontal, position, ship_type, move_ship, height, width):
        """
        Methode dient dazu, die Schiffe auf dem Spielfeld zu bewegen (mit WASD-Tasten)

        :param is_horizontal: bool - > Ist unser Schiff horizontal?
        :param position: list -> Liste, die die Startposition beschreibt
        :param ship_type: str -> Typ des Schiffs
        :param move_ship: str -> Richtung
        :return: None
        """

        position = list(position)  # tuple zu list
        ships_lengths = {'Carrier': 5, 'Battleship': 4, 'Cruiser': 3, 'Submarine': 2, 'Destroyer': 1}
        ship_length = ships_lengths[ship_type]
        if is_horizontal:
            if move_ship == 'w':
                if position[1] > 1:  # 0 col 1 row
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

        position = tuple(position)  # list zu tuple, position kann später nicht geändert werden

        return position

    @staticmethod
    def versteck_alle_schiffe(Ocean):
        """
        Methode, um die Schiffe vom Spielfeld zu verstecken
        (Es sollen schließlich nicht die Schiffe des Feindes gesehen werden)

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

    """

    def __init__(self, name, ocean, opponent_ocean):  # init: constructor
        """
        :param name: String -> Name des Spielers
        :param is_human: bool -> True, wenn er ein Mensch ist, sonst false
        :param ocean: Ocean -> Ozean des Spielers
        :param opponent_ocean: Ocean -> Ozean des Gegenspielers
        """
        self.name = name  # vom spieler
        self.ocean = ocean
        self.opponent_ocean = opponent_ocean
        #  self.name = name
        self.fired = 0
        self.ships_alive = 5
        self.opp_ships_alive = 5

    def tu_schiff_aufs_brett(self, ship_name, is_horizontal, starting_point, is_decoy=False):
        """
        Schiff-Objekt generieren und auf dem Spielfeld platzieren
        :param ship_name: String -> Name eines Schiffs
        :param is_horizontal: bool -> True, wenn das Schiff horizontal ist, sonst false
        :param starting_point: int, int -> Tuple mit Startpunkt eines Schiffs (Reihe, Spalte)
        :param is_decoy: bool -> True, wenn das Schiff [...] , sonst false
        """
        eval(ship_name)(self.ocean, is_horizontal, starting_point, is_decoy)

    def player_turn(self, player_name):
        """

        Spielfelder abbilden (von beiden Spielern)
        :param player_name: String -> Name eines Spieler-Objekts

        """
        ocean_lines = self.ocean.__str__().split('\n')
        Spiel.versteck_alle_schiffe(self.opponent_ocean)
        ocean2_lines = self.opponent_ocean.__str__().split('\n')
        Spiel.zeig_alle_schiffe(self.opponent_ocean)
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
       
        """  # reverse, weil sieht gut aus
        # row           column
        if not isinstance(self.opponent_ocean.board[positions[0]][positions[1]],
                          ShipSquare):  # wenn kein shipsquare, dann 0
            self.opponent_ocean.board[positions[0]][positions[1]].change_sign('0 ')
            self.fired += 1
            print('Schuss verfehlt!')
            return False
        else:
            self.opponent_ocean.board[positions[0]][positions[1]] = OceanSquare('X ')  # hitbox change
            self.fired += 1
            print('Treffer! :)')
            return True  # weil hit

    def __str__(self):  # definieren, damit der name gezeigt wird, sonst kommen unnoetige/komische sachen
        return self.name



## mehrspieler klasse, welche die spielklasse vererbt bekommt
#
class MultiPlayerSpiel(Spiel):  # childclass

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
        p_output, p_input = pipe_conn # pipe
        while True:
            if turn != '0':
                turn = p_output.recv() # input vom pipe bekommen
            if turn == '0': # wenn pipe = 0, dann ist spieler 1 dran
                self.player1.player_turn(self.player1.name)
                hit_position = self.user_input_bekommen(self.board_width, self.board_height)
                os.system(terminal_clear)
                is_hit = self.player1.schuss_ergebnis(hit_position)

                # für jedes Schiff
                for sign in self.ship_signs_player_2:
                    if self.check_ob_ein_schiff_kaputt(sign, self.ocean_player_2):
                        self.ship_signs_player_2.remove(sign)
                        self.player1.opp_ships_alive -= 1       # ein feindschiff weniger
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
                    p_input.send('Terminate') # dem child sagen, es soll enden (mit pipes)
                    break # prozess beenden

                if is_hit is True:
                    continue
                else:
                    p_input.send('1') # dem pipe '1' senden, somit ist jetzt spieler 2 dran
                    turn = '-1'

            elif turn == 'Terminate':   # hier wird gecheckt, ob dem child 'terminate' gesagt wurde (zeile 393)
                break # prozess beenden

    def player2_move(self, pipe_conn):      # ähnlich wie davor
        turn = '-1'
        sys.stdin = open(0) #standard input stream für child process öffnen, neuer input buffer
        p_output, p_input = pipe_conn # pipe
        p_input.send('0') # 0 auf der pipe senden, sagt aus, dass spieler 1 als erstes dran ist
        while True:
            if turn != '1':
                turn = p_output.recv() # input vom pipe bekommen
            if turn == '1': # wenn pipe = 1, dann ist Spieler 2 dran
                self.player2.player_turn(self.player2.name)
                hit_position = self.user_input_bekommen(self.board_width, self.board_height)
                os.system(terminal_clear)
                is_hit = self.player2.schuss_ergebnis(hit_position)

                for sign in self.ship_signs_player_1:
                    if self.check_ob_ein_schiff_kaputt(sign, self.ocean_player_1):
                        self.ship_signs_player_1.remove(sign)
                        self.player1.ships_alive -= 1           # alles wie davor nur andersrum
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
                    p_input.send('Terminate') #parent mit pipe-input sagen, es soll terminieren
                    break # process beenden

                if is_hit is True:
                    continue
                else:
                    p_input.send('0') # der pipe '0' senden um zu sagen, dass spieler 1 jetzt dran ist
                    turn = '-1'

            elif turn == 'Terminate':      # selbes Spiel wie davor :)
                break # prozess beenden


# Main-Funktion
def main():
    """
    Es geht um die Menu-Optionen

    """


    while True:
      #  os.system(terminal_clear)

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

            multiplayer_game = MultiPlayerSpiel(player_name1, player_name2, args.x, args.y)
            multiplayer_game.set_configuarations()

            start_time = time()
            p_output, p_input = Pipe() # neue pipe erstellen

            process_player2 = Process(target=multiplayer_game.player2_move, args=((p_output, p_input),)) # child process, wird die spielzüge von spieler 2 ausführen
            process_player2.start() # start des child process

            multiplayer_game.player1_move((p_output, p_input)) # parent process, wird die spielzüge von spieler 1 ausführen

            process_player2.join() # prozess 2 ende
            p_output.close()
            p_input.close()
            end_time = time() - start_time

            print('Dauer des Spiels: ', end_time, ' Sekunden' + '\n')

        elif option == '2':
            os.system(terminal_clear)
            exit("Danke für's spielen.")


if __name__ == "__main__":  # für arguments in terminal

    parser = argparse.ArgumentParser()
    parser.add_argument("-x", required=True, type=int)
    parser.add_argument("-y", required=True, type=int)

    args = parser.parse_args()
    main()
    
