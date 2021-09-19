import tkinter as tk
from tkinter import ttk
import os
import csv
from datetime import date
from typing import Optional
from decimal import Decimal, InvalidOperation
from enum import Enum

WE = (tk.W, tk.E)


class TkAction(Enum):
    DEL: str = "0"
    INSERT: str = "1"
    OTHER: str = "-1"


class TkEvent(Enum):
    FOCUS_OUT: str = "<FocusOut>"


class ValidatedMixin:
    """Adds a validation functionality to an input widget."""

    def __init__(self: ttk.Widget, *args, error_var=None, **kwargs) -> None:
        self.error: Optional[tk.StringVar] = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)
        val_cmd = self.register(self._validate)
        inv_cmd = self.register(self._invalid)
        self.configure(
            validate="all",
            validatecommand=(val_cmd, "%P", "%s", "%S", "%V", "%i", "%d"),
            invalidcommand=(inv_cmd, "%P", "%s", "%S", "%V", "%i", "%d"),
        )

    def _toggle_error(self: ttk.Widget, on: bool = False):
        self.configure(foreground=("red" if on else "black"))

    def _validate(
        self,
        proposed: str,
        current: str,
        char: str,
        event: str,
        index: str,
        action: str,
    ) -> bool:
        self._toggle_error(False)
        self.error.set("")
        valid = True
        if event == "focusout":
            valid = self._focusout_validate(event=event)
        elif event == "key":
            valid = self._key_validate(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action,
            )
        return valid

    def _focusout_validate(self, **kwargs) -> bool:
        return True

    def _key_validate(self, **kwargs) -> bool:
        return True

    def _invalid(
        self,
        proposed,
        current,
        char,
        event,
        index,
        action,
    ) -> None:
        if event == "focusout":
            self._focusout_invalid(event=event)
        elif event == "key":
            valid = self._key_invalid(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action,
            )

    def _focusout_invalid(self, **kwargs) -> None:
        self._toggle_error(True)

    def _key_invalid(self, **kwargs) -> None:
        ...

    def trigger_focusout_validation(self) -> bool:
        valid = self._validate("", "", "", "focusout", "", "")
        if not valid:
            self._focusout_invalid(event="focusout")
        return valid


class RequiredEntry(ValidatedMixin, ttk.Entry):
    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            valid = False
            self.error.set("A value is required")
        return valid


class DateEntry(ValidatedMixin, ttk.Entry):
    def _key_validate(self, action: str, index: str, char: str, **kwargs):
        if action == TkAction.DEL.value:
            return True
        if len(char) > 1:  # insertion via paste or direct setting
            return True
        elif index in "01235689":
            return char.isdigit()
        elif index in "47":
            return char == "-"
        else:
            return False

    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            self.error.set("A value is required")
            valid = False
        try:
            date.fromisoformat(self.get())
        except ValueError:
            self.error.set("Invalid date")
            valid = False
        return valid


class ValidatedCombobox(ValidatedMixin, ttk.Combobox):
    def _key_validate(self, proposed: str, action: str, **kwargs) -> bool:
        valid = True
        # if the user tries to delete, just clear the field
        if action == TkAction.DEL.value:
            self.set("")
            return True
        # get our values list
        values: list[str] = self.cget("values")
        matching = [x for x in values if x.lower().startswith(proposed.lower())]
        if not matching:
            valid = False
        elif len(matching) == 1:
            self.set(matching[0])
            self.icursor(tk.END)
            valid = False
        return valid

    def _focusout_validate(self, **kwargs) -> bool:
        valid = True
        if not self.get():
            valid = False
            self.error.set("A value is required")
        return valid


