import random, msvcrt as m
from time import sleep
import os
clear = lambda: os.system('cls')

CELLS = [
    (0,0),(1,0),(2,0),(3,0),(4,0),
    (0,1),(1,1),(2,1),(3,1),(4,1),
    (0,2),(1,2),(2,2),(3,2),(4,2),
    (0,3),(1,3),(2,3),(3,3),(4,3),
    (0,4),(1,4),(2,4),(3,4),(4,4),
  ]

MOVES = {"q": (-1,-1), "w": (0, -1), "e": (1, -1),
        "a": (-1, 0), "d": (1,0),
        "z": (-1,1), "x": (0,1), "c": (1,1)}

MOVE_INPUT = {"q","w","e","a","d","z","x","c"}

class Game:
    def __init__(self):
        self.p = Player()
        self.e1 = Egg()
        self.e2 = Egg()
        self.e3 = Egg()
        self.m = Monster()
        self.d = Door()
        self.b = Basket()        
        self.tokens = [self.e1 , self.e2 , self.e3 , self.p , self.m, self.d, self.b]
        self.board = dict.fromkeys(CELLS,[])
        self.assignSpaces()
        self.moveInvalid = False
        self.game_over = False
        self.play_again = 'y'
        self.messages = ''   
                                
    def assignSpaces(self):
        available_spaces = CELLS.copy()
        for token in self.tokens:
            token.position = random.choice(available_spaces)
            self.board[token.position] = self.board[token.position] + [token]
            available_spaces.remove(token.position)
                
    def display_interface(self):
        clear()
        self.display_items()
        self.draw_map()
        self.display_messages()
        self.player_move()
        
    def draw_map(self):
        print("|"+"-"*19+"|")
        print("|"+ " ".join( [self.get_space(cell) for cell in [CELLS[i] for i in range(5)]]) +"|", end="")
        print("\n|"+"- -|"*5)
        print("|"+ " ".join( [self.get_space(cell) for cell in [CELLS[i] for i in range(5,10)]]) +"|", end="")
        print("\n|"+"- -|"*5)
        print("|"+ " ".join( [self.get_space(cell) for cell in [CELLS[i] for i in range(10,15)]]) +"|", end="")
        print("\n|"+"- -|"*5)
        print("|"+ " ".join( [self.get_space(cell) for cell in [CELLS[i] for i in range(15,20)]]) +"|", end="")
        print("\n|"+"- -|"*5)
        print("|"+ " ".join( [self.get_space(cell) for cell in [CELLS[i] for i in range(20,25)]]) +"|", end="")
        print()
        print("|"+"-"*19+"|")
    
    def get_space(self, pos):
        if len(self.board) != 2:
            return "".join([token.rep for token in self.board[pos][::-1] if token.visible]).center(3)
        else:
            return " ".join([token.rep for token in self.board[pos][::-1] if token.visible])
    
    def player_move(self):
        while True:
            clear()
            self.display_items()
            self.draw_map()
            self.display_messages()      
            print()
            print("[q] [w] [e]     \u2196 \u2191 \u2197")
            print("[a]     [d]  =  \u2190   \u2192")
            print("[z] [x] [c]     \u2199 \u2193 \u2198")         
            move = input("\nChoose where to move: ").lower()
            if move not in MOVE_INPUT:
                print("I didn't recognize that as a direction.")
                sleep(3)
                continue
            new_position = self.calc_new_position(self.p, MOVES[move])
            if self.valid_move(new_position):
                self.moveInvalid = False
                self.update_board(self.p, new_position)
                self.detect_collision()
            else: 
                self.moveInvalid = True
                self.messages += 'Invalid move. Try again.'   
                continue         
            break
                    
    def calc_new_position(self, token, move):
        return tuple(map(sum, zip(token.position, move)))
            
    def valid_move(self, new_position):
        for p in new_position:
            if not 0 <= p < 5:
                return False
        return True
    
    def monster_move(self):
        moved = False
        while not moved:
            move = random.choice(list(MOVES.values()))
            new_position = self.calc_new_position(self.m, move)
            if self.valid_move(new_position):
                self.update_board(self.m, new_position)
                self.detect_collision()
                moved = True
    
    def update_board(self, token, new_position):
        self.remove_token(token)
        token.move(new_position)
        self.board[new_position] = self.board[new_position] + [token]
    
    def remove_token(self, token):
        self.board[token.position] = list(filter(lambda x: x != token, self.board[token.position]))
    
    def detect_collision(self):
        self.messages = ''
        if len(self.board[self.p.position]) > 1:
            # announce object found
            for token in self.board[self.p.position]:
                if token != self.p:
                    self.messages += f"There's {token.i_article} {token.name} here!"
            # switch visibility to true for token(s)
                    token.found()
            # if basket, has_basket = True
                if token.name == "monster":
                    self.die()
                if token.name == "basket":
                    self.find_basket()
                    self.remove_token(token)
                if token.name == "egg":
                    if self.p.has_basket:
                        self.p.eggs += 1
                        self.remove_token(token)
                if token.name == "door":
                    if self.p.eggs == 3:
                        self.win()
        
    def display_items(self):
        print(f"Basket: {'Yes' if self.p.has_basket else 'No'}", end = "   ")
        print(f"Eggs: {self.p.eggs}")
    
    def display_messages(self):
        if self.messages:
            print()
            print(self.messages)
            print()
    
    def find_basket(self):
        clear()
        self.p.has_basket = True
        self.display_items()
        self.draw_map()
        self.display_messages()
        self.wait()
                        
    def die(self):
        clear()
        self.display_items()
        self.draw_map()
        print("Oops, the monster found you and ripped you limb from limb! \nI'll spare you the remainder of the gory details and just conclude by saying you lost.")
        while True:
            self.play_again = input('\nWould you like to play again? (y/n)? ').lower()
            if self.play_again in ['y', 'n']:
                break
            else:
                print('That wasn\'t a "y" or "n"') 
        self.game_over = True
    
    def win(self):
        clear()
        self.display_items()
        self.draw_map()
        print('\nHorray! You won. You will be forever more known as "3-eggs, the Eggy"! ')
        while True:
            self.play_again = input('\nWould you like to play again? (y/n)? ').lower()
            if self.play_again in ['y', 'n']:
                break
            else:
                print('That wasn\'t a "y" or "n"')            
        self.game_over = True
        
    def wait(self):
        print("\nPress any key to continue...")
        m.getch()
    
class Token:
    def __init__(self):
        self.rep = ''
        self.position = ('','')
        self.visible = False
        self.name = ''
        self.i_article = "a"
    
class Findable():
    def found(self):
        self.visible = True
    
class Movable():        
    def move(self, position):
        self.position = position
    
class Player(Token,Movable):
    def __init__(self):
        super().__init__()
        self.rep = 'P'
        self.name = "player"
        self.has_basket = False
        self.eggs = 0
        self.visible = True

class Monster(Token,Movable,Findable):
    def __init__(self):
        super().__init__()
        self.rep = 'M'
        self.name = "monster"

class Egg(Token, Findable):
    def __init__(self):
        super().__init__()
        self.rep = 'O'
        self.i_article = "an"
        self.name = "egg"

class Basket(Token, Findable):
    def __init__(self):
        super().__init__()
        self.rep = 'U'
        self.name = "basket"

class Door(Token, Findable):
    def __init__(self):
        super().__init__()
        self.rep = 'D'
        self.name = "door"


def run():
    new_game = True
    while new_game or game.play_again == 'y':
        game = Game()
        new_game = False
        while True:
            clear()
            game.player_move()
            if game.game_over:
                break   
            game.monster_move()
            if game.game_over:
                break  

run()