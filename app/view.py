import matplotlib.pyplot as plt
import pandas as pd
import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ttkbootstrap.constants import *  # noqa: F403
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.toast import ToastNotification

from app.baseClass import CTRL
from app.helper import resource_path


class View(ttk.Window):
    head = [
        "NUMBER",
        "STATUS",
        "WORK CENTER TYPE",
        "PRIORITY",
        "DESCRIPTION",
        "FOUND DURING",
    ]
    value_table = []
    df_value = []

    def __init__(self, controller: CTRL) -> None:
        super().__init__(themename="superhero")
        self.controller = controller
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.title("DH Report")
        self.iconbitmap(resource_path("assets/C5.ico"))
        self.name = ttk.StringVar(value="")
        self.df = pd.DataFrame()
        self.file_name = ttk.StringVar(value="")
        self.file_folder = ttk.StringVar(value="")
        self.logo = ttk.PhotoImage(file=resource_path("assets/C5.png"))

        self._create_side_bar()
        self._create_main_frame()

    def _create_main_frame(self) -> None:
        self.home_frame = ttk.Frame(self)
        self.home_frame.grid(row=0, column=1, pady=(20, 10))

        browser_frame = ttk.Frame(self.home_frame)
        browser_frame.pack(side=TOP, fill=X, expand=YES, pady=5)

        btn_browse = ttk.Button(
            master=browser_frame,
            text="Browse File",
            command=self.controller.browse_file,
            bootstyle=PRIMARY,
            width=13,
        )
        btn_browse.pack(side=LEFT, padx=12)

        form_input = ttk.Entry(
            master=browser_frame, textvariable=self.file_name, font=("Consolas", 10)
        )
        form_input.pack(side=LEFT, padx=5, fill=X, expand=YES)

        self.content_frame = ttk.Frame(self.home_frame)
        self.content_frame.pack(side=TOP, fill=X, expand=YES, pady=5)

        self.table = self.create_table(head=self.head, df=self.value_table)
        self.table.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    def _create_side_bar(self) -> None:
        sidebar_frame = ttk.Frame(self, width=40)
        sidebar_frame.grid(row=0, column=0, sticky="NSW")

        hdr_label = ttk.Label(
            master=sidebar_frame,
            image=self.logo,
            bootstyle=(INVERSE, SECONDARY),
        )
        hdr_label.pack(side=TOP, padx=10, pady=(30, 10))

        btn_table = self.create_side_bar_btn(sidebar_frame, "TABLE")
        btn_table.configure(command=self.controller.btn_table_click)
        btn_table.pack(side=TOP, padx=10, pady=(30, 0))

        btn_dashboard = self.create_side_bar_btn(sidebar_frame, "DASHBOARD")
        btn_dashboard.configure(command=self.controller.btn_dashboard_click)
        btn_dashboard.pack(side=TOP, padx=10, pady=(30, 0))

        btn_report = self.create_side_bar_btn(sidebar_frame, "REPORT")
        btn_report.configure(command=self.controller.btn_report_click)
        btn_report.pack(side=TOP, padx=10, pady=(30, 0))

        btn_export = self.create_side_bar_btn(sidebar_frame, "EXPORT")
        btn_export.configure(command=self.controller.btn_export_click)
        btn_export.pack(side=TOP, padx=10, pady=(30, 0))

    def create_side_bar_btn(self, master, text: str) -> ttk.Button:
        btn = ttk.Button(
            master,
            text=text,
            bootstyle=PRIMARY,
            width=12,
        )
        return btn

    def create_table(self, head: list, df: list) -> Tableview:
        table = Tableview(
            master=self.content_frame,
            coldata=head,
            rowdata=df,
            paginated=False,
            searchable=True,
            bootstyle=DARK,
            autofit=True,
            height=20,
        )
        table.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        return table

    def create_dashboard(self) -> None:
        self.destroy_content_child()

        fig = plt.figure()
        fig.subplots_adjust(left=0.25, right=0.95, wspace=0.8)
        fig.set_figwidth(16)
        fig.set_dpi(70)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        ax1.barh(
            self.df["REPORTED BY"].value_counts(ascending=True).to_dict().keys(),
            self.df["REPORTED BY"].value_counts(ascending=True).to_dict().values(),
        )
        ax1.set_title("REPORTED BY")

        ax2.barh(
            self.df["CLOSED BY"].value_counts(ascending=True).to_dict().keys(),
            self.df["CLOSED BY"].value_counts(ascending=True).to_dict().values(),
        )
        ax2.set_title("CLOSED BY")

        # Chart 3: Bar chart of sales data
        fig2 = plt.figure()
        fig2.subplots_adjust(left=0.08, right=0.95, wspace=0.2, bottom=0.4)
        fig2.set_figwidth(16)
        fig2.set_dpi(70)
        ax3 = fig2.add_subplot(141)
        ax4 = fig2.add_subplot(142)
        ax5 = fig2.add_subplot(143)
        ax6 = fig2.add_subplot(144)

        df_cil = self.df[self.df["FOUND DURING"].isin(["CIL"])]
        ax3.bar(
            self.df["WORK CENTER TYPE"].value_counts(ascending=True).to_dict().keys(),
            self.df["WORK CENTER TYPE"].value_counts(ascending=True).to_dict().values(),
        )
        ax3.set_title("TOTAL DH FOUND")
        ax3.tick_params(axis="x", labelrotation=90)

        df_cil = self.df[self.df["FOUND DURING"].isin(["CIL"])]
        ax4.bar(
            df_cil["WORK CENTER TYPE"].value_counts(ascending=True).to_dict().keys(),
            df_cil["WORK CENTER TYPE"].value_counts(ascending=True).to_dict().values(),
        )
        ax4.set_title("FOUND DURING CIL")
        ax4.tick_params(axis="x", labelrotation=90)

        # Chart 5: Bar chart of sales data
        df_high = self.df[self.df["PRIORITY"].isin(["HIGH"])]
        ax5.bar(
            df_high["WORK CENTER TYPE"].value_counts(ascending=True).to_dict().keys(),
            df_high["WORK CENTER TYPE"].value_counts(ascending=True).to_dict().values(),
        )
        ax5.set_title("DH HIGH")
        ax5.tick_params(axis="x", labelrotation=90)

        # Chart 6: Bar chart of sales data
        df_cil = self.df[self.df["FOUND DURING"].isin(["CIL"])]
        ax6.bar(
            self.df["STATUS"].value_counts(ascending=True).to_dict().keys(),
            self.df["STATUS"].value_counts(ascending=True).to_dict().values(),
        )
        ax6.set_title("DH STATUS")
        ax6.tick_params(axis="x", labelrotation=90)

        upper_frame = ttk.Frame(self.content_frame)
        upper_frame.pack(side=TOP, fill="both", expand=True)

        canvas1 = FigureCanvasTkAgg(fig, upper_frame)
        canvas1.get_tk_widget().pack(side=LEFT, fill=X, expand=False, padx=10, pady=0)

        middle_frame = ttk.Frame(self.content_frame)
        middle_frame.pack(side=TOP, fill="both", expand=True)

        canvas3 = FigureCanvasTkAgg(fig2, middle_frame)
        canvas3.get_tk_widget().pack(side=LEFT, fill=Y, expand=False, padx=10, pady=0)

    def main(self) -> None:
        self.mainloop()

    def create_toast(self, message: str, bootstyle: str) -> ToastNotification:
        toast = ToastNotification(
            title="DH Report",
            message=message,
            bootstyle=bootstyle,
            duration=3000,
            alert=True,
            # position=(400, 300, "ne"),
        )
        toast.show_toast()

    def on_closing(self) -> None:
        # plt.close(self.fig)
        self.quit()

    def destroy_content_child(self) -> None:
        for child in self.content_frame.winfo_children():
            child.destroy()


if __name__ == "__main__":
    pass
