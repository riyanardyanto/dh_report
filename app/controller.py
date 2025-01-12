import os
from tkinter.filedialog import askopenfilenames

import customtkinter as ctk
import qrcode
import ttkbootstrap as ttk
from PIL import ImageTk
from ttkbootstrap.constants import *

from app.baseClass import CTRL
from app.helper import createDHReport, get_concate_df
from app.model import Model
from app.view import View


class Controller(CTRL):
    def __init__(self, path_file) -> None:
        self.model = Model()
        self.view = View(self)
        self.path_file = path_file

    def browse_file(self) -> None:
        try:
            text = askopenfilenames(
                title="Select file", filetypes=(("CSV Files", "*.csv"),)
            )
            self.view.file_folder = text[0].split(".")[0]
            self.view.file_name.set(value=text)
            self.view.df = get_concate_df(text)

            df_main = self.view.df[
                [
                    "NUMBER",
                    "STATUS",
                    "WORK CENTER TYPE",
                    "PRIORITY",
                    "DESCRIPTION",
                    "FOUND DURING",
                ]
            ]
            df_header = df_main.columns.to_list()
            self.view.df_value = df_main.values.tolist()
            # print(len(df_header))

            # head, val = get_df1(self.file_name.get())
            for child in self.view.content_frame.winfo_children():
                child.destroy()
            self.view.table = self.view.create_table(df_header, self.view.df_value)
        except Exception as e:
            self.view.create_toast(f"Error: {e}", WARNING)

    def btn_table_click(self) -> None:
        try:
            df_main = self.view.df[
                [
                    "NUMBER",
                    "STATUS",
                    "WORK CENTER TYPE",
                    "PRIORITY",
                    "DESCRIPTION",
                    "FOUND DURING",
                ]
            ]
            df_header = df_main.columns.to_list()
            df_value = df_main.values.tolist()

            for child in self.view.content_frame.winfo_children():
                child.destroy()
            self.table = self.view.create_table(df_header, df_value)
        except Exception as e:
            self.view.create_toast(f"Error: {e}", DANGER)

    def btn_dashboard_click(self) -> None:
        try:
            self.view.create_dashboard()
        except:
            self.view.create_toast("Error", DANGER)

    def btn_report_click(self) -> None:
        try:
            for child in self.view.content_frame.winfo_children():
                child.destroy()
            self.displayBox = ttk.Text(
                self.view.content_frame, width=100, height=30, font=("Consolas", 10)
            )
            self.displayBox.pack(side=LEFT, fill=X, expand=False, padx=(5, 5), pady=5)

            # QR Code
            self.qrLabel = ctk.CTkLabel(self.view.content_frame, text="")
            self.qrLabel.pack(side=LEFT, fill=X, expand=False, padx=(5, 5), pady=5)

            self.displayBox.delete("0.0", "200.0")
            text = self.view.file_name.get()
            # self.pathBox.insert("0.0", text)
            extract_text = createDHReport(self.view.df)
            self.displayBox.insert("0.0", extract_text)
            qr_img = self.generate_qr(extract_text)
            self.qrLabel.configure(image=qr_img)
        except Exception as e:
            self.view.create_toast(f"Error: {e}", DANGER)

    def btn_export_click(self) -> None:
        # x = askdirectory()
        mypath = os.path.join(self.path_file, "DH Report.pdf")
        import pdf.pdf_report as pdf_report

        try:
            # pdf_dh.PDFPSReporte(mypath, self.view.df)
            # self.view.df.to_csv(mypath)
            pdf_report.main(mypath, self.view.df)
            self.view.create_toast(f"Succesfully create PDF file \n{mypath}", SUCCESS)

        except Exception as e:
            self.view.create_toast(f"Error: {e}", DANGER)

    def generate_qr(self, text: str) -> ImageTk.PhotoImage:
        qr = qrcode.main.QRCode(box_size=10, border=5)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#252525", back_color="#f2bf2b")
        img = img.resize((300, 300))  # меняю размер чтобы красиво было
        img = ImageTk.PhotoImage(img)  # преобразуем в удобный формат
        return img

    def run(self) -> None:
        self.view.mainloop()
