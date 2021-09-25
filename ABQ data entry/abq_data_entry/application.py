import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from .constants import EW
from .images import ABQ_LOGO_32, ABQ_LOGO_64
from . import views as v
from . import models as m


class Application(tk.Tk):
    """Application root window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("ABQ Data Entry Application")
        self.resizable(width=False, height=False)
        self.logo = tk.PhotoImage(file=ABQ_LOGO_32)
        tk.Label(self, image=self.logo).grid(row=0)
        self.taskbar_icon = tk.PhotoImage(file=ABQ_LOGO_64)
        self.call("wm", "iconphoto", self._w, self.taskbar_icon)
        self.inserted_rows: list[int] = []
        self.updated_rows: list[int] = []

        default_filename = f"abc_data_record_{date.today().isoformat()}.csv"
        self.filename = tk.StringVar(value=default_filename)
        self.data_model = m.CSVModel(filename=self.filename.get())
        self.settings_model = m.SettingsModel()
        self.load_settings()
        self.callbacks = {
            "file->select": self.on_file_select,
            "file->quit": self.quit,
            "show_recordlist": self.show_recordlist,
            "new_record": self.open_record,
            "on_open_record": self.open_record,
            "on_save": self.on_save,
        }
        menu = v.MainMenu(self, settings=self.settings, callbacks=self.callbacks)
        self.config(menu=menu)

        self.record_form = v.DataRecordForm(
            self,
            fields=m.CSVModel.fields,
            settings=self.settings,
            callbacks=self.callbacks,
        )
        self.record_form.grid(row=1, padx=10, sticky=tk.NSEW)
        self.record_list = v.RecordList(
            self, self.callbacks, self.inserted_rows, self.updated_rows
        )
        self.record_list.grid(row=1, padx=10, sticky=tk.NSEW)
        self.populate_recordlist()
        self.status = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status)
        self.status_bar.grid(sticky=EW, row=2, padx=10)
        self.records_saved = 0

    def load_settings(self):
        """Load settings into our self.settings dict"""
        vartypes = {
            "bool": tk.BooleanVar,
            "str": tk.StringVar,
            "int": tk.IntVar,
            "float": tk.DoubleVar,
        }
        self.settings: dict[str, tk.Variable] = {}
        for key, data in self.settings_model.variables.items():
            vartype: tk.Variable = vartypes.get(data["type"], tk.StringVar)
            self.settings[key] = vartype(value=data["value"])
        for var in self.settings.values():
            var.trace("w", self.save_settings)

    def save_settings(self, *args):
        """Save the current settings to a preferences file"""
        for key, variable in self.settings.items():
            self.settings_model.set(key, variable.get())
        self.settings_model.save()

    def on_file_select(self):
        """Handle the file->select action from the menu"""
        filename = filedialog.asksaveasfilename(
            title="Select the target file for saving records",
            defaultextension=".csv",
            filetypes=[("Comma-Separated Values", "*.csv *.CSV")],
        )
        if filename:
            self.filename.set(filename)
            self.data_model = m.CSVModel(filename=self.filename.get())
            self.populate_recordlist()
            self.inserted_rows = []
            self.updated_rows = []

    def on_save(self):
        if e := self.record_form.get_errors():
            self.display_errors(e)
            return False
        data = self.record_form.get()
        rownum = self.record_form.current_record
        try:
            self.data_model.save_record(data, rownum)
        except IndexError as e:
            messagebox.showerror(
                title="Error", message="Invalid row specified", detail=str(e)
            )
            self.status.set("Tried to update invalid row")
        except Exception as e:
            messagebox.showerror(
                title="Error", message="Problem saving record", detail=str(e)
            )
            self.status.set("Problem saving record")
        else:
            self.records_saved += 1
            self.status.set(f"{self.records_saved} records saved this session.")
            if rownum is not None:
                self.updated_rows.append(rownum)
            else:
                rownum = len(self.data_model.get_all_records()) - 1
                self.inserted_rows.append(rownum)
            self.populate_recordlist()
            if self.record_form.current_record is None:
                self.record_form.reset()

    def populate_recordlist(self):
        try:
            rows = self.data_model.get_all_records()
        except Exception as e:
            messagebox.showerror(
                title="Error", message="Problem reading file", detail=str(e)
            )
        else:
            self.record_list.populate(rows)

    def display_errors(self, e: dict[str, str]):
        self.status.set(f"Cannot save, error in fields: {', '.join(e.keys())}")
        message = "Cannot save record"
        errors = "\n * ".join(e.keys())
        detail = f"The following fields have errors:\n * {errors}"
        messagebox.showerror(title="Error", message=message, detail=detail)

    def show_recordlist(self):
        self.record_list.tkraise()

    def open_record(self, rownum=None):
        if rownum is None:
            record = None
        else:
            rownum = int(rownum)
            try:
                record = self.data_model.get_record(rownum)
            except Exception as e:
                messagebox.showerror(
                    title="Error", message="Problem reading file", detail=str(e)
                )
                return
        self.record_form.load_record(rownum, data=record)
        self.record_form.tkraise()
