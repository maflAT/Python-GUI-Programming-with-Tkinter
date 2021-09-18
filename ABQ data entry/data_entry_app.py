import tkinter as tk
from tkinter import ttk
import os
import csv
from datetime import datetime

WE = (tk.W, tk.E)


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
        self.record_form = DataRecordForm(self)
        self.record_form.grid(row=1, padx=10)
        self.save_button = ttk.Button(self, text="Save", command=self.on_save)
        self.save_button.grid(sticky=tk.E, row=2, padx=10)
        self.status = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status)
        self.status_bar.grid(sticky=WE, row=3, padx=10)
        self.records_saved = 0

    def on_save(self):
        datestring = datetime.today().strftime(r"%Y-%m-%d")
        filename = f"abc_data_record_{datestring}.csv"
        newfile = not os.path.exists(filename)
        data = self.record_form.get()
        with open(filename, "a") as fh:
            csv_writer = csv.DictWriter(fh, fieldnames=data.keys())
            if newfile:
                csv_writer.writeheader()
            csv_writer.writerow(data)
        self.records_saved += 1
        self.status.set(f"{self.records_saved} records saved this session.")
        self.record_form.reset()


class LabelInput(tk.Frame):
    """A widget containing a label and input together."""

    def __init__(
        self,
        parent,
        label="",
        input_class: tk.Widget = ttk.Entry,
        input_var=None,
        input_args=None,
        label_args=None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.variable = input_var
        input_args = input_args or {}
        label_args = label_args or {}

        if input_class in (ttk.Checkbutton, ttk.Button, ttk.Radiobutton):
            input_args["text"] = label
            input_args["variable"] = input_var
        else:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=WE)
            input_args["textvariable"] = input_var

        self.input: tk.Widget = input_class(self, **input_args)
        self.input.grid(row=1, column=0, sticky=WE)
        self.columnconfigure(0, weight=1)

    def grid(self, sticky=WE, **kwargs):
        super().grid(sticky=sticky, **kwargs)
        return self

    def get(self):
        try:
            if self.variable:
                return self.variable.get()
            elif type(self.input) == tk.Text:
                return self.input.get("1.0", tk.END)
            else:
                return self.input.get()
        except (TypeError, tk.TclError):
            # happens when numeric fields are empty.
            return ""

    def set(self, value, *args, **kwargs):
        if type(self.variable) == tk.BooleanVar:
            self.variable.set(bool(value))
        elif type(self.input) in (ttk.Checkbutton, ttk.Radiobutton):
            if value:
                self.input.select()
            else:
                self.input.deselect()
        elif type(self.input) == tk.Text:
            self.input.delete("1.0", tk.END)
            self.input.insert("1.0", value)
        else:  # input must be entry type widget with no variable
            self.input.delete(0, tk.END)
            self.input.insert(0, value)


