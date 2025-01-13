import random
import time

class TicTacToe:
    def __init__(self):
        self.board = [' '] * 10  # Index 0 not used
        self.available = [str(num) for num in range(0, 10)]

    def display_welcome(self):
        print("\nWelcome! Let's play TIC TAC TOE!\n")
        print("The board positions correspond to your numpad:")
        print(" 7 | 8 | 9 ")
        print("-----------")
        print(" 4 | 5 | 6 ")
        print("-----------")
        print(" 1 | 2 | 3 ")
        print("\nJust input a position number (1-9).")

    def display_board(self):
        print("\n")
        print("    " + " {} | {} | {} ".format(self.board[7], self.board[8], self.board[9]))
        print("    " + "-----------")
        print("    " + " {} | {} | {} ".format(self.board[4], self.board[5], self.board[6]))
        print("    " + "-----------")
        print("    " + " {} | {} | {} ".format(self.board[1], self.board[2], self.board[3]))
        print("\nAvailable moves:", [i for i in range(1, 10) if self.board[i] == ' '])

    def make_move(self, position, marker):
        if self.is_space_free(position):
            self.board[position] = marker
            self.available[position] = ' '
            return True
        return False

    def is_space_free(self, position):
        return self.board[position] == ' '

    def is_board_full(self):
        return ' ' not in self.board[1:]

    def check_win(self, marker):
        win_combinations = [
            [1, 2, 3], [4, 5, 6], [7, 8, 9],  # Horizontal
            [1, 4, 7], [2, 5, 8], [3, 6, 9],  # Vertical
            [1, 5, 9], [3, 5, 7]  # Diagonal
        ]
        return any(all(self.board[pos] == marker for pos in combo) for combo in win_combinations)

class Player:
    def __init__(self, name, marker, is_computer=False):
        self.name = name
        self.marker = marker
        self.is_computer = is_computer

    def get_move(self, game):
        if self.is_computer:
            return self.get_computer_move(game)
        else:
            return self.get_human_move(game)

    def get_human_move(self, game):
        while True:
            try:
                position = int(input(f'\n{self.name} ({self.marker}), choose position (1-9): '))
                if 1 <= position <= 9 and game.is_space_free(position):
                    return position
                print("Invalid move. Try again.")
            except ValueError:
                print("Please enter a number between 1 and 9.")

    def get_computer_move(self, game):
        # Check for winning move
        for i in range(1, 10):
            if game.is_space_free(i):
                game.board[i] = self.marker
                if game.check_win(self.marker):
                    game.board[i] = ' '
                    return i
                game.board[i] = ' '

        # Check for blocking opponent's winning move
        opponent_marker = 'O' if self.marker == 'X' else 'X'
        for i in range(1, 10):
            if game.is_space_free(i):
                game.board[i] = opponent_marker
                if game.check_win(opponent_marker):
                    game.board[i] = ' '
                    return i
                game.board[i] = ' '

        # Choose center if available
        if game.is_space_free(5):
            return 5

        # Choose corners
        corners = [1, 3, 7, 9]
        available_corners = [x for x in corners if game.is_space_free(x)]
        if available_corners:
            return random.choice(available_corners)

        # Choose edges
        edges = [2, 4, 6, 8]
        available_edges = [x for x in edges if game.is_space_free(x)]
        if available_edges:
            return random.choice(available_edges)

def main():
    while True:
        game = TicTacToe()
        game.display_welcome()

        print("\n[0] Player vs Computer")
        print("[1] Player vs Player")
        print("[2] Computer vs Computer")
        
        while True:
            try:
                mode = int(input("\nSelect mode (0-2): "))
                if 0 <= mode <= 2:
                    break
                print("Please enter 0, 1, or 2.")
            except ValueError:
                print("Please enter a valid number.")

        if mode == 0:
            player1 = Player(input("Enter your name: ").capitalize(), 'X')
            player2 = Player("Computer", 'O', True)
        elif mode == 1:
            player1 = Player(input("Enter Player 1 name: ").capitalize(), 'X')
            player2 = Player(input("Enter Player 2 name: ").capitalize(), 'O')
        else:
            player1 = Player("Computer 1", 'X', True)
            player2 = Player("Computer 2", 'O', True)

        current_player = random.choice([player1, player2])
        print(f"\n{current_player.name} goes first!")

        while True:
            game.display_board()
            
            position = current_player.get_move(game)
            game.make_move(position, current_player.marker)

            if current_player.is_computer:
                print(f"\n{current_player.name} placed at position {position}")
                time.sleep(1)

            if game.check_win(current_player.marker):
                game.display_board()
                print(f"\nCongratulations! {current_player.name} wins!")
                break

            if game.is_board_full():
                game.display_board()
                print("\nIt's a draw!")
                break

            current_player = player2 if current_player == player1 else player1

        if input("\nPlay again? (y/n): ").lower() != 'y':
            break

    print("\nThanks for playing!")

if __name__ == "__main__":
    main()