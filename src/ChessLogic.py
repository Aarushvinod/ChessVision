import chess

#Gets a list of tuples with the first element being the piece and the seccond the corresponding square
#Takes in a board as input

def piece_squares(board):
    ps = []
    for i in chess.SQUARE_NAMES:
        piece = board.piece_at(chess.parse_square(i))
        ps.append((piece, i))
    return ps

#Given a squares index retrieves all of its neighbors
#Takes a square index as input

def get_adjacent_squares(square_name):
    square = chess.parse_square(square_name)
    rank = chess.square_rank(square)
    file = chess.square_file(square)
    directions = [(-1, 0), (-1, 1), (0, 1), (1, 1),
                  (1, 0), (1, -1), (0, -1), (-1, -1)]
    adjacent_squares = []
    for dr, df in directions:
        new_rank = rank + dr
        new_file = file + df
        if 0 <= new_rank <= 7 and 0 <= new_file <= 7:
            adj_square = chess.square(new_file, new_rank)
            adjacent_squares.append(chess.square_name(adj_square))
    return adjacent_squares

#Gets the color of a given piece on a given square on a given board
#As input accepts 
def get_piece_color(board, square_name):
    square = chess.parse_square(square_name)
    piece = board.piece_at(square)
    if piece:
        return "White" if piece.color == chess.WHITE else "Black"
    else:
        return "NA"

#Computes the distance betweeon two squares by finding the maximum horizontal/vertical distance between the two
#Accepts two squares (by regular naming convention) as inputs

def square_distance(square1_name, square2_name):
    sq1 = chess.parse_square(square1_name)
    sq2 = chess.parse_square(square2_name)
    rank1, file1 = divmod(sq1, 8)
    rank2, file2 = divmod(sq2, 8)
    rank_diff = abs(rank1 - rank2)
    file_diff = abs(file1 - file2)
    return max(rank_diff, file_diff)

#Finds the possible moves made between two boards:
#Takes as input the following: p1,2 are position boards - p1 is prev position, p2 is predicted position with model

def possible_moves_made(p1, p2):
    b1_pieces = piece_squares(p1)
    b2_pieces = piece_squares(p2)

    pred_moves = [str(i) for i in p1.legal_moves]

    piece_square_empty = []
    piece_square = []
    misclassified_list = []

    for ps in b2_pieces:
        if ps not in b1_pieces:
            p, s = ps
            if p != None:
                piece = str(p2.piece_at(chess.parse_square(s))) # gives notation Nf3
                for pc in b1_pieces:
                    p_init, s_init = pc
                    if str(p_init) == piece:
                        if (s_init + s) in pred_moves and p2.piece_at(chess.parse_square(s_init)) == None:
                            piece_square_empty.append(s_init + s)
                        elif (s_init + s) in pred_moves:
                            piece_square.append(s_init + s)
                    else: # checks if diff piece can move to the square
                        if (s_init + s) in pred_moves and p2.piece_at(chess.parse_square(s_init)) == None:
                            misclassified_list.append(s_init + s)
    if len(piece_square_empty) != 0:
        print("Chess Logic Status: Correct Piece to Correct Square, Init Square Empty")
        return piece_square_empty
    elif len(misclassified_list) != 0:
        print("Chess Logic Status: Incorrect Piece to Correct Square, Init Square Empty")
        return misclassified_list
    print("Chess Logic Status: No move")
    return []

#Makes the detected move on the board
#Takes as input the following
#pychess_board: board detected by pipeline
#previous_board: board from previous iteration of pipeline + chess logic
#root: TKinter UI root to make updates to the UI
#status_text: status bar in UI for showing users the models current processing step

def make_next_move(pychess_board, num_pieces, previous_board, root, status_text):
     if abs(len(pychess_board.piece_map()) - num_pieces) < 4: #can change #
        root.after(0, status_text.config(text="Status: Move Detected"))
        possible_moves = possible_moves_made(previous_board, pychess_board) # CHESS LOGIC
        if len(possible_moves) > 0:
            castled = False
            predicted_move = possible_moves[0]
            for mv in possible_moves: # CASTLING
                if mv in ["e8g8", "e8c8", "e1g1", "e1c1"]:
                    predicted_move = mv
                    castled = True
            if castled == False:
                if len(possible_moves) > 1:
                    move_lens = [(square_distance(move[0:2], move[2:4]), move) for move in possible_moves]
                    chosen = max(move_lens)
                    _, mv = chosen
                    predicted_move = mv
            previous_board.push_san(predicted_move)