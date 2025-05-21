import dearpygui.dearpygui as dpg
import random
import time
import pandas as pd
import os
import sys

# Initialize DearPyGUI
dpg.create_context()

# Game constants
CHOICES = ["Rock", "Paper", "Scissors"]

# Excel file path
EXCEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rps_data.xlsx")

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
    "panel": [45, 45, 48],
    "sidebar": [35, 35, 38],
    "sidebar_hover": [55, 55, 58],
    "sidebar_active": [75, 75, 78]
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
current_view = "game"

# Icons for choices and navigation
ICONS = {
    "Rock": "✊",
    "Paper": "✋",
    "Scissors": "✌️",
    "Game": "🎮",
    "Stats": "📊",
    "History": "📜",
    "Settings": "⚙️",
    "Export": "📤"
}

# Function to save game data to Excel
def save_to_excel():
    # Create DataFrame from game history
    if not game_history:
        return
        
    history_data = []
    for i, h in enumerate(game_history):
        try:
            # More robust parsing of history entries
            round_info = h.split(": ", 1)  # Split only on first occurrence
            if len(round_info) < 2:
                continue  # Skip malformed entries
                
            timestamp_part = round_info[0]
            timestamp = timestamp_part.split("[")[1].split("]")[0] if "[" in timestamp_part and "]" in timestamp_part else "unknown"
            
            # Extract choices and result
            game_detail = round_info[1]
            
            # Handle different possible formats
            if " - " in game_detail:
                choices_part, result = game_detail.split(" - ", 1)
            else:
                choices_part, result = game_detail, "Unknown"
                
            # Extract player and computer choices
            if ", " in choices_part:
                player_part, computer_part = choices_part.split(", ", 1)
            else:
                player_part, computer_part = choices_part, "PC: Unknown"
                
            player_choice = player_part.replace("You: ", "") if "You: " in player_part else player_part
            computer_choice = computer_part.replace("PC: ", "") if "PC: " in computer_part else computer_part
            
            history_data.append({
                "Round": i+1,
                "Timestamp": timestamp,
                "Player Choice": player_choice,
                "Computer Choice": computer_choice,
                "Result": result
            })
        except Exception as e:
            print(f"Error parsing history entry {i}: {e}")
            # Add a fallback entry with available information
            history_data.append({
                "Round": i+1,
                "Timestamp": "error",
                "Player Choice": "error",
                "Computer Choice": "error",
                "Result": "Error parsing entry"
            })
    
    df_history = pd.DataFrame(history_data)
    
    # Create stats DataFrame
    stats_data = {
        "Statistic": ["Player Score", "Computer Score", "Total Rounds", "Win Rate", "Draw Rate"],
        "Value": [player_score, computer_score, total_rounds, 
                 f"{win_percentage:.1f}%" if total_rounds > 0 else "0%", 
                 f"{draw_percentage:.1f}%" if total_rounds > 0 else "0%"]
    }
    df_stats = pd.DataFrame(stats_data)
    
    # Save to Excel with multiple sheets
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            df_history.to_excel(writer, sheet_name='Game History', index=False)
            df_stats.to_excel(writer, sheet_name='Statistics', index=False)
        dpg.configure_item("status_text", default_value=f"Data saved to {EXCEL_FILE}", color=COLORS["win"])
    except Exception as e:
        dpg.configure_item("status_text", default_value=f"Error saving data: {str(e)}", color=COLORS["lose"])

# Function to load game data from Excel
def load_from_excel():
    global player_score, computer_score, game_history, round_count, total_rounds, win_percentage, draw_percentage
    
    if not os.path.exists(EXCEL_FILE):
        dpg.configure_item("status_text", default_value="No saved data found", color=COLORS["accent"])
        return False
    
    try:
        # Read history sheet
        df_history = pd.read_excel(EXCEL_FILE, sheet_name='Game History')
        
        # Convert history data back to our format
        game_history = []
        for _, row in df_history.iterrows():
            entry = f"Round {row['Round']} [{row['Timestamp']}]: You: {row['Player Choice']}, PC: {row['Computer Choice']} - {row['Result']}"
            game_history.append(entry)
        
        # Read stats sheet
        df_stats = pd.read_excel(EXCEL_FILE, sheet_name='Statistics')
        
        # Extract stats
        stats_dict = dict(zip(df_stats['Statistic'], df_stats['Value']))
        player_score = int(stats_dict.get('Player Score', 0))
        computer_score = int(stats_dict.get('Computer Score', 0))
        total_rounds = int(stats_dict.get('Total Rounds', 0))
        
        # Parse percentage values
        win_rate_str = stats_dict.get('Win Rate', '0%')
        win_percentage = float(win_rate_str.replace('%', ''))
        
        draw_rate_str = stats_dict.get('Draw Rate', '0%')
        draw_percentage = float(draw_rate_str.replace('%', ''))
        
        round_count = len(game_history)
        
        # Update UI
        update_displays()
        dpg.configure_item("history_list", items=game_history[::-1])
        dpg.configure_item("status_text", default_value="Data loaded successfully", color=COLORS["win"])
        
        return True
    except Exception as e:
        dpg.configure_item("status_text", default_value=f"Error loading data: {str(e)}", color=COLORS["lose"])
        return False

