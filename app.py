import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random  # Added for computer player's random moves

# Initialize game state
if 'board' not in st.session_state:
    st.session_state.board = np.full((3, 3), '_')
if 'current_player' not in st.session_state:
    st.session_state.current_player = 'X'
if 'winner' not in st.session_state:
    st.session_state.winner = None
# Initialize game statistics
if 'stats' not in st.session_state:
    st.session_state.stats = {'X': 0, 'O': 0, 'Tie': 0}
# Initialize move history
if 'moves' not in st.session_state:
    st.session_state.moves = []
# Initialize game mode
if 'game_mode' not in st.session_state:
    st.session_state.game_mode = 'Two Players'

# Helper functions
def check_winner(board):
    lines = [*board, *board.T, board.diagonal(), np.fliplr(board).diagonal()]
    for line in lines:
        if np.all(line == 'X'):
            return 'X'
        if np.all(line == 'O'):
            return 'O'
    return None

def render_board(board):
    df = pd.DataFrame(board, columns=['0', '1', '2'], index=['0', '1', '2'])
    st.dataframe(df)

def plot_board(board):
    fig, ax = plt.subplots(figsize=(5, 5))
    # Draw grid
    for i in range(1, 3):
        ax.axhline(i - 0.5, color='black', linewidth=2)
        ax.axvline(i - 0.5, color='black', linewidth=2)
    
    # Draw X and O with colors
    for (i, j), mark in np.ndenumerate(board):
        if mark == 'X':
            ax.text(j, 2 - i, mark, fontsize=48, ha='center', va='center', color='blue')
        elif mark == 'O':
            ax.text(j, 2 - i, mark, fontsize=48, ha='center', va='center', color='red')
    
    # Highlight winning patterns if there's a winner
    if st.session_state.winner:
        board = st.session_state.board
        # Check rows
        for i in range(3):
            if np.all(board[i, :] == st.session_state.winner):
                ax.plot([0, 2], [2-i, 2-i], 'g-', linewidth=3)
        # Check columns
        for j in range(3):
            if np.all(board[:, j] == st.session_state.winner):
                ax.plot([j, j], [0, 2], 'g-', linewidth=3)
        # Check diagonals
        if np.all(np.diag(board) == st.session_state.winner):
            ax.plot([0, 2], [2, 0], 'g-', linewidth=3)
        if np.all(np.diag(np.fliplr(board)) == st.session_state.winner):
            ax.plot([0, 2], [0, 2], 'g-', linewidth=3)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-0.5, 2.5)
    ax.set_facecolor('#f0f0f0')  # Light background
    fig.tight_layout()
    st.pyplot(fig)

# Computer player functions
def computer_move_easy(board):
    empty_cells = [(i, j) for i in range(3) for j in range(3) if board[i, j] == '_']
    if empty_cells:
        return random.choice(empty_cells)
    return None

def computer_move_hard(board, computer_mark='O', player_mark='X'):
    # Check for winning move
    for i in range(3):
        for j in range(3):
            if board[i, j] == '_':
                board[i, j] = computer_mark
                if check_winner(board) == computer_mark:
                    board[i, j] = '_'
                    return (i, j)
                board[i, j] = '_'
    
    # Block player's winning move
    for i in range(3):
        for j in range(3):
            if board[i, j] == '_':
                board[i, j] = player_mark
                if check_winner(board) == player_mark:
                    board[i, j] = '_'
                    return (i, j)
                board[i, j] = '_'
    
    # Take center if available
    if board[1, 1] == '_':
        return (1, 1)
    
    # Take corners
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    empty_corners = [corner for corner in corners if board[corner] == '_']
    if empty_corners:
        return random.choice(empty_corners)
    
    # Take edges
    edges = [(0, 1), (1, 0), (1, 2), (2, 1)]
    empty_edges = [edge for edge in edges if board[edge] == '_']
    if empty_edges:
        return random.choice(empty_edges)
    
    return None

def make_move(i, j):
    st.session_state.board[i, j] = st.session_state.current_player
    # Record the move in history
    st.session_state.moves.append({
        'Move': len(st.session_state.moves) + 1,
        'Player': st.session_state.current_player,
        'Position': f"({i}, {j})"
    })
    # Check for winner
    st.session_state.winner = check_winner(st.session_state.board)
    # Switch player
    st.session_state.current_player = 'O' if st.session_state.current_player == 'X' else 'X'

