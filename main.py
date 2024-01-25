import tkinter as tk
import chess
from PIL import ImageTk, Image
import threading
import berserk

import requests
import json


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



def streamlink(id):
    return f"https://lichess.org/api/stream/game/{id}"

move_stack = []


class ChessGameGUI:
    def __init__(self):
        #self.root = root
        #self.root.title("Chess Game")

        self.board = chess.Board()
        self.selected_square = None

        #self.canvas = tk.Canvas(self.root, width=640, height=640)
        #self.canvas.pack()

        #self.images = self.load_images()

        #self.draw_board()
        #self.canvas.bind("<Button-1>", self.handle_click)

    def parsejson(self): #функция не относится к классу и дожна быть вынесена за класс
        url = streamlink(id)
        print(url)
        response = requests.get(url, stream=True)
        for line in response.iter_lines():
            dump = json.loads(line)
            try:
                last_move = dump["lm"];
                try:
                    if (move_stack[-1] != last_move):
                        move_stack.append(last_move)
                except IndexError:
                    move_stack.append(last_move)
                    print("INSTACK", last_move)
                    #self.board.push(chess.Move.from_uci(last_move))
                    #cur = move_stack[-1]
                    # while (cur == move_stack[-1]):
                    #     continue
                    if (last_move != move_stack[0]):
                        self.board.push(chess.Move.from_uci(last_move))
                    print("Stack is empty")
            except KeyError:
                print('Moves maked: 0')
        '''
        headers = {"Accept": "application/x-ndjson"}
        response = requests.get(url, headers=headers, stream=True)
        list_resp = response.text.splitlines()
        json_resp = list(map(lambda x: json.loads(x), list_resp))
        print( json_resp )
        '''
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
                #move_input = input("Enter your move in SAN notation (e.g. e4) or type 'exit' to quit: ")
                make_move(move_input)
                if move_input.lower() == 'exit':
                    break
                move = chess.Move.from_uci(move_input)
                # print("type", type(move));
                #print(type(self.board.legal_moves[0]), self.board.legal_moves[0])
                print("san", self.board.san(move))
                san = str(self.board.san(move))
                legal_moves = list(str(i) for i in tuple(self.board.legal_moves))
                #print("tuple", str(tup[0]))
                if san or move in legal_moves:
                    self.board.push(move)
                    #self.draw_board()
                else:
                    print("Invalid  move. Please try again.")
                try:
                    cur = move_stack[-1]
                    while (cur == move_stack[-1]):
                        continue

                    print("Lastmove", move_stack[-1])
                    cur = move_stack[-1]
                    while (cur == move_stack[-1]):
                        continue
                    print("Lastmove2", move_stack[-1])
                    self.board.push(chess.Move.from_uci(move_stack[-1]))
                    print(self.board)
                    #because ping of moves is very big

                except IndexError:
                    print("No one make move")
        thread = threading.Thread(target=self.parsejson)
        thread.start()
        thread = threading.Thread(target=accept_moves)
        thread.start()



if __name__ == "__main__":
    #root = tk.Tk()
    game = ChessGameGUI()
    game.input_moves_from_console()
    #root.mainloop()