# Function to reset the game
def reset_game():
    global player_score, computer_score, game_history, round_count, last_result, total_rounds, win_percentage, draw_percentage
    
    # Reset game state variables
    player_score = 0
    computer_score = 0
    game_history = []
    round_count = 0
    last_result = ""
    total_rounds = 0
    win_percentage = 0
    draw_percentage = 0
    
    # Helper function to safely configure items
    def safe_configure_item(tag, **kwargs):
        try:
            if dpg.does_item_exist(tag):
                dpg.configure_item(tag, **kwargs)
        except Exception as e:
            print(f"Error configuring item {tag} in reset_game: {e}")
    
    # Update UI elements safely
    try:
        update_displays()
        safe_configure_item("history_list", items=[])
        safe_configure_item("detailed_history", items=[])
        safe_configure_item("result_text", default_value="Make your choice!")
        safe_configure_item("win_percentage", default_value="Win Rate: 0%")
        safe_configure_item("draw_percentage", default_value="Draw Rate: 0%")
        safe_configure_item("total_rounds_text", default_value="Total Rounds: 0")
        safe_configure_item("status_text", default_value="Game reset", color=COLORS["accent"])
        
        # Reset statistics view items if they exist
        safe_configure_item("stats_player_wins", default_value="0")
        safe_configure_item("stats_win_rate", default_value="0%")
        safe_configure_item("stats_computer_wins", default_value="0")
        safe_configure_item("stats_computer_win_rate", default_value="0%")
        safe_configure_item("stats_total_rounds", default_value="0")
        safe_configure_item("stats_draws", default_value="0")
        safe_configure_item("stats_draw_rate", default_value="0%")
        safe_configure_item("stats_fav_choice", default_value="N/A")
        
    except Exception as e:
        print(f"Error in reset_game: {e}")
        try:
            dpg.configure_item("status_text", default_value=f"Error resetting game: {str(e)}", color=COLORS["lose"])
        except:
            print("Could not update status text")

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
    
    # Add to history (limit history size to prevent memory issues)
    MAX_HISTORY = 100
    round_count += 1
    total_rounds += 1
    timestamp = time.strftime("%H:%M:%S")
    history_entry = f"Round {round_count} [{timestamp}]: You: {player_choice}, PC: {computer_choice} - {result}"
    game_history.append(history_entry)
    
    # Trim history if it gets too large
    if len(game_history) > MAX_HISTORY:
        game_history = game_history[-MAX_HISTORY:]
    
    # Calculate statistics
    if total_rounds > 0:
        win_percentage = (player_score / total_rounds) * 100
        draw_count = total_rounds - player_score - computer_score
        draw_percentage = (draw_count / total_rounds) * 100
    
    # Update displays (use try-except to prevent crashes)
    try:
        update_displays(result, result_color)
        
        # Only update detailed history if history view is active
        if current_view == "history":
            dpg.configure_item("detailed_history", items=game_history[::-1])
    except Exception as e:
        print(f"Error updating displays: {e}")
        dpg.configure_item("status_text", default_value=f"Error: {str(e)}", color=COLORS["lose"])

