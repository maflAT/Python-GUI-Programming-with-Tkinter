import tkinter as tk
from tkinter import ttk
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
        self.record_form = v.DataRecordForm(self, fields=m.CSVModel.fields)
        self.record_form.grid(row=1, padx=10)
        self.save_button = ttk.Button(self, text="Save", command=self.on_save)
        self.save_button.grid(sticky=tk.E, row=2, padx=10)
        self.status = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status)
        self.status_bar.grid(sticky=EW, row=3, padx=10)
        self.records_saved = 0

    def on_save(self):
        # check for errors first
        if e := self.record_form.get_errors():
            self.status.set(f"Cannot save, error in fields: {', '.join(e.keys())}")
            return False
        filename = f"abc_data_record_{date.today().isoformat()}.csv"
        m.CSVModel(filename).save_record(self.record_form.get())
        self.records_saved += 1
        self.status.set(f"{self.records_saved} records saved this session.")
        self.record_form.reset()
