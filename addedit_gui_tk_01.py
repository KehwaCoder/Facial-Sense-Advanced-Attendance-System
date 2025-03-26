import logging
from tkinter import Toplevel, StringVar, Label, Frame, OptionMenu, Button, IntVar, Entry, messagebox, Checkbutton, BooleanVar, Tk
import sqlite3

# Database setup
def setup_database():
    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY,
            name TEXT,
            date TEXT,
            description TEXT,
            category TEXT
        )
    ''')
    conn.commit()
    return conn

class AddEditEntry(Frame):
    """
    Template widget for adding/editing the entry
    """
    def __init__(self, parent, possiblecats):
        Frame.__init__(self, parent)
        self.__months = ("January", "February", "March", "April", "May",
                         "June", "July", "August", "September", "October",
                         "November", "December")
        self.__month_selected = StringVar(self, value=self.__months[0])
        self.__cat_selected = StringVar(self, value="Other")
        self.__name_var = StringVar(self)
        self.__day_var = IntVar(self, value=1)
        self.__year_var = IntVar(self, value=2000)
        self.__desc_var = StringVar(self)

        # Entry Fields
        Label(self, text="Name:").grid(row=0, column=0)
        self.__e_name = Entry(self, textvariable=self.__name_var)
        self.__e_name.grid(row=0, column=1)

        Label(self, text="Day:").grid(row=1, column=0)
        self.__e_day = Entry(self, textvariable=self.__day_var)
        self.__e_day.grid(row=1, column=1)

        Label(self, text="Month:").grid(row=2, column=0)
        self.__om_month = OptionMenu(self, self.__month_selected, *self.__months)
        self.__om_month.grid(row=2, column=1)

        Label(self, text="Year:").grid(row=3, column=0)
        self.__e_year = Entry(self, textvariable=self.__year_var)
        self.__e_year.grid(row=3, column=1)

        Label(self, text="Description:").grid(row=4, column=0)
        self.__t_desc = Entry(self, textvariable=self.__desc_var)
        self.__t_desc.grid(row=4, column=1)

        Label(self, text="Category:").grid(row=5, column=0)
        self.__om_cat = OptionMenu(self, self.__cat_selected, *possiblecats)
        self.__om_cat.grid(row=5, column=1)

        self.__delete_var = BooleanVar()
        self.__checkbox = Checkbutton(self, text="Select for Deletion", variable=self.__delete_var)
        self.__checkbox.grid(row=6, columnspan=2)

    def set_values(self, day, monthint, year, name, desc, cat):
        monthint -= 1
        self.__name_var.set(name)
        self.__day_var.set(day)
        self.__month_selected.set(self.__months[monthint])
        self.__year_var.set(year)
        self.__desc_var.set(desc)
        self.__cat_selected.set(cat)

    def get_values(self):
        month = self.__months.index(self.__month_selected.get()) + 1
        date = f"{self.__day_var.get()}.{month}.{self.__year_var.get()}"
        return (
            self.__name_var.get(),
            date,
            self.__desc_var.get(),
            self.__cat_selected.get(),
            self.__delete_var.get()
        )

class AddEditWindow(Toplevel):
    """
    tkinter add/edit menu popup
    """
    def __init__(self, possiblecategories, on_save=None):
        Toplevel.__init__(self)
        self.wm_title("Add Entry")
        self.__the_entry = AddEditEntry(self, possiblecategories)
        self.__b_save = Button(self, text="Save", command=self.__save)
        self.__b_exit = Button(self, text="Exit", command=self.__closeWindow)
        self.__the_entry.pack()
        self.__b_save.pack()
        self.__b_exit.pack()
        self.on_save = on_save

    def __save(self):
        if self.on_save:
            data = self.__the_entry.get_values()
            self.on_save(data)
        self.__closeWindow()

    def __closeWindow(self):
        self.destroy()

    def load_data(self, day, monthint, year, name, desc, cat):
        self.wm_title("Edit Entry")
        logging.debug(f"Loading data: {day}, {monthint}, {year}, {name}, {desc}, {cat}")
        self.__the_entry.set_values(day, monthint, year, name, desc, cat)

class MainWindow(Frame):
    def __init__(self, parent, possiblecats):
        Frame.__init__(self, parent)
        self.pack()
        self.possiblecats = possiblecats
        self.entries = []
        
        self.__b_add = Button(self, text="Add Entry", command=self.add_entry)
        self.__b_delete = Button(self, text="Delete Selected", command=self.delete_selected)
        self.__b_save_exit = Button(self, text="Save and Exit", command=self.save_and_exit)

        self.__b_add.pack()
        self.__b_delete.pack()
        self.__b_save_exit.pack()

    def add_entry(self):
        window = AddEditWindow(self.possiblecats, on_save=self.save_entry)
        window.grab_set()

    def save_entry(self, data):
        # Save the entry to the database
        conn = setup_database()
        c = conn.cursor()
        c.execute("INSERT INTO entries (name, date, description, category) VALUES (?, ?, ?, ?)", data[:-1])
        conn.commit()
        conn.close()
        self.entries.append(data)

    def delete_selected(self):
        to_delete = [entry for entry in self.entries if entry[4]]  # Assuming entry[4] is the checkbox value
        for entry in to_delete:
            print(f"Deleting entry: {entry}")
            self.entries.remove(entry)
        messagebox.showinfo("Delete", "Selected entries deleted.")

    def save_and_exit(self):
        # Save all entries to the database here if needed
        print("Saving all entries and exiting...")
        self.quit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    root = Tk()
    possible_categories = ["Work", "Personal", "Other"]
    setup_database()
    app = MainWindow(root, possible_categories)
    root.mainloop()
