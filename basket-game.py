import random, msvcrt as m
from time import sleep
import os
clear = lambda: os.system('cls')

# CELLS = [
#     (0,0),(1,0),(2,0),(3,0),(4,0),
#     (0,1),(1,1),(2,1),(3,1),(4,1),
#     (0,2),(1,2),(2,2),(3,2),(4,2),
#     (0,3),(1,3),(2,3),(3,3),(4,3),
#     (0,4),(1,4),(2,4),(3,4),(4,4),
#   ]

MOVES = {"q": (-1,-1), "w": (0, -1), "e": (1, -1),
        "a": (-1, 0), "d": (1,0),
        "z": (-1,1), "x": (0,1), "c": (1,1)}

class Game:
    def __init__(self, board_size = 5):
        self.game_over = False
        self.play_again = 'y'
        self.messages = ''   
        self.p = Player()
        self.e1 = Egg()
        self.e2 = Egg()
        self.e3 = Egg()
        self.m = Monster()
        self.d = Door()
        self.b = Basket()        
        self.tokens = [self.e1 , self.e2 , self.e3 , self.p , self.m, self.d, self.b]
        self.board = Board(board_size)
        self.assign_token_spaces()
                                
    def assign_token_spaces(self):
        for token in self.tokens:
            self.board.assign_unoccupied_cell(token)
    
    def player_move(self):
        while not self.game_over:
            self.display_interface()     
            print()
            print("[q] [w] [e]     \u2196 \u2191 \u2197")
            print("[a]     [d]  =  \u2190   \u2192")
            print("[z] [x] [c]     \u2199 \u2193 \u2198")         
            move = input("\nChoose where to move: ").lower()
            if move not in MOVES:
                self.messages = "\nI didn't recognize that as a direction."
                continue
            move = MOVES[move]
            
            if move not in self.p.valid_moves(self.board.size):
                self.messages = "You can't move there because you don't have the power to pass through walls. \nAnd also, where would you be if not in this beautiful dungeon?\n"
                continue
            else:
                self.board.update_token_position(self.p, move)
                self.board.detect_collisions(self.p, self)      

    def monster_move(self):
        move = random.choice(self.m.valid_moves())
        self.board.update_token_position(self.m, move)
        self.board.detect_collisions(self.m, self)
            
    def display_interface(self): 
        if self.messages:
            clear()
            self.display_items()
            self.board.draw_map()
            self.display_messages()
            self.wait()
            self.messages = ''        
        clear()    
        self.display_items()
        self.board.draw_map()
        self.display_messages()
            
    def display_items(self):
        print(f"Basket: {'Yes' if self.p.has_basket else 'No'}", end = "   ")
        print(f"Eggs: {self.p.eggs}")
    
    def display_messages(self):
        if self.messages:
            print()
            print(self.messages)
                            
    def game_end(self):
        while True:
            self.play_again = input('\nWould you like to play again? (y/n)? ').lower()
            if self.play_again in ['y', 'n']:
                break
            else:
                print('That wasn\'t a "y" or "n"') 
                self.wait()
        self.game_over = True        
        
    def wait(self):
        print("\nPress any key to continue...")
        m.getch()
    
class Board:
    def __init__(self, size) -> None:
        self.size = size
        self.cell_arr = self.create_cell_arr()
        self.cells = self.create_cells()
        self.occupied_cells = set()
        self.unoccupied_cells = set(self.cells)
        
    def create_cells(self):
        return {cell: set() for cell in self.cell_arr}
        
    def create_cell_arr(self):
        return [(x,y)
                for y in range(self.size) 
                for x in range(self.size)]
    
    def assign_unoccupied_cell(self, token):
        cell = random.choice(list(self.unoccupied_cells))
        self.occupied_cells.add(cell)
        self.unoccupied_cells.remove(cell)
        self.place_token(token, cell)
        
    def draw_map(self):
        separator = "\n|"+"- -|"*self.size
        rows = []
        for row in range(self.size):
            
            rows.append("\n|"+ 
                        " ".join( [self.get_space(cell) 
                                   for cell in [
                self.cell_arr[i] for i in range(row*self.size,(row+1)*self.size)
                ]]) +"|")
            
        print("|"+"-"*(self.size*4-1)+"|", end = "")            
        print(separator.join(rows))
        print("|"+"-"*(self.size*4-1)+"|")
    
    def get_space(self, cell):
        if len(self.cells[cell]) == 2:
            return " ".join([token.rep for token in self.cells[cell] if token.visible]).center(3)
        else:
            return "".join([token.rep for token in self.cells[cell] if token.visible]).center(3)

    def update_token_position(self, token, move):
        """ removes token from old position and adds it to new position (on board)
        also updates position attribute of token"""
        cell = (token.position[0] + move[0], token.position[1] + move[1])
        self.remove_token(token)
        self.place_token(token,cell)

    def detect_collisions(self, token, game):
        """resets messages since all messages rendered after collision"""
        self.messages = ''
        if len(self.cells[token.position]) > 1:
            other_tokens = self.cells[token.position] - {token}
            # for all tokens 
            for other_token in other_tokens:
            # call collision method - 
                    other_token.collision(token, game)

    def remove_token(self, token):
        self.cells[token.position].remove(token)
    def place_token(self, token, cell):
        self.cells[cell].add(token)
        token.place(cell)

