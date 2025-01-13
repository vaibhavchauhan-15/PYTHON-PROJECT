# Tic Tac Toe Game

A Python implementation of the classic Tic Tac Toe game featuring multiple play modes including Player vs Player, Player vs Computer, and Computer vs Computer. The game includes an intelligent AI opponent and a user-friendly interface.

## Features

- Three game modes:
  - Player vs Computer
  - Player vs Player
  - Computer vs Computer
- Intelligent AI that:
  - Looks for winning moves
  - Blocks opponent's winning moves
  - Uses strategic position selection
- User-friendly command-line interface
- Visual board representation
- Input validation and error handling
- Easy-to-understand numpad-based move selection

## Requirements

- Python 3.6 or higher
- No external dependencies required

## Installation

1. Clone the repository:
```bash
git clone https://github.com/vaibhavchauhan-15/PYTHON-PROJECT/tree/main/TicTacToe
cd tic-tac-toe
```

2. Run the game:
```bash
python tic_tac_toe.py
```

## How to Play

1. Start the game and select a game mode (0-2):
   - 0: Player vs Computer
   - 1: Player vs Player
   - 2: Computer vs Computer

2. If playing as a human player, enter your name when prompted.

3. The board positions correspond to the numpad layout:
```
 7 | 8 | 9 
-----------
 4 | 5 | 6 
-----------
 1 | 2 | 3 
```

4. During your turn, enter a number (1-9) to place your marker in the corresponding position.

5. The game ends when either:
   - A player wins by getting three in a row (horizontally, vertically, or diagonally)
   - The board is full (draw)

## Game Rules

- Players take turns placing their markers (X or O) on the board
- The first player to get three of their markers in a row (horizontally, vertically, or diagonally) wins
- If all spaces are filled and no player has won, the game is a draw
- In AI mode, the computer makes strategic decisions based on:
  - Winning opportunities
  - Blocking opponent's winning moves
  - Controlling strategic positions (center, corners, edges)

## Project Structure

```
tic-tac-toe/
│
├── tic_tac_toe.py    # Main game file
├── README.md         # Project documentation
└── .gitignore       # Git ignore file
```

## Classes

### TicTacToe
- Manages the game board and game state
- Handles move validation and win checking
- Displays the game board

### Player
- Manages player information and move selection
- Handles both human and computer players
- Implements AI strategy for computer players

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## Future Improvements

- Add difficulty levels for AI
- Implement a graphical user interface (GUI)
- Add game statistics tracking
- Include unit tests
- Add network play capability
- Save/load game functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Vaibhav Chauhan

## Acknowledgments

- Thanks to python world
- Based on the classic Tic Tac Toe game

## Support

For support, issues, or suggestions, please create an issue in the GitHub repository or contact vaibhavchauhan.contact@gmail.com.