import math
import time
import json
import argparse
import curses
import curses.panel
import curses.textpad
import requests

URL = None
DEBUG_WINDOW = True
MAP_SCALE = 0.2 # Adjust this value to scale the map

# width and height should be float values representing
# the percentage of the screen which includes the popup
def _create_popup(panel, width=0.10, height=0.15):
    # Create the popup menu:
    stdscr = panel.window()
    max_y, max_x = stdscr.getmaxyx()
    temp_win_width = int(max_x * width) # default: 10% of width
    temp_win_height = int(max_y * height) # default: 15% of height
    start_x = int((max_x - temp_win_width) / 2) # centered x
    start_y = int((max_y - temp_win_height) / 2) # centered y
    popup = stdscr.derwin(temp_win_height, temp_win_width, start_y, start_x)
    popup.clear()
    popup.keypad(True) # enable keypad to receive multi-sequence keys as indiviual codes
    return popup

# used within a "Textbox.edit(validator)" call
def _arrow_validator(key):
    # arrow up and down to move between fields
    if key in (curses.KEY_UP, curses.KEY_DOWN):
        curses.ungetch(key)
        return 7
    # primary validation logic:
    elif key in range(48, 58) \
        or key in (ord('.'), ord('-')) \
        or key in range(0, 33) \
        or key in (curses.KEY_LEFT, curses.KEY_RIGHT) \
        or key == 263:
        if key == 10: curses.ungetch(curses.KEY_DOWN) # if the user presses enter, we can move to the next field
        return key
    # return nothing if input isn't a number or decimal-point or negative sign
    else:
        return None

def _cleanup_popup(popup_window):
    popup_window.bkgd(' ', 0) # set attributes to 0 (no attributes)
    popup_window.clear() # clear all text
    popup_window.refresh() # refresh to show changes

def _handle_popup_input(
        popup_window, # Window object
        popup_label, # Label for text box
        popup_fields, # Iterable of human-readable field names
        popup_types,): # Iterable of field types (INDICES MUST MATCH `popup_fields`)
    # Handle input:
    """
    _handle_popup_input returns a dictionary.
    The keys are the strings from `popup_fields`
    The values are the numbers from the textboxs
    """
    # Initial values:
    selected_field_index = 0
    POPUP_HEIGHT, POPUP_WIDTH = popup_window.getmaxyx()
    LONGEST_FIELD = max(map(lambda field: len(field), popup_fields))

    # 1. Create windows for inputs
    text_windows = []
    for index, field in enumerate(popup_fields):
        text_windows.append(popup_window.derwin(
            1, # 1 cell tall
            POPUP_WIDTH - LONGEST_FIELD - 1, # extend to right edge of window
            index + 1, # line number for textbox start
            LONGEST_FIELD + 1) # start 1 to the right of labels
        )

    # 2. create textpads for them
    text_boxes = []
    for window in text_windows:
        text_boxes.append(curses.textpad.Textbox(window))

    # 3. input loop until confirm is selected
    INPUT = True
    while INPUT:
        # Draw labels:
        label_left_start_x = int((POPUP_WIDTH - len(popup_label)) / 2) # Centered label
        popup_window.addstr(0, label_left_start_x, popup_label) # Static top label
        for line_num, field in enumerate(popup_fields):
            addstr_args = []
            if line_num == selected_field_index:
                addstr_args.append(curses.A_REVERSE) # Highlight label
            popup_window.addstr(line_num + 1, 0, field, *addstr_args) # Draw field label

        # Refresh all windows:
        popup_window.refresh()
        for window in text_windows:
            window.refresh()

        # Process input
        key = popup_window.getch()
        # Arrow up/down cases:
        if key == curses.KEY_UP and selected_field_index > 0:
            selected_field_index -= 1 # Move up the list
        elif key == curses.KEY_UP and selected_field_index == 0:
            selected_field_index = len(popup_fields) - 1 # Wrap to bottom of list
        elif key == curses.KEY_DOWN and selected_field_index < len(popup_fields) - 1:
            selected_field_index += 1 # Move down the list
        elif key == curses.KEY_DOWN and selected_field_index == len(popup_fields) - 1:
            selected_field_index = 0 # Wrap to top of list
        # Quit without saving case:
        elif key in (ord('q'), ord('Q')):
            INPUT = False
        # Enter to submit case:
        elif key == 10: # keycode 10 is enter to submit
            INPUT = False

            # Gather data:
            data = {}
            for index, field in enumerate(popup_fields):
                try:
                    data.update({field: float(text_boxes[index].gather())})
                # Silence Value Errors; they're thrown when input is, for example: '' or '-'
                except ValueError:
                    data.update({field: None})

            # Return data:
            return data
        # Edit textbox case - all other keys
        else:
            selected_window = text_windows[selected_field_index] # select the window so we can highlight it
            selected_window.bkgd(' ', curses.A_REVERSE) # highlight window

            # Begin editing:
            selected_textbox = text_boxes[selected_field_index]
            if key in range(48, 58) or key == 45: curses.ungetch(key) # Pass the first number typed to the textbox for convenience
            selected_textbox.edit(_arrow_validator)

            # Restore attributes after editing:
            selected_window.bkgd(' ', POPUP_COLOR)

