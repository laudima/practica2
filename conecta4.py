import pygame
import sys
import math
import random
import copy
import argparse

class Connect4:
    # Colores 
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    def __init__(self, difficulty, rows=6, columns=7, piece_size=80):
        
        # Constantes para la dimension del tablero
        self.ROWS = rows
        self.COLUMNS = columns
        self.PIECE_SIZE = piece_size
        self.WINDOW_LENGTH = 4 # Longitud de la ventana (4 fichas en linea)
        self.PLAYER_PIECE = 1
        self.BOT_PIECE = 2
        self.PLAYER = 0
        self.BOT = 1
        self.EMPTY = 0
        self.DIFFICULTY = difficulty

        # Dimensiones de la ventana
        self.WIDTH = self.COLUMNS * self.PIECE_SIZE
        self.HEIGHT = (self.ROWS + 1) * self.PIECE_SIZE
        self.RADIUS = int(self.PIECE_SIZE/2 - 5)

        # Variables de estado del juego
        self.board = self.create_board()
        self.game_over = False
        self.turn = 0

        # Set up 
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Connect 4')
        self.myfont = pygame.font.SysFont("monospace", 40)

    def create_board(self):
        """Creamos el tablero como una matriz de 0s."""
        return [[0 for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]

    def draw_board(self):
        """Dibujamos el tablero en la ventana."""
        # Dibujamos la matriz de celdas
        for c in range(self.COLUMNS):
            for r in range(self.ROWS):
                pygame.draw.rect(self.screen, self.BLUE, 
                    (c*self.PIECE_SIZE, r*self.PIECE_SIZE+self.PIECE_SIZE, 
                     self.PIECE_SIZE, self.PIECE_SIZE))
                pygame.draw.circle(self.screen, self.BLACK, 
                    (int(c*self.PIECE_SIZE+self.PIECE_SIZE/2), 
                     int(r*self.PIECE_SIZE+self.PIECE_SIZE+self.PIECE_SIZE/2)), 
                    self.RADIUS)
        
        # Creamos los circulitos de las fichas
        for c in range(self.COLUMNS):
            for r in range(self.ROWS):		
                if self.board[r][c] == 1:
                    pygame.draw.circle(self.screen, self.RED, 
                        (int(c*self.PIECE_SIZE+self.PIECE_SIZE/2), 
                         self.HEIGHT-int(r*self.PIECE_SIZE+self.PIECE_SIZE/2)), 
                        self.RADIUS)
                elif self.board[r][c] == 2: 
                    pygame.draw.circle(self.screen, self.YELLOW, 
                        (int(c*self.PIECE_SIZE+self.PIECE_SIZE/2), 
                         self.HEIGHT-int(r*self.PIECE_SIZE+self.PIECE_SIZE/2)), 
                        self.RADIUS)
        pygame.display.update()

    def is_valid_location(self,board, col):
        """Checa si la columna no esta llena"""
        return board[self.ROWS-1][col] == 0

    def get_next_open_row(self,board, col):
        """Encuentra la siguiente fila vacía en la columna *aquí cae por gravedad nuestra ficha *."""
        for r in range(self.ROWS):
            if board[r][col] == 0:
                return r
        return None

    def drop_piece(self, board,row, col, piece):
        """Coloca la ficha en la posición indicada."""
        board[row][col] = piece

    # Checa si hay un ganador
    def winning_move(self,board,piece):
        """Checa si hay un ganador."""
        # Checa las horizontales
        for c in range(self.COLUMNS-3):
            for r in range(self.ROWS):
                if (board[r][c] == piece and 
                    board[r][c+1] == piece and 
                    board[r][c+2] == piece and 
                    board[r][c+3] == piece):
                    return True

        # Checa las verticales 
        for c in range(self.COLUMNS):
            for r in range(self.ROWS-3):
                if (board[r][c] == piece and 
                    board[r+1][c] == piece and 
                    board[r+2][c] == piece and 
                    board[r+3][c] == piece):
                    return True

        # Checa las diagonales 
        for c in range(self.COLUMNS-3):
            for r in range(self.ROWS-3):
                if (board[r][c] == piece and 
                    board[r+1][c+1] == piece and 
                    board[r+2][c+2] == piece and 
                    board[r+3][c+3] == piece):
                    return True

        # Checa las diagonales invertidas 
        for c in range(self.COLUMNS-3):
            for r in range(3, self.ROWS):
                if (board[r][c] == piece and 
                    board[r-1][c+1] == piece and 
                    board[r-2][c+2] == piece and 
                    board[r-3][c+3] == piece):
                    return True

        return False

    # Evalua la posicion 
    def score_position(self,board, piece):
        score = 0

        # Puntaje de la columna centra 
        # Se cuenta cuantas fichas del jugador hay en la columna central y se multiplica por 3
        # Las fichas centrales le dan ventaja al jugador
        centre_array = [row[self.COLUMNS // 2] for row in board]
        centre_count = centre_array.count(piece)
        score += centre_count * 3

        # Puntaje horizontal
        for r in range(self.ROWS):
            row_array = [int(i) for i in list(board[r])]
            for c in range(self.COLUMNS - 3):
                # Create a horizontal window of 4
                window = row_array[c:c + self.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Puntaje vertical
        for c in range(self.COLUMNS):
            col_array = [int(row[c]) for row in board]
            for r in range(self.ROWS - 3):
                # Create a vertical window of 4
                window = col_array[r:r + self.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Puntaje diagonales positivas
        for r in range(self.ROWS - 3):
            for c in range(self.COLUMNS - 3):
                # Create a positive diagonal window of 4
                window = [board[r + i][c + i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        # Puntaje diagonales negativas
        for r in range(self.ROWS - 3):
            for c in range(self.COLUMNS - 3):
                # Create a negative diagonal window of 4
                window = [board[r + 3 - i][c + i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        return score
    
    # Evalua la ventana
    def evaluate_window(self, window, piece):
        score = 0
        
        # Obtenemos la ficha del oponente 
        
        opp_piece = self.PLAYER_PIECE
        if piece == self.PLAYER_PIECE:
            opp_piece = self.BOT_PIECE

        # Puntaje de los movimientos

        # Si hay 4 fichas en linea, el jugador gana
        if window.count(piece) == 4:
            score += 100
        # Si hay 3 fichas en linea y una casilla vacía, el jugador tiene ventaja
        elif window.count(piece) == 3 and window.count(self.EMPTY) == 1:
            score += 5
        # Si hay 2 fichas en linea y dos casillas vacías, el jugador tiene ventaja
        elif window.count(piece) == 2 and window.count(self.EMPTY) == 2:
            score += 2
        # bloquea al oponente para que no gane 
        if window.count(opp_piece) == 3 and window.count(self.EMPTY) == 1:
            score -= 4

        return score
    
    # Función para saber cuando el juego termina
    # Si hay un ganador o si el tablero esta lleno
    def is_terminal_node(self,board):
        return self.winning_move(board,self.PLAYER_PIECE) or self.winning_move(board,self.BOT_PIECE) or len(self.get_valid_locations(board)) == 0

    # Checa donde hay espacio para poner fichas 
    def get_valid_locations(self,board):
        valid_locations = []
        for col in range(self.COLUMNS):
            if self.is_valid_location(board, col):
                valid_locations.append(col)
        return valid_locations
    
    def min_max(self,board,depth,max_player):
        valid_locations = self.get_valid_locations(board) # vemos las posiciones disponibles para el jugador
        is_terminal = self.is_terminal_node(board)        # vemos si el juego termino

        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board,self.BOT_PIECE):      # si el bot gana le damos puntos, pues queremos que gane
                    return (None,100000000000000)
                elif self.winning_move(board,self.PLAYER_PIECE): 
                    return (None,-10000000000000)
                else:
                    return (None,0)
            else:
                return (None,self.score_position(board,self.BOT_PIECE))  # si no es terminal, calculamos el puntaje de la posición
            
        if max_player:
            value = -math.inf
            column = random.choice(valid_locations)  # escogemos una columna aleatoria
            for col in valid_locations:
                row = self.get_next_open_row(board,col) # la ficha cae 
                b_copy = copy.deepcopy(board)
                self.drop_piece(b_copy,row,col,self.BOT_PIECE)    # se coloca la ficha
                new_score = self.min_max(b_copy,depth-1,False)[1]  # escogemos el mejor movimiento a partir de la posición actual
                if new_score > value:
                    value = new_score
                    column = col
            return column,value
        else: # Minimizing player
            value = math.inf
            for col in valid_locations:
                row = self.get_next_open_row(board,col)
                b_copy = copy.deepcopy(board)
                self.drop_piece(b_copy,row,col,self.PLAYER_PIECE)
                new_score = self.min_max(b_copy,depth-1,True)[1]
                if new_score < value:
                    value = new_score
                    column = col
            return column,value
    
    def poda_beta_alpha(self,board,depth,alpha,beta,max_player):
        valid_locations = self.get_valid_locations(board)
        is_terminal = self.is_terminal_node(board)

        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board,self.BOT_PIECE):
                    return (None,100000000000000)
                elif self.winning_move(board,self.PLAYER_PIECE):
                    return (None,-10000000000000)
                else:
                    return (None,0)
            else:
                return (None,self.score_position(board,self.BOT_PIECE))

        if max_player:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board,col)
                b_copy = copy.deepcopy(board)
                self.drop_piece(b_copy,row,col,self.BOT_PIECE)
                new_score = self.poda_beta_alpha(b_copy,depth-1,alpha,beta,False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha,value)
                if alpha >= beta:
                    break
            return column,value
        else: # Minimizing player
            value = math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = copy.deepcopy(board)
                self.drop_piece(b_copy, row, col, self.PLAYER_PIECE)
                new_score = self.poda_beta_alpha(b_copy, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value

    def turn_bot(self,board,difficulty):
        b_copy = board.copy()
        if difficulty == 'easy':
            b_copy = board.copy()
            col, _ = self.min_max(b_copy, 2, True)
        elif difficulty == 'medium':
            col, _ = self.poda_beta_alpha(b_copy, 5, -math.inf, math.inf, True)
        elif difficulty == 'hard':
            col, _ = self.poda_beta_alpha(b_copy, 7, -math.inf, math.inf, True)
        else:
            raise ValueError("Invalid strategy. Use 'minimax' or 'poda_beta_alpha'.")
    
        if self.is_valid_location(board, col):

            row = self.get_next_open_row(board, col)
            self.drop_piece(board, row, col, self.BOT_PIECE)

            if self.winning_move(board, self.BOT_PIECE):
                label = self.myfont.render("Te gano el bot jiji", 1, self.YELLOW)
                self.screen.blit(label, (40, 10))
                self.game_over = True
            self.draw_board()
            self.turn = (self.turn + 1) % 2

    def run(self):
        """Funcion para correr el juego."""
        self.draw_board()

        while not self.game_over:
            for event in pygame.event.get():
                # Salir del juego
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(self.screen, self.BLACK, (0, 0, self.WIDTH, self.PIECE_SIZE))
                    posx = event.pos[0]
                    
                    # Dibujamos la ficha de inicio
                    if self.turn == 0:
                        pygame.draw.circle(self.screen, self.RED, (posx, int(self.PIECE_SIZE/2)), self.RADIUS)
                    else: 
                        pygame.draw.circle(self.screen, self.YELLOW, (posx, int(self.PIECE_SIZE/2)), self.RADIUS)
                    pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(self.screen, self.BLACK, (0, 0, self.WIDTH, self.PIECE_SIZE))
                    
                    if self.turn == self.PLAYER:
                        # Obtener la columna donde se hizo click
                        posx = event.pos[0]
                        col = int(math.floor(posx/self.PIECE_SIZE))

                        # Checar si la columna esta llena
                        if self.is_valid_location(self.board,col):
                            row = self.get_next_open_row(self.board,col)
                            self.drop_piece(self.board,row, col, self.turn + 1)

                            # Checamos si el jugador 1 gana
                            if self.winning_move(self.board,self.turn + 1):
                                label = self.myfont.render("Player 1 wins!!", 1, self.RED)
                                self.screen.blit(label, (40,10))
                                self.game_over = True
                            
                            # Actualizamos el tablero
                            self.turn = (self.turn + 1) % 2
                            self.draw_board()

            if self.turn == self.BOT and not self.game_over:
                self.turn_bot(self.board,self.DIFFICULTY)
                #self.turn_bot('poda_beta_alpha')
            if self.game_over:
                pygame.time.wait(3000)

            

def main():
    """Entry point of the game."""
    parser = argparse.ArgumentParser(description='Start a Connect4 game.')
    parser.add_argument('difficulty', type=str, choices=['easy', 'medium', 'hard'], help='Difficulty level of the game')
    args = parser.parse_args()

    game = Connect4(args.difficulty)
    game.run()

if __name__ == "__main__":
    main()