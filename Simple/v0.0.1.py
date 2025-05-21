import dearpygui.dearpygui as dpg
import random
import time

# Initialize DearPyGUI
dpg.create_context()

# Game constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CHOICES = ["Rock", "Paper", "Scissors"]

# Color theme
COLORS = {
    "background": [32, 32, 32],
    "primary": [65, 105, 225],    # Royal Blue
    "secondary": [70, 70, 70],
    "accent": [255, 165, 0],      # Orange
    "text": [240, 240, 240],
    "win": [0, 200, 0],
    "lose": [200, 0, 0],
    "draw": [200, 200, 0],
    "panel": [45, 45, 48]
}

# Game state
player_score = 0
computer_score = 0
game_history = []
round_count = 0
last_result = ""
total_rounds = 0
win_percentage = 0
draw_percentage = 0

# Function to reset the game
def reset_game():
    global player_score, computer_score, game_history, round_count, last_result, total_rounds, win_percentage, draw_percentage
    player_score = 0
    computer_score = 0
    game_history = []
    round_count = 0
    last_result = ""
    total_rounds = 0
    win_percentage = 0
    draw_percentage = 0
    update_displays()
    dpg.configure_item("history_list", items=[])
    dpg.configure_item("result_text", default_value="Make your choice!")
    dpg.configure_item("win_percentage", default_value="Win Rate: 0%")
    dpg.configure_item("draw_percentage", default_value="Draw Rate: 0%")

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
    global player_score, computer_score, game_history, round_count, last_result, total_rounds, win_percentage, draw_percentage
    
    # Get player choice and generate computer choice
    player_choice = user_data
    computer_choice = random.choice(CHOICES)
    
    # Determine the winner
    result = determine_winner(player_choice, computer_choice)
    last_result = f"You chose {player_choice}, Computer chose {computer_choice}."
    
    # Update scores
    if result == "You win!":
        player_score += 1
        result_color = COLORS["win"]
    elif result == "Computer wins!":
        computer_score += 1
        result_color = COLORS["lose"]
    else:
        result_color = COLORS["draw"]
    
    # Add to history
    round_count += 1
    total_rounds += 1
    timestamp = time.strftime("%H:%M:%S")
    history_entry = f"Round {round_count} [{timestamp}]: You: {player_choice}, PC: {computer_choice} - {result}"
    game_history.append(history_entry)
    
    # Calculate statistics
    if total_rounds > 0:
        win_percentage = (player_score / total_rounds) * 100
        draw_count = total_rounds - player_score - computer_score
        draw_percentage = (draw_count / total_rounds) * 100
    
    update_displays(result, result_color)

# Function to update all displays
def update_displays(result="", result_color=COLORS["text"]):
    # Update result
    if not result:
        dpg.configure_item("result_text", default_value=last_result)
    else:
        dpg.configure_item("result_text", default_value=last_result)
        dpg.configure_item("result_outcome", default_value=result, color=result_color)
    
    # Update score
    player_color = COLORS["win"] if player_score > computer_score else COLORS["text"]
    computer_color = COLORS["lose"] if player_score > computer_score else COLORS["text"]
    if player_score == computer_score:
        player_color = computer_color = COLORS["draw"]
    
    dpg.configure_item("player_score", default_value=str(player_score), color=player_color)
    dpg.configure_item("computer_score", default_value=str(computer_score), color=computer_color)
    
    # Update statistics
    dpg.configure_item("win_percentage", default_value=f"Win Rate: {win_percentage:.1f}%")
    dpg.configure_item("draw_percentage", default_value=f"Draw Rate: {draw_percentage:.1f}%")
    
    # Update history (show most recent first)
    dpg.configure_item("history_list", items=game_history[::-1])

# Create theme
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, COLORS["background"])
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, COLORS["primary"])
        dpg.add_theme_color(dpg.mvThemeCol_Button, COLORS["secondary"])
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, COLORS["primary"])
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, COLORS["accent"])
        dpg.add_theme_color(dpg.mvThemeCol_Text, COLORS["text"])
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, COLORS["panel"])
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)

# Create viewport and window
dpg.create_viewport(title="Rock Paper Scissors", width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
dpg.bind_theme(global_theme)

# Icons for choices (using text as placeholder - in a real app you'd use actual images)
ICONS = {
    "Rock": "✊",
    "Paper": "✋",
    "Scissors": "✌️"
}

with dpg.window(label="Rock Paper Scissors Dashboard", tag="primary_window", no_resize=True):
    # Header
    with dpg.group(horizontal=True):
        dpg.add_text("ROCK PAPER SCISSORS", color=COLORS["accent"])
        dpg.add_spacer(width=20)
        dpg.add_button(label="Reset Game", callback=reset_game, width=100, height=30)
    
    dpg.add_separator()
    
    # Main dashboard layout
    with dpg.group(horizontal=True):
        # Left panel - Game controls
        with dpg.child_window(width=250, height=450, border=False):
            with dpg.collapsing_header(label="Game Controls", default_open=True):
                dpg.add_text("Choose your weapon:", color=COLORS["text"])
                dpg.add_spacer(height=10)
                
                # Choice buttons with icons
                for choice in CHOICES:
                    with dpg.group(horizontal=True):
                        dpg.add_button(label=f"{ICONS[choice]} {choice}", callback=play_round, 
                                      user_data=choice, width=200, height=50)
                    dpg.add_spacer(height=5)
                
                dpg.add_separator()
                
                # Result display
                dpg.add_spacer(height=10)
                dpg.add_text("", tag="result_text", color=COLORS["text"])
                dpg.add_text("", tag="result_outcome", color=COLORS["text"])
                
                dpg.add_separator()
                
                # Scoreboard
                with dpg.group(horizontal=True):
                    dpg.add_text("YOU", color=COLORS["text"])
                    dpg.add_spacer(width=30)
                    dpg.add_text("vs", color=COLORS["text"])
                    dpg.add_spacer(width=30)
                    dpg.add_text("CPU", color=COLORS["text"])
                
                with dpg.group(horizontal=True):
                    dpg.add_text("0", tag="player_score", color=COLORS["text"])
                    dpg.add_spacer(width=40)
                    dpg.add_text("0", tag="computer_score", color=COLORS["text"])
        
        dpg.add_spacer(width=10)
        
        # Right panel - Stats and History
        with dpg.child_window(width=500, height=450, border=False):
            # Stats section
            with dpg.collapsing_header(label="Statistics", default_open=True):
                with dpg.group(horizontal=True):
                    dpg.add_text(f"Win Rate: 0%", tag="win_percentage", color=COLORS["win"])
                    dpg.add_spacer(width=40)
                    dpg.add_text(f"Draw Rate: 0%", tag="draw_percentage", color=COLORS["draw"])
                    dpg.add_spacer(width=40)
                    dpg.add_text(f"Total Rounds: {total_rounds}", tag="total_rounds", color=COLORS["text"])
            
            # History section
            with dpg.collapsing_header(label="Game History", default_open=True):
                dpg.add_text("Recent matches:", color=COLORS["text"])
                dpg.add_listbox(items=[], tag="history_list", width=-1, num_items=8)

# Setup and start
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("primary_window", True)

# Main application loop
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

dpg.destroy_context()
