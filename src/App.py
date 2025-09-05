import cv2
from BoardRecognizerFullGame import BoardRecognizerFullGame
import chess
import chess.svg
import chess.pgn as out
from tkinter.scrolledtext import ScrolledText
from wand.image import Image as imgW
from wand.color import Color
import tkinter as tk
from PIL import ImageTk, Image
import threading
import time
from ChessLogic import make_next_move

#This file contains both the developer UI and all the detailed chess logic algorithms
#Self correct algorithm is not implemented here (please check self_correct.py in miscallaneous for more info)
#Run this file to get the demo of how the pipeline works and have your mind blown by seeing the pieces on the board and screen move.
#TODO: PLEASE PLEASE PLEASE refactor this code so that the chess logic is encapsulated in its own module (we didn't get to this in time)
class App:
    def __init__(self, root: tk.Tk):
        root = root
        root.title("ChessVision Developer UI")
        root.attributes("-fullscreen", True)
        root.bind("<Escape>", lambda _: root.attributes("-fullscreen", False))
        root.protocol("WM_DELETE_WINDOW", self.save_pgn)

        root.rowconfigure(index = 0, weight = 1)
        root.rowconfigure(index = 1, weight = 30)
        root.columnconfigure(index = 0, weight = 1)

        self.title_panel = tk.Label(root, borderwidth=1, text="ChessVision Developer Interface", relief="solid", background="Cyan", font=("Courier", 30))
        self.title_panel.grid(row = 0, column = 0, sticky="nsew")

        self.main_panel = tk.Frame(root, borderwidth=1, relief="solid")
        self.main_panel.grid(row=1, column=0, sticky="nsew")
        self.main_panel.columnconfigure(index = 0, weight = 2, uniform="equal")
        self.main_panel.columnconfigure(index = 1, weight = 3, uniform="equal")
        self.main_panel.rowconfigure(index = 0, weight = 1)

        self.left_panel = tk.Frame(self.main_panel, borderwidth=1, relief="solid")
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        self.left_panel.rowconfigure(index = 0, weight = 4, uniform="equal")
        self.left_panel.rowconfigure(index = 1, weight = 3, uniform="equal")
        self.left_panel.columnconfigure(index = 0, weight = 1)

        self.right_panel = tk.Frame(self.main_panel, borderwidth=1, relief="solid")
        self.right_panel.grid(row = 0, column  = 1, sticky="nsew")
        self.right_panel.rowconfigure(index = 0, weight = 5)
        self.right_panel.rowconfigure(index = 1, weight = 1)
        self.right_panel.columnconfigure(index = 0, weight = 1)

        self.tk_img = None
        self.leftImagePanel = tk.Label(self.left_panel, bg="lightgray", text="Board State", anchor="center", borderwidth=1)
        self.leftImagePanel.grid(row=0, column=0, sticky="nsew")

        self.tk_img_vid = None
        self.leftVideoPanel = tk.Label(self.left_panel, bg = "darkgray", text = "Video Feed", anchor = 'center', borderwidth=1)
        self.leftVideoPanel.grid(row=1, column=0, sticky="nsew")

        self.count = 0
        self.previous_board = chess.Board() # assume starting board for testing

        self.log_text = ScrolledText(self.right_panel, wrap=tk.WORD, font=("Courier", 14))
        self.log_text.insert(tk.END, 'Log will start displaying once process begins' + "\n")
        self.log_text.see(tk.END)
        self.log_text.grid(row=0, column=0, sticky="nsew")

        self.status_text = tk.Label(self.right_panel, text="Status: Waiting", anchor="w", background="lightgray", font=("Courier", 14))
        self.status_text.grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        
        root.after(1000, self.preprocessing_and_update)
    
    def save_pgn(self):
        with open('Game.pgn', 'w', encoding='utf-8') as pgn_file:
            game = out.Game()
            node = game
            for move in self.previous_board.move_stack: node = node.add_variation(move)
            exporter = out.FileExporter(pgn_file)
            game.accept(exporter)
        root.destroy()
    
    def preprocessing_and_update(self):        
        self.cap = cv2.VideoCapture(1)
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.videoCapture(0)
        self.cap_lock = threading.Lock()
        _, frame = self.cap.read()

        self.status_text.config(text="Status: Loading Piece and Board Detection Models")
        self.Board_Recog = BoardRecognizerFullGame("PieceDetector.pt")
        self.Board_Recog.set_image(frame)
        self.status_text.config(text="Status: Running Initial Piece Detection")

        boxes, classes = self.Board_Recog.run_piece_detection(confidence=0.25)
        self.status_text.config(text="Status: Running Initial Board Detection")
        self.warp_image = self.Board_Recog.find_corners_perspective_transform()
        board, formatted_output = self.Board_Recog.find_board(self.warp_image, boxes, classes, board_num=self.count, table=True)
        final_board = self.Board_Recog.get_rotation(board)
        pychess_board, table = self.Board_Recog.make_pychess_board(final_board, formatted_output=formatted_output, table=True, save=True)
        self.num_pieces = len(pychess_board.piece_map())

        self.log_text.insert(tk.END, table + "\n\n" + str(pychess_board) + "\n")
        self.log_text.see(tk.END)

        with imgW(blob=chess.svg.board(self.previous_board).encode('utf-8'), format="svg") as img: # SVG --> PNG
            img.background_color = Color("white")
            img.alpha_channel = 'remove'
            img.save(filename="chess_board.png")
        
        width, height = self.leftImagePanel.winfo_width(), self.leftImagePanel.winfo_height()
        img = cv2.imread("chess_board.png")
        img = cv2.resize(img, (width, height))
        img_tk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))

        self.tk_img = img_tk  # Avoid garbage collection
        self.leftImagePanel.configure(image=img_tk)
        self.leftImagePanel.image = self.tk_img

        self.status_text.config(text="Status: Starting Board Generated")

        #Two daemonized threads for updating the board and updating the video
        threading.Thread(target=self.update_video, daemon=True).start()
        threading.Thread(target=self.update_board, daemon=True).start()

    def update_board(self):
        while True:
            ret, frame = False, None
            with self.cap_lock:
                ret, frame = self.cap.read()
            print(ret)
            if ret:
                
                #Running the pipeline in this chunk of code
                self.Board_Recog.set_image(frame:=cv2.resize(frame, (1280, 1280)))
                boxes, classes = self.Board_Recog.run_piece_detection(confidence=0.4)
                self.warp_image = self.Board_Recog.update_transform()
                board, formatted_output = self.Board_Recog.find_board(self.warp_image, boxes, classes, board_num = self.count, table=True)
                final_board = self.Board_Recog.get_rotation(board)
                pychess_board, table = self.Board_Recog.make_pychess_board(final_board, formatted_output=formatted_output, table=True) 

                #Running the chess logic housed in ChessLogic.py
                make_next_move(pychess_board, self.num_pieces, self.previous_board, root, self.status_text)

                with imgW(blob=chess.svg.board(self.previous_board).encode('utf-8'), format="svg") as img: # SVG --> PNG
                    img.background_color = Color("white")
                    img.alpha_channel = 'remove'
                    img.save(filename="chess_board.png")
                    
                    width, height = self.leftImagePanel.winfo_width(), self.leftImagePanel.winfo_height()
                    img = cv2.imread("chess_board.png")
                    img = cv2.resize(img, (width, height))
                    img_tk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
                    self.tk_img = img_tk  # Avoid garbage collection
                    root.after(0, lambda: self.leftImagePanel.configure(image=img_tk))
                    root.after(0, lambda: self.log_text.insert(tk.END, table + "\n\n" + str(pychess_board) + "\n"))
                    root.after(0, lambda: self.log_text.see(tk.END))
                    self.count+=1
                    self.num_pieces = len(pychess_board.piece_map())
            time.sleep(1/3)

    def update_video(self):
        while True:
            ret, frame = False, None
            with self.cap_lock:
                ret, frame = self.cap.read()
            if ret:
                new_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                width, height = self.leftVideoPanel.winfo_width(), self.leftVideoPanel.winfo_height()
                new_frame = cv2.resize(new_frame, (width, height))
                pillow_img = Image.fromarray(new_frame)
                self.tk_img_vid = ImageTk.PhotoImage(pillow_img)
                root.after(0, lambda: self.leftVideoPanel.configure(image=self.tk_img_vid))
                self.leftVideoPanel.image = self.tk_img_vid
            time.sleep(1/15) #15 fps for displaying video to UI

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