# Function to update all displays
def update_displays(result="", result_color=COLORS["text"]):
    try:
        # Helper function to safely configure items
        def safe_configure_item(tag, **kwargs):
            try:
                if dpg.does_item_exist(tag):
                    dpg.configure_item(tag, **kwargs)
            except Exception as e:
                print(f"Error configuring item {tag}: {e}")
        
        # Update result
        if not result:
            safe_configure_item("result_text", default_value=last_result)
        else:
            safe_configure_item("result_text", default_value=last_result)
            safe_configure_item("result_outcome", default_value=result, color=result_color)
        
        # Update score
        player_color = COLORS["win"] if player_score > computer_score else COLORS["text"]
        computer_color = COLORS["lose"] if player_score > computer_score else COLORS["text"]
        if player_score == computer_score:
            player_color = computer_color = COLORS["draw"]
        
        safe_configure_item("player_score", default_value=str(player_score), color=player_color)
        safe_configure_item("computer_score", default_value=str(computer_score), color=computer_color)
        
        # Update statistics
        safe_configure_item("win_percentage", default_value=f"Win Rate: {win_percentage:.1f}%")
        safe_configure_item("draw_percentage", default_value=f"Draw Rate: {draw_percentage:.1f}%")
        safe_configure_item("total_rounds_text", default_value=f"Total Rounds: {total_rounds}")
        
        # Only update history in game view (detailed history updated separately)
        if game_history:
            safe_configure_item("history_list", items=game_history[-8:][::-1])  # Show only last 8 entries for better performance
    except Exception as e:
        print(f"Error in update_displays: {e}")

# Function to switch views
def switch_view(sender, app_data, user_data):
    global current_view
    current_view = user_data
    
    try:
        # Hide all views
        dpg.configure_item("game_view", show=False)
        dpg.configure_item("stats_view", show=False)
        dpg.configure_item("history_view", show=False)
        dpg.configure_item("settings_view", show=False)
        
        # Show selected view
        dpg.configure_item(f"{user_data}_view", show=True)
        
        # Update sidebar buttons
        for view in ["game", "stats", "history", "settings"]:
            if view == user_data:
                dpg.bind_item_theme(f"{view}_button", active_button_theme)
            else:
                dpg.bind_item_theme(f"{view}_button", button_theme)
        
        # Update view-specific data
        if user_data == "history":
            dpg.configure_item("detailed_history", items=game_history[::-1])
        elif user_data == "stats" and total_rounds > 0:
            update_statistics_view()
    except Exception as e:
        print(f"Error switching views: {e}")
        dpg.configure_item("status_text", default_value=f"Error: {str(e)}", color=COLORS["lose"])

# New function to update stats view separately (for better performance)
def update_statistics_view():
    if total_rounds == 0:
        return
        
    try:
        dpg.configure_item("stats_player_wins", default_value=str(player_score))
        dpg.configure_item("stats_win_rate", default_value=f"{win_percentage:.1f}%")
        
        dpg.configure_item("stats_computer_wins", default_value=str(computer_score))
        computer_win_rate = (computer_score / total_rounds) * 100
        dpg.configure_item("stats_computer_win_rate", default_value=f"{computer_win_rate:.1f}%")
        
        dpg.configure_item("stats_total_rounds", default_value=str(total_rounds))
        draws = total_rounds - player_score - computer_score
        dpg.configure_item("stats_draws", default_value=str(draws))
        dpg.configure_item("stats_draw_rate", default_value=f"{draw_percentage:.1f}%")
        
        # Calculate favorite choice if there's history
        if game_history:
            choices_count = {"Rock": 0, "Paper": 0, "Scissors": 0}
            # Only process the last 50 games for performance
            for entry in game_history[-50:]:
                for choice in CHOICES:
                    if f"You: {choice}" in entry:
                        choices_count[choice] += 1
            
            favorite = max(choices_count, key=choices_count.get)
            dpg.configure_item("stats_fav_choice", default_value=f"{favorite} ({choices_count[favorite]} times)")
    except Exception as e:
        print(f"Error updating statistics: {e}")

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

# Create button themes
with dpg.theme() as button_theme:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, COLORS["sidebar"])
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, COLORS["sidebar_hover"])
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, COLORS["sidebar_active"])
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)

with dpg.theme() as active_button_theme:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, COLORS["primary"])
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, COLORS["primary"])
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, COLORS["primary"])
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)

# Create viewport
dpg.create_viewport(title="Rock Paper Scissors Dashboard", width=1200, height=800)
dpg.bind_theme(global_theme)

# Setup viewport configuration for fullscreen
dpg.configure_viewport(0, maximized=True)

