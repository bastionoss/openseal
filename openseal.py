import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, scrolledtext
import gnupg
import os

# --- INITIALIZATION ---
# Secure home directory for the BastionOSS keyring
home_dir = os.path.expanduser('~/.openseal_keys')
if not os.path.exists(home_dir):
    os.makedirs(home_dir, mode=0o700)

gpg = gnupg.GPG(gnupghome=home_dir)

class OpenSeal:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenSeal - PGP Vault v1.0")
        
        # --- WINDOW CONFIGURATION ---
        self.root.configure(bg="#1a252f")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # --- TOP NAVIGATION BAR ---
        self.top_bar = tk.Frame(root, bg="#2c3e50", height=60)
        self.top_bar.grid(row=0, column=0, sticky="ew")
        self.top_bar.grid_columnconfigure(1, weight=1)

        tk.Label(self.top_bar, text="🔒 OPENSEAL", font=("Helvetica", 14, "bold"), 
                 fg="#ecf0f1", bg="#2c3e50", padx=20).grid(row=0, column=0)
        
        self.selected_key = tk.StringVar(root)
        self.key_menu = tk.OptionMenu(self.top_bar, self.selected_key, "Scanning...")
        self.key_menu.config(bg="#34495e", fg="white", highlightthickness=0, bd=0, font=("Monospace", 9))
        self.key_menu.grid(row=0, column=1, sticky="e", padx=10)
        
        tk.Button(self.top_bar, text="About", command=self.show_about, bg="#34495e", 
                  fg="white", bd=0, padx=15, font=("Helvetica", 9, "bold"), cursor="hand2").grid(row=0, column=2, padx=10)

        # --- CENTRAL VAULT AREA ---
        self.vault_frame = tk.Frame(root, bg="#1a252f", padx=20, pady=10)
        self.vault_frame.grid(row=1, column=0, sticky="nsew")
        self.vault_frame.grid_columnconfigure(0, weight=1)
        self.vault_frame.grid_rowconfigure(1, weight=1)

        tk.Label(self.vault_frame, text="SECURE MESSAGE VAULT", font=("Helvetica", 9, "bold"), 
                 fg="#3498db", bg="#1a252f").grid(row=0, column=0, sticky="w", pady=5)

        self.text_area = scrolledtext.ScrolledText(self.vault_frame, font=("Monospace", 12),
                                                   bg="#0d1117", fg="#2ecc71", borderwidth=0,
                                                   padx=15, pady=15, insertbackground="white")
        self.text_area.grid(row=1, column=0, sticky="nsew")

        # --- ACTION BAR ---
        self.action_bar = tk.Frame(self.vault_frame, bg="#1a252f", pady=10)
        self.action_bar.grid(row=2, column=0, sticky="ew")
        
        self.create_tool_btn(self.action_bar, "📋 Paste", self.paste_text, "#7f8c8d").pack(side=tk.LEFT, padx=2)
        self.create_tool_btn(self.action_bar, "✂️ Copy", self.copy_text, "#7f8c8d").pack(side=tk.LEFT, padx=2)
        self.create_tool_btn(self.action_bar, "🗑️ Clear", self.clear_vault, "#c0392b").pack(side=tk.LEFT, padx=2)
        
        self.create_tool_btn(self.action_bar, "DECRYPT", self.decrypt_text, "#e67e22").pack(side=tk.RIGHT, padx=5)
        self.create_tool_btn(self.action_bar, "ENCRYPT", self.encrypt_text, "#27ae60").pack(side=tk.RIGHT, padx=5)

        # --- CONTROL PANEL ---
        self.control_panel = tk.Frame(root, bg="#2c3e50", pady=15)
        self.control_panel.grid(row=2, column=0, sticky="ew")
        
        self.center_panel = tk.Frame(self.control_panel, bg="#2c3e50")
        self.center_panel.pack(expand=True)

        # File Sealing
        file_frame = tk.LabelFrame(self.center_panel, text=" File Sealing ", bg="#2c3e50", fg="#bdc3c7", font=("Helvetica", 8))
        file_frame.pack(side=tk.LEFT, padx=20, fill=tk.Y)
        self.create_panel_btn(file_frame, "Seal File", self.encrypt_file, "#2980b9").pack(pady=5, padx=10)
        self.create_panel_btn(file_frame, "Unseal File", self.decrypt_file, "#c0392b").pack(pady=5, padx=10)

        # Key Management
        key_frame = tk.LabelFrame(self.center_panel, text=" Key Management ", bg="#2c3e50", fg="#bdc3c7", font=("Helvetica", 8))
        key_frame.pack(side=tk.LEFT, padx=20, fill=tk.Y)
        
        tk.Button(key_frame, text="Gen", command=self.generate_key, bg="#34495e", fg="white", bd=0, width=6, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(key_frame, text="Imp", command=self.import_key, bg="#34495e", fg="white", bd=0, width=6, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(key_frame, text="Exp", command=self.export_key, bg="#34495e", fg="white", bd=0, width=6, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(key_frame, text="MANAGE", command=self.manage_keys_window, bg="#3498db", fg="white", bd=0, width=10, pady=5, font=("Helvetica", 8, "bold"), cursor="hand2").pack(side=tk.LEFT, padx=5)

        # Footer Status
        self.status_bar = tk.Frame(root, bg="#11181f")
        self.status_bar.grid(row=3, column=0, sticky="ew")
        self.status_label = tk.Label(self.status_bar, text="Secure Core Active", fg="#2ecc71", bg="#11181f", font=("Helvetica", 9))
        self.status_label.pack(side=tk.LEFT, padx=15, pady=12)

        self.refresh_keys()

    # --- UI HELPERS ---
    def create_tool_btn(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="white", font=("Helvetica", 9, "bold"), bd=0, padx=15, pady=8, cursor="hand2")

    def create_panel_btn(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="white", font=("Helvetica", 10, "bold"), bd=0, width=15, pady=6, cursor="hand2")

    def update_status(self, text, color="#2ecc71"):
        self.status_label.config(text=text, fg=color)

    # --- ABOUT SECTION ---
    def show_about(self):
        about = tk.Toplevel(self.root)
        about.title("About OpenSeal")
        about.geometry("480x580")
        about.configure(bg="#1a252f")
        about.transient(self.root)
        about.grab_set()

        tk.Label(about, text="🔒", font=("Helvetica", 50), bg="#1a252f", fg="#3498db").pack(pady=(30, 5))
        tk.Label(about, text="OPENSEAL", font=("Helvetica", 24, "bold"), fg="#ecf0f1", bg="#1a252f").pack()
        tk.Label(about, text="Version 1.0 (LTS)", font=("Helvetica", 10), fg="#3498db", bg="#1a252f").pack()

        tk.Label(about, text="Developed by", font=("Helvetica", 9), fg="#7f8c8d", bg="#1a252f").pack(pady=(20, 0))
        tk.Label(about, text="BASTION OPEN SOURCE SOFTWARES (BastionOSS)", font=("Helvetica", 10, "bold"), fg="#bdc3c7", bg="#1a252f").pack()
        tk.Label(about, text="A Subsidiary of", font=("Helvetica", 8, "italic"), fg="#7f8c8d", bg="#1a252f").pack(pady=(5,0))
        tk.Label(about, text="BASTION OPEN FOUNDATION", font=("Helvetica", 11, "bold"), fg="#ecf0f1", bg="#1a252f").pack()

        tk.Frame(about, height=1, width=320, bg="#2c3e50").pack(pady=15)
        tk.Label(about, text="LICENSE: GNU GPLv3", font=("Helvetica", 9, "bold"), fg="#3498db", bg="#1a252f").pack()
        tk.Label(about, text="This software is free and open-source.\nCopyright © 2026 Bastion Open Foundation.", font=("Helvetica", 9), fg="#95a5a6", bg="#1a252f", justify=tk.CENTER).pack(pady=5)

        tk.Button(about, text="CLOSE", command=about.destroy, bg="#34495e", fg="white", font=("Helvetica", 9, "bold"), bd=0, width=15, pady=10).pack(side=tk.BOTTOM, pady=20)

    # --- KEY MANAGEMENT DASHBOARD ---
    def manage_keys_window(self):
        manage_win = tk.Toplevel(self.root)
        manage_win.title("Keyring Manager")
        manage_win.geometry("700x500")
        manage_win.configure(bg="#1a252f")
        manage_win.transient(self.root)
        manage_win.grab_set()

        tk.Label(manage_win, text="KEYRING DATABASE", font=("Helvetica", 12, "bold"), fg="#ecf0f1", bg="#1a252f").pack(pady=10)

        list_frame = tk.Frame(manage_win, bg="#0d1117")
        list_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        canvas = tk.Canvas(list_frame, bg="#0d1117", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg="#0d1117")

        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")

        def refresh_manage_list():
            for widget in scroll_content.winfo_children(): widget.destroy()
            keys = gpg.list_keys()
            secret_fps = [k['fingerprint'] for k in gpg.list_keys(secret=True)]

            for k in keys:
                is_sec = k['fingerprint'] in secret_fps
                item = tk.Frame(scroll_content, bg="#1c2833", pady=10, padx=10, highlightbackground="#2c3e50", highlightthickness=1)
                item.pack(fill=tk.X, pady=2, padx=5)

                txt_frame = tk.Frame(item, bg="#1c2833")
                txt_frame.pack(side=tk.LEFT)
                tk.Label(txt_frame, text=f"{'[FULL]' if is_sec else '[PUB]'} {k['uids'][0]}", font=("Helvetica", 10, "bold"), 
                         fg="#2ecc71" if is_sec else "#3498db", bg="#1c2833").pack(anchor="w")
                tk.Label(txt_frame, text=f"ID: {k['keyid']}", font=("Monospace", 8), fg="#7f8c8d", bg="#1c2833").pack(anchor="w")

                btn_frame = tk.Frame(item, bg="#1c2833")
                btn_frame.pack(side=tk.RIGHT)
                tk.Button(btn_frame, text="Details", command=lambda key=k, s=is_sec: self.show_key_details(key, s, manage_win), bg="#34495e", fg="white", bd=0, padx=10).pack(side=tk.LEFT, padx=2)
                tk.Button(btn_frame, text="Delete", command=lambda fp=k['fingerprint'], s=is_sec: self.delete_key_action(fp, s, refresh_manage_list, manage_win), bg="#c0392b", fg="white", bd=0, padx=10).pack(side=tk.LEFT, padx=2)

        refresh_manage_list()

    def show_key_details(self, key, is_secret, parent_win):
        details = f"UID: {key['uids'][0]}\nFP: {key['fingerprint']}\nType: RSA-4096\nStatus: {'Full Bundle (Ready)' if is_secret else 'Encryption-Only'}"
        messagebox.showinfo("Key Identity", details, parent=parent_win)

    def delete_key_action(self, fp, is_secret, refresh_callback, parent_win):
        if messagebox.askyesno("Confirm Deletion", "This will permanently remove the key. Continue?", parent=parent_win):
            if is_secret: gpg.delete_keys(fp, secret=True)
            gpg.delete_keys(fp)
            self.refresh_keys()
            refresh_callback()

    # --- COMBINED BUNDLE EXPORT ---
    def export_key(self):
        fp = self.get_selected_fingerprint()
        if not fp: return
        
        is_sec = any(k['fingerprint'] == fp for k in gpg.list_keys(secret=True))
        exp_sec = False
        passphrase = None
        
        if is_sec:
            exp_sec = messagebox.askyesno("Export Type", "Include PRIVATE key block?\n(Exporting a Full Bundle is recommended for backups)")
            if exp_sec:
                passphrase = simpledialog.askstring("Authorize", "Enter passphrase for secret key export:", show='*', parent=self.root)
                if passphrase is None: return

        path = filedialog.asksaveasfilename(defaultextension=".asc", title="Save Key Bundle")
        if path:
            try:
                # Always get the Public block (Padlock)
                public_data = gpg.export_keys(fp)
                final_data = public_data

                # If requested, append the Private block (Key)
                if exp_sec:
                    private_data = gpg.export_keys(fp, secret=True, passphrase=passphrase)
                    if not private_data:
                        raise Exception("Passphrase invalid or Private export failed.")
                    final_data = public_data + "\n" + private_data
                
                with open(path, "w") as f: f.write(final_data)
                self.update_status("Key Bundle Exported" if exp_sec else "Public Key Exported")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

    # --- CORE ACTIONS ---
    def refresh_keys(self):
        public_keys = gpg.list_keys()
        secret_fps = [k['fingerprint'] for k in gpg.list_keys(secret=True)]
        menu = self.key_menu["menu"]
        menu.delete(0, "end")
        if not public_keys:
            self.selected_key.set("No Keys Found")
            menu.add_command(label="No Keys Found")
        else:
            for key in public_keys:
                status = "[FULL]" if key['fingerprint'] in secret_fps else "[PUB] "
                label = f"{status} {key['uids'][0][:20]}... ({key['keyid']})"
                menu.add_command(label=label, command=lambda v=label: self.selected_key.set(v))
            self.selected_key.set(f"{'[FULL]' if public_keys[0]['fingerprint'] in secret_fps else '[PUB] '} {public_keys[0]['uids'][0][:20]}...")

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
        pw = simpledialog.askstring("Passphrase", "Enter Passphrase to Unseal:", show='*', parent=self.root)
        if not pw: return
        dec = gpg.decrypt(content, passphrase=pw)
        if dec.ok:
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, str(dec))
            self.update_status("Decryption Successful")
        else:
            messagebox.showerror("Failed", "Invalid passphrase or key not found in keyring.", parent=self.root)

    def generate_key(self):
        n = simpledialog.askstring("Identity", "Name:", parent=self.root)
        e = simpledialog.askstring("Identity", "Email:", parent=self.root)
        p = simpledialog.askstring("Security", "Passphrase:", show='*', parent=self.root)
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

    def encrypt_file(self):
        path = filedialog.askopenfilename()
        fp = self.get_selected_fingerprint()
        if path and fp:
            with open(path, 'rb') as f: gpg.encrypt_file(f, recipients=[fp], output=path + ".seal", always_trust=True)
            self.update_status("File Sealed")

    def decrypt_file(self):
        path = filedialog.askopenfilename()
        if path:
            pw = simpledialog.askstring("Passphrase", "Enter Passphrase:", show='*', parent=self.root)
            with open(path, 'rb') as f: gpg.decrypt_file(f, passphrase=pw, output=path.replace(".seal", ".decrypted"))
            self.update_status("File Unsealed")

    def clear_vault(self):
        self.text_area.delete("1.0", tk.END)
        self.root.clipboard_clear()
        self.update_status("Vault Purged", "#e74c3c")

    def copy_text(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.text_area.get("1.0", tk.END).strip())
        self.update_status("Text Copied")

    def paste_text(self):
        try:
            self.text_area.insert(tk.INSERT, self.root.clipboard_get())
            self.update_status("Text Pasted")
        except: self.update_status("Clipboard Empty", "#e74c3c")

if __name__ == "__main__":
    root = tk.Tk()
    app = OpenSeal(root)
    root.mainloop()
