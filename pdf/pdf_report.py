import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.baseClass import BasePDF
from app.helper import resource_path

try:
    from cStringIO import StringIO as BytesIO  # type: ignore
except ImportError:
    from io import BytesIO


PERIOD = ""


def get_script_folder() -> str:
    if getattr(sys, "frozen", False):
        script_path = os.path.dirname(sys.executable)
    else:
        script_path = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))
    return script_path


class FooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs) -> None:
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.width, self.height = LETTER

    def showPage(self) -> None:
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            if self._pageNumber > 1:
                self.draw_canvas(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_canvas(self, page_count) -> None:
        page = "Page %s of %s" % (str(self._pageNumber), str(page_count))
        footer_text = "PM Champion Cell 5"
        header_text = f"DH Report: {PERIOD}"
        x = 128
        self.saveState()
        self.setStrokeColorRGB(0, 0, 0)
        self.setLineWidth(0.5)

        self.drawImage(
            resource_path("assets/C5.png"),
            self.width - inch * 2,
            self.height - 40,
            width=100,
            height=30,
            preserveAspectRatio=True,
            mask="auto",
        )
        self.line(50, 740, LETTER[0] - 50, 740)
        self.line(50, 60, LETTER[0] - 50, 60)
        self.setFont("Times-Roman", 8)
        self.drawString(LETTER[0] - 530, self.height - 40, header_text)
        self.setFont("Times-Roman", 10)
        self.drawString(LETTER[0] - 530, 45, footer_text)
        self.drawString(LETTER[0] - x, 45, page)
        self.restoreState()


class DHReport(BasePDF):
    def __init__(self, path: str, dataframe: pd.DataFrame) -> None:
        self.path = path
        self.styleSheet = getSampleStyleSheet()
        self.elements = []
        self.df = dataframe
        df_date = pd.to_datetime(self.df["REPORTED AT"]).dt.strftime("%d-%m-%Y")

        global PERIOD
        PERIOD = f"{df_date.min()} to {df_date.max()}"

        # colors - Azul turkeza 367AB3
        self.colorOhkaGreen0 = Color((45.0 / 255), (166.0 / 255), (153.0 / 255), 1)
        self.colorOhkaGreen1 = Color((182.0 / 255), (227.0 / 255), (166.0 / 255), 1)
        self.colorOhkaGreen2 = Color((140.0 / 255), (222.0 / 255), (192.0 / 255), 1)
        # self.colorOhkaGreen2 = Color((140.0/255), (222.0/255), (192.0/255), 1)
        self.colorOhkaBlue0 = Color((54.0 / 255), (122.0 / 255), (179.0 / 255), 1)
        self.colorOhkaBlue1 = Color((122.0 / 255), (180.0 / 255), (225.0 / 255), 1)
        self.colorOhkaGreenLineas = Color((50.0 / 255), (140.0 / 255), (140.0 / 255), 1)

        self.firstPage()
        self.create_graph_contributor()
        self.create_graph_details()
        self.create_table_dh_open()

        # Build
        self.doc = SimpleDocTemplate(
            path,
            pagesize=LETTER,
            title="DH REPORT CELL 5",
            author="rardyant",
            subject="Simply report DH record use DIGI DH csv",
        )
        self.doc.multiBuild(self.elements, canvasmaker=FooterCanvas)

    def firstPage(self) -> None:
        psTitle = ParagraphStyle(
            "Resumen",
            fontSize=24,
            leading=14,
            justifyBreaks=1,
            alignment=TA_CENTER,
            justifyLastLine=1,
        )

        text = f"""DH REPORT CELL 5<br/>"""
        paragraphReportSummary = Paragraph(text, psTitle)
        self.elements.append(paragraphReportSummary)

        spacer = Spacer(30, 200)
        self.elements.append(spacer)

        img = Image(resource_path("assets/C5_logo.png"))
        img.drawHeight = 2 * inch
        img.drawWidth = 2 * inch
        self.elements.append(img)

        spacer = Spacer(10, 200)
        self.elements.append(spacer)

        psDetalle = ParagraphStyle(
            "Resumen",
            fontSize=12,
            leading=14,
            justifyBreaks=1,
            alignment=TA_CENTER,
            justifyLastLine=1,
        )
        link_up = ""
        list_lu = list(self.df["WORK CENTER TYPE"].unique())
        for i in range(len(list_lu)):
            link_up = f"{link_up},  {list_lu[i]}"

        df_date = self.df["REPORTED AT"].apply(lambda x: x.strftime("%d.%m.%Y"))
        df_date = pd.to_datetime(self.df["REPORTED AT"]).dt.strftime("%d-%m-%Y")
        period = f"{df_date.min()} to {df_date.max()}"

        text = f"""Work Center : {link_up.lstrip(", ")}<br/>
        Period : {period}<br/>
        """
        paragraphReportSummary = Paragraph(text, psDetalle)
        self.elements.append(paragraphReportSummary)
        self.elements.append(PageBreak())

    def nextPagesHeader(self, isSecondPage: bool) -> None:
        if isSecondPage:
            psHeaderText = ParagraphStyle(
                "Hed0",
                fontSize=16,
                alignment=TA_LEFT,
                borderWidth=3,
                textColor=self.colorOhkaGreen0,
            )
            text = "REPORTE DE SESIONES"
            paragraphReportHeader = Paragraph(text, psHeaderText)
            self.elements.append(paragraphReportHeader)

            spacer = Spacer(10, 10)
            self.elements.append(spacer)

            d = Drawing(500, 1)
            line = Line(-20, 0, 480, 0)
            line.strokeColor = self.colorOhkaGreenLineas
            line.strokeWidth = 2
            d.add(line)
            self.elements.append(d)

            spacer = Spacer(10, 1)
            self.elements.append(spacer)

            d = Drawing(500, 1)
            line = Line(-20, 0, 480, 0)
            line.strokeColor = self.colorOhkaGreenLineas
            line.strokeWidth = 0.5
            d.add(line)
            self.elements.append(d)

            spacer = Spacer(10, 22)
            self.elements.append(spacer)

    def create_graph_contributor(self) -> None:
        # self.elements.append(PageBreak())
        psHeaderText = ParagraphStyle(
            "Hed0",
            fontSize=12,
            alignment=TA_CENTER,
            borderWidth=3,
            textColor=self.colorOhkaBlue0,
        )
        text = "DH CELL 5"
        paragraphReportHeader = Paragraph(text, psHeaderText)
        # self.elements.append(paragraphReportHeader)

        # spacer = Spacer(5, 5)
        # self.elements.append(spacer)

        fig = plt.figure(figsize=(5, 6.5))

        fig.subplots_adjust(left=0.3, right=0.9, top=0.95, bottom=0.1, hspace=0.3)
        fig.set_figwidth(6)
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)

        ax1.barh(
            self.df["REPORTED BY"].value_counts(ascending=True).to_dict().keys(),
            self.df["REPORTED BY"].value_counts(ascending=True).to_dict().values(),
            height=0.4,
            align="center",
        )
        ax1.set_title("REPORTED BY")
        ax1.tick_params(axis="x", labelsize=6)
        ax1.tick_params(axis="y", labelsize=4)

        ax2.barh(
            self.df["CLOSED BY"].value_counts(ascending=True).to_dict().keys(),
            self.df["CLOSED BY"].value_counts(ascending=True).to_dict().values(),
            height=0.4,
            align="center",
        )
        ax2.set_title("CLOSED BY")
        ax2.tick_params(axis="x", labelsize=6)
        ax2.tick_params(axis="y", labelsize=4)

        imgdata = BytesIO()
        fig.savefig(imgdata, format="png", dpi=400)

        img = Image(imgdata)
        img.drawHeight = 220 * mm
        img.drawWidth = 180 * mm

        self.elements.append(img)

    def create_graph_details(self) -> None:
        self.elements.append(PageBreak())
        psHeaderText = ParagraphStyle(
            "Hed0",
            fontSize=12,
            alignment=TA_CENTER,
            borderWidth=3,
            textColor=self.colorOhkaBlue0,
        )
        text = "SESIONES EN SITIO"
        paragraphReportHeader = Paragraph(text, psHeaderText)
        # self.elements.append(paragraphReportHeader)

        # spacer = Spacer(5, 5)
        # self.elements.append(spacer)
        """
        Create the line items
        """

        fig = plt.figure()
        fig.subplots_adjust(
            left=0.15, right=0.9, top=0.95, bottom=0.11, hspace=0.7, wspace=0.3
        )
        fig.set_figwidth(5)
        fig.set_figheight(6.5)
        ax1 = fig.add_subplot(321)
        ax2 = fig.add_subplot(322)
        ax3 = fig.add_subplot(323)
        ax4 = fig.add_subplot(324)
        ax5 = fig.add_subplot(325)
        ax6 = fig.add_subplot(326)

        # axes 1
        df_cil = self.df[self.df["FOUND DURING"].isin(["CIL"])]
        ax1.bar(
            self.df["WORK CENTER TYPE"].value_counts(ascending=False).to_dict().keys(),
            self.df["WORK CENTER TYPE"]
            .value_counts(ascending=False)
            .to_dict()
            .values(),
        )
        ax1.set_title("DH FOUND")
        ax1.tick_params(axis="both", labelsize=6)
        ax1.tick_params(axis="x", labelsize=6, labelrotation=90)

        # axes 2
        df_cil = self.df[self.df["FOUND DURING"].isin(["CIL"])]
        ax2.bar(
            df_cil["WORK CENTER TYPE"].value_counts(ascending=False).to_dict().keys(),
            df_cil["WORK CENTER TYPE"].value_counts(ascending=False).to_dict().values(),
        )
        ax2.set_title("FOUND DURING CIL")
        ax2.tick_params(axis="both", labelsize=6)
        ax2.tick_params(axis="x", labelsize=6, labelrotation=90)

        # axes 3
        df_cil = self.df[self.df["FOUND DURING"].isin(["CIL"])]
        ax3.bar(
            self.df["STATUS"].value_counts(ascending=False).to_dict().keys(),
            self.df["STATUS"].value_counts(ascending=False).to_dict().values(),
        )
        ax3.set_title("DH STATUS")
        ax3.tick_params(axis="both", labelsize=6)
        ax3.tick_params(axis="x", labelsize=6, labelrotation=90)

        # axes 4
        df_high = self.df[self.df["PRIORITY"].isin(["HIGH"])]
        ax4.bar(
            df_high["WORK CENTER TYPE"].value_counts(ascending=False).to_dict().keys(),
            df_high["WORK CENTER TYPE"]
            .value_counts(ascending=False)
            .to_dict()
            .values(),
        )
        ax4.set_title("DH HIGH")
        ax4.tick_params(axis="both", labelsize=6)
        ax4.tick_params(axis="x", labelsize=6, labelrotation=90)

        # axes 5
        df_cil = self.df[self.df["STATUS"].isin(["OPEN"])]
        ax5.bar(
            df_cil["WORK CENTER TYPE"].value_counts(ascending=False).to_dict().keys(),
            df_cil["WORK CENTER TYPE"].value_counts(ascending=False).to_dict().values(),
        )
        ax5.set_title("DH OPEN")
        ax5.tick_params(axis="both", labelsize=6)
        ax5.tick_params(axis="x", labelsize=6, labelrotation=90)

        # axes 6
        df_high = self.df[self.df["PRIORITY"].isin(["HIGH"])]
        ax6.bar(
            self.df["MACHINE MODULE"].value_counts(ascending=False).to_dict().keys(),
            self.df["MACHINE MODULE"].value_counts(ascending=False).to_dict().values(),
        )
        ax6.set_title("DH BY MACHINE")
        ax6.tick_params(axis="both", labelsize=6)
        ax6.tick_params(axis="x", labelsize=6, labelrotation=90)

        imgdata = BytesIO()
        fig.savefig(imgdata, format="png", dpi=400)
        img = Image(imgdata)
        img.drawHeight = 220 * mm
        img.drawWidth = 180 * mm

        self.elements.append(img)

    def create_table_dh_open(self) -> None:
        self.elements.append(PageBreak())
        psHeaderText = ParagraphStyle(
            "Hed0",
            fontSize=12,
            alignment=TA_LEFT,
            borderWidth=3,
            textColor=self.colorOhkaBlue0,
        )
        text = "TABLE DH OPEN"
        paragraphReportHeader = Paragraph(text, psHeaderText)
        self.elements.append(paragraphReportHeader)

        spacer = Spacer(10, 22)
        self.elements.append(spacer)
        """
        Create the line items
        """
        d = []
        df_open = self.df[self.df["STATUS"].isin(["OPEN"])]
        df_report = df_open[
            [
                "NUMBER",
                "STATUS",
                "WORK CENTER TYPE",
                "PRIORITY",
                # "FOUND DURING",
                "DESCRIPTION",
            ]
        ]

        textData = df_report.columns.to_list()

        fontSize = 8
        centered = ParagraphStyle(name="centered", alignment=TA_CENTER)
        for text in textData:
            ptext = "<font size='%s'><b>%s</b></font>" % (str(fontSize), str(text))
            titlesTable = Paragraph(ptext, centered)
            d.append(titlesTable)

        alignStyle = [
            ParagraphStyle(name="01", alignment=TA_LEFT),
            ParagraphStyle(name="02", alignment=TA_LEFT),
            ParagraphStyle(name="03", alignment=TA_LEFT),
            ParagraphStyle(name="04", alignment=TA_LEFT),
            ParagraphStyle(name="05", alignment=TA_LEFT),
        ]

        data = [d]
        lineNum = 1
        formattedLineData = []
        df_value = df_report.values.tolist()
        for i in range(len(df_value)):
            columnNumber = 0
            for item in df_value[i]:
                ptext = "<font size='%s'>%s</font>" % (str(fontSize - 1), str(item))
                p = Paragraph(ptext, alignStyle[columnNumber])
                formattedLineData.append(p)
                columnNumber = columnNumber + 1
            data.append(formattedLineData)
            formattedLineData = []

        table = Table(data, colWidths=[55, 50, 70, 55, 260])
        tStyle = TableStyle(
            [  # ('GRID',(0, 0), (-1, -1), 0.5, grey),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ("LINEABOVE", (0, 0), (-1, -1), 1, self.colorOhkaBlue1),
                ("BACKGROUND", (0, 0), (-1, 0), self.colorOhkaGreenLineas),
                # ("BACKGROUND", (0, -1), (-1, -1), self.colorOhkaBlue1),
                # ("SPAN", (0, -1), (-2, -1)),
            ]
        )
        table.setStyle(tStyle)
        self.elements.append(table)


def main(path: str, dataframe: pd.DataFrame) -> None:
    DHReport(path, dataframe)


if __name__ == "__main__":
    from app.helper import get_concate_df

    df = get_concate_df(
        [r"C:\Users\USER\Downloads\DH_2024-07-29_11-39_Maker12_Packer12.csv"]
    )
    path_file = "test.pdf"
    main(path_file, df)
