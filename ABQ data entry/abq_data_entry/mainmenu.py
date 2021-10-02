import tkinter as tk
from functools import partial
from tkinter import messagebox, ttk
from typing import Callable


class GenericMainMenu(tk.Menu):
    def __init__(
        self,
        parent,
        settings: dict[str, tk.Variable],
        callbacks: dict[str, Callable],
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self.settings = settings
        self.callbacks = callbacks
        self._build_menu()
        self._bind_accelerators()

    def _build_menu(self):
        # file menu
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(
            label="Quit", command=self.callbacks["file->quit"], accelerator="Ctrl+Q"
        )
        self.add_cascade(label="File", menu=file_menu)

        # options menu
        options_menu = tk.Menu(self, tearoff=False)
        options_menu.add_checkbutton(
            label="Autofill Date", variable=self.settings["autofill date"]
        )
        options_menu.add_checkbutton(
            label="Autofill Sheet data", variable=self.settings["autofill sheet data"]
        )
        #   font size sub-menu
        font_size_menu = tk.Menu(self, tearoff=False)
        for size in range(6, 17):
            font_size_menu.add_radiobutton(
                label=size, value=size, variable=self.settings["font size"]
            )
        options_menu.add_cascade(label="Font size", menu=font_size_menu)

        #   theme selection sub-menu
        themes_menu = tk.Menu(self, tearoff=False)
        for theme in ttk.Style().theme_names():
            themes_menu.add_radiobutton(
                label=theme,
                value=theme,
                variable=self.settings["theme"],
            )
        options_menu.add_cascade(label="Theme", menu=themes_menu)
        self.settings["theme"].trace("w", self.on_theme_change)
        self.add_cascade(label="Options", menu=options_menu)

        # go menu
        go_menu = tk.Menu(self, tearoff=False)
        go_menu.add_command(
            label="Record List",
            command=self.callbacks["show_recordlist"],
            accelerator="Ctrl+L",
        )
        go_menu.add_command(
            label="New Record",
            command=self.callbacks["new_record"],
            accelerator="Ctrl+N",
        )
        self.add_cascade(label="Go", menu=go_menu)

        # tools menu
        tools_menu = tk.Menu(self, tearoff=False)
        tools_menu.add_command(
            label="Update weather Data", command=self.callbacks["'update_weather_data'"]
        )
        self.add_cascade(label="Tools", menu=tools_menu)

        # help menu
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about)
        self.add_cascade(label="Help", menu=help_menu)

    def show_about(self):
        """Show the about dialog"""
        about_message = "ABQ Data Entry"
        about_detail = "by Alan D Moore\nFor assistance please contact the author."
        messagebox.showinfo(title="About", message=about_message, detail=about_detail)

    def on_theme_change(self, *args):
        """Popup a message about theme changes"""
        message = "Change requires restart"
        detail = "Theme changes do not take effect until application resart"
        messagebox.showwarning(title="Warning", message=message, detail=detail)

    def get_keybinds(self):
        return {
            "<Control-o>": self.callbacks["file->select"],
            "<Control-q>": self.callbacks["file->quit"],
            "<Control-n>": self.callbacks["new_record"],
            "<Control-l>": self.callbacks["show_recordlist"],
        }

    def _bind_accelerators(self):
        keybinds = self.get_keybinds()
        for key, command in keybinds.items():
            self.bind_all(key, partial(self._argstrip, command))

    @staticmethod
    def _argstrip(function: Callable, *args):
        return function()


