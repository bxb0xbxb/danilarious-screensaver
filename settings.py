#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import glob

CONFIG_FILE = "config.json"
ASSETS_DIR = "assets"

DEFAULT_CONFIG = {
    "speed": 1.0,
    "population": 17,
    "background_effect": "pure-black",
    "scale": 1.0,
    "randomness": 0.5,
    "cycle_settings": False,
    "bg_cycle_seconds": 10,
    "lens_effect": "none",
    "enabled_characters": []
}

class ScreensaverSettings(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Danilarious Screensaver Settings")
        self.geometry("450x550")
        self.resizable(False, False)

        self.config_data: dict[str, float | int | str | bool | list] = self.load_config()
        
        # Discover available assets
        self.available_assets = self.get_available_assets()
        
        # Initialize enabled characters if empty or missing
        saved_chars = self.config_data.get('enabled_characters', [])
        # Ensure that it's a list since Pyre type union is weak
        if not isinstance(saved_chars, list):
            saved_chars = []
        if len(saved_chars) == 0:
            self.config_data['enabled_characters'] = self.available_assets
            
        # Pre-declare variables for Pyre2
        self.speed_var = tk.DoubleVar()
        self.population_var = tk.IntVar()
        self.scale_var = tk.DoubleVar()
        self.rand_var = tk.DoubleVar()
        self.bg_var = tk.StringVar()
        self.cycle_settings_var = tk.BooleanVar()
        self.bg_cycle_sec_var = tk.IntVar()
        self.lens_var = tk.StringVar()
        
        # Dynamic var mapping for character checkboxes
        self.char_vars = {}

        self.create_widgets()

    def get_available_assets(self) -> list[str]:
        if not os.path.exists(ASSETS_DIR):
            return []
        # Find all svgs in the assets directory, return just the basename
        svgs = glob.glob(os.path.join(ASSETS_DIR, '*.svg'))
        return [os.path.basename(f) for f in svgs]

    def load_config(self) -> dict[str, float | int | str | bool | list]:
        if not os.path.exists(CONFIG_FILE):
            return DEFAULT_CONFIG.copy()
        
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()

    def save_config(self, show_msg=True):
        try:
            # Build list of chosen chars
            chosen_chars = [char for char, var in self.char_vars.items() if var.get()]
            if not chosen_chars:
                if show_msg: messagebox.showerror("Error", "You must select at least one character.")
                return False

            # Type cast the config_data assignments
            new_config = {
                'speed': float(self.speed_var.get()),
                'population': int(self.population_var.get()),
                'scale': float(self.scale_var.get()),
                'randomness': float(self.rand_var.get()),
                'background_effect': str(self.bg_var.get()),
                'cycle_settings': bool(self.cycle_settings_var.get()),
                'bg_cycle_seconds': int(self.bg_cycle_sec_var.get()),
                'lens_effect': str(self.lens_var.get()),
                'enabled_characters': chosen_chars
            }
            self.config_data.update(new_config)

            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            
            if show_msg:
                messagebox.showinfo("Success", "Settings saved successfully!\nThey will apply next time the screensaver starts.")
            
            return True
        except ValueError:
             if show_msg: messagebox.showerror("Error", "Invalid numeric values entered.")
             return False
        except Exception as e:
            if show_msg: messagebox.showerror("Error", f"Could not save config: {e}")
            return False

    def preview_screensaver(self):
        if self.save_config(show_msg=False):
            try:
                # Make sure the local python server is running if it isn't
                # Note: This is a hacky fallback. idle_monitor.sh usually handles this
                subprocess.Popen(["python3", "-m", "http.server", "8080"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Launch chromium pointing to the python server with the preview flag
                cmd = [
                    "chromium-browser",
                    "--app=http://localhost:8080/index.html?preview=1",
                    "--kiosk",
                    "--incognito",
                    "--new-window"
                ]
                subprocess.Popen(cmd)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open preview: {e}")

    def create_widgets(self):
        # Create Notebook Tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Configuration
        config_tab = ttk.Frame(notebook, padding="10")
        notebook.add(config_tab, text="Configuration")

        # Tab 2: Characters
        chars_tab = ttk.Frame(notebook, padding="10")
        notebook.add(chars_tab, text="Characters")
        
        self.build_config_tab(config_tab)
        self.build_chars_tab(chars_tab)

        # Bottom Button Frame (Constant across tabs)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10, fill=tk.X, padx=20)

        save_btn = ttk.Button(btn_frame, text="Save Settings", command=self.save_config)
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        preview_btn = ttk.Button(btn_frame, text="Preview", command=self.preview_screensaver)
        preview_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

    def build_config_tab(self, parent_frame):
        # Speed (Slider)
        speed_frame = ttk.Frame(parent_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="Speed Multiplier:").pack(side=tk.LEFT, padx=(0, 10))
        self.speed_var = tk.DoubleVar(value=float(str(self.config_data.get('speed', 1.0))))
        ttk.Scale(speed_frame, from_=0.1, to=5.0, variable=self.speed_var, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        speed_display = tk.StringVar()
        def update_speed_display(*args): speed_display.set(f"{self.speed_var.get():.1f}")
        self.speed_var.trace_add("write", update_speed_display)
        update_speed_display()
        ttk.Label(speed_frame, textvariable=speed_display, width=5).pack(side=tk.RIGHT)

        # Population (Slider)
        pop_frame = ttk.Frame(parent_frame)
        pop_frame.pack(fill=tk.X, pady=5)
        ttk.Label(pop_frame, text="Population (1-100):").pack(side=tk.LEFT, padx=(0, 10))
        self.population_var = tk.IntVar(value=int(str(self.config_data.get('population', 17))))
        ttk.Scale(pop_frame, from_=1, to=100, variable=self.population_var, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(pop_frame, textvariable=self.population_var, width=5).pack(side=tk.RIGHT)

        # Scale (Slider)
        scale_frame = ttk.Frame(parent_frame)
        scale_frame.pack(fill=tk.X, pady=5)
        ttk.Label(scale_frame, text="Scale Multiplier:").pack(side=tk.LEFT, padx=(0, 10))
        self.scale_var = tk.DoubleVar(value=float(str(self.config_data.get('scale', 1.0))))
        ttk.Scale(scale_frame, from_=0.1, to=3.0, variable=self.scale_var, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        scale_display = tk.StringVar()
        def update_scale_display(*args): scale_display.set(f"{self.scale_var.get():.1f}")
        self.scale_var.trace_add("write", update_scale_display)
        update_scale_display()
        ttk.Label(scale_frame, textvariable=scale_display, width=5).pack(side=tk.RIGHT)

        # Randomness (Slider)
        rand_frame = ttk.Frame(parent_frame)
        rand_frame.pack(fill=tk.X, pady=5)
        ttk.Label(rand_frame, text="Randomness (0-1):").pack(side=tk.LEFT, padx=(0, 10))
        self.rand_var = tk.DoubleVar(value=float(str(self.config_data.get('randomness', 0.5))))
        ttk.Scale(rand_frame, from_=0.0, to=1.0, variable=self.rand_var, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        rand_display = tk.StringVar()
        def update_rand_display(*args): rand_display.set(f"{self.rand_var.get():.2f}")
        self.rand_var.trace_add("write", update_rand_display)
        update_rand_display()
        ttk.Label(rand_frame, textvariable=rand_display, width=5).pack(side=tk.RIGHT)

        # Cycle Settings Checkbox
        cycle_frame = ttk.Frame(parent_frame)
        cycle_frame.pack(fill=tk.X, pady=10)
        self.cycle_settings_var = tk.BooleanVar(value=bool(self.config_data.get('cycle_settings', False)))
        ttk.Checkbutton(cycle_frame, text="Continuously Churn Speed & Scale Organically", variable=self.cycle_settings_var).pack(side=tk.LEFT)

        ttk.Separator(parent_frame, orient='horizontal').pack(fill=tk.X, pady=15)

        # Background Effect (Dropdown)
        bg_frame = ttk.Frame(parent_frame)
        bg_frame.pack(fill=tk.X, pady=5)
        ttk.Label(bg_frame, text="Background Effect:").pack(side=tk.LEFT, padx=(0, 10))
        self.bg_var = tk.StringVar(value=str(self.config_data.get('background_effect', 'pure-black')))
        bg_options = ["pure-black", "stars", "gradient", "rainbow-pulse", "hyperspace", "neon-grid", "random"]
        
        bg_dropdown = ttk.Combobox(bg_frame, textvariable=self.bg_var, values=bg_options, state="readonly")
        bg_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Background Cycle Time (Text Entry)
        # We only want this to show if 'random' is selected, so we place it dynamically
        self.bg_cycle_sec_var = tk.IntVar(value=int(str(self.config_data.get('bg_cycle_seconds', 10))))
        cycle_time_frame = ttk.Frame(parent_frame)
        
        ttk.Label(cycle_time_frame, text="Switch Random BG Every X Sec:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(cycle_time_frame, textvariable=self.bg_cycle_sec_var, width=5).pack(side=tk.LEFT)
        
        def update_cycle_visibility(*args):
             if self.bg_var.get() == "random":
                 cycle_time_frame.pack(fill=tk.X, pady=5)
             else:
                 cycle_time_frame.pack_forget()

        self.bg_var.trace_add("write", update_cycle_visibility)
        update_cycle_visibility() # Initial run

        # Lens Effect (Dropdown)
        lens_frame = ttk.Frame(parent_frame)
        lens_frame.pack(fill=tk.X, pady=15)
        ttk.Label(lens_frame, text="Lens FX:").pack(side=tk.LEFT, padx=(0, 10))
        self.lens_var = tk.StringVar(value=str(self.config_data.get('lens_effect', 'none')))
        lens_options = ["none", "trails", "kaleidoscope"]
        lens_dropdown = ttk.Combobox(lens_frame, textvariable=self.lens_var, values=lens_options, state="readonly")
        lens_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def build_chars_tab(self, parent_frame):
        ttk.Label(parent_frame, text="Select Assets for the Swarm:", font=("Helvetica", 10, "bold")).pack(pady=(0, 10))
        
        if not self.available_assets:
            ttk.Label(parent_frame, text="No SVG assets found in 'assets/' directory.").pack(pady=20)
            return

        # Use a canvas/scrollbar so we can scroll if user adds 50 SVGs
        canvas = tk.Canvas(parent_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load currently enabled chars, default to all if this array is somehow empty/malformed
        saved_chars = self.config_data.get('enabled_characters', [])
        if not isinstance(saved_chars, list): saved_chars = []

        # Build Checkboxes
        for asset in self.available_assets:
            var = tk.BooleanVar(value=(asset in saved_chars))
            self.char_vars[asset] = var
            chk = ttk.Checkbutton(scrollable_frame, text=asset, variable=var)
            chk.pack(anchor=tk.W, pady=2, padx=5)

if __name__ == "__main__":
    app = ScreensaverSettings()
    app.mainloop()