def add_unit(panel):
    # Create and style the derived window:
    add_unit_window = _create_popup(panel)
    add_unit_window.bkgd(' ', POPUP_COLOR)

    # Handle input:
    data = _handle_popup_input(add_unit_window, "Add Unit", ('x', 'y'), (float, float),)
    response = requests.post(f"{URL}/units", json=data)

    # Clean up:
    _cleanup_popup(add_unit_window)
    return response

def delete_unit(panel):
    # Create and style the derived window:
    delete_unit_window = _create_popup(panel)
    delete_unit_window.bkgd(' ', POPUP_COLOR)

    # Handle input:
    data = _handle_popup_input(delete_unit_window, "Delete Unit", ('idx',), (int,),)
    index = data.pop('idx')
    if index is None: index = 0
    response = requests.delete(f"{URL}/units/{int(index)}")

    # Clean up:
    _cleanup_popup(delete_unit_window)
    return response
    

def set_destination(panel):
    # Create and style the derived window:
    set_destination_window = _create_popup(panel)
    set_destination_window.bkgd(' ', POPUP_COLOR)

    # Handle input:
    data = _handle_popup_input(set_destination_window, "Set Destination", ('x', 'y', 'idx',), (float, float, int,),)
    index = data.pop('idx')
    response = requests.post(f"{URL}/units/{int(index)}", json=data)

    # Clean up:
    _cleanup_popup(set_destination_window)
    return response

def add_target(panel):
    # Create and style the derived window:
    add_target_window = _create_popup(panel)
    add_target_window.bkgd(' ', POPUP_COLOR)

    # Handle input:
    data = _handle_popup_input(add_target_window, "Add Target", ('x', 'y'), (float, float,),)
    response = requests.post(f"{URL}/targets", json=data)

    # Clean up:
    _cleanup_popup(add_target_window)
    return response

def delete_target(panel):
    response = requests.delete(f"{URL}/targets")
    return response

def run_turn(panel):
    response = requests.post(f"{URL}/game/run")
    return response

