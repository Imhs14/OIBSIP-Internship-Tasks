import tkinter as tk
import secrets
import string

# ═══════════════════════════════════════════════════════════
#  STAGE 3 — Password generation logic
# ═══════════════════════════════════════════════════════════

def generate_password(length, use_upper, use_lower, use_digits, use_symbols):
    pool = ""
    guaranteed = []

    if use_upper:
        pool += string.ascii_uppercase
        guaranteed.append(secrets.choice(string.ascii_uppercase))

    if use_lower:
        pool += string.ascii_lowercase
        guaranteed.append(secrets.choice(string.ascii_lowercase))

    if use_digits:
        pool += string.digits
        guaranteed.append(secrets.choice(string.digits))

    if use_symbols:
        pool += string.punctuation
        guaranteed.append(secrets.choice(string.punctuation))

    if not pool:
        return None

    remaining = [secrets.choice(pool) for _ in range(length - len(guaranteed))]
    password_chars = guaranteed + remaining
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


# ═══════════════════════════════════════════════════════════
#  STAGE 5 — Strength checker
# ═══════════════════════════════════════════════════════════

def check_strength(password):
    if not password:
        return "", "white"
    length = len(password)
    has_upper   = any(c in string.ascii_uppercase for c in password)
    has_lower   = any(c in string.ascii_lowercase for c in password)
    has_digit   = any(c in string.digits          for c in password)
    has_symbol  = any(c in string.punctuation     for c in password)
    variety = sum([has_upper, has_lower, has_digit, has_symbol])

    if length >= 16 and variety == 4:
        return "Strong 💪", "#2e7d32"
    elif length >= 12 and variety >= 3:
        return "Medium 👍", "#e65100"
    else:
        return "Weak ⚠️",  "#c62828"


# ═══════════════════════════════════════════════════════════
#  STAGE 1 — Main window
# ═══════════════════════════════════════════════════════════

root = tk.Tk()
root.title("Password Generator")
root.geometry("440x560")
root.resizable(False, False)

PAD = {"padx": 20, "pady": 6}

# ═══════════════════════════════════════════════════════════
#  STAGE 2 — All widgets
# ═══════════════════════════════════════════════════════════

# ── Title ─────────────────────────────────────────────────
tk.Label(root, text="Password Generator",
         font=("Arial", 18, "bold")).pack(pady=(20, 2))
tk.Label(root, text="Customize and generate a secure password",
         font=("Arial", 10), foreground="gray").pack()

# ── Length slider ──────────────────────────────────────────
length_frame = tk.Frame(root)
length_frame.pack(fill="x", **PAD)

tk.Label(length_frame, text="Password Length",
         font=("Arial", 11, "bold")).pack(anchor="w")

length_var = tk.IntVar(value=16)

slider = tk.Scale(
    length_frame,
    from_=6, to=64,
    orient="horizontal",
    variable=length_var,
    font=("Arial", 10)
)
slider.pack(fill="x")

# ── Checkboxes ─────────────────────────────────────────────
options_frame = tk.Frame(root)
options_frame.pack(fill="x", **PAD)

tk.Label(options_frame, text="Include",
         font=("Arial", 11, "bold")).pack(anchor="w")

use_upper   = tk.IntVar(value=1)
use_lower   = tk.IntVar(value=1)
use_digits  = tk.IntVar(value=1)
use_symbols = tk.IntVar(value=0)

tk.Checkbutton(options_frame, text="Uppercase letters  (A–Z)", variable=use_upper).pack(anchor="w")
tk.Checkbutton(options_frame, text="Lowercase letters  (a–z)", variable=use_lower).pack(anchor="w")
tk.Checkbutton(options_frame, text="Numbers  (0–9)",           variable=use_digits).pack(anchor="w")
tk.Checkbutton(options_frame, text="Symbols  (!@#$...)",       variable=use_symbols).pack(anchor="w")

# ── Output field ───────────────────────────────────────────
output_frame = tk.Frame(root)
output_frame.pack(fill="x", **PAD)

tk.Label(output_frame, text="Generated Password",
         font=("Arial", 11, "bold")).pack(anchor="w")

password_var = tk.StringVar()

output_entry = tk.Entry(
    output_frame,
    textvariable=password_var,
    font=("Arial", 13),
    state="readonly",
    width=35
)
output_entry.pack(fill="x", pady=(4, 0))

# ── Strength label (Stage 5) ───────────────────────────────
strength_label = tk.Label(output_frame, text="", font=("Arial", 10, "bold"))
strength_label.pack(anchor="w", pady=(4, 0))

# ── Status message (Stage 5 — validation feedback) ────────
status_label = tk.Label(root, text="", font=("Arial", 10), foreground="red")
status_label.pack()

# ── Buttons ────────────────────────────────────────────────
btn_frame = tk.Frame(root)
btn_frame.pack(fill="x", **PAD)

generate_btn = tk.Button(btn_frame, text="Generate Password",
                          font=("Arial", 11, "bold"),
                          bg="#4A90D9", fg="white", padx=10, pady=6,
                          command=lambda: on_generate())
generate_btn.pack(fill="x", pady=(10, 4))

copy_btn = tk.Button(btn_frame, text="Copy to Clipboard",
                      font=("Arial", 10), padx=10, pady=5,
                      command=lambda: on_copy())
copy_btn.pack(fill="x")


# ═══════════════════════════════════════════════════════════
#  STAGE 4 — Connect buttons to logic
# ═══════════════════════════════════════════════════════════

def on_generate():
    # Stage 5: clear old status
    status_label.config(text="")

    # Stage 5: validate — at least one type must be selected
    if not any([use_upper.get(), use_lower.get(),
                use_digits.get(), use_symbols.get()]):
        status_label.config(text="⚠️  Please select at least one character type.")
        password_var.set("")
        strength_label.config(text="")
        return

    # Read values from widgets
    length  = length_var.get()
    upper   = use_upper.get()
    lower   = use_lower.get()
    digits  = use_digits.get()
    symbols = use_symbols.get()

    # Call the generator
    password = generate_password(length, upper, lower, digits, symbols)

    # Show password in the entry field
    output_entry.config(state="normal")
    password_var.set(password)
    output_entry.config(state="readonly")

    # Stage 5: update strength indicator
    strength_text, strength_color = check_strength(password)
    strength_label.config(text=f"Strength: {strength_text}", foreground=strength_color)


def on_copy():
    password = password_var.get()

    # Stage 5: nothing to copy if field is empty
    if not password:
        status_label.config(text="⚠️  Generate a password first.")
        return

    # Copy to macOS clipboard
    root.clipboard_clear()
    root.clipboard_append(password)
    root.update()

    status_label.config(text="✅  Password copied to clipboard!", foreground="green")


# ═══════════════════════════════════════════════════════════
#  Start the app
# ═══════════════════════════════════════════════════════════
root.mainloop()
