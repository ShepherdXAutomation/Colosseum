import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

class SQLExecutorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Executor")
        self.conn = sqlite3.connect('game.db')
        self.c = self.conn.cursor()

        # Create the dropdown to select tables
        self.create_table_dropdown()

        # Create the text box for SQL commands
        self.sql_input = tk.Text(root, height=10, width=80)
        self.sql_input.pack(pady=10)

        # Create the execute button
        execute_button = tk.Button(root, text="Execute SQL", command=self.execute_sql)
        execute_button.pack(pady=10)

        # Output box to show results
        self.output_box = tk.Text(root, height=10, width=80)
        self.output_box.pack(pady=10)

        self.refresh_table_list()

    def create_table_dropdown(self):
        """ Create a dropdown to select existing tables """
        self.table_list = ttk.Combobox(self.root, state="readonly")
        self.table_list.pack(pady=10)

        # Refresh button to update the list of tables
        refresh_button = tk.Button(self.root, text="Refresh Tables", command=self.refresh_table_list)
        refresh_button.pack(pady=5)

    def refresh_table_list(self):
        """ Fetch the list of tables and update the dropdown """
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in self.c.fetchall()]
        self.table_list['values'] = tables
        if tables:
            self.table_list.current(0)

    def execute_sql(self):
        """ Execute SQL command from input box """
        sql_command = self.sql_input.get("1.0", tk.END).strip()
        try:
            self.c.execute(sql_command)
            self.conn.commit()

            # Fetch result if it's a SELECT query
            if sql_command.lower().startswith("select"):
                rows = self.c.fetchall()
                self.output_box.delete("1.0", tk.END)
                for row in rows:
                    self.output_box.insert(tk.END, f"{row}\n")
            else:
                messagebox.showinfo("Success", "SQL command executed successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SQLExecutorApp(root)
    root.mainloop()