class Token:
    def __init__(self):
        self.rep = ''
        self.position = ('','')
        self.visible = False
        self.name = ''
        self.i_article = "a"
        
    def place(self, cell):
        self.position = cell

class Movable():
    possible_moves = [(x,y) for x in range(-1,2) for y in range(-1,2) if not (x == 0 and y == 0)]
    def __init__(self, position):
        self.position = position
    
    def valid_moves(self, board_size):
        """returns list of valid moves (-1,0), etc"""
        valid_moves = set()
        for (x,y) in self.possible_moves:
            if 0 <=x + self.position[0] < board_size \
            and 0 <= y + self.position[1] < board_size:
                valid_moves.add((x,y))
        return valid_moves
    
class Findable():
    def __init__(self) -> None:        
        self.visible = False
    def found(self):
        self.visible = True

class Player(Token, Movable):
    def __init__(self):
        super().__init__()
        self.rep = 'P'
        self.name = "player"
        self.has_basket = False
        self.eggs = 0
        self.visible = True

class Monster(Token, Movable, Findable):
    def __init__(self):
        super().__init__()
        self.rep = 'M'
        self.name = "monster"
    def collision(self, token, game):
        if token.name == "player":
            self.found()
            game.messages += "Oops, the monster found you and ripped you limb from limb! \nI'll spare you the remainder of the gory details and just conclude by saying you lost."
            game.display_interface()
            game.game_end()

class Egg(Token, Findable):
    def __init__(self):
        super().__init__()
        self.rep = 'O'
        self.i_article = "an"
        self.name = "egg"
    def collision(self, token, game):
        if token.name == 'player':
            if not self.visible:
                self.found()
                game.messages += 'You found an egg!'
                if token.has_basket:
                    game.messages += '\n\n... and you put it in your basket!'
                    game.display_interface()
                    game.board.remove_token(self)
                    token.eggs += 1
                else:
                    game.messages += '\n\n... but you don\'t have a basket!'
                    game.display_interface()
            else:
                game.messages += 'You put an egg in your basket!'
                game.display_interface()
                game.board.remove_token(self)
                token.eggs += 1
                
class Basket(Token, Findable):
    def __init__(self):
        super().__init__()
        self.rep = 'U'
        self.name = "basket"
    def collision(self, token,game):
        if token.name == 'player':
            self.found()
            game.messages += 'You found a basket!'
            game.display_interface()
            token.has_basket = True
            game.board.remove_token(self)

class Door(Token, Findable):
    def __init__(self):
        super().__init__()
        self.rep = 'D'
        self.name = "door"
    def collision(self,token,game):
        if token.name == 'player':
            if not self.visible:
                game.messages ='You found a door!'
            self.found()
            if token.eggs == 3:
                game.messages +='Horray! You won. You will be forever more known as "3-eggs, the Eggy"!'
                game.display_interface()
                game.game_end()
            else:
                game.messages +='\n\n... but you don\'t have all three eggs!'

def run():
    new_game = True
    while new_game or game.play_again == 'y':
        while True:
            size = input('What size board would you like to play on? (3-9) ')
            if size in ['3','4','5','6','7','8','9']:
                size = int(size)
                break
        game = Game(size)
        new_game = False
        while True:
            game.player_move()
            if game.game_over:
                break
            game.monster_move()
            if game.game_over:
                break

run()