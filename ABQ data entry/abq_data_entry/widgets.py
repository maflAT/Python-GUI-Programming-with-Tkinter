import tkinter as tk
from tkinter import ttk
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Optional
from .constants import EW, TkAction, TkEvent, FieldTypes as FT


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


class LabelInput(tk.Frame):
    """A widget containing a label, input and error label together."""

    field_types: dict[int, tuple[tk.Widget, Any]] = {
        FT.string: (RequiredEntry, tk.StringVar),
        FT.string_list: (ValidatedCombobox, tk.StringVar),
        FT.iso_date_string: (DateEntry, tk.StringVar),
        FT.long_string: (tk.Text, lambda: None),
        FT.decimal: (ValidatedSpinBox, tk.DoubleVar),
        FT.integer: (ValidatedSpinBox, tk.IntVar),
        FT.boolean: (ttk.Checkbutton, tk.BooleanVar),
    }

    def __init__(
        self,
        parent,
        label: str = "",
        input_class: tk.Widget = None,
        input_var=None,
        input_args: dict[str, Any] = None,
        label_args: dict[str, Any] = None,
        field_spec: dict[str, Any] = None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        input_args = input_args or {}
        label_args = label_args or {}
        if field_spec:
            field_type = field_spec.get("type", FT.string)
            input_class = input_class or self.field_types.get(field_type)[0]
            var_type = self.field_types.get(field_type)[1]
            self.variable = input_var or var_type()
            # min, max, increment
            if "min" in field_spec and "from_" not in input_args:
                input_args["from_"] = field_spec.get("min")
            if "max" in field_spec and "to" not in input_args:
                input_args["to"] = field_spec.get("max")
            if "inc" in field_spec and "increment" not in input_args:
                input_args["increment"] = field_spec.get("inc")
            # values
            if "values" in field_spec and "values" not in input_args:
                input_args["values"] = field_spec.get("values")
        else:
            self.variable = input_var
        if input_class in (ttk.Checkbutton, ttk.Button, ttk.Radiobutton):
            input_args["text"] = label
            input_args["variable"] = self.variable
        else:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=EW)
            input_args["textvariable"] = self.variable
        self.input: tk.Widget = input_class(self, **input_args)
        self.input.grid(row=1, column=0, sticky=EW)
        self.error = getattr(self.input, "error", tk.StringVar())
        self.error_label = ttk.Label(self, textvariable=self.error)
        self.error_label.grid(row=2, column=0, sticky=EW)
        self.columnconfigure(0, weight=1)

    def grid(self, sticky=EW, **kwargs):
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
        elif self.variable:
            self.variable.set(value, *args, **kwargs)
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
