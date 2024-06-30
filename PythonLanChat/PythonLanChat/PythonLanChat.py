import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ChatApp:
    def __init__(self, master):
        self.master = master
        self.master.title("LAN Chat")

        self.frame = tk.Frame(master)
        self.frame.pack()

        self.chat_area = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, state='disabled')
        self.chat_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.msg_entry = tk.Entry(self.frame, width=50)
        self.msg_entry.grid(row=1, column=0, padx=10, pady=10)
        self.msg_entry.bind("<Return>", self.send_message)

        self.send_btn = tk.Button(self.frame, text="Send", command=self.send_message)
        self.send_btn.grid(row=1, column=1, padx=10, pady=10)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 12345))

        self.broadcast_address = ('<broadcast>', 12345)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.local_ip = self.get_local_ip()

        self.receive_thread = threading.Thread(target=self.receive_message)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def send_message(self, event=None):
        message = self.msg_entry.get()
        if message:
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, "Me: " + message + "\n")
            self.chat_area.config(state='disabled')
            self.chat_area.yview(tk.END)
            self.sock.sendto(message.encode('utf-8'), self.broadcast_address)
            self.msg_entry.delete(0, tk.END)

    def receive_message(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            if addr[0] != self.local_ip:  # Ignore messages from own IP address
                message = data.decode('utf-8')
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, addr[0] + ": " + message + "\n")
                self.chat_area.config(state='disabled')
                self.chat_area.yview(tk.END)

    def close(self):
        self.sock.close()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
