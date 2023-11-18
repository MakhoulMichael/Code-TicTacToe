import copy
import sys
import pygame
import numpy as np

from constants import *

# --- PYGAME SETUP ---

pygame.init()
screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
pygame.display.set_caption('TIC TAC TOE AI_minimax')
screen.fill( BG_COLOR )

# --- CLASSES ---

class Board:

    def __init__(self):
        self.squares = np.zeros( (ROWS, COLS) )
        self.empty_sqrs = self.squares # [squares]
        self.marked_sqrs = 0

    def final_state(self, show=False):
        '''
            @return 0 if there is no win yet
            @return 1 if player 1 wins
            @return 2 if player 2 wins
        '''

        # vertical wins
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[0][col] == 2 else CROSS_COLOR
                    iPos = (col * SQSIZE + SQSIZE // 2, 20)
                    fPos = (col * SQSIZE + SQSIZE // 2, HEIGHT - 20)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[0][col]

        # horizontal wins
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[row][0] == 2 else CROSS_COLOR
                    iPos = (20, row * SQSIZE + SQSIZE // 2)
                    fPos = (WIDTH - 20, row * SQSIZE + SQSIZE // 2)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[row][0]

        # desc diagonal
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, 20)
                fPos = (WIDTH - 20, HEIGHT - 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        # asc diagonal
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, HEIGHT - 20)
                fPos = (WIDTH - 20, 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        # no win yet
        return 0


        
    

    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        empty_sqrs = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_sqr(row, col):
                    empty_sqrs.append( (row, col) )
        
        return empty_sqrs

    def isfull(self):
        return self.marked_sqrs == 9

    def isempty(self):
        return self.marked_sqrs == 0

class AI_minimax:

    def __init__(self, player=2):
        self.player = player


    # --- MINIMAX ---

    def minimax(self, board, maximizing): #dispatch 
        
        # terminal case
        case = board.final_state()

        # player 1 wins
        if case == 1:
            return 1, None # eval, move

        # player 2 wins
        if case == 2:
            return -1, None

        # draw
        elif board.isfull():
            return 0, None

        if maximizing:
            return self.max(board)

        else:
            return self.min(board)
        
    def max(self, board):
        max_eval = -100
        best_move = None
        empty_sqrs = board.get_empty_sqrs()

        for (row, col) in empty_sqrs:
            temp_board = copy.deepcopy(board)
            temp_board.mark_sqr(row, col, 1)
            eval = self.minimax(temp_board, False)[0]
            if eval > max_eval:
                max_eval = eval
                best_move = (row, col)
        return max_eval, best_move
        
        
    def min(self, board):  
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)
            return min_eval, best_move
        
    

    # --- MAIN EVAL ---

    def eval(self, main_board):

            # minimax algo choice
            eval, move = self.minimax(main_board, False)

            print(f'AI_minimax has chosen to mark the square in pos {move} with an eval of: {eval}')

            return move # row, col

class AI_DLS:
    def __init__(self,  player=2):
        self.player = player

    def set_depth(self):
        chosen_depth = int(input("What depth? "))
        self.depth = chosen_depth

    # --- MAIN EVAL ---

    def eval(self, main_board):
        # Perform depth-limited search
        _, move = self.dls(main_board, self.depth, False)
        print(f'AI_DLS has chosen to mark the square in pos {move}')
        return move

    def dls(self, board, depth, maximizing):
        # Terminal case
        case = board.final_state()

        if case == 1:
            return 1, None

        if case == 2:
            return -1, None

        if board.isfull() or depth == 0:
            return 0, None

        if maximizing:
            return self.max_dls(board, depth)
        else:
            return self.min_dls(board, depth)

    def max_dls(self, board, depth):
        max_eval = -100
        best_move = None
        empty_sqrs = board.get_empty_sqrs()

        for (row, col) in empty_sqrs:
            temp_board = copy.deepcopy(board)
            temp_board.mark_sqr(row, col, 1)
            eval, _ = self.dls(temp_board, depth - 1, False)

            # Modify the evaluation to prioritize winning or blocking opponent
            eval += self.evaluate_move(temp_board, row, col)

            if eval > max_eval:
                max_eval = eval
                best_move = (row, col)
        return max_eval, best_move

    def min_dls(self, board, depth):
        min_eval = 100
        best_move = None
        empty_sqrs = board.get_empty_sqrs()

        for (row, col) in empty_sqrs:
            temp_board = copy.deepcopy(board)
            temp_board.mark_sqr(row, col, self.player)
            eval, _ = self.dls(temp_board, depth - 1, True)

            # Modify the evaluation to prioritize winning or blocking opponent
            eval += self.evaluate_move(temp_board, row, col)

            if eval < min_eval:
                min_eval = eval
                best_move = (row, col)
        return min_eval, best_move

    def evaluate_move(self, board, row, col):
        temp_board = copy.deepcopy(board)
        temp_board.mark_sqr(row, col, 1)
        
        # Check if the move leads to a win
        if temp_board.final_state() == 1:
            return 10  # Priority for winning

        temp_board.mark_sqr(row, col, self.player)
        
        # Check if the move blocks the opponent from winning
        if temp_board.final_state() == 2:
            return 9  # Priority for blocking opponent from winning

        return 0  # No immediate win or block

class AI_AlphaBeta:

    def __init__(self, player=2):
        self.player = player

    # --- MINIMAX WITH ALPHA-BETA PRUNING ---

    def minimax_alpha_beta(self, board, depth, maximizing, alpha, beta): 
        case = board.final_state()

        if case == 1:
            return 1, None 

        if case == 2:
            return -1, None

        if board.isfull():
            return 0, None

        if depth == 0:
            return self.evaluate(board), None

        if maximizing:
            return self.max_alpha_beta(board, depth, alpha, beta)

        else:
            return self.min_alpha_beta(board, depth, alpha, beta)

    def max_alpha_beta(self, board, depth, alpha, beta):
        max_eval = -100
        best_move = None
        empty_sqrs = board.get_empty_sqrs()

        for (row, col) in empty_sqrs:
            temp_board = copy.deepcopy(board)
            temp_board.mark_sqr(row, col, 1)
            eval = self.minimax_alpha_beta(temp_board, depth - 1, False, alpha, beta)[0]
            if eval > max_eval:
                max_eval = eval
                best_move = (row, col)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # beta cutoff
        return max_eval, best_move

    def min_alpha_beta(self, board, depth, alpha, beta):
        min_eval = 100
        best_move = None
        empty_sqrs = board.get_empty_sqrs()

        for (row, col) in empty_sqrs:
            temp_board = copy.deepcopy(board)
            temp_board.mark_sqr(row, col, self.player)
            eval = self.minimax_alpha_beta(temp_board, depth - 1, True, alpha, beta)[0]
            if eval < min_eval:
                min_eval = eval
                best_move = (row, col)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # alpha cutoff
        return min_eval, best_move

    def evaluate(self, board):
              # Check for wins
        winner = board.final_state()
        if winner == 1:
            return 10  # Player 1 wins, return a high score
        elif winner == 2:
            return -10  # Player 2 wins, return a low score

        # Check for potential wins in the next move
        for row in range(ROWS):
            for col in range(COLS):
                if board.empty_sqr(row, col):
                    temp_board = copy.deepcopy(board)
                    temp_board.mark_sqr(row, col, 1)
                    if temp_board.final_state() == 1:
                        return 1  # Player 1 can win in the next move
                    temp_board.mark_sqr(row, col, self.player)
                    if temp_board.final_state() == 2:
                        return -1  # Player 2 can win in the next move

        # If no one is about to win, return a neutral score
        return 0

    # --- MAIN EVAL ---

    def eval_alpha_beta(self, main_board, depth=3):
        eval, move = self.minimax_alpha_beta(main_board, depth, False, -100, 100)
        print(f'AI_AlphaBeta has chosen to mark the square in pos {move} with an eval of: {eval}')
        return move  # row, col

class Game:

    def __init__(self, opponent_choice):
        self.board = Board()
        self.player = 1
        self.running = True
        self.show_lines()

        if opponent_choice == '1':
            self.opponent = AI_minimax()
        elif opponent_choice == '2':
            
            self.opponent = AI_DLS()
            self.opponent.set_depth()
        elif opponent_choice=='3':
            
            self.opponent=AI_AlphaBeta()
        else:
            print("Invalid opponent choice. Exiting.")
            sys.exit()
            
    # --- DRAW METHODS ---

    def show_lines(self):
        # bg
        screen.fill( BG_COLOR )

        # vertical
        pygame.draw.line(screen, LINE_COLOR, (SQSIZE, 0), (SQSIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (WIDTH - SQSIZE, 0), (WIDTH - SQSIZE, HEIGHT), LINE_WIDTH)

        # horizontal
        pygame.draw.line(screen, LINE_COLOR, (0, SQSIZE), (WIDTH, SQSIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, HEIGHT - SQSIZE), (WIDTH, HEIGHT - SQSIZE), LINE_WIDTH)

    def draw_fig(self, row, col):
        if self.player == 1:
            # draw cross
            # desc line
            start_desc = (col * SQSIZE + OFFSET, row * SQSIZE + OFFSET)
            end_desc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH)
            # asc line
            start_asc = (col * SQSIZE + OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            end_asc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH)
        
        elif self.player == 2:
            # draw circle
            center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
            pygame.draw.circle(screen, CIRC_COLOR, center, RADIUS, CIRC_WIDTH)

    # --- OTHER METHODS ---

    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()

    def next_turn(self):
        self.player = self.player % 2 + 1

    def change_gamemode(self):
        self.gamemode = 'ai' if self.gamemode == 'pvp' else 'pvp'

    def isover(self):
        return self.board.final_state(show=True) != 0 or self.board.isfull()

    def reset(self):
        self.__init__()

def main():
    opponent_choice = input("Choose your opponent (1 for Minimax, 2 for DLS, 3 for Alpha-Beta Pruning): ")
    game = Game(opponent_choice)

    # Initialize depth outside the loop
    if opponent_choice == "3":
        depth = 3 
    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                row = pos[1] // SQSIZE
                col = pos[0] // SQSIZE

                if game.board.empty_sqr(row, col) and game.running:
                    game.make_move(row, col)

                    if game.isover():
                        game.running = False

        if game.player != 1 and game.running:
            # Check if the opponent is an AI_minimax, AI_DLS, or AI_AlphaBeta
            if isinstance(game.opponent, AI_minimax):
                row, col = game.opponent.eval(game.board)
                game.make_move(row, col)
            elif isinstance(game.opponent, AI_DLS):
                row, col = game.opponent.eval(game.board)  # Remove the depth argument
                game.make_move(row, col)
            elif isinstance(game.opponent, AI_AlphaBeta):
                row, col = game.opponent.eval_alpha_beta(game.board, depth)
                game.make_move(row, col)

            if game.isover():
                game.running = False

        pygame.display.update()

main()
