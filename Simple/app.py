import dearpygui.dearpygui as dpg
import random
import time

# Initialize DearPyGUI
dpg.create_context()

# Game constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
CHOICES = ["Rock", "Paper", "Scissors"]

# Game state
player_score = 0
computer_score = 0
game_history = []
round_count = 0
last_result = ""

# Function to reset the game
def reset_game():
    global player_score, computer_score, game_history, round_count, last_result
    player_score = 0
    computer_score = 0
    game_history = []
    round_count = 0
    last_result = ""
    update_displays()
    dpg.configure_item("history_list", items=[])
    dpg.configure_item("result_text", default_value="Make your choice!")

# Function to determine winner
def determine_winner(player, computer):
    if player == computer:
        return "Draw!"
    elif (player == "Rock" and computer == "Scissors") or \
         (player == "Paper" and computer == "Rock") or \
         (player == "Scissors" and computer == "Paper"):
        return "You win!"
    else:
        return "Computer wins!"

# Function to make a choice and play a round
def play_round(sender, app_data, user_data):
    global player_score, computer_score, game_history, round_count, last_result
    
    # Get player choice and generate computer choice
    player_choice = user_data
    computer_choice = random.choice(CHOICES)
    
    # Determine the winner
    result = determine_winner(player_choice, computer_choice)
    last_result = f"You chose {player_choice}, Computer chose {computer_choice}. {result}"
    
    # Update scores
    if result == "You win!":
        player_score += 1
    elif result == "Computer wins!":
        computer_score += 1
    
    # Add to history
    round_count += 1
    timestamp = time.strftime("%H:%M:%S")
    history_entry = f"Round {round_count} [{timestamp}]: You: {player_choice}, PC: {computer_choice} - {result}"
    game_history.append(history_entry)
    
    update_displays()

# Function to update all displays
def update_displays():
    # Update result
    dpg.configure_item("result_text", default_value=last_result)
    
    # Update score
    dpg.configure_item("score_text", default_value=f"Score: You {player_score} - {computer_score} Computer")
    
    # Update history (show most recent first)
    dpg.configure_item("history_list", items=game_history[::-1])

# Create viewport and window
dpg.create_viewport(title="Rock Paper Scissors", width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

with dpg.window(label="Rock Paper Scissors", tag="primary_window", no_resize=True):
    dpg.add_text("Welcome to Rock Paper Scissors!", color=[0, 255, 0])
    dpg.add_text("Choose your weapon:", color=[200, 200, 200])
    
    # Add buttons for choices
    with dpg.group(horizontal=True):
        for choice in CHOICES:
            with dpg.group():
                dpg.add_button(label=choice, callback=play_round, user_data=choice, width=120, height=60)
                choice_image = f"{choice.lower()}_image"  # Placeholder for potential image
    
    dpg.add_spacer(height=10)
    
    # Display result and score
    dpg.add_text("Make your choice!", tag="result_text", color=[255, 255, 0])
    dpg.add_text("Score: You 0 - 0 Computer", tag="score_text")
    
    dpg.add_separator()
    
    # Reset button
    dpg.add_button(label="Reset Game", callback=reset_game, width=120)
    
    dpg.add_spacer(height=10)
    
    # Game history
    dpg.add_text("Game History:", color=[200, 200, 200])
    dpg.add_listbox(items=[], tag="history_list", width=-1, num_items=8)

# Setup and start
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("primary_window", True)

# Main application loop
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

dpg.destroy_context()
