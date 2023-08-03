import tkinter as tk
import chess
from PIL import ImageTk, Image
import threading
import berserk

API_TOKEN = "YOUR_TOKEN"

session = berserk.TokenSession(API_TOKEN)
client = berserk.Client(session=session)


def create_game():
    return client.challenges.create_ai(color='white', level=1, clock_limit=120, clock_increment=3)


# Функция для создания новой игры
game = create_game()
id = game['id']
queue = -1
if (game['player'] == 'white'):
    queue = 0
else:
    queue = 1


# 0 - white, 1 - black

def make_move(move):
    global queue
    print(game)
    if queue == 0:
        client.board.make_move(id, move)
    else:
        client.board.make_move(id, move)


class ChessGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")

        self.board = chess.Board()
        self.selected_square = None

        self.canvas = tk.Canvas(self.root, width=640, height=640)
        self.canvas.pack()

        self.images = self.load_images()

        self.draw_board()
        self.canvas.bind("<Button-1>", self.handle_click)

    def load_images(self):
        images = {}
        pieces = ["Pw", "Rw", "Nw", "Bw", "Qw", "Kw",
                  'pb', 'rb', 'nb', 'bb', 'qb', 'kb']
        for piece in pieces:
            img = Image.open(f"pieces/{piece}.png")
            img = img.resize((60, 60))
            images[piece] = ImageTk.PhotoImage(img)
        return images

    def draw_board(self):
        self.canvas.delete("all")
        dark_color = "#B58863"
        light_color = "#F0D9B5"

        for row in range(8):
            for column in range(8):
                x1 = column * 80
                y1 = row * 80
                x2 = x1 + 80
                y2 = y1 + 80

                if (row + column) % 2 == 0:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=light_color)
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=dark_color)

        for move in self.board.legal_moves:
            x = chess.square_file(move.to_square) * 80 + 40
            y = (7 - chess.square_rank(move.to_square)) * 80 + 40
            self.canvas.create_text(x, y, text=str(move), font=("Arial", 10, "bold"), fill="red")

        for square, piece in self.board.piece_map().items():
            x = chess.square_file(square) * 80 + 40
            y = (7 - chess.square_rank(square)) * 80 + 40
            if piece.symbol() == piece.symbol().lower():
                piece_image = self.images.get(piece.symbol() + 'b')
            else:
                piece_image = self.images.get(piece.symbol() + 'w')
            if piece_image:
                self.canvas.create_image(x, y, image=piece_image, anchor="c")

    def handle_click(self, event):
        x = event.x // 80
        y = event.y // 80
        square = chess.square(x, 7 - y)

        if self.selected_square is None:
            self.selected_square = square
        else:
            move = chess.Move(self.selected_square, square)
            global queue
            if move in self.board.legal_moves:
                self.board.push(move)
                make_move(move)
            self.selected_square = None

        self.draw_board()

    def input_moves_from_console(self):
        def accept_moves():
            global queue
            while True:
                move_input = input("Enter your move in UCI notation (e.g. e2e4) or type 'exit' to quit: ")
                make_move(move_input)
                if move_input.lower() == 'exit':
                    break
                move = chess.Move.from_uci(move_input)
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.draw_board()
                else:
                    print("Invalid  move. Please try again.")

        thread = threading.Thread(target=accept_moves)
        thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGameGUI(root)
    game.input_moves_from_console()
    root.mainloop()