# Main UI
st.title("Tic Tac Toe")

# Sidebar configuration
with st.sidebar:
    # Game mode selection
    st.header("Game Settings")
    game_mode = st.radio(
        "Game Mode",
        ['Two Players', 'vs Computer (Easy)', 'vs Computer (Hard)']
    )
    
    if game_mode != st.session_state.game_mode:
        st.session_state.game_mode = game_mode
        # Reset game when mode changes
        for key in ['board', 'current_player', 'winner', 'moves']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    # Game statistics
    st.header("Game Statistics")
    st.write(f"Player X wins: {st.session_state.stats['X']}")
    st.write(f"Player O wins: {st.session_state.stats['O']}")
    st.write(f"Ties: {st.session_state.stats['Tie']}")
    
    # Move history
    if st.session_state.moves:
        st.header("Move History")
        moves_df = pd.DataFrame(st.session_state.moves)
        st.dataframe(moves_df)
    
    # Game analysis
    st.header("Game Analysis")
    if st.button("Show Analysis") and st.session_state.moves:
        moves_df = pd.DataFrame(st.session_state.moves)
        
        # Analysis 1: Moves per player
        st.subheader("Moves per Player")
        player_counts = moves_df['Player'].value_counts()
        st.bar_chart(player_counts)
        
        # Analysis 2: Board positions heatmap
        st.subheader("Board Position Heatmap")
        position_counts = np.zeros((3, 3))
        for move in st.session_state.moves:
            pos = move['Position'].strip('()').split(',')
            i, j = int(pos[0]), int(pos[1])
            position_counts[i, j] += 1
            
        fig, ax = plt.subplots()
        im = ax.imshow(position_counts, cmap='viridis')
        for i in range(3):
            for j in range(3):
                ax.text(j, i, int(position_counts[i, j]), 
                        ha="center", va="center", color="w")
        plt.colorbar(im)
        st.pyplot(fig)

# Display board and interactive buttons
cols = st.columns(3)
for i in range(3):
    for j in range(3):
        with cols[j]:
            label = st.session_state.board[i, j]
            key = f"button_{i}_{j}"
            if st.button(label if label != '_' else ' ', key=key, disabled=(label != '_' or st.session_state.winner is not None)):
                make_move(i, j)
                
                # Computer's turn if in computer mode and no winner yet
                if (st.session_state.game_mode in ['vs Computer (Easy)', 'vs Computer (Hard)'] and 
                    st.session_state.winner is None and 
                    '_' in st.session_state.board):
                    
                    # Computer makes a move
                    if st.session_state.game_mode == 'vs Computer (Easy)':
                        comp_i, comp_j = computer_move_easy(st.session_state.board)
                    else:  # Hard mode
                        comp_i, comp_j = computer_move_hard(st.session_state.board)
                    
                    if comp_i is not None and comp_j is not None:
                        make_move(comp_i, comp_j)
                
                # Rerun to update the UI
                st.rerun()

# Show board state
render_board(st.session_state.board)
plot_board(st.session_state.board)

# Game status
ingame = '_' in st.session_state.board and st.session_state.winner is None
if st.session_state.winner:
    st.success(f"Player {st.session_state.winner} wins!")
    # Update statistics
    if 'stats' in st.session_state:
        st.session_state.stats[st.session_state.winner] += 1
elif not ingame:
    st.info("It's a tie!")
    # Update statistics for ties
    if 'stats' in st.session_state:
        st.session_state.stats['Tie'] += 1
else:
    st.write(f"Current player: {st.session_state.current_player}")
    if st.session_state.game_mode != 'Two Players' and st.session_state.current_player == 'O':
        st.write("Computer is thinking...")

# Reset button
if st.button('Restart'):
    # Preserve statistics but reset the game
    stats = st.session_state.stats
    for key in list(st.session_state.keys()):
        if key != 'stats' and key != 'game_mode':
            del st.session_state[key]
    st.session_state.stats = stats
    st.rerun()