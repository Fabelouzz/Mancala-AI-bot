#!/usr/bin/python           # This is server.py file
import socket  # Import socket module
import numpy as np
import time
from multiprocessing.pool import ThreadPool
import os
import random
import copy


def simulate_move(board, move, player_turn):
    stones = board[move] # number of stones in the pit the move starts from
    board[move] = 0 # remove the stones from the pit
    last_index = move # initially the last index is the move
    while stones > 0:
        move += 1
        if player_turn == 1 and move == 13:  # If it's the maximizer's turn, skip the minimizer's mancala
            move += 1
        elif player_turn == 2 and move == 6:  # If it's the minimizer's turn, skip the maximizer's mancala
            move += 1
        move = move % 14  # Use modulo to automatically reset to the start of the board
        board[move] += 1 # drop a stone in the current pit
        stones -= 1 # remove a stone from your hand
        last_index = move # update the last index to wher ethe last stone was dropped
    # Rule 8: If the last piece you drop is in an empty hole on your side, you capture that piece and any pieces in the hole directly opposite.
    if 0 <= last_index <= 5 and board[last_index] == 1: #if the last stone lands in a pit on the player's side and the pit is empty
        board[6] += board[13 - last_index] + 1  # Capture the stones from the opponent's pit
        board[last_index] = board[13 - last_index] = 0  # Clear both pits
    elif 7 <= last_index <= 12 and board[last_index] == 1:  # Minimizing player
        board[13] += board[12 - last_index] + 1  # Capture the stones from the opponent's pit
        board[last_index] = board[12 - last_index] = 0  # Clear both pits

    return board, last_index in {6, 13} # return the board and a boolean indicating if the last stone landed in the player's Mancala or opponent's Mancala


def utility(board, player_turn):
    mancala_difference = board[6] - board[13]
    side_difference = sum(board[0:6]) - sum(board[7:13])
    empty_pits_difference = board[0:6].count(0) - board[7:13].count(0)

    # Bonus for free turn for maximizing player (player 1)
    free_turn_bonus_maximizer = sum([1 for i in range(0, 6) if board[i] == (6 - i)])

    # Penalty for potential free turn for minimizing player (player 2)
    free_turn_penalty_minimizer = sum([1 for i in range(7, 13) if board[i] == (13 - i)])

    score = mancala_difference + 0.5 * side_difference + 0.5 * empty_pits_difference + (free_turn_bonus_maximizer - free_turn_penalty_minimizer)

    return score
#
# def utility(board, player_turn):
#     if player_turn == 1:  # Maximizing player
#         mancala_difference = board[6] - board[13]
#         side_difference = sum(board[0:6]) - sum(board[7:13])
#         empty_pits_difference = board[0:6].count(0) - board[7:13].count(0)
#         # Bonus for free turn for maximizing player (player 1)
#         free_turn_bonus_maximizer = sum([1 for i in range(0, 6) if board[i] == (6 - i)])
#         # Penalty for potential free turn for minimizing player (player 2)
#         free_turn_penalty_minimizer = sum([1 for i in range(7, 13) if board[i] == (13 - i)])
#
#         return mancala_difference + 0.5 * side_difference + 0.5 * empty_pits_difference + (free_turn_bonus_maximizer - free_turn_penalty_minimizer)
#
#     elif player_turn == 2:  # Minimizing player
#         mancala_difference = board[13] - board[6]
#         side_difference = sum(board[7:13]) - sum(board[0:6])
#         empty_pits_difference = board[7:13].count(0) - board[0:6].count(0)
#         # Penalty for potential free turn for maximizing player (player 1)
#         free_turn_penalty_maximizer = sum([1 for i in range(0, 6) if board[i] == (6 - i)])
#         # Bonus for free turn for minimizing player (player 2)
#         free_turn_bonus_minimizer = sum([1 for i in range(7, 13) if board[i] == (13 - i)])
#
#         return mancala_difference + 0.5 * side_difference + 0.5 * empty_pits_difference + (free_turn_bonus_minimizer - free_turn_penalty_maximizer)
#


