import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3

class DisplayEntries(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title("Registered User Entries")
        
        self.conn = sqlite3.connect('face.db')
        self.cursor = self.conn.cursor()

        self.create_widgets()
        self.load_entries()

    def create_widgets(self):
        # Style configuration for Treeview
        style = ttk.Style()
        style.configure("Treeview", 
                        rowheight=25, 
                        borderwidth=1)
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'), background='lightgray', foreground='black')
        style.map("Treeview", background=[('selected', 'lightblue')])  # Highlight selected rows
        
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Date", "Description", "Category"), show='headings', height=15)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Category", text="Category")

        # Configure column widths
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=150)
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Description", width=200)
        self.tree.column("Category", width=100, anchor="center")

        self.tree.pack(pady=10, padx=10)

        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Buttons for Delete, Save and Exit
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        self.select_all_button = tk.Button(button_frame, text="Select All", command=self.select_all)
        self.select_all_button.grid(row=0, column=0, padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete Selected", command=self.delete_selected)
        self.delete_button.grid(row=0, column=1, padx=5)

        self.save_exit_button = tk.Button(button_frame, text="Save and Exit", command=self.save_and_exit)
        self.save_exit_button.grid(row=0, column=2, padx=5)

        self.pack()

    def load_entries(self):
        """Load entries from the database"""
        self.tree.delete(*self.tree.get_children())  # Clear existing entries
        self.cursor.execute("SELECT * FROM user")  # Adjust according to your table
        for entry in self.cursor.fetchall():
            self.tree.insert('', tk.END, values=entry)  # Customize formatting as needed

    def select_all(self):
        """Select all entries in the treeview"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def delete_selected(self):
        """Delete selected entries from both the database and the treeview"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "No entries selected for deletion.")
            return
        
        for item in selected_items:
            entry_id = self.tree.item(item, 'values')[0]  # Assuming ID is the first column
            # Delete from database
            self.cursor.execute("DELETE FROM user WHERE id=?", (entry_id,))
            self.conn.commit()
            # Remove from Treeview
            self.tree.delete(item)

        # Reset IDs and reload entries after deletion
        self.reset_ids()
        self.load_entries()

        messagebox.showinfo("Info", "Selected entries deleted.")

    def reset_ids(self):
        """Reset the ID column to be sequential after deletion"""
        self.cursor.execute("SELECT MAX(id) FROM user")
        max_id = self.cursor.fetchone()[0]
        
        if max_id is None:  # If there are no entries, set next ID to 1
            next_id = 1
        else:
            next_id = 1
        
        # Update IDs in the user table
        self.cursor.execute("UPDATE user SET id = NULL")  # Clear existing IDs
        self.conn.commit()

        self.cursor.execute("SELECT * FROM user ORDER BY id")  # Re-fetch entries ordered by ID
        rows = self.cursor.fetchall()

        for i, row in enumerate(rows):
            new_row = (i + 1, row[1], row[2], row[3], row[4])  # Re-assign new IDs (starting from 1)
            self.cursor.execute("UPDATE user SET id = ? WHERE rowid = ?", (new_row[0], row[0]))
        
        self.conn.commit()

    def save_and_exit(self):
        """Save changes and close the application"""
        self.conn.close()
        self.parent.destroy()

    def on_closing(self):
        """Handle window close event"""
        self.conn.close()
        self.parent.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DisplayEntries(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