class ValidatedSpinBox(ValidatedMixin, tk.Spinbox):
    def __init__(
        self,
        *args,
        min_var: Optional[tk.DoubleVar] = None,
        max_var: Optional[tk.DoubleVar] = None,
        focus_update_var: Optional[tk.DoubleVar] = None,
        from_="-Infinity",
        to="Infinity",
        **kwargs,
    ) -> None:
        super().__init__(*args, from_=from_, to=to, **kwargs)
        self.resolution = Decimal(str(kwargs.get("increment", "1.0")))
        self.precision = self.resolution.normalize().as_tuple().exponent
        # there should always be a variable, or some of our code will fail
        self.variable: tk.DoubleVar = kwargs.get("textvariable") or tk.DoubleVar()
        if min_var:
            self.min_var = min_var
            self.min_var.trace("w", self._set_minimum)
        if max_var:
            self.max_var = max_var
            self.max_var.trace("w", self._set_maximum)
        self.focus_update_var = focus_update_var
        self.bind(TkEvent.FOCUS_OUT.value, self._set_focus_update_var)

    def _set_focus_update_var(self, event):
        value = self.get()
        if self.focus_update_var and not self.error.get():
            self.focus_update_var.set(value)

    def _set_minimum(self, *args):
        current = self.get()
        try:
            new_min = self.min_var.get()
            self.config(from_=new_min)
        except (tk.TclError, ValueError):
            pass
        if not current:
            self.delete(0, tk.END)
        else:
            self.variable.set(current)
        self.trigger_focusout_validation()

    def _set_maximum(self, *args):
        current = self.get()
        try:
            new_max = self.max_var.get()
            self.config(to=new_max)
        except (tk.TclError, ValueError):
            pass
        if not current:
            self.delete(0, tk.END)
        else:
            self.variable.set(current)
        self.trigger_focusout_validation()

    def _key_validate(
        self, char: str, index: str, current: str, proposed: str, action: str, **kwargs
    ) -> bool:  # sourcery skip: return-identity
        if action == TkAction.DEL.value:
            return True
        if char not in "-1234567890.,":
            return False
        if char == "-" and (self.cget("from") >= 0 or index != "0"):
            return False
        if char in ".," and (self.precision >= 0 or [c in current for c in ".,"]):
            return False
        # At this point, proposed is either '-', '.', '-.',
        # or a valid Decimal string
        if proposed in "-.":
            return True
        # Proposed is a valid Decimal string
        # convert to Decimal and check more:
        proposed: Decimal = Decimal(proposed)
        if proposed > self.cget("to"):
            return False
        if proposed.as_tuple().exponent < self.precision:
            return False
        return True

    def _focusout_validate(self, **kwargs) -> bool:
        valid = True
        value = self.get()
        try:
            value = Decimal(value)
        except InvalidOperation:
            self.error.set(f"Invalid number string: {value}")
            return False
        min_val = self.cget("from")
        if value < min_val:
            self.error.set(f"Value is too low (min {min_val})")
            valid = False
        max_val = self.cget("to")
        if value > max_val:
            self.error.set(f"Value is too high (max {max_val})")
            valid = False
        return valid


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
        # check for errors first
        errors = self.record_form.get_errors()
        if errors:
            self.status.set(f"Cannot save, error in fields: {', '.join(errors.keys())}")
            return False
        datestring = date.today().isoformat()
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
    """A widget containing a label, input and error label together."""

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
        self.error = getattr(self.input, "error", tk.StringVar())
        self.error_label = ttk.Label(self, textvariable=self.error)
        self.error_label.grid(row=2, column=0, sticky=WE)
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
            parent=record_info,
            label="Date",
            input_class=DateEntry,
            input_var=tk.StringVar(),
        ).grid(row=0, column=0)
        self.inputs["Time"] = LabelInput(
            parent=record_info,
            label="Time",
            input_class=ValidatedCombobox,
            input_var=tk.StringVar(),
            input_args={"values": ["8:00", "12:00", "16:00", "20:00"]},
        ).grid(row=0, column=1)
        self.inputs["Technician"] = LabelInput(
            parent=record_info,
            label="Technician",
            input_class=RequiredEntry,
            input_var=tk.StringVar(),
        ).grid(row=0, column=2)

        self.inputs["Lab"] = LabelInput(
            parent=record_info,
            label="Lab",
            input_class=ValidatedCombobox,
            input_var=tk.StringVar(),
            input_args={"values": ["A", "B", "C", "D", "E"]},
        ).grid(row=1, column=0)
        self.inputs["Plot"] = LabelInput(
            parent=record_info,
            label="Plot",
            input_class=ValidatedCombobox,
            input_var=tk.StringVar(),
            input_args={"values": [str(n) for n in range(1, 21)]},
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
            input_class=ValidatedSpinBox,
            input_var=tk.DoubleVar(),
            input_args={"from_": "0.5", "to": "52.0", "increment": "0.01"},
        ).grid(row=0, column=0)
        self.inputs["Light"] = LabelInput(
            parent=env_info,
            label="Light (klx)",
            input_class=ValidatedSpinBox,
            input_var=tk.DoubleVar(),
            input_args={"from_": "0", "to": "100", "increment": "0.1"},
        ).grid(row=0, column=1)
        self.inputs["Temperature"] = LabelInput(
            parent=env_info,
            label="Temperature (°C)",
            input_class=ValidatedSpinBox,
            input_var=tk.DoubleVar(),
            input_args={"from_": "4", "to": "40", "increment": "0.1"},
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
            input_class=ValidatedSpinBox,
            input_var=tk.IntVar(),
            input_args={"from_": "0", "to": "20"},
        ).grid(row=0, column=0)
        self.inputs["Blossoms"] = LabelInput(
            parent=plant_info,
            label="Blossoms",
            input_class=ValidatedSpinBox,
            input_var=tk.IntVar(),
            input_args={"from_": "0", "to": "1000"},
        ).grid(row=0, column=1)
        self.inputs["Fruit"] = LabelInput(
            parent=plant_info,
            label="Fruit",
            input_class=ValidatedSpinBox,
            input_var=tk.IntVar(),
            input_args={"from_": "0", "to": "1000"},
        ).grid(row=0, column=2)

        # Height data
        # create variables to be updated for min/max height
        # they can be referenced for min/max variables
        min_height_var = tk.DoubleVar(value="-infinity")
        max_height_var = tk.DoubleVar(value="infinity")
        self.inputs["Min Height (cm)"] = LabelInput(
            parent=plant_info,
            label="Min Height",
            input_class=ValidatedSpinBox,
            input_var=tk.DoubleVar(),
            input_args={
                "from_": "0",
                "to": "1000",
                "increment": "1",
                "max_var": max_height_var,
                "focus_update_var": min_height_var,
            },
        ).grid(row=1, column=0)
        self.inputs["Max Height (cm)"] = LabelInput(
            parent=plant_info,
            label="Max Height",
            input_class=ValidatedSpinBox,
            input_var=tk.DoubleVar(),
            input_args={
                "from_": "0",
                "to": "1000",
                "increment": "1",
                "min_var": min_height_var,
                "focus_update_var": max_height_var,
            },
        ).grid(row=1, column=1)
        self.inputs["Median Height"] = LabelInput(
            parent=plant_info,
            label="Median Height (cm)",
            input_class=ValidatedSpinBox,
            input_var=tk.DoubleVar(),
            input_args={
                "from_": "0",
                "to": "1000",
                "increment": "1",
                "min_var": min_height_var,
                "max_var": max_height_var,
            },
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
        self.inputs["Date"].set(date.today().isoformat())
        if plot in ("", plot_values[-1]):
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
        errors = {}
        for name, widget in self.inputs.items():
            if hasattr(widget.input, "trigger_focusout_validation"):
                widget.input.trigger_focusout_validation()
            if e := widget.error.get():
                errors[name] = e
        return errors


def main(args) -> None:
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    import sys

    main_rv = main(sys.argv)
    sys.exit(main_rv)
