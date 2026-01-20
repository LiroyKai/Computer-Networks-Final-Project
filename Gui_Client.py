import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime

# הגדרות עיצוב
BG_COLOR = "#2C2F33"
PANEL_BG = "#23272A"
TEXT_COLOR = "#FFFFFF"
ENTRY_BG = "#40444B"
ENTRY_FG = "#FFFFFF"
ACCENT_COLOR = "#5865F2"
HOVER_COLOR = "#4752C4"
CLICK_COLOR = "#3C45A5"
SUCCESS_COLOR = "#43B581"
ERROR_COLOR = "#F04747"
USER_LIST_BG = "#2F3136"

# צבעי הבועות
MY_MSG_BG = "#005C4B"         
OTHER_MSG_BG = "#36393F"
PRIVATE_BG = "#6A0DAD"      
SYSTEM_BG = "#C0C000"      

class ModernButton(tk.Label):
    def __init__(self, parent, text, command, bg=ACCENT_COLOR, width=15):
        super().__init__(parent, text=text, bg=bg, fg="white", 
                         font=("Verdana", 10, "bold"), cursor="hand2", padx=15, pady=8)
        self.command = command
        self.default_bg = bg
        self.hover_bg = HOVER_COLOR
        self.click_bg = CLICK_COLOR
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def on_enter(self, e):
        if self['state'] != 'disabled': self.config(bg=self.hover_bg)
    def on_leave(self, e):
        if self['state'] != 'disabled': self.config(bg=self.default_bg)
    def on_click(self, e):
        if self['state'] != 'disabled': self.config(bg=self.click_bg)
    def on_release(self, e):
        if self['state'] != 'disabled':
            self.config(bg=self.hover_bg)
            if self.command: self.command()
    def set_enabled(self, enabled):
        if enabled: self.config(state='normal', bg=self.default_bg, cursor="hand2")
        else: self.config(state='disabled', bg="#555555", cursor="arrow")

class HitChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Chat")
        self.root.geometry("800x600")
        self.root.configure(bg=BG_COLOR)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.client_socket = None
        self.is_connected = False
        self.my_username = ""

        # GUI Setup 
        send_frame = tk.Frame(root, bg=BG_COLOR, pady=15)
        send_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20)

        tk.Label(send_frame, text="TO:", bg=BG_COLOR, fg="#AAAAAA").pack(side=tk.LEFT)
        self.entry_target = tk.Entry(send_frame, bg=ENTRY_BG, fg="#43B581", width=12, font=("Arial", 11, "bold"), relief="flat")
        self.entry_target.insert(0, "All")
        self.entry_target.pack(side=tk.LEFT, ipady=8, padx=10)

        self.entry_msg = tk.Entry(send_frame, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 13), relief="flat")
        self.entry_msg.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=10)
        self.entry_msg.bind("<Return>", self.send_message)

        self.btn_send = ModernButton(send_frame, text="SEND", command=self.send_message, width=10)
        self.btn_send.pack(side=tk.RIGHT)

        header_frame = tk.Frame(root, bg=BG_COLOR, pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Label(header_frame, text="SECURE CHAT", font=("Montserrat", 20, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack()
        self.status_lbl = tk.Label(header_frame, text="○ Disconnected", font=("Arial", 9), bg=BG_COLOR, fg=ERROR_COLOR)
        self.status_lbl.pack()

        conn_frame = tk.Frame(root, bg=PANEL_BG, pady=15)
        conn_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)

        tk.Label(conn_frame, text="IP:", bg=PANEL_BG, fg="#AAAAAA").grid(row=0, column=0)
        self.entry_ip = tk.Entry(conn_frame, bg=ENTRY_BG, fg=ENTRY_FG, width=15, font=("Consolas", 11), relief="flat")
        self.entry_ip.insert(0, "127.0.0.1")
        self.entry_ip.grid(row=1, column=0, padx=5)

        tk.Label(conn_frame, text="PORT:", bg=PANEL_BG, fg="#AAAAAA").grid(row=0, column=1)
        self.entry_port = tk.Entry(conn_frame, bg=ENTRY_BG, fg=ENTRY_FG, width=8, font=("Consolas", 11), relief="flat")
        self.entry_port.insert(0, "12345")
        self.entry_port.grid(row=1, column=1, padx=5)

        tk.Label(conn_frame, text="NAME:", bg=PANEL_BG, fg="#AAAAAA").grid(row=0, column=2)
        self.entry_name = tk.Entry(conn_frame, bg=ENTRY_BG, fg=ENTRY_FG, width=15, font=("Arial", 11, "bold"), relief="flat")
        self.entry_name.grid(row=1, column=2, padx=5)

        self.btn_connect = ModernButton(conn_frame, text="LOGIN", command=self.connect_to_server)
        self.btn_connect.grid(row=1, column=3, padx=15)

        main_content = tk.Frame(root, bg=BG_COLOR)
        main_content.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20)

        user_panel = tk.Frame(main_content, bg=USER_LIST_BG, width=180)
        user_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        user_panel.pack_propagate(False)
        tk.Label(user_panel, text="ONLINE USERS", bg=USER_LIST_BG, fg="#AAAAAA", pady=10).pack(fill=tk.X)
        self.users_listbox = tk.Listbox(user_panel, bg=USER_LIST_BG, fg=TEXT_COLOR, bd=0, highlightthickness=0)
        self.users_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.users_listbox.bind('<<ListboxSelect>>', self.on_user_select)

        self.chat_area = scrolledtext.ScrolledText(main_content, bg=PANEL_BG, fg=TEXT_COLOR, font=("Segoe UI", 11), bd=0, padx=15, pady=15)
        self.chat_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # הגדרת הבועות והעיצוב 
        
        # 1. בועות שלי (ימין)
        self.chat_area.tag_config('bubble_me', 
                                  background=MY_MSG_BG, foreground="white", 
                                  justify='right', rmargin=20, lmargin1=100, spacing1=2, spacing3=2,
                                  font=("Segoe UI", 11))

        self.chat_area.tag_config('bubble_me_private', 
                                  background=PRIVATE_BG, foreground="white", 
                                  justify='right', rmargin=20, lmargin1=100, spacing1=2, spacing3=2,
                                  font=("Segoe UI", 11))

        # 2. בועות אחרות (שמאל)
        self.chat_area.tag_config('bubble_other', 
                                  background=OTHER_MSG_BG, foreground="white", 
                                  justify='left', lmargin1=20, rmargin=100, spacing1=2, spacing3=2,
                                  font=("Segoe UI", 11))

        self.chat_area.tag_config('bubble_private_incoming', 
                                  background=PRIVATE_BG, foreground="white", 
                                  justify='left', lmargin1=20, rmargin=100, spacing1=2, spacing3=2,
                                  font=("Segoe UI", 11))

        # 3. מערכת ושעונים
        self.chat_area.tag_config('server', foreground=SYSTEM_BG, justify='center', font=("Verdana", 9, "italic"), spacing1=10)
        self.chat_area.tag_config('error', foreground=ERROR_COLOR, justify='center', font=("Verdana", 10, "bold"))
        self.chat_area.tag_config('timestamp_style', font=("Consolas", 8), foreground="#CCCCCC")

        # 4.  תגית לרווח בין הודעות 

        # גופן קטן שיוצר שורה ריקה דקה
        self.chat_area.tag_config('spacer', font=("Arial", 4)) 

    def connect_to_server(self):
        if self.is_connected: return
        self.my_username = self.entry_name.get().strip()
        if not self.my_username: return messagebox.showwarning("Error", "Enter username!")

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.entry_ip.get(), int(self.entry_port.get())))
            self.is_connected = True
            
            self.client_socket.send(self.my_username.encode('utf-8'))
            
            self.status_lbl.config(text=f"● Connected: {self.my_username}", fg=SUCCESS_COLOR)
            self.btn_connect.set_enabled(False)
            self.entry_name.config(state='disabled')
            self.users_listbox.delete(0, tk.END)
            self.add_to_chat("--- Connected to server ---", "server")

            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def receive_messages(self):
        while self.is_connected:
            try:
                data = self.client_socket.recv(4096).decode('utf-8')
                if not data: raise ConnectionResetError
                
                data = data.replace("USERS_LIST:", "\nUSERS_LIST:")
                messages = data.split('\n')
                
                for message in messages:
                    if not message.strip(): continue
                    
                    if "USERS_LIST:" in message:
                        try:
                            parts = message.split("USERS_LIST:")
                            if parts[0].strip():
                                self.root.after(0, lambda m=parts[0].strip(): self.parse_and_display(m))
                            if len(parts) > 1:
                                user_list = parts[1].split(",")
                                self.root.after(0, lambda l=user_list: self.refresh_user_list(l))
                        except: pass
                    else:
                        self.root.after(0, lambda m=message: self.parse_and_display(m))
            except:
                self.is_connected = False
                self.root.after(0, self.handle_disconnect)
                break

    def refresh_user_list(self, user_list):
        self.users_listbox.delete(0, tk.END)
        for name in user_list:
            clean_name = name.strip()
            if clean_name and "USERS_LIST" not in clean_name and "Server:" not in clean_name:
                self.users_listbox.insert(tk.END, clean_name)

    def on_user_select(self, event):
        if self.users_listbox.curselection():
            self.entry_target.delete(0, tk.END)
            self.entry_target.insert(0, self.users_listbox.get(self.users_listbox.curselection()[0]))

    def send_message(self, event=None):
        if not self.is_connected: return
        msg = self.entry_msg.get()
        msg = msg.replace('\n', ' ') 
        target = self.entry_target.get().strip()
        
        if msg and target:
            if target.lower() != "all":
                online_users = self.users_listbox.get(0, tk.END)
                if target not in online_users:
                    self.parse_and_display(f"System: User '{target}' is not connected!", is_error=True)
                    return 

            try:
                self.client_socket.send(f"{target}:{msg}".encode('utf-8'))
                
                # הודעה יוצאת 
                timestamp = datetime.now().strftime("%H:%M")
                self.chat_area.config(state='normal')
                
                display_msg = f" {msg} "
                display_time = f" {timestamp} "

                if target.lower() != "all":
                    self.chat_area.insert(tk.END, f"(To {target}){display_msg}", 'bubble_me_private')
                    self.chat_area.insert(tk.END, f"{display_time}\n", ('bubble_me_private', 'timestamp_style'))
                else:
                    self.chat_area.insert(tk.END, f"{display_msg}", 'bubble_me')
                    self.chat_area.insert(tk.END, f"{display_time}\n", ('bubble_me', 'timestamp_style'))

                #  הוספת שורת רווח לניתוק הבועות 
                self.chat_area.insert(tk.END, "\n", 'spacer') 

                self.chat_area.see(tk.END)
                self.chat_area.config(state='disabled')
                self.entry_msg.delete(0, tk.END)
            except:
                self.handle_disconnect()

    def parse_and_display(self, message, is_error=False):
        self.chat_area.config(state='normal')
        
        if is_error:
            self.chat_area.insert(tk.END, f"{message}\n", 'error')
            self.chat_area.insert(tk.END, "\n", 'spacer')
            self.chat_area.see(tk.END)
            self.chat_area.config(state='disabled')
            return

        # הודעה נכנסת 
        timestamp = datetime.now().strftime("%H:%M")
        display_time = f" {timestamp} "

        if message.startswith("Server:") or "joined" in message or "left" in message:
             self.chat_area.insert(tk.END, f"{message}\n", 'server')
             self.chat_area.insert(tk.END, "\n", 'spacer')
        
        elif "(Private)" in message:
            clean_msg = message.replace("(Private)", "").strip()
            self.chat_area.insert(tk.END, f"{display_time}", ('bubble_private_incoming', 'timestamp_style'))
            self.chat_area.insert(tk.END, f"{clean_msg} \n", 'bubble_private_incoming')
            self.chat_area.insert(tk.END, "\n", 'spacer') # רווח
            
        elif ":" in message:
            sender, content = message.split(":", 1)
            if sender == self.my_username: 
                pass 
            else:
                self.chat_area.insert(tk.END, f"{display_time}", ('bubble_other', 'timestamp_style'))
                self.chat_area.insert(tk.END, f"{sender}: {content} \n", 'bubble_other')
                self.chat_area.insert(tk.END, "\n", 'spacer') # רווח
        else:
            self.chat_area.insert(tk.END, f"{message}\n", 'other')
            self.chat_area.insert(tk.END, "\n", 'spacer')

        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')

    def add_to_chat(self, message, tag):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{message}\n", tag)
        self.chat_area.insert(tk.END, "\n", 'spacer')
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')

    def handle_disconnect(self):
        self.status_lbl.config(text="○ Disconnected", fg=ERROR_COLOR)
        self.btn_connect.set_enabled(True)
        self.entry_name.config(state='normal')
        self.users_listbox.delete(0, tk.END)
        self.add_to_chat("Disconnected from server.", "error")

    def on_closing(self):
        if self.client_socket:
            try: self.client_socket.close()
            except: pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HitChatClient(root)
    root.mainloop()