# Main window
with dpg.window(label="Rock Paper Scissors Dashboard", tag="primary_window", no_resize=True, no_close=True, no_collapse=True, no_move=True):
    # Main layout (sidebar + content area)
    with dpg.group(horizontal=True):
        # Sidebar
        with dpg.child_window(width=200, tag="sidebar", border=False, height=-1):
            dpg.add_text("NAVIGATION", color=COLORS["accent"])
            dpg.add_separator()
            
            # Navigation buttons
            with dpg.group():
                dpg.add_button(label=f"{ICONS['Game']} Game", callback=switch_view, user_data="game", width=-1, height=40, tag="game_button")
                dpg.bind_item_theme("game_button", active_button_theme)
                
                dpg.add_button(label=f"{ICONS['Stats']} Statistics", callback=switch_view, user_data="stats", width=-1, height=40, tag="stats_button")
                dpg.bind_item_theme("stats_button", button_theme)
                
                dpg.add_button(label=f"{ICONS['History']} History", callback=switch_view, user_data="history", width=-1, height=40, tag="history_button")
                dpg.bind_item_theme("history_button", button_theme)
                
                dpg.add_button(label=f"{ICONS['Settings']} Settings", callback=switch_view, user_data="settings", width=-1, height=40, tag="settings_button")
                dpg.bind_item_theme("settings_button", button_theme)
            
            dpg.add_spacer(height=20)
            
            # Excel Export/Import
            dpg.add_text("DATA", color=COLORS["accent"])
            dpg.add_separator()
            dpg.add_button(label=f"{ICONS['Export']} Save to Excel", callback=save_to_excel, width=-1, height=30)
            dpg.add_button(label="📥 Load from Excel", callback=load_from_excel, width=-1, height=30)
            
            dpg.add_spacer(height=20)
            dpg.add_text("Actions", color=COLORS["accent"])
            dpg.add_separator()
            dpg.add_button(label="🔄 Reset Game", callback=reset_game, width=-1, height=30)
            dpg.add_button(label="❌ Exit", callback=lambda: sys.exit(0), width=-1, height=30)
            
            # Status text at the bottom of sidebar
            dpg.add_spacer(height=20)
            dpg.add_separator()
            dpg.add_text("Status: Ready", tag="status_text", color=COLORS["text"], wrap=180)
        
        # Content Area
        with dpg.child_window(tag="content_area", border=False):
            # Game View
            with dpg.child_window(tag="game_view", show=True, border=False):
                with dpg.group(horizontal=True):
                    # Game controls panel
                    with dpg.child_window(width=400, height=-1, border=False):
                        with dpg.collapsing_header(label="Game Controls", default_open=True):
                            dpg.add_text("Choose your weapon:", color=COLORS["text"])
                            dpg.add_spacer(height=10)
                            
                            # Choice buttons with icons
                            for choice in CHOICES:
                                with dpg.group(horizontal=True):
                                    dpg.add_button(label=f"{ICONS[choice]} {choice}", callback=play_round, 
                                                  user_data=choice, width=350, height=70)
                                dpg.add_spacer(height=10)
                            
                            dpg.add_separator()
                            
                            # Result display
                            dpg.add_spacer(height=10)
                            dpg.add_text("", tag="result_text", color=COLORS["text"])
                            dpg.add_text("", tag="result_outcome", color=COLORS["text"])
                        
                        dpg.add_separator()
                        
                        # Scoreboard
                        with dpg.collapsing_header(label="Scoreboard", default_open=True):
                            dpg.add_spacer(height=10)
                            with dpg.table(header_row=False):
                                dpg.add_table_column()
                                dpg.add_table_column()
                                dpg.add_table_column()
                                
                                with dpg.table_row():
                                    dpg.add_text("YOU", color=COLORS["text"])
                                    dpg.add_text("vs", color=COLORS["text"])
                                    dpg.add_text("CPU", color=COLORS["text"])
                                
                                with dpg.table_row():
                                    dpg.add_text("0", tag="player_score", color=COLORS["text"])
                                    dpg.add_text("-", color=COLORS["text"])
                                    dpg.add_text("0", tag="computer_score", color=COLORS["text"])
                    
                    dpg.add_spacer(width=10)
                    
                    # Game stats panel
                    with dpg.child_window(width=-1, height=-1, border=False):
                        with dpg.collapsing_header(label="Quick Statistics", default_open=True):
                            with dpg.group():
                                dpg.add_text(f"Win Rate: 0%", tag="win_percentage", color=COLORS["win"])
                                dpg.add_spacer(width=40)
                                dpg.add_text(f"Draw Rate: 0%", tag="draw_percentage", color=COLORS["draw"])
                                dpg.add_spacer(width=40)
                                dpg.add_text(f"Total Rounds: {total_rounds}", tag="total_rounds", color=COLORS["text"])
                        
                        # Recent History section
                        with dpg.collapsing_header(label="Recent Matches", default_open=True):
                            dpg.add_text("Recent matches:", color=COLORS["text"])
                            dpg.add_listbox(items=[], tag="history_list", width=-1, num_items=8)
            
            # Statistics View
            with dpg.child_window(tag="stats_view", show=False, border=False):
                dpg.add_text("GAME STATISTICS", color=COLORS["accent"])
                dpg.add_separator()
                
                with dpg.group(horizontal=True):
                    # Player stats
                    with dpg.child_window(width=350, height=300, label="Player Stats"):
                        dpg.add_text("Player Performance", color=COLORS["accent"])
                        dpg.add_separator()
                        
                        with dpg.group():
                            with dpg.group(horizontal=True):
                                dpg.add_text("Wins:", color=COLORS["win"])
                                dpg.add_spacer(width=10)
                                dpg.add_text("0", tag="stats_player_wins", color=COLORS["win"])
                            
                            with dpg.group(horizontal=True):
                                dpg.add_text("Win Rate:", color=COLORS["win"])
                                dpg.add_spacer(width=10)
                                dpg.add_text("0%", tag="stats_win_rate", color=COLORS["win"])
                            
                            with dpg.group(horizontal=True):
                                dpg.add_text("Favorite Choice:", color=COLORS["text"])
                                dpg.add_spacer(width=10)
                                dpg.add_text("N/A", tag="stats_fav_choice", color=COLORS["text"])
                    
                    # Computer stats
                    with dpg.child_window(width=350, height=300, label="Computer Stats"):
                        dpg.add_text("Computer Performance", color=COLORS["accent"])
                        dpg.add_separator()
                        
                        with dpg.group():
                            with dpg.group(horizontal=True):
                                dpg.add_text("Wins:", color=COLORS["lose"])
                                dpg.add_spacer(width=10)
                                dpg.add_text("0", tag="stats_computer_wins", color=COLORS["lose"])
                            
                            with dpg.group(horizontal=True):
                                dpg.add_text("Win Rate:", color=COLORS["lose"])
                                dpg.add_spacer(width=10)
                                dpg.add_text("0%", tag="stats_computer_win_rate", color=COLORS["lose"])
                
                # Game summary
                with dpg.child_window(width=-1, height=200, label="Game Summary"):
                    dpg.add_text("Overall Game Statistics", color=COLORS["accent"])
                    dpg.add_separator()
                    
                    with dpg.table(header_row=True):
                        dpg.add_table_column(label="Statistic")
                        dpg.add_table_column(label="Value")
                        
                        with dpg.table_row():
                            dpg.add_text("Total Rounds")
                            dpg.add_text("0", tag="stats_total_rounds")
                        
                        with dpg.table_row():
                            dpg.add_text("Draws")
                            dpg.add_text("0", tag="stats_draws")
                        
                        with dpg.table_row():
                            dpg.add_text("Draw Rate")
                            dpg.add_text("0%", tag="stats_draw_rate")
            
            # History View
            with dpg.child_window(tag="history_view", show=False, border=False):
                dpg.add_text("GAME HISTORY", color=COLORS["accent"])
                dpg.add_separator()
                
                # Full history display with filtering options
                dpg.add_text("Complete Match History:", color=COLORS["text"])
                dpg.add_listbox(items=[], tag="detailed_history", width=-1, num_items=15)
                
                # Export options
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Export History to Excel", callback=save_to_excel, width=200, height=30)
                    dpg.add_spacer(width=10)
                    dpg.add_button(label="Clear History", callback=reset_game, width=150, height=30)
            
            # Settings View
            with dpg.child_window(tag="settings_view", show=False, border=False):
                dpg.add_text("SETTINGS", color=COLORS["accent"])
                dpg.add_separator()
                
                dpg.add_text("Game Settings", color=COLORS["text"])
                
                # Placeholder for future settings
                dpg.add_text("Settings will be available in future updates.")
                
                dpg.add_separator()
                
                # About section
                dpg.add_text("About this Application", color=COLORS["accent"])
                dpg.add_text("Rock Paper Scissors Dashboard")
                dpg.add_text("A simple game with statistics tracking and Excel export.")

# Setup and start
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("primary_window", True)

# Main application loop
last_stats_update = time.time()
update_interval = 0.5  # Update stats every 0.5 seconds at most

while dpg.is_dearpygui_running():
    try:
        # Only update stats periodically instead of every frame
        current_time = time.time()
        if current_view == "stats" and total_rounds > 0 and (current_time - last_stats_update) > update_interval:
            update_statistics_view()
            last_stats_update = current_time
            
        dpg.render_dearpygui_frame()
    except Exception as e:
        print(f"Error in main loop: {e}")
        time.sleep(0.1)  # Give the system some time to recover if there's an error
