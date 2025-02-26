import os
import shutil
import json
import tkinter as tk
from tkinter import filedialog, messagebox

# Dark theme configuration
BG_COLOR = "#2E2E2E"  # Dark background
BUTTON_COLOR = "#414141"  # Dark buttons
BUTTON_ACCENT_COLOR = "#0078D7"  # Accent buttons
BUTTON_REMOVE_COLOR = "#D9534F"  # Remove button
BUTTON_TEXT_COLOR = "white"  # Button text color
LABEL_COLOR = "#FFFFFF"  # Label text color
FONT = ("Arial", 12)  # Global font style

config_file = "config.json"
profiles_file = "profiles.json"


# Functions to load and save configurations
def load_config():
    """Load configuration file if exists, otherwise return an empty dictionary."""
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            return json.load(f)
    return {}


def save_config(config):
    """Save the given config dictionary to the configuration file."""
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)


# Functions to load and save profiles
def load_profiles():
    """Load profiles file if exists, otherwise return an empty dictionary."""
    if os.path.exists(profiles_file):
        with open(profiles_file, "r") as f:
            return json.load(f)
    return {}


def save_profiles(profiles):
    """Save the given profiles dictionary to the profiles file."""
    with open(profiles_file, "w") as f:
        json.dump(profiles, f, indent=4)


# Set up FiveM directory
config = load_config()
if "fivem_path" not in config:
    fivem_path = filedialog.askdirectory(title="Select FiveM directory")
    if not fivem_path:
        messagebox.showerror("Error", "You must select a directory for FiveM.")
        exit()
    config["fivem_path"] = fivem_path
    save_config(config)

des = config["fivem_path"]
status_file = os.path.join(des, "mod_status.txt")


# Refresh the profile list in the UI
def refresh_profile_list():
    """Refresh the listbox showing all the profiles."""
    profile_listbox.delete(0, tk.END)
    profiles = load_profiles()
    for profile_name in profiles.keys():
        profile_listbox.insert(tk.END, profile_name)


# Load a profile
def switch_profile(profile_name):
    """Switch to the selected profile by copying its folders into the FiveM directory."""
    profiles = load_profiles()
    if profile_name not in profiles:
        messagebox.showerror("Error", "Profile not found.")
        return

    profile = profiles[profile_name]
    destination = config["fivem_path"]
    subfolders = ["citizen", "mods", "plugins"]

    try:
        # Remove existing folders
        for folder in subfolders:
            dest_folder = os.path.join(destination, folder)
            if os.path.exists(dest_folder):
                shutil.rmtree(dest_folder)

        # Copy profile folders to the FiveM directory
        for folder in subfolders:
            source_folder = profile[folder]
            dest_folder = os.path.join(destination, folder)
            if os.path.exists(source_folder):
                shutil.copytree(source_folder, dest_folder)

        set_current_status(profile_name)
        messagebox.showinfo("Success", f"Profile \"{profile_name}\" loaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading the profile: {e}")


# Set the current profile status
def set_current_status(status):
    """Set the status of the current profile."""
    with open(status_file, "w") as f:
        f.write(status)


# Open the directory of the currently selected profile
def open_profile_directory():
    """Open the file explorer to the directory of the selected profile."""
    selected_profile = profile_listbox.get(tk.ACTIVE)
    profiles = load_profiles()
    if selected_profile in profiles:
        profile_path = profiles[selected_profile]["path"]
        if os.path.exists(profile_path):
            os.startfile(profile_path)
        else:
            messagebox.showerror("Error", f"The directory for profile \"{selected_profile}\" does not exist.")
    else:
        messagebox.showerror("Error", "Please select a valid profile to open.")


