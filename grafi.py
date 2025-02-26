import os
import shutil
import json
import tkinter as tk
from tkinter import filedialog, messagebox

# Percorso per salvare la configurazione e i profili
config_file = "config.json"
profiles_file = "profiles.json"


def load_config():
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            return json.load(f)
    return {}


def save_config(config):
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)


# Funzione per caricare i profili
def load_profiles():
    if os.path.exists(profiles_file):
        with open(profiles_file, "r") as f:
            return json.load(f)
    return {}


# Funzione per salvare i profili
def save_profiles(profiles):
    with open(profiles_file, "w") as f:
        json.dump(profiles, f, indent=4)


# Carica la configurazione
config = load_config()

# Se la directory di FiveM non è impostata, chiedila all'utente
if "fivem_path" not in config:
    root = tk.Tk()
    root.withdraw()
    fivem_path = filedialog.askdirectory(title="Seleziona la directory di FiveM")
    if not fivem_path:
        messagebox.showerror("Errore", "Devi selezionare una directory per FiveM.")
        exit()
    config["fivem_path"] = fivem_path
    save_config(config)

des = config["fivem_path"]
descon = os.path.join(os.getenv("APPDATA"), "CitizenFX")
status_file = os.path.join(des, "mod_status.txt")


def refresh_profile_list():
    """Aggiorna la lista dei profili nella Listbox."""
    profile_listbox.delete(0, tk.END)  # Pulisce la Listbox
    profiles = load_profiles()  # Carica i profili aggiornati
    for profile_name in profiles.keys():
        profile_listbox.insert(tk.END, profile_name)


def add_profile():
    profile_window = tk.Toplevel(root)
    profile_window.title("Aggiungi Profilo")

    tk.Label(profile_window, text="Nome profilo:").grid(row=0, column=0)
    name_entry = tk.Entry(profile_window)
    name_entry.grid(row=0, column=1)

    def create_profile_folders(profile_name):
        # Directory di base per salvare i profili
        profile_base_path = os.path.join(des, "profiles")
        os.makedirs(profile_base_path, exist_ok=True)

        # Percorso specifico del nuovo profilo
        profile_path = os.path.join(profile_base_path, profile_name)
        os.makedirs(profile_path, exist_ok=True)

        # Creazione delle cartelle necessarie
        os.makedirs(os.path.join(profile_path, "citizen"), exist_ok=True)
        os.makedirs(os.path.join(profile_path, "mods"), exist_ok=True)
        os.makedirs(os.path.join(profile_path, "plugins"), exist_ok=True)

        return profile_path

    def save_profile():
        name = name_entry.get().strip()
        if not name:
            messagebox.showerror("Errore", "Il nome del profilo è obbligatorio.")
            return

        profiles = load_profiles()
        if name in profiles:
            messagebox.showerror("Errore", f"Il profilo \"{name}\" esiste già.")
            return

        # Creazione delle cartelle del profilo
        profile_path = create_profile_folders(name)

        # Salva il profilo nella configurazione
        profiles[name] = {
            "path": profile_path,
            "mods": os.path.join(profile_path, "mods"),
            "citizen": os.path.join(profile_path, "citizen"),
            "plugins": os.path.join(profile_path, "plugins"),
        }
        save_profiles(profiles)
        messagebox.showinfo("Successo", f"Profilo {name} creato con successo!")
        refresh_profile_list()  # Aggiorna la lista dei profili
        profile_window.destroy()

    tk.Button(profile_window, text="Salva", command=save_profile).grid(row=1, column=1)


def switch_profile(profile_name):
    profiles = load_profiles()
    if profile_name not in profiles:
        messagebox.showerror("Errore", "Profilo non trovato.")
        return

    profile = profiles[profile_name]
    set_current_status(profile_name)
    messagebox.showinfo("Successo", f"Profilo {profile_name} caricato!")


def get_current_status():
    if os.path.exists(status_file):
        with open(status_file, "r") as f:
            return f.read().strip()
    return None


def set_current_status(status):
    with open(status_file, "w") as f:
        f.write(status)


def open_profile_directory():
    """Apre la directory del profilo selezionato."""
    selected_profile = profile_listbox.get(tk.ACTIVE)  # Ottieni il profilo selezionato
    profiles = load_profiles()

    if selected_profile in profiles:
        profile_path = profiles[selected_profile]["path"]
        if os.path.exists(profile_path):
            os.startfile(profile_path)
        else:
            messagebox.showerror("Errore", f"La directory del profilo \"{selected_profile}\" non esiste.")
    else:
        messagebox.showerror("Errore", "Seleziona un profilo valido per aprirlo.")


# Creazione della finestra principale
root = tk.Tk()
root.title("FiveM Mod Manager")
root.geometry("400x400")

# Etichetta del programma
tk.Label(root, text="Gestione Profili FiveM", font=("Arial", 14)).pack(pady=10)

# Lista dei profili
profile_listbox = tk.Listbox(root, height=10, width=50)
profile_listbox.pack(pady=10)
refresh_profile_list()  # Carica i profili all'avvio

# Bottoni principali
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Aggiungi Profilo", command=add_profile).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Carica Profilo", command=lambda: switch_profile(profile_listbox.get(tk.ACTIVE))).grid(
    row=0, column=1, padx=5)
tk.Button(button_frame, text="Apri Directory Profilo", command=open_profile_directory).grid(row=0, column=2, padx=5)

# Avvia l'interfaccia grafica
root.mainloop()