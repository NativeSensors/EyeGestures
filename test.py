import tkinter as tk

def make_transparent(window):
    window.attributes('-type', 'dock')  # Set window type to 'dock' for _NET_WM_WINDOW_OPACITY to work
    window.attributes('-alpha', 0.2)  # Set the transparency level

root = tk.Tk()

# Set window size and position
root.geometry('300x200+100+100')

# Make the window transparent
make_transparent(root)

# Add some content to the window
label = tk.Label(root, text='Transparent Window')
label.pack(padx=20, pady=20)

# Run the Tkinter event loop
root.mainloop()