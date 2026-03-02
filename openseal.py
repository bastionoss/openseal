# OpenSeal v3.6 - PGP Vault
# Copyright (C) 2024-2026 Bastion Open Foundation
# Distributed under the terms of the GNU General Public License v3.0 (GPL-3.0)
# Part of the Bastion Open Foundation Initiative


import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, scrolledtext
import gnupg
import os

# --- INITIALIZATION ---
home_dir = os.path.expanduser('~/.openseal_keys')
if not os.path.exists(home_dir):
    os.makedirs(home_dir, mode=0o700)

gpg = gnupg.GPG(gnupghome=home_dir)

class OpenSeal:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenSeal - PGP Vault")
        
        # --- TOTAL UNLOCK ---
        # We removed ALL attributes, types, and state calls.
        # This allows the OS to treat it as a generic, resizable window.
        self.root.geometry("800x850")
        self.root.configure(bg="#1a252f")

        # Responsive Grid Configuration
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # --- TOP NAVIGATION BAR ---
        self.top_bar = tk.Frame(root, bg="#2c3e50", height=60)
        self.top_bar.grid(row=0, column=0, sticky="ew")
        self.top_bar.grid_columnconfigure(1, weight=1)

        tk.Label(self.top_bar, text="🔒 OPENSEAL", font=("Helvetica", 14, "bold"), 
                 fg="#ecf0f1", bg="#2c3e50", padx=20).grid(row=0, column=0)
        
        self.selected_key = tk.StringVar(root)
        self.key_menu = tk.OptionMenu(self.top_bar, self.selected_key, "Loading...")
        self.key_menu.config(bg="#34495e", fg="white", highlightthickness=0, bd=0, font=("Helvetica", 9))
        self.key_menu.grid(row=0, column=1, sticky="e", padx=10)

        tk.Button(self.top_bar, text="About", command=self.show_about, bg="#34495e", 
                  fg="white", bd=0, padx=15, font=("Helvetica", 10, "bold"), cursor="hand2").grid(row=0, column=2, padx=10)

        # --- CENTRAL CONTENT (TEXT VAULT) ---
        self.vault_frame = tk.Frame(root, bg="#1a252f", padx=20, pady=10)
        self.vault_frame.grid(row=1, column=0, sticky="nsew")
        self.vault_frame.grid_columnconfigure(0, weight=1)
        self.vault_frame.grid_rowconfigure(1, weight=1)

        tk.Label(self.vault_frame, text="SECURE MESSAGE AREA", font=("Helvetica", 9, "bold"), 
                 fg="#3498db", bg="#1a252f").grid(row=0, column=0, sticky="w", pady=5)

        self.text_area = scrolledtext.ScrolledText(self.vault_frame, font=("Monospace", 13),
                                                   bg="#0d1117", fg="#2ecc71", borderwidth=0,
                                                   padx=10, pady=10, insertbackground="white")
        self.text_area.grid(row=1, column=0, sticky="nsew")

        # --- ACTION BAR (Vault Controls) ---
        self.action_bar = tk.Frame(self.vault_frame, bg="#1a252f", pady=10)
        self.action_bar.grid(row=2, column=0, sticky="ew")
        
        self.create_tool_btn(self.action_bar, "📋 Paste", self.paste_text, "#7f8c8d").pack(side=tk.LEFT, padx=2)
        self.create_tool_btn(self.action_bar, "✂️ Copy", self.copy_text, "#7f8c8d").pack(side=tk.LEFT, padx=2)
        self.create_tool_btn(self.action_bar, "🗑️ Clear", self.clear_vault, "#c0392b").pack(side=tk.LEFT, padx=2)
        
        self.create_tool_btn(self.action_bar, "DECRYPT", self.decrypt_text, "#e67e22").pack(side=tk.RIGHT, padx=5)
        self.create_tool_btn(self.action_bar, "ENCRYPT", self.encrypt_text, "#27ae60").pack(side=tk.RIGHT, padx=5)

        # --- LOWER CONTROL PANEL ---
        self.control_panel = tk.Frame(root, bg="#2c3e50", pady=15)
        self.control_panel.grid(row=2, column=0, sticky="ew")
        
        self.center_panel = tk.Frame(self.control_panel, bg="#2c3e50")
        self.center_panel.pack(expand=True)

        file_frame = tk.LabelFrame(self.center_panel, text=" File Operations ", bg="#2c3e50", fg="#bdc3c7", font=("Helvetica", 8))
        file_frame.pack(side=tk.LEFT, padx=20, fill=tk.Y)
        self.create_panel_btn(file_frame, "Seal File", self.encrypt_file, "#2980b9").pack(pady=5, padx=10)
        self.create_panel_btn(file_frame, "Unseal File", self.decrypt_file, "#c0392b").pack(pady=5, padx=10)

        key_frame = tk.LabelFrame(self.center_panel, text=" Key Management ", bg="#2c3e50", fg="#bdc3c7", font=("Helvetica", 8))
        key_frame.pack(side=tk.LEFT, padx=20, fill=tk.Y)
        tk.Button(key_frame, text="Generate", command=self.generate_key, bg="#34495e", fg="white", bd=0, width=10, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5, pady=10)
        tk.Button(key_frame, text="Import", command=self.import_key, bg="#34495e", fg="white", bd=0, width=10, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5, pady=10)
        tk.Button(key_frame, text="Export", command=self.export_key, bg="#34495e", fg="white", bd=0, width=10, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5, pady=10)

        # --- STATUS & FOOTER ---
        self.status_bar = tk.Frame(root, bg="#11181f")
        self.status_bar.grid(row=3, column=0, sticky="ew")
        
        self.status_label = tk.Label(self.status_bar, text="Ready", fg="#2ecc71", bg="#11181f", font=("Helvetica", 9))
        self.status_label.pack(side=tk.LEFT, padx=15, pady=12)

        tk.Label(self.status_bar, text="A BASTION OPEN FOUNDATION INITIATIVE  ", 
                 font=("Helvetica", 12, "bold"), fg="#ecf0f1", bg="#11181f").pack(side=tk.RIGHT, padx=10)

        self.refresh_keys()

    # Helpers
    def create_tool_btn(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="white", font=("Helvetica", 9, "bold"), bd=0, padx=15, pady=8, cursor="hand2")

    def create_panel_btn(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="white", font=("Helvetica", 10, "bold"), bd=0, width=15, pady=6, cursor="hand2")

    def show_about(self):
        about_win = tk.Toplevel(self.root)
        about_win.title("About OpenSeal")
        about_win.geometry("400x480")
        about_win.configure(bg="#1a252f")
        about_win.resizable(False, False)
        
        tk.Label(about_win, text="🔒", font=("Helvetica", 40), bg="#1a252f").pack(pady=(20, 5))
        tk.Label(about_win, text="OPENSEAL", font=("Helvetica", 20, "bold"), fg="#ecf0f1", bg="#1a252f").pack()
        tk.Label(about_win, text="v3.6 Bastion Edition", font=("Helvetica", 10), fg="#3498db", bg="#1a252f").pack()
        tk.Frame(about_win, height=2, width=300, bg="#2c3e50").pack(pady=15)
        
        info_text = (
            "OpenSeal is a high-security PGP frontend\n"
            "designed for the Bastion Open Foundation.\n\n"
            "• End-to-End RSA-4096 Encryption\n"
            "• Secure Clipboard Integration\n"
            "• Local Keyring Management\n"
            "• Zero-Telemetry Architecture"
        )
        tk.Label(about_win, text=info_text, font=("Helvetica", 10), fg="#bdc3c7", 
                 bg="#1a252f", justify=tk.LEFT, padx=20).pack(pady=5)

        tk.Label(about_win, text="LICENSE & PHILOSOPHY", font=("Helvetica", 8, "bold"), fg="#7f8c8d", bg="#1a252f").pack(pady=(20, 0))
        tk.Label(about_win, text="Open Source / GPL-3.0\nSecuring the digital frontier.", 
                 font=("Helvetica", 9, "italic"), fg="#95a5a6", bg="#1a252f").pack(pady=5)
        tk.Button(about_win, text="DISMISS", command=about_win.destroy, bg="#2ecc71", 
                  fg="white", font=("Helvetica", 10, "bold"), bd=0, width=15, pady=8).pack(side=tk.BOTTOM, pady=25)

    def update_status(self, text, color="#2ecc71"):
        self.status_label.config(text=text, fg=color)

    def refresh_keys(self):
        keys = gpg.list_keys()
        menu = self.key_menu["menu"]
        menu.delete(0, "end")
        if not keys:
            self.selected_key.set("No Keys Found")
            menu.add_command(label="No Keys Found")
        else:
            for key in keys:
                label = f"{key['uids'][0][:25]}... ({key['keyid']})"
                menu.add_command(label=label, command=lambda v=label: self.selected_key.set(v))
            self.selected_key.set(f"{keys[0]['uids'][0][:25]}... ({keys[0]['keyid']})")

    def clear_vault(self):
        self.text_area.delete("1.0", tk.END)
        self.root.clipboard_clear()
        self.update_status("Vault & Clipboard Purged", "#e74c3c")

    def copy_text(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.text_area.get("1.0", tk.END).strip())
        self.update_status("Text Copied")

    def paste_text(self):
        try:
            self.text_area.insert(tk.INSERT, self.root.clipboard_get())
            self.update_status("Text Pasted")
        except:
            self.update_status("Clipboard Empty", "#e74c3c")

    def get_selected_fingerprint(self):
        selection = self.selected_key.get()
        keys = gpg.list_keys()
        for k in keys:
            if k['keyid'] in selection: return k['fingerprint']
        return None

    def encrypt_text(self):
        content = self.text_area.get("1.0", tk.END).strip()
        fp = self.get_selected_fingerprint()
        if not content or not fp: return
        enc = gpg.encrypt(content, recipients=[fp], always_trust=True)
        if enc.ok:
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, str(enc))
            self.update_status("Text Sealed")

    def decrypt_text(self):
        content = self.text_area.get("1.0", tk.END).strip()
        if not content: return
        pw = simpledialog.askstring("Passphrase", "Enter Passphrase:", show='*')
        if not pw: return
        dec = gpg.decrypt(content, passphrase=pw)
        if dec.ok:
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, str(dec))
            self.update_status("Decryption Successful")
        else:
            self.update_status("Decryption Failed", "#e74c3c")

    def generate_key(self):
        n = simpledialog.askstring("Identity", "Name:")
        e = simpledialog.askstring("Identity", "Email:")
        p = simpledialog.askstring("Passphrase", "Passphrase:", show='*')
        if n and e and p:
            gpg.gen_key(gpg.gen_key_input(name_real=n, name_email=e, passphrase=p, key_type="RSA", key_length=4096))
            self.refresh_keys()
            self.update_status("Key Generated")

    def import_key(self):
        path = filedialog.askopenfilename()
        if path:
            with open(path, "r") as f: gpg.import_keys(f.read())
            self.refresh_keys()
            self.update_status("Key Imported")

    def export_key(self):
        fp = self.get_selected_fingerprint()
        if not fp: return
        path = filedialog.asksaveasfilename(defaultextension=".asc")
        if path:
            with open(path, "w") as f: f.write(gpg.export_keys(fp))
            self.update_status("Public Key Exported")

    def encrypt_file(self):
        path = filedialog.askopenfilename()
        fp = self.get_selected_fingerprint()
        if path and fp:
            with open(path, 'rb') as f:
                res = gpg.encrypt_file(f, recipients=[fp], output=path + ".seal", always_trust=True)
            self.update_status("File Sealed" if res.ok else "Seal Failed")

    def decrypt_file(self):
        path = filedialog.askopenfilename()
        if path:
            pw = simpledialog.askstring("Passphrase", "Enter Passphrase:", show='*')
            with open(path, 'rb') as f:
                res = gpg.decrypt_file(f, passphrase=pw, output=path.replace(".seal", ".decrypted"))
            self.update_status("File Unsealed" if res.ok else "Decryption Failed")

if __name__ == "__main__":
    root = tk.Tk()
    # By not calling anything here, we allow the OS to use its defaults.
    app = OpenSeal(root)
    root.mainloop()
