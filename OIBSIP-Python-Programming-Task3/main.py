import tkinter as tk

# creating the main window
root = tk.Tk()
root.title("Password Generator")
root.geometry("420x520")
root.resizable(False, False)

# Padding helper
PAD = {"padx": 20, "pady": 8}

# Title labels
tk.Label(root, text="Password Generator", font=("Arial", 18, "bold")).pack(pady=(20, 4))
tk.Label(root, text="Customize and generate a secure password",
         font=("Arial", 10), foreground="gray").pack()

# Password length slider
length_frame = tk.Frame(root)          # THIS was missing in your code
length_frame.pack(fill="x", **PAD)

tk.Label(length_frame, text="Password Length", font=("Arial", 11, "bold")).pack(anchor="w")

length_var = tk.IntVar(value=16)

slider = tk.Scale(
    length_frame,
    from_=6, to=64,
    orient="horizontal",
    variable=length_var,
    font=("Arial", 10)
)
slider.pack(fill="x")

# Character type checkboxes
options_frame = tk.Frame(root)
options_frame.pack(fill="x", **PAD)

tk.Label(options_frame, text="Include", font=("Arial", 11, "bold")).pack(anchor="w")

use_upper = tk.IntVar(value=1)
use_lower = tk.IntVar(value=1)
use_digits = tk.IntVar(value=1)
use_symbols = tk.IntVar(value=0)

tk.Checkbutton(options_frame, text="Uppercase letters  (A–Z)", variable=use_upper).pack(anchor="w")
tk.Checkbutton(options_frame, text="Lowercase letters  (a–z)", variable=use_lower).pack(anchor="w")
tk.Checkbutton(options_frame, text="Numbers  (0–9)",           variable=use_digits).pack(anchor="w")
tk.Checkbutton(options_frame, text="Symbols  (!@#$...)",       variable=use_symbols).pack(anchor="w")

# Output field
output_frame = tk.Frame(root)
output_frame.pack(fill="x", **PAD)

tk.Label(output_frame, text="Generated Password", font=("Arial", 11, "bold")).pack(anchor="w")

password_var = tk.StringVar()

output_entry = tk.Entry(
    output_frame,
    textvariable=password_var,
    font=("Arial", 13),
    state="readonly",
    width=35
)
output_entry.pack(fill="x", pady=(4, 0))

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(fill="x", **PAD)

generate_btn = tk.Button(btn_frame, text="Generate Password", font=("Arial", 11, "bold"),
                          bg="#4A90D9", fg="white", padx=10, pady=6)
generate_btn.pack(fill="x", pady=(10, 4))

copy_btn = tk.Button(btn_frame, text="Copy to Clipboard", font=("Arial", 10),
                      padx=10, pady=5)
copy_btn.pack(fill="x")

root.mainloop()