class WindowsMainMenu(GenericMainMenu):
    def _build_menu(self):
        # file menu
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label="Exit", command=self.callbacks["file->quit"])
        self.add_cascade(label="File", menu=file_menu)

        # tools menu
        tools_menu = tk.Menu(self, tearoff=False)
        tools_menu.add_command(
            label="Update weather Data", command=self.callbacks["update_weather_data"]
        )
        tools_menu.add_command(
            label="Upload CSV to corporate REST",
            command=self.callbacks["upload_to_corporate_rest"],
        )
        tools_menu.add_command(
            label="Upload CSV to corporate FTP",
            command=self.callbacks["upload_to_corporate_ftp"],
        )
        tools_menu.add_separator()
        #   options sub menu
        options_menu = tk.Menu(tools_menu, tearoff=False)
        options_menu.add_checkbutton(
            label="Autofill Date", variable=self.settings["autofill date"]
        )
        options_menu.add_checkbutton(
            label="Autofill Sheet data", variable=self.settings["autofill sheet data"]
        )
        #     font size sub-menu
        font_size_menu = tk.Menu(options_menu, tearoff=False)
        for size in range(6, 17):
            font_size_menu.add_radiobutton(
                label=size, value=size, variable=self.settings["font size"]
            )
        options_menu.add_cascade(label="Font size", menu=font_size_menu)
        #     theme selection sub-menu
        themes_menu = tk.Menu(options_menu, tearoff=False)
        for theme in ttk.Style().theme_names():
            themes_menu.add_radiobutton(
                label=theme,
                value=theme,
                variable=self.settings["theme"],
            )
        self.settings["theme"].trace("w", self.on_theme_change)
        options_menu.add_cascade(label="Theme", menu=themes_menu)
        tools_menu.add_cascade(label="Options", menu=options_menu)
        self.add_cascade(label="Tools", menu=tools_menu)

        # go to record list
        self.add_command(
            label="Record List",
            command=self.callbacks["show_recordlist"],
            accelerator="Ctrl+L",
        )

        # create new record
        self.add_command(
            label="New Record",
            command=self.callbacks["new_record"],
            accelerator="Ctrl+N",
        )

        # help menu
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about)
        self.add_cascade(label="Help", menu=help_menu)

    def get_keybinds(self):
        return {
            "<Control-o>": self.callbacks["file->select"],
            "<Control-n>": self.callbacks["new_record"],
            "<Control-l>": self.callbacks["show_recordlist"],
        }


class LinuxMainMenu(GenericMainMenu):
    def _build_menu(self):
        # file menu
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(
            label="Select file...",
            command=self.callbacks["file->select"],
            accelerator="Ctrl+O",
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Quit", command=self.callbacks["file->quit"], accelerator="Ctrl+Q"
        )
        self.add_cascade(label="File", menu=file_menu)

        # edit menu
        edit_menu = tk.Menu(self, tearoff=False)
        edit_menu.add_checkbutton(
            label="Autofill Date", variable=self.settings["autofill date"]
        )
        edit_menu.add_checkbutton(
            label="Autofill Sheet data", variable=self.settings["autofill sheet data"]
        )
        self.add_cascade(label="Edit", menu=edit_menu)

        # view menu
        view_menu = tk.Menu(self, tearoff=False)
        #   font size sub-menu
        font_size_menu = tk.Menu(view_menu, tearoff=False)
        for size in range(6, 17):
            font_size_menu.add_radiobutton(
                label=size, value=size, variable=self.settings["font size"]
            )
        view_menu.add_cascade(label="Font size", menu=font_size_menu)
        #   theme selection sub-menu
        themes_menu = tk.Menu(view_menu, tearoff=False)
        for theme in ttk.Style().theme_names():
            themes_menu.add_radiobutton(
                label=theme,
                value=theme,
                variable=self.settings["theme"],
            )
        self.settings["theme"].trace("w", self.on_theme_change)
        view_menu.add_cascade(label="Theme", menu=themes_menu)
        self.add_cascade(label="Options", menu=view_menu)

        # go menu
        go_menu = tk.Menu(self, tearoff=False)
        go_menu.add_command(
            label="Record List",
            command=self.callbacks["show_recordlist"],
            accelerator="Ctrl+L",
        )
        go_menu.add_command(
            label="New Record",
            command=self.callbacks["new_record"],
            accelerator="Ctrl+N",
        )
        self.add_cascade(label="Go", menu=go_menu)

        # help menu
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about)
        self.add_cascade(label="Help", menu=help_menu)


class MacOsMainMenu(GenericMainMenu):
    ...  # TODO


def get_main_menu_for_os(os_name):
    menus = {
        "Linux": LinuxMainMenu,
        "Darwin": MacOsMainMenu,
        "freebsd7": LinuxMainMenu,
        "Windows": WindowsMainMenu,
    }
    return menus.get(os_name, GenericMainMenu)