class DataRecordForm(tk.Frame):
    """The input form for our widgets"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.inputs: dict[str, LabelInput] = {}
        self.init_record_info().grid(sticky=WE, row=0, column=0)
        self.init_env_info().grid(sticky=WE, row=1, column=0)
        self.init_plant_info().grid(sticky=WE, row=2, column=0)
        self.init_notes().grid(sticky=tk.W, row=3, column=0)
        self.reset()

    def init_record_info(self):
        record_info = tk.LabelFrame(self, text="Record Information")
        self.inputs["Date"] = LabelInput(
            parent=record_info, label="Date", input_var=tk.StringVar()
        ).grid(row=0, column=0)
        self.inputs["Time"] = LabelInput(
            parent=record_info,
            label="Time",
            input_class=ttk.Combobox,
            input_var=tk.StringVar(),
            input_args={"values": ["8:00", "12:00", "16:00", "20:00"]},
        ).grid(row=0, column=1)
        self.inputs["Technician"] = LabelInput(
            parent=record_info,
            label="Technician",
            input_var=tk.StringVar(),
        ).grid(row=0, column=2)

        self.inputs["Lab"] = LabelInput(
            parent=record_info,
            label="Lab",
            input_class=ttk.Combobox,
            input_var=tk.StringVar(),
            input_args={"values": ["A", "B", "C", "D", "E"]},
        ).grid(row=1, column=0)
        self.inputs["Plot"] = LabelInput(
            parent=record_info,
            label="Plot",
            input_class=ttk.Combobox,
            input_var=tk.IntVar(),
            input_args={"values": list(range(1, 21))},
        ).grid(row=1, column=1)
        self.inputs["Seed sample"] = LabelInput(
            parent=record_info,
            label="Seed sample",
            input_var=tk.StringVar(),
        ).grid(row=1, column=2)
        return record_info

    def init_env_info(self):
        env_info = tk.LabelFrame(self, text="Environment Data")
        self.inputs["Humidity"] = LabelInput(
            parent=env_info,
            label="Humidity (g/m³)",
            input_class=ttk.Spinbox,
            input_var=tk.DoubleVar(),
            input_args={"from_": 0.5, "to": 52.0, "increment": 0.01},
        ).grid(row=0, column=0)
        self.inputs["Light"] = LabelInput(
            parent=env_info,
            label="Light (klx)",
            input_class=ttk.Spinbox,
            input_var=tk.DoubleVar(),
            input_args={"from_": 0, "to": 100, "increment": 0.1},
        ).grid(row=0, column=1)
        self.inputs["Temperature"] = LabelInput(
            parent=env_info,
            label="Temperature (°C)",
            input_class=ttk.Spinbox,
            input_var=tk.DoubleVar(),
            input_args={"from_": 4, "to": 40, "increment": 0.1},
        ).grid(row=0, column=2)
        self.inputs["Equipment Fault"] = LabelInput(
            parent=env_info,
            label="Equipment Fault",
            input_class=ttk.Checkbutton,
            input_var=tk.BooleanVar(),
        ).grid(row=1, column=0, columnspan=3)
        return env_info

    def init_plant_info(self):
        plant_info = tk.LabelFrame(self, text="Plant Data")
        self.inputs["Plants"] = LabelInput(
            parent=plant_info,
            label="Plants",
            input_class=ttk.Spinbox,
            input_var=tk.IntVar(),
            input_args={"from_": 0, "to": 20},
        ).grid(row=0, column=0)
        self.inputs["Blossoms"] = LabelInput(
            parent=plant_info,
            label="Blossoms",
            input_class=ttk.Spinbox,
            input_var=tk.IntVar(),
            input_args={"from_": 0, "to": 1000},
        ).grid(row=0, column=1)
        self.inputs["Fruit"] = LabelInput(
            parent=plant_info,
            label="Fruit",
            input_class=ttk.Spinbox,
            input_var=tk.IntVar(),
            input_args={"from_": 0, "to": 1000},
        ).grid(row=0, column=2)
        self.inputs["Min Height"] = LabelInput(
            parent=plant_info,
            label="Min Height",
            input_class=ttk.Spinbox,
            input_var=tk.IntVar(),
            input_args={"from_": 0, "to": 1000},
        ).grid(row=1, column=0)
        self.inputs["Max Height"] = LabelInput(
            parent=plant_info,
            label="Max Height",
            input_class=ttk.Spinbox,
            input_var=tk.IntVar(),
            input_args={"from_": 0, "to": 1000},
        ).grid(row=1, column=1)
        self.inputs["Median Height"] = LabelInput(
            parent=plant_info,
            label="Median Height",
            input_class=ttk.Spinbox,
            input_var=tk.IntVar(),
            input_args={"from_": 0, "to": 1000},
        ).grid(row=1, column=2)
        return plant_info

    def init_notes(self):
        self.inputs["Notes"] = LabelInput(
            parent=self,
            label="Notes",
            input_class=tk.Text,
            input_args={"width": 75, "height": 10},
        )
        return self.inputs["Notes"]

    def get(self):
        return {key: widget.get() for key, widget in self.inputs.items()}

    def reset(self):
        for widget in self.inputs.values():
            widget.set("")


def main(args) -> None:
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    import sys

    main_rv = main(sys.argv)
    sys.exit(main_rv)
