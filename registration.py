# -*- coding: utf-8 -*-

from tkinter import *
import sqlite3
import tkinter.messagebox
import re
from PIL import Image, ImageTk

root = Tk()
root.geometry('500x500')
root.title("Registration Form")

# Background Image Setup
image2 = Image.open('m.jpg')
image2 = image2.resize((500, 500))
background_image = ImageTk.PhotoImage(image2)

background_label = Label(root, image=background_image)
background_label.image = background_image
background_label.place(x=0, y=0)

# Variables to hold input data
Name = StringVar()
LastName = StringVar()
Address = StringVar()
status1 = StringVar()
Mobile = StringVar()

# Function to validate mobile number and avoid duplicates
def database():
    name = Name.get()
    lastname = LastName.get()
    address = Address.get()
    status = status1.get()
    mobileno = Mobile.get()

    # Validate Mobile Number (10 digits, no letters)
    if not re.match(r'^\d{10}$', mobileno):
        tkinter.messagebox.showerror('Error', 'Please enter a valid 10-digit mobile number!')
        return

    if name == "" or lastname == "":
        tkinter.messagebox.showerror('Error', 'Name and Last Name are required fields!')
        return

    conn = sqlite3.connect('face.db')
    cursor = conn.cursor()

    # Check for duplicate user (same name and lastname)
    cursor.execute("SELECT * FROM User WHERE Name=? AND Lastname=?", (name, lastname))
    result = cursor.fetchone()

    if result:
        tkinter.messagebox.showwarning('Warning', 'User with this name and last name already exists!')
    else:
        cursor.execute('INSERT INTO User (Name, Lastname, Address, Status, Mobileno) VALUES (?, ?, ?, ?, ?)', 
                       (name, lastname, address, status, mobileno))
        conn.commit()
        tkinter.messagebox.showinfo('Success', 'User Registered Successfully.')

    conn.close()

# Function to display entries
def display():
    print("Display.....")
    from subprocess import call
    call(["python", "display.py"])

# UI Elements
label_0 = Label(root, text="Registration Form", width=25, font=("bold", 22), fg="#FF8040", bg="black")
label_0.place(x=50, y=50)

label_1 = Label(root, text="Name", width=20, font=("bold", 10))
label_1.place(x=80, y=130)
entry_1 = Entry(root, textvar=Name, width=20, font=("bold", 10))
entry_1.place(x=280, y=130)

label_2 = Label(root, text="Last Name", width=20, font=("bold", 10))
label_2.place(x=80, y=180)
entry_2 = Entry(root, textvar=LastName, width=20, font=("bold", 10))
entry_2.place(x=280, y=180)

label_3 = Label(root, text="Address", width=20, font=("bold", 10))
label_3.place(x=80, y=230)
entry_3 = Entry(root, textvar=Address, width=20, font=("bold", 10))
entry_3.place(x=280, y=230)

label_4 = Label(root, text="Status", width=20, font=("bold", 10))
label_4.place(x=80, y=280)
entry_4 = Entry(root, textvar=status1, width=20, font=("bold", 10))
entry_4.place(x=280, y=280)

label_5 = Label(root, text="Mobile No", width=20, font=("bold", 10))
label_5.place(x=80, y=330)
entry_5 = Entry(root, textvar=Mobile, width=20, font=("bold", 10))
entry_5.place(x=280, y=330)

# Submit and Display Buttons
Button(root, text='Submit', width=20, bg='red', fg='white', command=database).place(x=80, y=380)
Button(root, text='Display', width=20, bg='red', fg='white', command=display).place(x=280, y=380)

root.mainloop()
