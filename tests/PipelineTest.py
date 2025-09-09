import sys
import cv2
import chess.svg
from wand.image import Image as imgW
from wand.color import Color
from pathlib import Path
from src.BoardConstructionPipeline import ImageBoardRecognizer

#Code for running the pipeline on a test image (one-shot image detection test file)
#Pass image filename as command line argument

image = cv2.imread(f"tests/TestImages/{sys.argv[1]}")
resized_image = cv2.resize(image, (1280, 1280))

print('Reading in files')

#Initialization of Board Recognizer Object -> Pass names of piece detection model and board detection model
Board_Recog = ImageBoardRecognizer("PieceDetector.pt", "BoardDetector.pth")

#Give pipeline a target image
Board_Recog.set_image(image)

print('Running detections')

#Piece detection function, runs YOLO piece detection and returns bounding boxes w/ class identifications
boxes, classes = Board_Recog.run_piece_detection(confidence=0.4, save=True)

print('Piece Detection Finished')

#Perspective transformation of the image given the polygon of the board
board_mask = Board_Recog.run_board_detection(save=True)
print('Chessboard has been found\n')

#Function to place pieces on squares given the perspective transformation info and the location and identification of pieces
warped_image = Board_Recog.perspective_transform(board_mask)

board, formatted_output = Board_Recog.find_board(warped_image, boxes, classes, table=True, save=True, board_num = 1)
#Gets correct orientation of the board based on piece locations

final_board = Board_Recog.get_rotation(board)

print("Final Board\n")
Board_Recog.print_board(final_board)
print()

pychess_board, table = Board_Recog.make_pychess_board(final_board, table = True, formatted_output = formatted_output)

with imgW(blob=chess.svg.board(pychess_board).encode('utf-8'), format="svg") as img: # SVG --> PNG
    img.background_color = Color("white")
    img.alpha_channel = 'remove'
    img.save(filename="tests/chess_board.png")

print('             Piece Detection Model Report\n')
print(table + "\n")

cv2.namedWindow("Warped Image", cv2.WINDOW_NORMAL)
cv2.imshow("Warped Image", warped_image)
cv2.waitKey(0)

print('Test was successful!')
