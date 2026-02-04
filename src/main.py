import time
import threading
import random
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

# --- AUTO-INSTALL DEPENDENCIES ---
def install_and_import(package, import_name=None):
    import_name = import_name or package
    try:
        __import__(import_name)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        try:
            __import__(import_name)
        except ImportError:
            messagebox.showerror("Error", f"Failed to install {package}. Please run 'pip install -r requirements.txt' manually.")
            sys.exit(1)

install_and_import("pynput")
install_and_import("pygetwindow")
install_and_import("pyrect")

from pynput.mouse import Button, Controller, Listener as MouseListener
from pynput.keyboard import Listener as KeyListener, KeyCode, Key
import pygetwindow as gw

class AutoclickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agalar911 AutoClicker")
        self.root.geometry("400x780")
        self.root.resizable(False, False)
        
        # --- PROFESSIONAL DARK THEME ---
        self.bg_black = "#0b0c10"   
        self.bg_card = "#1f2833"    
        self.accent_blue = "#66fcf1" 
        self.accent_dim = "#45a29e"  
        self.fg_white = "#c5c6c7"    
        self.btn_bg = "#121212"     
        self.kill_red = "#f7768e"   
        
        self.root.configure(bg=self.bg_black)

        self.mouse = Controller()
        self.running = False
        self.binding_mode = None 
        self.picking_pos = False
        
        # --- STATE VARIABLES ---
        self.unit_var = tk.StringVar(value="ms")
        self.button_var = tk.StringVar(value="left")
        self.click_type_var = tk.StringVar(value="single")
        
        self.jitter_var = tk.BooleanVar(value=False)
        self.always_on_top_var = tk.BooleanVar(value=False)
        self.click_limit_enabled = tk.BooleanVar(value=False)
        self.timer_enabled = tk.BooleanVar(value=False)
        self.lock_pos_enabled = tk.BooleanVar(value=False)
        self.lock_window_enabled = tk.BooleanVar(value=False)
        
        self.click_limit_val = tk.StringVar(value="1000")
        self.timer_min_val = tk.StringVar(value="10")
        self.target_pos = None 
        self.target_window_title = tk.StringVar(value="No Window Captured")
        
        self.hotkey_start_stop = Key.f6
        self.hotkey_kill = Key.esc
        
        self.clicks_done = 0
        self.start_time = 0
        
        self.setup_ui()
        
        # Separate listeners
        self.key_listener = KeyListener(on_press=self.on_press)
        self.mouse_listener = MouseListener(on_click=self.on_click_global)
        self.key_listener.start()
        self.mouse_listener.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        title_font = ("Segoe UI", 24, "bold")
        header_font = ("Segoe UI", 10, "bold")
        label_font = ("Segoe UI", 10)
        
        def create_card(parent, text):
            frame = tk.LabelFrame(parent, text=f" {text} ", bg=self.bg_black, fg=self.accent_blue, 
                                 font=header_font, padx=15, pady=10, borderwidth=1, relief="flat", highlightthickness=1)
            frame.config(highlightbackground="#1f2833", highlightcolor=self.accent_blue)
            return frame

        # Header
        tk.Label(self.root, text="AGALAR911", font=title_font, bg=self.bg_black, fg="#ffffff").pack(pady=(25, 10))
        
        # Main Layout Container
        main_container = tk.Frame(self.root, bg=self.bg_black)
        main_container.pack(fill="both", expand=True, padx=25)

        radio_style = {"bg": self.bg_black, "fg": self.fg_white, "selectcolor": self.bg_black, 
                       "activebackground": self.bg_black, "activeforeground": self.accent_blue, 
                       "font": label_font, "padx": 5}

        # --- INTERVAL SECTION ---
        frame_speed = create_card(main_container, "CLICK INTERVAL")
        frame_speed.pack(fill="x", pady=5)
        
        speed_row = tk.Frame(frame_speed, bg=self.bg_black)
        speed_row.pack(fill="x")
        self.interval_entry = tk.Entry(speed_row, width=8, justify='center', bg=self.btn_bg, fg="#ffffff", borderwidth=0, font=("Segoe UI", 12))
        self.interval_entry.insert(0, "100")
        self.interval_entry.pack(side=tk.LEFT, padx=(0, 10))

        tk.Radiobutton(speed_row, text="ms", variable=self.unit_var, value="ms", **radio_style).pack(side=tk.LEFT)
        tk.Radiobutton(speed_row, text="sec", variable=self.unit_var, value="sec", **radio_style).pack(side=tk.LEFT)
        tk.Radiobutton(speed_row, text="CPS", variable=self.unit_var, value="cps", **radio_style).pack(side=tk.LEFT)

        # --- MOUSE SECTION ---
        frame_mouse = create_card(main_container, "MOUSE SETTINGS")
        frame_mouse.pack(fill="x", pady=5)
        
        m_row1 = tk.Frame(frame_mouse, bg=self.bg_black)
        m_row1.pack(fill="x")
        tk.Label(m_row1, text="Button:", bg=self.bg_black, fg=self.accent_dim, width=8, anchor="w").pack(side=tk.LEFT)
        tk.Radiobutton(m_row1, text="Left", variable=self.button_var, value="left", **radio_style).pack(side=tk.LEFT)
        tk.Radiobutton(m_row1, text="Right", variable=self.button_var, value="right", **radio_style).pack(side=tk.LEFT)
        tk.Radiobutton(m_row1, text="Mid", variable=self.button_var, value="middle", **radio_style).pack(side=tk.LEFT)

        m_row2 = tk.Frame(frame_mouse, bg=self.bg_black)
        m_row2.pack(fill="x", pady=(5,0))
        tk.Label(m_row2, text="Type:", bg=self.bg_black, fg=self.accent_dim, width=8, anchor="w").pack(side=tk.LEFT)
        tk.Radiobutton(m_row2, text="Single", variable=self.click_type_var, value="single", **radio_style).pack(side=tk.LEFT)
        tk.Radiobutton(m_row2, text="Double", variable=self.click_type_var, value="double", **radio_style).pack(side=tk.LEFT)

        # --- AUTOMATION SECTION ---
        frame_auto = create_card(main_container, "AUTO-STOP CONDITIONS")
        frame_auto.pack(fill="x", pady=5)

        limit_row = tk.Frame(frame_auto, bg=self.bg_black)
        limit_row.pack(fill="x")
        tk.Checkbutton(limit_row, text="Max Clicks:", variable=self.click_limit_enabled, **radio_style).pack(side=tk.LEFT)
        tk.Entry(limit_row, textvariable=self.click_limit_val, width=10, bg=self.btn_bg, fg="#ffffff", borderwidth=0).pack(side=tk.RIGHT)

        timer_row = tk.Frame(frame_auto, bg=self.bg_black)
        timer_row.pack(fill="x", pady=(5,0))
        tk.Checkbutton(timer_row, text="Stop Timer (min):", variable=self.timer_enabled, **radio_style).pack(side=tk.LEFT)
        tk.Entry(timer_row, textvariable=self.timer_min_val, width=10, bg=self.btn_bg, fg="#ffffff", borderwidth=0).pack(side=tk.RIGHT)

        # --- LOCKS SECTION ---
        frame_locks = create_card(main_container, "POSITIONAL LOCKS")
        frame_locks.pack(fill="x", pady=5)

        l_row1 = tk.Frame(frame_locks, bg=self.bg_black)
        l_row1.pack(fill="x")
        tk.Checkbutton(l_row1, text="Lock Coordinates", variable=self.lock_pos_enabled, **radio_style).pack(side=tk.LEFT)
        tk.Button(l_row1, text="Select Spot", command=self.start_picking_pos, bg=self.bg_card, fg=self.accent_blue, borderwidth=0, padx=8).pack(side=tk.RIGHT)

        l_row2 = tk.Frame(frame_locks, bg=self.bg_black)
        l_row2.pack(fill="x", pady=(5,0))
        tk.Checkbutton(l_row2, text="Lock Target Window", variable=self.lock_window_enabled, **radio_style).pack(side=tk.LEFT)
        tk.Button(l_row2, text="Capture", command=self.pick_active_window, bg=self.bg_card, fg=self.accent_blue, borderwidth=0, padx=8).pack(side=tk.RIGHT)
        
        tk.Label(frame_locks, textvariable=self.target_window_title, bg=self.bg_black, fg=self.accent_dim, font=("Segoe UI", 7), wraplength=300).pack(fill="x", pady=(5,0))

        # --- HOTKEYS SECTION ---
        frame_keys = create_card(main_container, "HOTKEYS")
        frame_keys.pack(fill="x", pady=5)
        
        self.btn_bind_start = tk.Button(frame_keys, text=f"Toggle: {self.format_key(self.hotkey_start_stop)}", 
                                        command=lambda: self.start_binding('start_stop'), bg=self.btn_bg, fg=self.accent_blue, borderwidth=1, relief="solid", pady=6)
        self.btn_bind_start.pack(fill="x", pady=2)
        
        self.btn_bind_kill = tk.Button(frame_keys, text=f"Exit App: {self.format_key(self.hotkey_kill)}", 
                                       command=lambda: self.start_binding('kill'), bg=self.btn_bg, fg=self.kill_red, borderwidth=1, relief="solid", pady=6)
        self.btn_bind_kill.pack(fill="x")

        # --- FOOTER OPTIONS ---
        tk.Checkbutton(main_container, text="Humanize (Random Jitter/Offset)", variable=self.jitter_var, **radio_style).pack(anchor="w", pady=(10, 0))
        tk.Checkbutton(main_container, text="Always On Top", variable=self.always_on_top_var, command=self.toggle_on_top, **radio_style).pack(anchor="w")

        # --- STATUS FOOTER ---
        self.status_bar = tk.Frame(self.root, bg=self.btn_bg, pady=12)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_label = tk.Label(self.status_bar, text="STATUS: READY", font=("Segoe UI", 10, "bold"), bg=self.btn_bg, fg=self.accent_blue)
        self.status_label.pack()

        tk.Label(self.root, text="Developed by KenzoNight", font=("Segoe UI", 7), bg=self.bg_black, fg="#313244").pack(side="bottom", pady=5)

    def toggle_on_top(self):
        self.root.attributes("-topmost", self.always_on_top_var.get())

    def start_picking_pos(self):
        self.picking_pos = True
        self.status_label.config(text="STATUS: CLICK TO LOCK POS", fg="#ffffff")

    def pick_active_window(self):
        def countdown(count):
            if count > 0:
                self.status_label.config(text=f"STATUS: FOCUS TARGET IN {count}s...", fg=self.kill_red)
                self.root.after(1000, lambda: countdown(count - 1))
            else:
                try:
                    active = gw.getActiveWindow()
                    if active:
                        self.target_window_title.set(active.title)
                        self.status_label.config(text="STATUS: WINDOW CAPTURED", fg=self.accent_blue)
                    else:
                        self.status_label.config(text="STATUS: CAPTURE FAILED", fg=self.kill_red)
                except:
                    self.status_label.config(text="STATUS: CAPTURE ERROR", fg=self.kill_red)
        
        countdown(3)

    def start_binding(self, mode):
        self.binding_mode = mode
        btn = self.btn_bind_start if mode == 'start_stop' else self.btn_bind_kill
        btn.config(text="... PRESS ANY KEY ...", fg="#ffffff")
        self.status_label.config(text="STATUS: LISTENING FOR KEY", fg="#ffffff")

    def format_key(self, key):
        if isinstance(key, Key): return key.name.upper()
        if isinstance(key, KeyCode): return str(key.char).upper() if key.char else f"K:{key.vk}"
        return str(key)

    def get_sleep_interval(self):
        try:
            val = float(self.interval_entry.get())
            unit = self.unit_var.get()
            interval = val if unit == "sec" else (val / 1000.0 if unit == "ms" else 1.0 / max(0.1, val))
        except: interval = 0.1
        if self.jitter_var.get(): interval += random.uniform(-interval*0.15, interval*0.15)
        return max(0.001, interval)

    def clicker_loop(self):
        button_map = {"left": Button.left, "right": Button.right, "middle": Button.middle}
        btn = button_map.get(self.button_var.get(), Button.left)
        is_double = self.click_type_var.get() == "double"
        
        while self.running:
            try:
                if self.click_limit_enabled.get() and self.clicks_done >= int(self.click_limit_val.get()): 
                    self.root.after(0, self.stop_clicking)
                    break
                if self.timer_enabled.get() and (time.time() - self.start_time) >= float(self.timer_min_val.get()) * 60:
                    self.root.after(0, self.stop_clicking)
                    break
                if self.lock_window_enabled.get():
                    active = gw.getActiveWindow()
                    if not active or self.target_window_title.get() not in active.title:
                        time.sleep(0.1)
                        continue
            except: break

            interval = self.get_sleep_interval()
            st = time.perf_counter()
            
            if self.lock_pos_enabled.get() and self.target_pos:
                # If "Humanize" is on, add slight jitter to the locked position
                if self.jitter_var.get():
                    jx = self.target_pos[0] + random.randint(-3, 3)
                    jy = self.target_pos[1] + random.randint(-3, 3)
                    self.mouse.position = (jx, jy)
                else:
                    self.mouse.position = self.target_pos
            elif self.jitter_var.get():
                # If humanize is on but NOT locked, subtle shake in place
                cur_x, cur_y = self.mouse.position
                self.mouse.position = (cur_x + random.randint(-1, 1), cur_y + random.randint(-1, 1))

            # Execution
            self.mouse.press(btn)
            time.sleep(random.uniform(0.01, 0.03) if self.jitter_var.get() else 0.01)
            self.mouse.release(btn)
            self.clicks_done += 1
            
            if is_double:
                time.sleep(random.uniform(0.01, 0.03) if self.jitter_var.get() else 0.01)
                self.mouse.press(btn)
                time.sleep(random.uniform(0.01, 0.03) if self.jitter_var.get() else 0.01)
                self.mouse.release(btn)
                self.clicks_done += 1

            # Precise Idle
            rem = interval - (time.perf_counter() - st)
            if rem > 0:
                end = time.perf_counter() + rem
                while self.running and time.perf_counter() < end:
                    diff = end - time.perf_counter()
                    if diff > 0.015: time.sleep(diff - 0.010)

    def start_clicking(self):
        if not self.running:
            self.clicks_done = 0
            self.start_time = time.time()
            self.running = True
            self.status_label.config(text="STATUS: RUNNING", fg="#a6e3a1")
            threading.Thread(target=self.clicker_loop, daemon=True).start()

    def stop_clicking(self):
        if self.running:
            self.running = False
            self.status_label.config(text="STATUS: STOPPED", fg=self.kill_red)

    def on_press(self, key):
        if self.binding_mode:
            if self.binding_mode == 'start_stop':
                self.hotkey_start_stop = key
                self.btn_bind_start.config(text=f"Toggle: {self.format_key(key)}", fg=self.accent_blue)
            else:
                self.hotkey_kill = key
                self.btn_bind_kill.config(text=f"Exit App: {self.format_key(key)}", fg=self.kill_red)
            self.binding_mode = None
            self.status_label.config(text="STATUS: KEY BOUND", fg=self.accent_blue)
            return
        
        if key == self.hotkey_start_stop:
            self.stop_clicking() if self.running else self.start_clicking()
        elif key == self.hotkey_kill:
            self.on_closing()

    def on_click_global(self, x, y, button, pressed):
        if self.picking_pos and pressed:
            self.target_pos = (x, y)
            self.picking_pos = False
            def update_ui():
                messagebox.showinfo("Selection", f"Position locked to {x}, {y}")
                self.status_label.config(text="STATUS: POSITION LOCKED", fg=self.accent_blue)
            self.root.after(0, update_ui)

    def on_closing(self):
        self.running = False
        if hasattr(self, 'key_listener'): self.key_listener.stop()
        if hasattr(self, 'mouse_listener'): self.mouse_listener.stop()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoclickerApp(root)
    root.mainloop()