# return [i for i in range(0, 6) if board[i] > 0] possible future implementation
def possible_moves(board, playerTurn):
    # list comprehension
    if playerTurn == 1:
        return [i for i, val in enumerate(board[:6]) if val > 0] # slice the board to get only the pits between index 0 and 5
    if playerTurn == 2:
        #sequence of tuples
        return [i for i, val in enumerate(board[7:13]) if val > 0] # slice the board to get only the pits between index 7 and 12

#
# def alpha_beta_pruning(board, depth, player_turn, alpha, beta):
#     if depth == 0 or sum(board[0:6]) == 0 or sum(board[7:13]) == 0:
#         return utility(board), None
#
#     if player_turn == 1:  # Maximizing player
#         best_value = float('-inf')
#         best_move = None
#         for move in possible_moves(board, player_turn):
#             new_board, last_stone_in_mancala = simulate_move(copy.deepcopy(board), move, player_turn)
#             print(board,"= board before move", "player =", player_turn, "maximizing")
#             print(new_board,"=board after move","move =",move,)
#             next_turn = player_turn if last_stone_in_mancala else 3 - player_turn
#             eval, _ = alpha_beta_pruning(new_board, depth-1, next_turn, alpha, beta)
#             if eval > best_value:
#                 best_value = eval
#                 best_move = move
#             alpha = max(alpha, best_value) # Update alpha to the maximum value between alpha and the best value
#             if beta <= alpha: # If beta is less than or equal to alpha, prune the rest of the tree
#                 break
#         return best_value, best_move
#
#     elif player_turn == 2:  # Minimizing player
#         best_value = float('inf')
#         best_move = None
#         for move in possible_moves(board, player_turn):
#             actual_move = move + 7 if player_turn == 2 else move
#             new_board, last_stone_in_mancala = simulate_move(copy.deepcopy(board), actual_move, player_turn)
#             print(board,"= board before move", "player =", player_turn, "minimizing")
#             print(new_board, "= board after move" "move =", actual_move)
#             next_turn = player_turn if last_stone_in_mancala else 3 - player_turn
#             eval, _ = alpha_beta_pruning(new_board, depth-1, next_turn, alpha, beta)
#             if eval < best_value:
#                 best_value = eval
#                 best_move = actual_move
#             beta = min(beta, best_value)
#             if beta <= alpha:
#                 break
#         return best_value, best_move


def maximize(board, depth, alpha, beta):
    # base case when depth is 0 in a deep recursive call
    # or when the game is over inside a deep recursive call
    if depth == 0 or sum(board[0:6]) == 0 or sum(board[7:13]) == 0:
        return utility(board, 1), None

    best_value = float('-inf') # any real utility value will be greater than this
    best_move = None
    for move in possible_moves(board, 1):
        # for each move, simulates a move by Player 1 and returns the new board state
        # and a boolean indicating if the last stone landed in the player's own Mancala.
        new_board, last_stone_in_mancala = simulate_move(copy.deepcopy(board), move, 1) # copy to avoid messing up the original board
        print(board,"= board before move", "player = 1", "maximizing")
        print(new_board,"=board after move","move =",move,)
        # two more recursive calls reach the base case and return the utility value
        if last_stone_in_mancala:
            eval, _ = maximize(new_board, depth - 1, alpha, beta)
        else:
            eval, _ = minimize(new_board, depth - 1, alpha, beta)
        # after reaching the base case, the utility value is returned and compared to the best value
        # this is done
        if eval > best_value:
            best_value = eval
            best_move = move
        alpha = max(alpha, best_value)
        if beta <= alpha: # If beta is less than or equal to alpha, prune the rest of the tree
            # because minimizing player has a move that will result in a lower utility value
            break
    return best_value, best_move


def minimize(board, depth, alpha, beta):
    if depth == 0 or sum(board[0:6]) == 0 or sum(board[7:13]) == 0:
        return utility(board, 2), None

    best_value = float('inf')
    best_move = None
    for move in possible_moves(board, 2):
        actual_move = move + 7
        new_board, last_stone_in_mancala = simulate_move(copy.deepcopy(board), actual_move, 2)
        print(board,"= board before move", "player = 2", "minimizing")
        print(new_board, "= board after move" "move =", actual_move)
        if last_stone_in_mancala:
            eval, _ = minimize(new_board, depth - 1, alpha, beta)
        else:
            eval, _ = maximize(new_board, depth - 1, alpha, beta)
        if eval < best_value:
            best_value = eval
            best_move = actual_move
        beta = min(beta, best_value)
        if beta <= alpha:
            break
    return best_value, best_move


