import tkinter as tk
from tkinter import ttk
from datetime import date
from tkinter import messagebox
from typing import Any, Callable, Optional
from . import widgets as w
from .constants import EW


class MainMenu(tk.Menu):
    def __init__(
        self, parent, settings: dict, callbacks: dict[str, Callable], **kwargs
    ) -> None:
        super().__init__(parent, **kwargs)

        # file menu
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label="Select file...", command=callbacks["file->select"])
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=callbacks["file->quit"])
        self.add_cascade(label="File", menu=file_menu)

        # options menu
        options_menu = tk.Menu(self, tearoff=False)
        options_menu.add_checkbutton(
            label="Autofill Date", variable=settings["autofill date"]
        )
        options_menu.add_checkbutton(
            label="Autofill Sheet data", variable=settings["autofill sheet data"]
        )
        #   font size sub-menu
        font_size_menu = tk.Menu(self, tearoff=False)
        for size in range(6, 17):
            font_size_menu.add_radiobutton(
                label=size, value=size, variable=settings["font size"]
            )
        options_menu.add_cascade(label="Font size", menu=font_size_menu)
        self.add_cascade(label="Options", menu=options_menu)

        # go menu
        go_menu = tk.Menu(self, tearoff=False)
        go_menu.add_command(label="Record List", command=callbacks["show_recordlist"])
        go_menu.add_command(label="New Record", command=callbacks["new_record"])
        self.add_cascade(label="Go", menu=go_menu)

        # help menu
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about)
        self.add_cascade(label="Help", menu=help_menu)

    def show_about(self):
        """Show the about dialog"""
        about_message = "ABQ Data Entry"
        about_detail = "by Alan D Moore\nFor assistance please contact the author."
        messagebox.showinfo(title="About", message=about_message, detail=about_detail)


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

        self.init_record_info(fields).grid(sticky=EW, row=1, column=0)
        self.init_env_info(fields).grid(sticky=EW, row=2, column=0)
        self.init_plant_info(fields).grid(sticky=EW, row=3, column=0)
        self.init_notes().grid(sticky=tk.W, row=4, column=0)
        self.save_button = ttk.Button(
            self, text="Save", command=self.callbacks["on_save"]
        )
        self.save_button.grid(sticky=tk.E, row=5, padx=10)
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
        self.inputs["Technician"] = w.LabelInput(
            parent=record_info,
            label="Technician",
            field_spec=fields["Technician"],
            label_args={"style": "RecordInfo.TLabel"},
        ).grid(row=0, column=2)

        self.inputs["Lab"] = w.LabelInput(
            parent=record_info,
            label="Lab",
            field_spec=fields["Lab"],
            label_args={"style": "RecordInfo.TLabel"},
        ).grid(row=1, column=0)
        self.inputs["Plot"] = w.LabelInput(
            parent=record_info,
            label="Plot",
            field_spec=fields["Plot"],
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
            self.inputs["Time"].input.focus()
        if not self.settings["autofill sheet data"].get() or (
            plot in ("", plot_values[-1])
        ):
            self.inputs["Time"].input.focus()
            return
        self.inputs["Lab"].set(lab)
        self.inputs["Time"].set(time)
        self.inputs["Technician"].set(technician)
        next_plot_idx = plot_values.index(plot) + 1
        self.inputs["Plot"].set(plot_values[next_plot_idx])
        self.inputs["Seed sample"].input.focus()

    def get_errors(self):
        """Get a list of field errors in the form."""
        errors: dict[str, str] = {}
        for name, widget in self.inputs.items():
            if hasattr(widget.input, "trigger_focusout_validation"):
                widget.input.trigger_focusout_validation()
            if e := widget.error.get():
                errors[name] = e
        return errors

    def load_record(self, rownum, data: Optional[dict[str, str]] = None):
        self.current_record = rownum
        if rownum is None:
            self.reset()
            self.record_label.config(text="New Record")
            return
        self.record_label.config(text=f"Record #{rownum}")
        for key, widget in self.inputs.items():
            self.inputs[key].set(data.get(key, ""))
            try:
                widget.input.trigger_focusout_validation()
            except AttributeError:
                pass


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
        self.tv.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="NSW")
        self.tv.bind("<<TreeviewOpen>>", self.on_open_record)

    def populate(self, rows: list[dict[str, dict]]):
        """Clear the treeview and write the supplied data rows to it."""
        for row in self.tv.get_children():
            self.tv.delete(row)
        valuekeys = list(self.column_defs.keys())[1:]
        for rownum, rowdata in enumerate(rows):
            if self.inserted and rownum in self.inserted:
                tag = "inserted"
            if self.updated and rownum in self.updated:
                tag = "updated"
            else:
                tag = ""
            values = [rowdata[key] for key in valuekeys]
            self.tv.insert(
                "", "end", iid=str(rownum), text=str(rownum), values=values, tag=tag
            )
        if rows:
            self.tv.focus_set()
            self.tv.selection_set(0)
            self.tv.focus("0")

    def on_open_record(self, *args):
        self.callbacks["on_open_record"](self.tv.selection()[0])