# Add a new profile
def add_profile():
    """Open a window to add a new profile."""
    profile_window = tk.Toplevel(root)
    profile_window.title("Add Profile")
    profile_window.configure(bg=BG_COLOR)

    tk.Label(profile_window, text="Profile name:", font=FONT, bg=BG_COLOR, fg=LABEL_COLOR).grid(row=0, column=0, pady=5,
                                                                                                padx=5)
    name_entry = tk.Entry(profile_window, font=FONT)
    name_entry.grid(row=0, column=1, pady=5, padx=5)

    def create_profile_folders(profile_name):
        """Create directory structure for a new profile."""
        profile_base_path = os.path.join(des, "profiles")
        os.makedirs(profile_base_path, exist_ok=True)
        profile_path = os.path.join(profile_base_path, profile_name)
        os.makedirs(profile_path, exist_ok=True)
        os.makedirs(os.path.join(profile_path, "citizen"), exist_ok=True)
        os.makedirs(os.path.join(profile_path, "mods"), exist_ok=True)
        os.makedirs(os.path.join(profile_path, "plugins"), exist_ok=True)
        return profile_path

    def save_profile():
        """Save the new profile to the profiles file."""
        name = name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Profile name is required.")
            return
        profiles = load_profiles()
        if name in profiles:
            messagebox.showerror("Error", f"The profile \"{name}\" already exists.")
            return
        profile_path = create_profile_folders(name)
        profiles[name] = {
            "path": profile_path,
            "mods": os.path.join(profile_path, "mods"),
            "citizen": os.path.join(profile_path, "citizen"),
            "plugins": os.path.join(profile_path, "plugins"),
        }
        save_profiles(profiles)
        messagebox.showinfo("Success", f"Profile {name} created successfully!")
        refresh_profile_list()
        profile_window.destroy()

    tk.Button(profile_window, text="Save", command=save_profile, font=FONT, bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR).grid(
        row=1, column=1, pady=10)


def remove_profile():
    """Remove the selected profile and its directory after user confirmation."""
    selected = profile_listbox.curselection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a profile to remove.")
        return

    profiles = load_profiles()
    index = selected[0]
    profile_name = list(profiles.keys())[index]
    profile_path = profiles[profile_name]["path"]  # Percorso della cartella del profilo

    # Conferma prima dell'eliminazione
    confirm = messagebox.askyesno(
        "Confirm",
        f"Are you sure you want to delete the profile '{profile_name}' and its folder?"
    )
    if not confirm:
        return

    try:
        # Elimina la cartella del profilo se esiste
        if os.path.exists(profile_path):
            shutil.rmtree(profile_path)  # Rimuove l'intera directory del profilo
        else:
            messagebox.showwarning("Warning", f"The directory for the profile '{profile_name}' does not exist.")

        # Rimuove il profilo dal file dei profili
        del profiles[profile_name]
        save_profiles(profiles)
        refresh_profile_list()  # Aggiorna la lista dei profili

        messagebox.showinfo("Success", f"The profile '{profile_name}' and its folder have been successfully removed.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while removing the profile: {e}")

def unload_profile():
    """Unload the currently active profile by deleting its folders in the FiveM directory."""
    subfolders = ["citizen", "mods", "plugins"]
    destination = config["fivem_path"]

    confirm = messagebox.askyesno(
        "Confirm",
        "Are you sure you want to unload the current profile? This will remove all mods from your FiveM directory."
    )
    if not confirm:
        return

    try:
        for folder in subfolders:
            dest_folder = os.path.join(destination, folder)
            if os.path.exists(dest_folder):
                shutil.rmtree(dest_folder)  # Rimuove l'intera directory
        set_current_status("No profile loaded")  # Segna lo stato come "nessun profilo caricato"
        messagebox.showinfo("Success", "The current profile has been unloaded successfully!")
    except Exception as e:
        messagebox.show


# Main GUI setup
root = tk.Tk()
root.title("FiveM Graphics Switch")
root.geometry("600x550")
root.configure(bg=BG_COLOR)

tk.Label(root, text="FiveM Graphics Switch", font=("Helvetica", 18, "bold"), bg=BG_COLOR, fg=LABEL_COLOR).pack(pady=10)

profile_listbox = tk.Listbox(root, height=15, width=50, font=FONT, bg="#3B3B3B", fg=LABEL_COLOR,
                             selectbackground=BUTTON_ACCENT_COLOR, selectforeground="white")
profile_listbox.pack(pady=10)
refresh_profile_list()

button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Add Profile", command=add_profile, font=FONT, bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR).grid(
    row=0, column=0, padx=5)
tk.Button(button_frame, text="Load Profile", command=lambda: switch_profile(profile_listbox.get(tk.ACTIVE)), font=FONT,
          bg=BUTTON_ACCENT_COLOR, fg=BUTTON_TEXT_COLOR).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Open Directory", command=open_profile_directory, font=FONT, bg=BUTTON_COLOR,
          fg=BUTTON_TEXT_COLOR).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Remove Profile", command=remove_profile, font=FONT, bg=BUTTON_REMOVE_COLOR,
          fg=BUTTON_TEXT_COLOR).grid(row=0, column=3, padx=5)
tk.Button(button_frame, text="Unload Profile", command=unload_profile, font=FONT, bg=BUTTON_REMOVE_COLOR,
          fg=BUTTON_TEXT_COLOR).grid(row=0, column=4, padx=5)


root.mainloop()
