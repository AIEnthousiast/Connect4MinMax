import numpy as np
import pygame
import sys
import math
import random

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)


DEPTH = 8
PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4

ROW_COUNT = 6
COLUMN_COUNT = 7
def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board

def drop_piece(board, row , col , piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[0][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT-1,-1,-1):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    # Check horizontal locations for win

    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    
    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    
    #check positively sloped diagonal
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    #check negatively sloped diagonal
    for c in range(COLUMN_COUNT-3):
        for r in range(3,ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def evalutate_window(window, piece):
    opp_piece = PLAYER_PIECE 
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    score = 0


    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 15
    
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 90
    
    


    return score

def is_terminal_node(board):
    return winning_move(board,PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta,maximizingPlayer):
    valid_locations = get_valid_locations(board)
    terminal_node = is_terminal_node(board)
    if depth == 0 or terminal_node:
        if terminal_node:
            if winning_move(board,AI_PIECE):
                return (None,1000000000)
            elif winning_move(board,PLAYER_PIECE):
                return (None,-1000000000)
            else:
                return (None,0)
        else:
            return (None,score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        colum  = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy,depth-1,alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            
            alpha = max(alpha,value)
            if (alpha >= beta):
                break
            
        return (column,value)
    else:
        value = math.inf
        colum  = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board,col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy,depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            
            beta = min(beta,value)
            if (alpha >= beta):
                break
        return (column, value)



def score_position(board, piece):


    score = 0 

    ##score center
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)

    score += 3 * center_count
    ##score horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            
            score += evalutate_window(window,piece)

    ##score vertical
    for c in range(COLUMN_COUNT):
        colum_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT - 3):
            window = colum_array[r:r+WINDOW_LENGTH]

            score += evalutate_window(window,piece)

    ##score negative slope diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]

            score += evalutate_window(window,piece)
    
    ##score positive slope diagonal
    for c in range(COLUMN_COUNT-3):
        for r in range(3,ROW_COUNT):
            window = [board[r-i][c+i] for i in range(WINDOW_LENGTH)]

            score += evalutate_window(window,piece)
            
            
    return score


def get_valid_locations(board):
    return [col for col in range(COLUMN_COUNT) if is_valid_location(board,col)]

def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_column = random.choice(valid_locations)

    for col in valid_locations:
        row = get_next_open_row(board,col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)

        if score > best_score:
            best_score = score
            best_column = col

    return best_column

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, (r + 1) * SQUARESIZE, SQUARESIZE, SQUARESIZE) )

            if board[r][c] == 0:
                pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE + SQUARESIZE / 2), int((r + 1) * SQUARESIZE+ SQUARESIZE / 2)),RADIUS)
            
            elif board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE + SQUARESIZE / 2), int((r + 1) * SQUARESIZE+ SQUARESIZE / 2)),RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE + SQUARESIZE / 2), int((r + 1) * SQUARESIZE+ SQUARESIZE / 2)),RADIUS)

board = create_board()

print(board)
game_over = False
turn = random.randint(0,1)


pygame.init()

SQUARESIZE = 90

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1 ) * SQUARESIZE 


size = (width,height)


RADIUS = int(SQUARESIZE / 2  -  5)


screen = pygame.display.set_mode(size)


draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace",75)

while not game_over:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen,BLACK, (0,0,width,SQUARESIZE))
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (event.pos[0], int(SQUARESIZE / 2)), RADIUS)
            

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen,BLACK, (0,0,width,SQUARESIZE))
            #Ask for player 1 input
            if turn == PLAYER:
                col = int(math.floor(event.pos[0] / SQUARESIZE))


                if is_valid_location(board, col):
                    row = get_next_open_row(board,col)
                    drop_piece(board,row,col,PLAYER_PIECE)

                    if winning_move(board,PLAYER_PIECE):
                        label = myfont.render("Player 1 wins!!", 1 , RED)
                        screen.blit(label,(40,10))
                        game_over = True
                    
                    draw_board(board)
                    pygame.display.update()
                    turn += 1
                    turn = turn % 2

            #Ask for player 2 input
    if turn == AI and not game_over:
        #col = random.randint(0,COLUMN_COUNT-1)
        #col = pick_best_move(board,AI_PIECE)

        col = minimax(board,DEPTH,-math.inf, math.inf,True)[0]


        if is_valid_location(board, col):
            row = get_next_open_row(board,col)
            drop_piece(board,row,col,AI_PIECE)

            if winning_move(board,AI_PIECE):
                label = myfont.render("Player 2 wins!!", 1 , YELLOW)
                screen.blit(label,(40,10))
                game_over = True
                
            
            turn += 1
            turn = turn % 2

    print(board)


    draw_board(board)
    pygame.display.update()
    if game_over:
        pygame.time.wait(3000)

