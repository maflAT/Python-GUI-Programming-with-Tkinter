import os
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.font import nametofont
from tempfile import mkdtemp
from datetime import date
from queue import Queue

from . import models as m
from . import network as n
from . import views as v
from .images import ABQ_LOGO_32, ABQ_LOGO_64
from .mainmenu import get_main_menu_for_os


class Application(tk.Tk):
    """Application root window"""

    config_dirs = {
        "Linux": os.environ.get("$XDG_CONFIG_HOME", "~/.config"),
        "freebsd7": os.environ.get("$XDG_CONFIG_HOME", "~/.config"),
        "Darwin": "~/Library/Application Support",
        "Windows": "~/AppData/Local",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # hide main window while initialization isn't completed
        self.withdraw()

        # init settings
        config_dir = self.config_dirs.get(platform.system(), "~")
        self.settings_model = m.SettingsModel(path=config_dir)
        self.load_settings()
        default_filename = f"abq_data_record_{date.today().isoformat()}.csv"
        self.filename = tk.StringVar(value=default_filename)

        # main window styling
        self.resizable(width=False, height=False)
        self.title("ABQ Data Entry Application")
        self.taskbar_icon = tk.PhotoImage(file=ABQ_LOGO_64)
        self.call("wm", "iconphoto", self._w, self.taskbar_icon)

        # init data model
        self.database_login()
        if not hasattr(self, "data_model"):
            self.destroy()
            return

        # callbacks
        self.callbacks = {
            "file->select": self.on_file_select,
            "file->quit": self.quit,
            "show_recordlist": self.show_recordlist,
            "new_record": self.open_record,
            "on_open_record": self.open_record,
            "on_save": self.on_save,
            "get_seed_sample": self.get_current_seed_sample,
            "get_check_tech": self.get_tech_for_lab_check,
            "update_weather_data": self.update_weather_data,
            "upload_to_corporate_rest": self.upload_to_corporate_rest,
            "upload_to_corporate_ftp": self.upload_to_corporate_ftp,
            "show_growth_chart": self.show_growth_chart,
        }

        # set global theme
        style = ttk.Style()
        theme = self.settings.get("theme").get()
        if theme in style.theme_names():
            style.theme_use(theme)

        # set global fonts
        self.set_font()
        self.settings["font size"].trace("w", self.set_font)

        # top level widgets
        #   main menu
        menu_class = get_main_menu_for_os(platform.system())
        menu = menu_class(self, settings=self.settings, callbacks=self.callbacks)
        self.config(menu=menu)

        #   logo / header
        self.logo = tk.PhotoImage(file=ABQ_LOGO_32)
        tk.Label(self, image=self.logo).grid(row=0)

        #   record form
        self.record_form = v.DataRecordForm(
            self,
            fields=self.data_model.fields,
            settings=self.settings,
            callbacks=self.callbacks,
        )
        self.record_form.grid(row=1, padx=10, sticky=tk.NSEW)

        #   record list
        self.inserted_rows: list[int] = []
        self.updated_rows: list[int] = []
        self.record_list = v.RecordList(
            self, self.callbacks, self.inserted_rows, self.updated_rows
        )
        self.record_list.grid(row=1, padx=10, sticky=tk.NSEW)
        self.populate_recordlist()

        # status bar
        self.status = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status)
        self.status_bar.grid(sticky=tk.EW, row=2, padx=10)
        self.records_saved = 0

        # show main window
        self.deiconify()

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
        try:
            self.data_model.save_record(data)
        except Exception as e:
            messagebox.showerror(
                title="Error", message="Problem saving record", detail=str(e)
            )
            self.status.set("Problem saving record")
        else:
            self.records_saved += 1
            self.status.set(f"{self.records_saved} records saved this session.")
        key = (data["Date"], data["Time"], data["Lab"], data["Plot"])
        if self.data_model.last_write == "update":
            self.updated_rows.append(key)
        else:
            self.inserted_rows.append(key)
        self.populate_recordlist()
        if self.data_model.last_write == "insert":
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

    def open_record(self, rowkey=None):
        if rowkey is None:
            record = None
        else:
            try:
                record = self.data_model.get_record(*rowkey)
            except Exception as e:
                messagebox.showerror(
                    title="Error", message="Problem reading file", detail=str(e)
                )
                return
        self.record_form.load_record(rowkey, data=record)
        self.record_form.tkraise()

    def set_font(self, *args):
        font_size = self.settings["font size"].get()
        font_names = ("TkDefaultFont", "TkMenuFont", "TkTextFont")
        for font in font_names:
            tk_font = nametofont(font)
            tk_font.config(size=font_size)

    def database_login(self):
        db_host = self.settings["db_host"].get()
        db_name = self.settings["db_name"].get()
        title = f"Login to {db_name} at {db_host}"
        error = ""

        while True:
            login = v.LoginDialog(self, title, error)
            if not login.result:
                break
            username, password = login.result
            try:
                self.data_model = m.SQLModel(db_host, db_name, username, password)
            except m.pg.OperationalError:
                error = "Login Failed"
            else:
                break

    def get_current_seed_sample(self, *args):
        if not (
            hasattr(self, "record_form") and self.settings["autofill sheet data"].get()
        ):
            return
        data = self.record_form.get()
        plot = data["Plot"]
        lab = data["Lab"]
        if plot and lab:
            seed = self.data_model.get_current_seed_sample(lab, plot)
            self.record_form.inputs["Seed sample"].set(seed)
            self.record_form.focus_next_empty()

    def get_tech_for_lab_check(self, *args):
        if not (
            hasattr(self, "record_form") and self.settings["autofill sheet data"].get()
        ):
            return
        data = self.record_form.get()
        date = data["Date"]
        time = data["Time"]
        lab = data["Lab"]
        if all([date, time, lab]):
            check = self.data_model.get_lab_check(date, time, lab)
            tech = check["lab_tech"] if check else ""
            self.record_form.inputs["Technician"].set(tech)
            self.record_form.focus_next_empty()

    #####################
    # Weather functions #
    #####################

    def update_weather_data(self):
        """Download weather data and store it in our data model."""
        try:
            weather_data = n.get_local_weather(self.settings["weather_station"].get())
        except Exception as e:
            messagebox.showerror(
                title="Error",
                message="Problem retrieving weather data",
                detail=str(e),
            )
            self.status.set("Problem retrieving weather data")
        else:
            self.data_model.add_weather_data(weather_data)
            self.status.set(
                f"Weather data recorded for {weather_data['observation_time_rfc822']}"
            )

    ##########################
    # Data upload functions: #
    ##########################

    def _create_csv_extract(self):
        tmpfilepath = mkdtemp()
        csvmodel = m.CSVModel(filename=self.filename.get(), filepath=tmpfilepath)
        records = self.data_model.get_all_records()
        if not records:
            return None
        for record in records:
            csvmodel.save_record(record)
        return csvmodel.filename

    def upload_to_corporate_rest(self):
        csvfile = self._create_csv_extract()
        if csvfile is None:
            messagebox.showwarning(
                title="No records",
                message="There are noe records to upload",
            )
            return
        d = v.LoginDialog(self, "Login to ABQ Corporate REST API")
        if not d.result:
            return
        username, password = d.result
        self.rest_queue = Queue()
        self.uploader = n.CorporateRestUploaderWithQueue(
            filepath=csvfile,
            upload_url=self.settings["abq_upload_url"].get(),
            auth_url=self.settings["abq_auth_url"].get(),
            username=username,
            password=password,
            queue=self.rest_queue,
        )
        self.uploader.start()
        self.check_queue(self.rest_queue)

    def upload_to_corporate_ftp(self):
        """Upload CSV records to corporate ftp server."""
        csvfile = self._create_csv_extract()
        d = v.LoginDialog(parent=self, title="Login to ABQ Corporate FTP server")
        if d.result is not None:
            username, password = d.result
            try:
                n.upload_to_corporate_ftp(
                    filepath=csvfile,
                    ftp_host=self.settings["abq_ftp_host"].get(),
                    ftp_port=self.settings["abq_ftp_port"].get(),
                    ftp_user=username,
                    ftp_pass=password,
                )
            except n.ftp.all_errors as e:
                messagebox.showerror(title="Error connecting to ftp", message=str(e))
            else:
                messagebox.showinfo(
                    title="Success",
                    message=f"'{csvfile}' successfully uploaded to FTP server.",
                )

    def check_queue(self, queue: Queue):
        if not queue.empty():
            item: n.Message = queue.get()
            if item.status == "done":
                messagebox.showinfo(
                    title=item.status,
                    message=item.subject,
                    detail=item.body,
                )
                self.status.set(item.subject)
                return
            elif item.status == "error":
                messagebox.showerror(
                    title=item.status,
                    message=item.subject,
                    detail=item.body,
                )
                self.status.set(item.subject)
                return
            else:
                self.status.set(item.body)
        self.after(100, self.check_queue, queue)

    ###########################
    # Visualization functions #
    ###########################

    def show_growth_chart(self):
        data = self.data_model.get_growth_by_lab()
        max_x = max(x["day"] for x in data)
        max_y = max(x["avg_height"] for x in data)

        popup = tk.Toplevel()
        chart = v.LineChartView(
            popup,
            chart_width=600,
            chart_height=300,
            x_axis="day",
            y_axis="cm",
            max_x=max_x,
            max_y=max_y,
        )
        chart.pack(fill="both", expand=1)

        legend = {
            "A": "green",
            "B": "blue",
            "C": "cyan",
            "D": "yellow",
            "E": "purple",
        }
        chart.draw_legend(legend)
        for lab, color in legend.items():
            dataxy = [(x["day"], x["avg_height"]) for x in data if x["lab_id"] == lab]
            chart.plot_line(data=dataxy, color=color)