def receive(socket):
    msg = ''.encode()  # type: str

    try:
        data = socket.recv(1024)  # type: object
        msg += data
    except:
        pass
    return msg.decode()


def send(socket, msg):
    socket.sendall(msg.encode())


# VARIABLES
playerName = 'Fabiano'
namn = random.randint(1, 1000)
namn = str(namn)
playerName = playerName + namn
host = '127.0.0.1'
port = 30000  # Reserve a port for your service.
s = socket.socket()  # Create a socket object
pool = ThreadPool(processes=1) # create a thread pool, a thread pool is a group of threads that are waiting for a job to do
gameEnd = False # game is not over
MAX_RESPONSE_TIME = 5
DEPTH = 3
print('The player: ' + playerName + ' starts!')
s.connect((host, port))
print('The player: ' + playerName + ' connected!')
game_count = 0
while not gameEnd: # while game is not over
    # receive data from server
    asyncResult = pool.apply_async(receive, (s,))
    # start timer
    startTime = time.time()
    currentTime = 0
    received = 0
    data = []
    # wait for data from server
    while received == 0 and currentTime < MAX_RESPONSE_TIME: # while no data is received and time is less than max response time
        # if data is received
        if asyncResult.ready():
            # get data
            data = asyncResult.get()
            # set received to 1
            received = 1
            # stop timer
        currentTime = time.time() - startTime
    # if no data is received
    if received == 0:
        print('No response in ' + str(MAX_RESPONSE_TIME) + ' sec')
        gameEnd = 1
    # if data is 'N' means that it is your turn
    if data == 'N':
        send(s, playerName) # send your name to server
    # if data is 'E' means that the game is over
    if data == 'E':
        gameEnd = 1

    if len(data) > 1: # if data is not 'N' or 'E' means that it is not your turn

        # Read the board and player turn
        board = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # playerTurn is the first character of data
        playerTurn = int(data[0])
        # i is the index of board
        i = 0
        # j is the index of data
        j = 1
        while i <= 13: # while i is less than 14 because there are 14 elements in board
            board[i] = int(data[j]) * 10 + int(data[j + 1]) # convert data to int and add it to board because data is string
            i += 1
            j += 2
        if board == [4,4,4,4,4,4,0,4,4,4,4,4,4,0]:
            game_count += 1
            print("game count = ", game_count)
        print("Board before minimax: the turn is now player ", playerTurn,   board)  # debug print

        if playerTurn == 1:
            best_value, best_move = maximize(board, DEPTH, float('-inf'), float('inf'))
            print("player 1 best move = ", best_move)
            send(s, str(best_move + 1))
            print("Best move: ", best_move)  # debug print
            print("utility: ", best_value)
            print("previous board from computation above: done by turn", playerTurn, board)  # debug print

        elif playerTurn == 2:
            best_value, best_move = minimize(board, DEPTH, float('-inf'), float('inf'))
            print("player 2 best move = ", best_move)
            server_move = best_move - 6
            print("fixed move = ", server_move)
            send(s, str(server_move))
            print("Best move: ", best_move)  # debug print
            print("utility: ", best_value)
            print("previous board from computation above: done by turn", playerTurn, board)  # debug print

        # if (playerTurn == 1 and game_count % 2 == 1) or (playerTurn == 2 and game_count % 2 == 0):
        #     best_value, best_move = maximize(board, DEPTH, float('-inf'), float('inf'))
        #     print("best move = ", best_move)
        #     if playerTurn == 1:
        #         send(s, str(best_move + 1))
        #     else:
        #         send(s, str(best_move))
        # elif (playerTurn == 2 and game_count % 2 == 1) or (playerTurn == 1 and game_count % 2 == 0):
        #     best_value, best_move = minimize(board, DEPTH, float('-inf'), float('inf'))
        #     print("best move = ", best_move)
        #     if playerTurn == 2:
        #         server_move = best_move - 6
        #         send(s, str(server_move))
        #     else:
        #         send(s, str(best_move + 1))
