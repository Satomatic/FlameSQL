try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

class Placeholder_State(object):
     __slots__ = 'normal_color', 'normal_font', 'placeholder_text', 'placeholder_color', 'placeholder_font', 'with_placeholder'

def add_placeholder_to(entry, placeholder, char, color="grey", font=None):
    normal_color = entry.cget("fg")
    normal_font = entry.cget("font")
    
    if font is None:
        font = normal_font

    state = Placeholder_State()
    state.normal_color=normal_color
    state.normal_font=normal_font
    state.placeholder_color=color
    state.placeholder_font=font
    state.placeholder_text = placeholder
    state.with_placeholder=True

    def on_focusin(event, entry=entry, state=state):
        if state.with_placeholder:
            entry.delete(0, "end")
            entry.config(fg = state.normal_color, font=state.normal_font, show=char)
        
            state.with_placeholder = False

    def on_focusout(event, entry=entry, state=state):
        if entry.get() == '':
            entry.insert(0, state.placeholder_text)
            entry.config(fg = state.placeholder_color, font=state.placeholder_font, show="")
            
            state.with_placeholder = True

    entry.insert(0, placeholder)
    entry.config(fg = color, font=font)

    entry.bind('<FocusIn>', on_focusin, add="+")
    entry.bind('<FocusOut>', on_focusout, add="+")
    
    entry.placeholder_state = state

    return state

def centerwindow(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def ClearPanel(panel):
    for widget in panel.winfo_children():
        widget.destroy()


def CheckPasswordStrength(password):
    password_value = 0
    strength = ""

    char_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    char_lower = "abdefghijklmnopqrstuvwxyz"
    char_special = '!"£$%^&*()'
    char_numbers = "1234567890"

    if len(password) > 5:
        password_value = password_value + 2

    for letter in char_upper:
        if letter in password:
            password_value = password_value + 0.5

    for letter in char_lower:
        if letter in password:
            password_value = password_value + 0.5

    for letter in char_special:
        if letter in password:
            password_value = password_value + 3

    for letter in char_numbers:
        if letter in password:
            password_value = password_value + 2

    value_round = int(
        password_value)

    if value_round < 5:
        strength = "weak"
    elif value_round < 10:
        strength = "good"
    elif value_round > 10:
        strength = "strong"

    return strength

def raiseFrame(window):
    window.attributes("-topmost", True)
    window.attributes("-topmost", False)

def limitText(limit, text):
    text_length = len(text)
    text_sub = text_length - limit

    newText = text[:-text_sub]
    newText = newText + "..."

    return newText

def extendText(extendto, text):
    text_length = len(text)
    text_addition = extendto - text_length

    newText = text
    while True:
        text_length = text_length + 1

        newText = newText + " "

        if text_length == extendto:
            break
        else:
            continue

    return newText