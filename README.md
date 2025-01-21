# Clobber

Contains a CLI for the game clobber, and two computer players (mcts.py and proof_number.py). Monte Carlo Tree Search is deprecated. Proof Number Search works but currently runs until the game is solved. 

## Description



## Getting Started

To get things working, you'll need to install PrettyPrintTree (see: https://github.com/AharonSambol/PrettyPrintTree). You can do this with `pip`:

```
pip install PrettyPrintTree
```

If you want to run the program without dependencies, you can comment out the import in clobber.py and any reference to `pt` or `PrettyPrintTree` (but why??). Run the game from the command line by navigating to the project directory and typing:

```
python clobber.py
```

If you elect to pretty print the search tree, the console will print every step of proof number search. If you are playing on a board with more than ~9 squares, this will make a mess. 

The CLI recognizes the following commands:
-"quit" (exits the CLI)
-"size" (board size, e.g. "size 5x3")
-"play" (play a move, e.g. "play x b3 s" will move the piece x at position b3 south to capture the piece at b4)
-"show" (prints the current board)
-"pn" (runs proof number search for player, e.g. "pn x")

If you try to break the CLI, you will succeed. The checks to catch bad inputs are not robust. 

## Authors

Contributors names and contact info

Abel Romer  
[Website](https://ww.abelromer.com)
