import tkinter as tk
from base.constants import TITLE_WINDOW, WINDOW_SIZE, FB
from functions.facebook.log_fb import startLogingFb


# Tạo cửa sổ chính
root = tk.Tk()
root.title(TITLE_WINDOW)
root.geometry(WINDOW_SIZE)

# Tạo nút
logFb = tk.Button(root, text="Button 1", command=lambda: startLogingFb())
logFb.pack(pady=20)

# Chạy vòng lặp chính của Tkinter
root.mainloop()
