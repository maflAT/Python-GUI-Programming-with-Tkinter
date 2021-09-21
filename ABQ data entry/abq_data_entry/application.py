import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from .constants import EW
from . import views as v
from . import models as m


class Application(tk.Tk):
    """Application root window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("ABQ Data Entry Application")
        self.resizable(width=False, height=False)
        ttk.Label(
            self,
            text="ABQ Data Entry Application",
            font=("TkDefaultFont", 16),
        ).grid(row=0)
        default_filename = f"abc_data_record_{date.today().isoformat()}.csv"
        self.filename = tk.StringVar(value=default_filename)
        self.settings = {
            "autofill date": tk.BooleanVar(),
            "autofill sheet data": tk.BooleanVar(),
        }
        self.callbacks = {"file->select": self.on_file_select, "file->quit": self.quit}
        menu = v.MainMenu(self, settings=self.settings, callbacks=self.callbacks)
        self.config(menu=menu)

        self.record_form = v.DataRecordForm(
            self, fields=m.CSVModel.fields, settings=self.settings
        )
        self.record_form.grid(row=1, padx=10)
        self.save_button = ttk.Button(self, text="Save", command=self.on_save)
        self.save_button.grid(sticky=tk.E, row=2, padx=10)
        self.status = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status)
        self.status_bar.grid(sticky=EW, row=3, padx=10)
        self.records_saved = 0

    def on_file_select(self):
        """Handle the file->select action from the menu"""
        filename = filedialog.asksaveasfilename(
            title="Select the target file for saving records",
            defaultextension=".csv",
            filetypes=[("Comma-Separated Values", "*.csv *.CSV")],
        )
        if filename:
            self.filename.set(filename)

    def on_save(self):
        if e := self.record_form.get_errors():
            self.display_errors(e)
            return False
        m.CSVModel(self.filename.get()).save_record(self.record_form.get())
        self.records_saved += 1
        self.status.set(f"{self.records_saved} records saved this session.")
        self.record_form.reset()

    def display_errors(self, e: dict[str, str]):
        self.status.set(f"Cannot save, error in fields: {', '.join(e.keys())}")
        message = "Cannot save record"
        errors = "\n * ".join(e.keys())
        detail = f"The following fields have errors:\n * {errors}"
        messagebox.showerror(title="Error", message=message, detail=detail)
