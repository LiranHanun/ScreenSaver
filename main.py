import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import glob
import shutil
import os
from datetime import datetime
import ctypes
import sys

# Settings
settings = {
    "queue_size": 10,
    "start_time": "08:00",
    "end_time": "23:50",
    "time_between_images": 10000,
    "screen_control": False
}

input_dir = "C:/Users/User/Desktop/images/*"
deleted_img_dir = "C:/Users/User/Desktop/deleted images"

# Checking if the input directory exists
if not os.path.exists(input_dir.split('*')[0]):
    print(f"Error: The input directory '{input_dir.split('*')[0]}' was not found.")
    sys.exit(1)

if not os.path.exists(deleted_img_dir):
    print(f"Error: The deleted images directory '{deleted_img_dir}' was not found.")
    sys.exit(1)

window = tk.Tk()
window.attributes('-fullscreen', True)
window.configure(bg='black')


def open_settings_window():
    settings_window = tk.Toplevel(window)
    settings_window.title("Settings")
    settings_window.geometry("300x250")

    # Entry variables
    queue_size_var = tk.IntVar(value=settings["queue_size"])
    start_time_var = tk.StringVar(value=settings["start_time"])
    end_time_var = tk.StringVar(value=settings["end_time"])
    time_between_images_var = tk.IntVar(value=settings["time_between_images"])
    screen_control_var = tk.BooleanVar(value=settings["screen_control"])

    # Labels and Entries
    tk.Label(settings_window, text="Queue Size:").grid(row=0, column=0, sticky="e")
    tk.Entry(settings_window, textvariable=queue_size_var).grid(row=0, column=1)

    tk.Label(settings_window, text="Start Time (HH:MM):").grid(row=1, column=0, sticky="e")
    tk.Entry(settings_window, textvariable=start_time_var).grid(row=1, column=1)

    tk.Label(settings_window, text="End Time (HH:MM):").grid(row=2, column=0, sticky="e")
    tk.Entry(settings_window, textvariable=end_time_var).grid(row=2, column=1)

    tk.Label(settings_window, text="Time Between Images (ms):").grid(row=3, column=0, sticky="e")
    tk.Entry(settings_window, textvariable=time_between_images_var).grid(row=3, column=1)

    tk.Label(settings_window, text="Screen Control (On/Off):").grid(row=4, column=0, sticky="e")
    tk.Checkbutton(settings_window, variable=screen_control_var).grid(row=4, column=1)

    # Apply settings button
    def apply_settings():
        try:
            settings["queue_size"] = queue_size_var.get()
            settings["start_time"] = start_time_var.get()
            settings["end_time"] = end_time_var.get()
            settings["time_between_images"] = time_between_images_var.get()
            settings["screen_control"] = screen_control_var.get()
            messagebox.showinfo("Settings", "Settings updated successfully!")
            settings_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update settings: {e}")

    tk.Button(settings_window, text="Apply", command=apply_settings).grid(row=5, columnspan=2, pady=10)


# Bind 'S' key to open the settings window
window.bind("s", lambda event: open_settings_window())


# Functions
def manage_images():
    global image_files
    image_files = glob.glob(input_dir)
    # Adjust based on queue size setting
    while len(image_files) > settings["queue_size"]:
        old_image = image_files.pop(0)
        try:
            shutil.move(old_image, deleted_img_dir)
        except Exception as e:
            print(f"Error moving file: {old_image}. Error: {e}")


def load_images():
    global images, dates
    images = []
    dates = []
    for file in image_files:
        img = Image.open(file)
        filename = os.path.basename(file)
        date_str = filename.split(' at ')[0].split(' ')[-1]
        dates.append(date_str)

        img_width, img_height = img.size
        aspect_ratio = img_width / img_height
        screen_aspect_ratio = screen_width / screen_height
        if aspect_ratio > screen_aspect_ratio:
            new_width = screen_width
            new_height = int(screen_width / aspect_ratio)
        else:
            new_height = screen_height
            new_width = int(screen_height * aspect_ratio)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        images.append(ImageTk.PhotoImage(img))


screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
manage_images()
load_images()

label = tk.Label(window, bg='black')
label.pack(expand=True)
date_label = tk.Label(window, bg='black', fg='white', font=('Arial', 24))
date_label.pack(side='top', anchor='ne')
index_label = tk.Label(window, bg='black', fg='white', font=('Arial', 20))
index_label.pack(side='bottom', anchor='se')


def is_within_time_range():
    now = datetime.now().time()
    start_time = datetime.strptime(settings["start_time"], "%H:%M").time()
    end_time = datetime.strptime(settings["end_time"], "%H:%M").time()
    return start_time <= now <= end_time


def update_image():
    global index
    manage_images()
    load_images()
    if is_within_time_range():
        index = (index + 1) % len(images)
        date_label.config(text=dates[index])
        index_label.config(text=f"{index + 1}/{len(images)}")
        label.config(image=images[index])
        label.place(relx=0.5, rely=0.5, anchor='center')
    else:
        label.config(image='', bg='black')
        date_label.config(text='')
        index_label.config(text='')
    window.after(settings["time_between_images"], update_image)


index = 0


def key_handler(event):
    global index
    if event.keysym == 'Right':
        index = (index + 1) % len(images)
        show_image()
    elif event.keysym == 'Left':
        index = (index - 1) % len(images)
        show_image()
    elif event.keysym == 'Up':
        if images:
            old_image = image_files[index]
            try:
                shutil.move(old_image, deleted_img_dir)
                images.pop(index)
                dates.pop(index)
                if index >= len(images):
                    index = 0
                show_image()
            except Exception as e:
                print(f"Error moving file: {old_image}. Error: {e}")
    elif event.keysym == "Escape":
        window.destroy()


def show_image():
    if images:
        label.config(image=images[index])
        date_label.config(text=dates[index])
        index_label.config(text=f"{index + 1}/{len(images)}")
        label.place(relx=0.5, rely=0.5, anchor='center')


window.bind('<Key>', key_handler)
update_image()
window.mainloop()
