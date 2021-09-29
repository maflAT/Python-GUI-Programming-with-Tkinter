import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import Dialog
from datetime import date
from typing import Any, Callable, Optional
from . import widgets as w


class DataRecordForm(tk.Frame):
    """The input form for our widgets"""

    def __init__(
        self,
        parent: tk.Widget,
        fields: dict[str, dict],
        settings: dict[str, tk.Variable],
        callbacks: dict[str, Callable],
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.inputs: dict[str, w.LabelInput] = {}
        self.settings = settings
        self.callbacks = callbacks
        self.current_record = None

        style = ttk.Style()
        style.configure("RecordInfo.TLabel", background="khaki")
        style.configure("EnvironmentInfo.TLabel", background="lightblue")
        style.configure("EnvironmentInfo.TCheckbutton", background="lightblue")
        style.configure("PlantInfo.TLabel", background="lightgreen")

        self.record_label = ttk.Label(self)
        self.record_label.grid(row=0, column=0)

        self.init_record_info(fields).grid(sticky=tk.EW, row=1, column=0)
        self.init_env_info(fields).grid(sticky=tk.EW, row=2, column=0)
        self.init_plant_info(fields).grid(sticky=tk.EW, row=3, column=0)
        self.init_notes().grid(sticky=tk.W, row=4, column=0)
        self.save_button = ttk.Button(
            self, text="Save", command=self.callbacks["on_save"]
        )
        self.save_button.grid(sticky=tk.E, row=5, padx=10)

        for field in ("Lab", "Plot"):
            self.inputs[field].variable.trace("w", self.callbacks["get_seed_sample"])
        for field in ("Date", "Time", "Lab"):
            self.inputs[field].variable.trace("w", self.callbacks["get_check_tech"])

        self.reset()

    def init_record_info(self, fields: dict[str, dict]):
        record_info = tk.LabelFrame(
            self, text="Record Information", bg="khaki", padx=10, pady=10
        )
        self.inputs["Date"] = w.LabelInput(
            parent=record_info,
            label="Date",
            field_spec=fields["Date"],
            label_args={"style": "RecordInfo.TLabel"},
        ).grid(row=0, column=0)
        self.inputs["Time"] = w.LabelInput(
            parent=record_info,
            label="Time",
            field_spec=fields["Time"],
            label_args={"style": "RecordInfo.TLabel"},
        ).grid(row=0, column=1)
        self.inputs["Lab"] = w.LabelInput(
            parent=record_info,
            label="Lab",
            field_spec=fields["Lab"],
            label_args={"style": "RecordInfo.TLabel"},
        ).grid(row=0, column=2)

        self.inputs["Plot"] = w.LabelInput(
            parent=record_info,
            label="Plot",
            field_spec=fields["Plot"],
            label_args={"style": "RecordInfo.TLabel"},
        ).grid(row=1, column=0)
        self.inputs["Technician"] = w.LabelInput(
            parent=record_info,
            label="Technician",
            field_spec=fields["Technician"],
            label_args={"style": "RecordInfo.TLabel"},
        ).grid(row=1, column=1)
        self.inputs["Seed sample"] = w.LabelInput(
            parent=record_info,
            label="Seed sample",
            field_spec=fields["Seed sample"],
            label_args={"style": "RecordInfo.TLabel"},
        ).grid(row=1, column=2)
        return record_info

    def init_env_info(self, fields: dict[str, dict]):
        env_info = tk.LabelFrame(
            self, text="Environment Data", bg="lightblue", padx=10, pady=10
        )
        self.inputs["Humidity"] = w.LabelInput(
            parent=env_info,
            label="Humidity (g/m³)",
            field_spec=fields["Humidity"],
            label_args={"style": "EnvironmentInfo.TLabel"},
        ).grid(row=0, column=0)
        self.inputs["Light"] = w.LabelInput(
            parent=env_info,
            label="Light (klx)",
            field_spec=fields["Light"],
            label_args={"style": "EnvironmentInfo.TLabel"},
        ).grid(row=0, column=1)
        self.inputs["Temperature"] = w.LabelInput(
            parent=env_info,
            label="Temperature (°C)",
            field_spec=fields["Temperature"],
            label_args={"style": "EnvironmentInfo.TLabel"},
        ).grid(row=0, column=2)
        self.inputs["Equipment Fault"] = w.LabelInput(
            parent=env_info,
            label="Equipment Fault",
            field_spec=fields["Equipment Fault"],
            label_args={"style": "EnvironmentInfo.TLabel"},
            input_args={"style": "EnvironmentInfo.TCheckbutton"},
        ).grid(row=1, column=0, columnspan=3)
        return env_info

    def init_plant_info(self, fields: dict[str, dict]):
        plant_info = tk.LabelFrame(
            self, text="Plant Data", bg="lightgreen", padx=10, pady=10
        )
        self.inputs["Plants"] = w.LabelInput(
            parent=plant_info,
            label="Plants",
            field_spec=fields["Plants"],
            label_args={"style": "PlantInfo.TLabel"},
        ).grid(row=0, column=0)
        self.inputs["Blossoms"] = w.LabelInput(
            parent=plant_info,
            label="Blossoms",
            field_spec=fields["Blossoms"],
            label_args={"style": "PlantInfo.TLabel"},
        ).grid(row=0, column=1)
        self.inputs["Fruit"] = w.LabelInput(
            parent=plant_info,
            label="Fruit",
            field_spec=fields["Fruit"],
            label_args={"style": "PlantInfo.TLabel"},
        ).grid(row=0, column=2)

        # Height data
        # create variables to be updated for min/max height
        # they can be referenced for min/max variables
        min_height_var = tk.DoubleVar(value="-infinity")
        max_height_var = tk.DoubleVar(value="infinity")
        self.inputs["Min Height"] = w.LabelInput(
            parent=plant_info,
            label="Min Height (cm)",
            field_spec=fields["Min Height"],
            input_args={
                "max_var": max_height_var,
                "focus_update_var": min_height_var,
            },
            label_args={"style": "PlantInfo.TLabel"},
        ).grid(row=1, column=0)
        self.inputs["Max Height"] = w.LabelInput(
            parent=plant_info,
            label="Max Height (cm)",
            field_spec=fields["Max Height"],
            input_args={
                "min_var": min_height_var,
                "focus_update_var": max_height_var,
            },
            label_args={"style": "PlantInfo.TLabel"},
        ).grid(row=1, column=1)
        self.inputs["Median Height"] = w.LabelInput(
            parent=plant_info,
            label="Median Height (cm)",
            field_spec=fields["Median Height"],
            input_args={
                "min_var": min_height_var,
                "max_var": max_height_var,
            },
            label_args={"style": "PlantInfo.TLabel"},
        ).grid(row=1, column=2)
        return plant_info

    def init_notes(self):
        self.inputs["Notes"] = w.LabelInput(
            parent=self,
            label="Notes",
            input_class=tk.Text,
            input_args={"width": 75, "height": 10},
            padx=10,
            pady=10,
        )
        return self.inputs["Notes"]

    def get(self):
        return {key: widget.get() for key, widget in self.inputs.items()}

    def reset(self):
        """Reset the form for entries"""
        # get current values for auto-filling
        lab = self.inputs["Lab"].get()
        time = self.inputs["Time"].get()
        technician = self.inputs["Technician"].get()
        plot = self.inputs["Plot"].get()
        plot_values = self.inputs["Plot"].input.cget("values")

        # clear all fields
        for widget in self.inputs.values():
            widget.set("")

        # set defaults
        if self.settings["autofill date"].get():
            self.inputs["Date"].set(date.today().isoformat())
            self.focus_next_empty()
        if not self.settings["autofill sheet data"].get() or (
            plot in ("", plot_values[-1])
        ):
            self.focus_next_empty()
            return
        self.inputs["Lab"].set(lab)
        self.inputs["Time"].set(time)
        self.inputs["Technician"].set(technician)
        next_plot_idx = plot_values.index(plot) + 1
        self.inputs["Plot"].set(plot_values[next_plot_idx])
        self.focus_next_empty()

    def get_errors(self):
        """Get a list of field errors in the form."""
        errors: dict[str, str] = {}
        for name, widget in self.inputs.items():
            if hasattr(widget.input, "trigger_focusout_validation"):
                widget.input.trigger_focusout_validation()
            if e := widget.error.get():
                errors[name] = e
        return errors

    def load_record(self, rowkey: tuple, data: Optional[dict[str, str]] = None):
        self.current_record = rowkey
        if rowkey is None:
            self.reset()
            self.record_label.config(text="New Record")
            return
        text = "Record for Lab {2}, Plot {3} at {0} {1}".format(*rowkey)
        self.record_label.config(text=text)
        for key, widget in self.inputs.items():
            self.inputs[key].set(data.get(key, ""))
            try:
                widget.input.trigger_focusout_validation()
            except AttributeError:
                pass

    def focus_next_empty(self):
        for labelwidget in self.inputs.values():
            if labelwidget.get() == "":
                labelwidget.input.focus()
                break


class RecordList(tk.Frame):
    """Display for CSV file contents"""

    column_defs: dict[str, dict[str, Any]] = {
        "#0": {"label": "Row", "anchor": tk.W},
        "Date": {"label": "Date", "width": 150, "stretch": True},
        "Time": {"label": "Time"},
        "Lab": {"label": "Lab", "width": 40},
        "Plot": {"label": "Plot", "width": 80},
    }
    default_width = 100
    default_minwidth = 10
    default_anchor = tk.CENTER

    def __init__(
        self,
        parent: tk.Widget,
        callbacks: dict[str, Callable],
        inserted: list[int],
        updated: list[int],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)
        self.callbacks = callbacks
        self.inserted = inserted
        self.updated = updated
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tv = ttk.Treeview(
            self, columns=list(self.column_defs.keys())[1:], selectmode="browse"
        )
        self.tv.grid(row=0, column=0, sticky=tk.NSEW)
        for name, definition in self.column_defs.items():
            label = definition.get("label", "")
            anchor = definition.get("anchor", self.default_anchor)
            minwidth = definition.get("minwidth", self.default_minwidth)
            width = definition.get("width", self.default_width)
            stretch = definition.get("stretch", False)
            self.tv.heading(name, text=label, anchor=anchor)
            self.tv.column(
                name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch
            )
        self.tv.tag_configure("inserted", background="lightgreen")
        self.tv.tag_configure("updated", background="lightblue")
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tv.yview)
        self.tv.configure(show="headings", yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="NSW")
        self.tv.bind("<<TreeviewOpen>>", self.on_open_record)

    def populate(self, rows: list[dict[str, dict]]):
        """Clear the treeview and write the supplied data rows to it."""
        for row in self.tv.get_children():
            self.tv.delete(row)
        valuekeys = list(self.column_defs.keys())[1:]
        for rowdata in rows:
            rowkey = (
                str(rowdata["Date"]),
                rowdata["Time"],
                rowdata["Lab"],
                str(rowdata["Plot"]),
            )
            values = [rowdata[key] for key in valuekeys]
            if self.inserted and rowkey in self.inserted:
                tag = "inserted"
            if self.updated and rowkey in self.updated:
                tag = "updated"
            else:
                tag = ""
            stringkey = "|".join(rowkey)
            self.tv.insert(
                "", "end", iid=stringkey, text=stringkey, values=values, tag=tag
            )
        if rows:
            self.tv.focus_set()
            firstrow = self.tv.identify_row(0)
            self.tv.selection_set(firstrow)
            self.tv.focus(firstrow)

    def on_open_record(self, *args):
        self.callbacks["on_open_record"](self.tv.selection()[0].split("|"))


class LoginDialog(Dialog):
    """Login Dialog class for database connection."""

    def __init__(self, parent, title: str, error: str = "") -> None:
        self.pw = tk.StringVar()
        self.user = tk.StringVar()
        self.error = tk.StringVar(value=error)
        super().__init__(parent, title=title)

    def body(self, parent):
        """Dialog form is defined here."""
        lf = tk.Frame(self)
        ttk.Label(lf, text="Login ot ABQ", font="Sans 20").grid()
        if self.error.get():
            tk.Label(lf, textvariable=self.error, bg="darkred", fg="white").grid()
        ttk.Label(lf, text="User name:").grid()
        self.username_inp = ttk.Entry(lf, textvariable=self.user)
        self.username_inp.grid()
        ttk.Label(lf, text="Password:").grid()
        self.password_inp = ttk.Entry(lf, show="*", textvariable=self.pw)
        self.password_inp.grid()
        lf.pack()
        return self.username_inp

    def apply(self):
        self.result = (self.user.get(), self.pw.get())
