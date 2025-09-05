import chess
import cv2
import numpy as np

#Class Defining a square
#A board is an 8x8 matrix of squares
#Each square is defined by its 4 corner points and the piece it contains

class Square:

    def __init__(self, p1: tuple[int, int], p2: tuple[int, int], p3: tuple[int, int], p4: tuple[int, int]):
        self.names_dict = {
        0: chess.Piece(chess.BISHOP, chess.BLACK), 
        1: chess.Piece(chess.KING, chess.BLACK), 
        2: chess.Piece(chess.KNIGHT, chess.BLACK), 
        3: chess.Piece(chess.PAWN, chess.BLACK), 
        4: chess.Piece(chess.QUEEN, chess.BLACK), 
        5: chess.Piece(chess.ROOK, chess.BLACK), 
        6: chess.Piece(chess.BISHOP, chess.WHITE), 
        7: chess.Piece(chess.KING, chess.WHITE), 
        8: chess.Piece(chess.KNIGHT, chess.WHITE), 
        9: chess.Piece(chess.PAWN, chess.WHITE), 
        10: chess.Piece(chess.QUEEN, chess.WHITE), 
        11: chess.Piece(chess.ROOK, chess.WHITE)
        }
        self.x1, self.y1 = p1
        self.x2, self.y2 = p2
        self.x3, self.y3 = p3
        self.x4, self.y4 = p4
        self.piece: chess.Piece = None
        self.hash_value = ((self.y1 // 160) << 3) | (self.x1 // 160)
    
    def get_piece(self): return self.piece
    def set_piece(self, piece_num: int): self.piece = self.names_dict[piece_num]

    #Gives a pretty representation of the piece
    def __repr__(self): return self.get_piece().symbol()

    def __eq__(self, other):
        if not isinstance(other, Square):
            return False
        return self.x1 == other.x1 and self.y1 == other.y1
    
    def __hash__(self):
        return self.hash_value
    #Checks whether a given point is contained within the square

    def in_square(self, point) -> bool:
        x0, y0 = point
        x_max, x_min = max(x_vals:=[self.x1, self.x2, self.x3, self.x4]), min(x_vals)
        y_max, y_min = max(y_vals:=[self.y1, self.y2, self.y3, self.y4]), min(y_vals)
        return x0 >= x_min and x0 <= x_max and y0 >= y_min and y0 <= y_max
    
    #Gets the subimage captured by the points of the square

    def get_image(self, image):
        x_max, x_min = max(x_vals:=[self.x1, self.x2, self.x3, self.x4]), min(x_vals)
        y_max, y_min = max(y_vals:=[self.y1, self.y2, self.y3, self.y4]), min(y_vals)
        return image[y_min:y_max, x_min:x_max]

    #Returns intersection area between the square and the polygon (bottom of piece bounding box) provided

    def get_intersect_area(self, box_poly, homography):
        proj_points = cv2.perspectiveTransform(np.float32([box_poly]), homography)[0]
        square_points = np.float32([[self.x1, self.y1], [self.x2, self.y2], [self.x4, self.y4], [self.x3, self.y3]])
        return cv2.intersectConvexConvex(square_points, proj_points, handleNested=True)
#EOF