def main(stdscr):
    # Initial setup:
    stdscr.keypad(True)
    stdscr_panel = curses.panel.new_panel(stdscr)

    # Initialize colors:
    curses.start_color()
    global GROUND_COLOR
    GROUND_COLOR = 0 # 0 is hardcoded White on Black by curses
    GROUND_COLOR = curses.color_pair(GROUND_COLOR) | curses.A_DIM
    global UNIT_COLOR
    UNIT_COLOR = 1
    curses.init_pair(UNIT_COLOR, curses.COLOR_CYAN, curses.COLOR_BLACK)
    UNIT_COLOR = curses.color_pair(UNIT_COLOR)
    global TARGET_COLOR
    TARGET_COLOR = 2
    curses.init_pair(TARGET_COLOR, curses.COLOR_RED, curses.COLOR_BLACK)
    TARGET_COLOR = curses.color_pair(TARGET_COLOR)
    global BASE_COLOR
    BASE_COLOR = 3
    curses.init_pair(BASE_COLOR, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    BASE_COLOR = curses.color_pair(BASE_COLOR)
    global POPUP_COLOR
    POPUP_COLOR = 4
    curses.init_pair(POPUP_COLOR, curses.COLOR_BLACK, curses.COLOR_BLUE)
    POPUP_COLOR = curses.color_pair(POPUP_COLOR) | curses.A_DIM
    # These constants can be used directly in `addstr` calls
    # For example: stdscr.addstr(y, x, "@", UNIT_COLOR)

    # Define the action menu; keys are displayed to user; callbacks should call the API
    actions = {
        "Add unit": add_unit,
        "Set destination": set_destination,
        "Delete unit": delete_unit,
        "Add target": add_target,
        "Delete target": delete_target,
        "Run turn": run_turn,
    }
    get_action = lambda index: list(actions.values())[index]
    selected_action_index = 0

    # Main loop:
    gamestate = None
    RUNNING = True
    LAST_UPDATE = time.time() - 5.0 # subtract 5 to guarantee update on the first iteration
    last_response = None
    max_y, max_x = stdscr.getmaxyx()
    if DEBUG_WINDOW:
        debug_window = stdscr.derwin(20, 60, 0, max_x - 61)
    while RUNNING:
        # Update the game's state:
        if time.time() - LAST_UPDATE > 4.0: # Only update ever 4 seconds
            gamestate = data = requests.get(f"{URL}/game").json()
            unit_iter = requests.get(f"{URL}/units").json().get('positions').get('Coordinates')
            target_iter = requests.get(f"{URL}/targets").json().get('targets').get('Coordinates')

        # Draw the debugger:
        if DEBUG_WINDOW and last_response:
            debug_window.clear()
            try:
                formatted_response_list = json.dumps(last_response.json(), indent=4)
            except requests.exceptions.JSONDecodeError:
                formatted_response_list = last_response.text
            for index, line_item in enumerate(formatted_response_list.split('\n')):
                debug_window.addnstr(index, 0, str(line_item), 60)
            debug_window.refresh()
            

        # Draw the actions:
        for line_num, (menu_str, menu_action) in enumerate(actions.items()):
            addstr_args = [] # Add text attributes here for conditionals, colors
            if line_num == selected_action_index:
                addstr_args.append(curses.A_REVERSE)
            stdscr.addstr(line_num, 0, menu_str, *addstr_args)

        # Draw the map to the screen:
        z = MAP_SCALE # Scale the circle
        map_radius = gamestate['base_radius']['F32'] * z # Scaled map radius
        left_bound, right_bound = int(-gamestate['map_radius']['F32'] * z), int(gamestate['map_radius']['F32'] * z) # Left and right coordinates for the map
        top_bound, bottom_bound = int(-gamestate['map_radius']['F32'] * z), int(gamestate['map_radius']['F32'] * z) # Top and bottom coordinates for the map
        left_padding = 20 # Shift the circle this many cells right
        top_padding = 0 # Shift the circle this many cells down
        # Multiply by negative 1 to ensure the sum of *start and *bound == 0, and then add padding
        left_start = (left_bound * -1) + left_padding # x + left_start will ALWAYS be the correct starting cell for this for loop
        top_start = (top_bound * -1) + top_padding # y + top_start will ALWAYS be the correct starting cell for this for loop
        for y in range(top_bound, bottom_bound+1):
            for x in range(left_bound, right_bound+1):
                # Draw blank:
                stdscr.addstr(y + top_start, x + left_start, ' ')
                # If coordinate is in the base:
                if round(math.sqrt(x*x + y*y)) <= map_radius:
                    stdscr.addstr(y + top_start, x + left_start, '0', BASE_COLOR)
                # Otherwise, if the coordinate is in the map:
                elif round(math.sqrt(x*x + y*y)) <= bottom_bound:
                    stdscr.addstr(y + top_start, x + left_start, '*', GROUND_COLOR)

        # Draw units on the screen:
        for unit in unit_iter: # y-coordinates need to be inverted to be drawn properly
            stdscr.addstr(int(2 * map_radius - unit['y'] * z + top_start), int(unit['x'] * z + left_start), '@', UNIT_COLOR)

        # Draw targets on the screen:
        for target in target_iter: # y-coordinates need to be inverted to be drawn properly
            stdscr.addstr(int(2 * map_radius - target['y'] * z + top_start), int(target['x'] * z + left_start), "X", TARGET_COLOR)

        # Process input:
        key = stdscr.getch()
        # Arrow up in main menu:
        if key == curses.KEY_UP and selected_action_index > 0:
            selected_action_index -= 1
        # Arrow down in main menu:
        elif key == curses.KEY_DOWN and selected_action_index < len(actions) - 1:
            selected_action_index += 1
        # Enter key in main menu:
        elif key == 10: # 10 is integer keycode for "Enter" key (curses.KEY_ENTER is not reliable)
            # Bug? menu_action will not be set properly if called out of the scope of this elif
            # i.e. calling get_action(selected_action_index) immediately after the variables are initialized
            # will result in the wrong function being selected (it seems to always be list[-1],
            # but I would need to create more tests to isolate the scoping issue)
            menu_action = get_action(selected_action_index)
            last_response = menu_action(stdscr_panel)
        # q key in main menu:
        elif key in (ord('q'), ord('Q')):
            RUNNING = False

if __name__=="__main__":
    parser = argparse.ArgumentParser(
            description='A client written with Python\'s ncurses for the Artillery game.')
    parser.add_argument('--url', type=str, required=True)
    args = parser.parse_args()
    URL = args.url
    curses.wrapper(main)
