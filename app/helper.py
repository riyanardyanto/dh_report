import os
import sys

import pandas as pd


def get_concate_df(text: str) -> pd.DataFrame:
    df_list = []
    for i in range(len(text)):
        df_list.append(pd.read_csv(text[i]))
    df = pd.DataFrame()
    for i in range(len(df_list)):
        df = pd.concat([df, df_list[i]], ignore_index=True)

    df["REPORTED AT"] = pd.to_datetime(df["REPORTED AT"], dayfirst=True)
    df["CLOSED AT"] = pd.to_datetime(df["CLOSED AT"], dayfirst=True)

    return df.reset_index()


def createDHReport(df: pd.DataFrame):
    link_up = ""
    list_lu = list(df["WORK CENTER TYPE"].unique())
    for i in range(len(list_lu)):
        link_up = f"{link_up},  {list_lu[i]}"

    df_date = pd.to_datetime(df["REPORTED AT"], dayfirst=True).dt.strftime("%d-%m-%Y")
    period = f"*DH {df_date.min()} to {df_date.max()}*"

    total_found = len(df["WORK CENTER TYPE"])
    DH_found = df.groupby(["WORK CENTER TYPE"]).size().reset_index()
    DH_found.rename(
        columns={"WORK CENTER TYPE": "WORK CENTER", 0: "FOUND"}, inplace=True
    )

    def get_detail_DH(df: pd.DataFrame, value: str):
        DH_detail = df.groupby(["WORK CENTER TYPE"]).size().reset_index()
        DH_detail.rename(
            columns={"WORK CENTER TYPE": "WORK CENTER", 0: value}, inplace=True
        )
        return f"`{str(DH_detail.to_markdown(tablefmt='pipe', index=False)).replace('\n', '`\n`')}`"

    # DH FOUND
    df_total = df
    total_found = len(df_total)
    detail_found = get_detail_DH(df_total, " FOUND")

    # DH FOUND DURING CIL
    df_cil = df.loc[df["FOUND DURING"].isin(["CIL"])]
    total_found_cil = len(df_cil)
    detail_found_cil = get_detail_DH(df_cil, "   CIL")

    # DH FIX (CLOSED)
    df_close = df.loc[df["STATUS"].isin(["CLOSED"])]
    total_close = len(df_close)
    detail_close = get_detail_DH(df_close, "CLOSED")

    # DH SOC
    df_soc = df.loc[df["DEFECT TYPES"].str.contains("SOURCE_OF_CONTAMINATION")]
    total_soc = len(df_soc)
    # for item in df["DEFECT TYPES"].values.tolist():
    #     if "SOURCE_OF_CONTAMINATION" in item:
    #         total_soc += 1
    detail_soc = get_detail_DH(df_soc, "DH SOC")

    # open
    is_exist = False
    try:
        df_open = df.loc[df["STATUS"].isin(["OPEN"])][
            ["NUMBER", "DESCRIPTION", "PRIORITY"]
        ]

        li_val = df_open.values.tolist()
        data_open = []
        for i in range(len(li_val)):
            a = f"""{1 + i}. {li_val[i][0]}: {li_val[i][1]}\n"""
            data_open.append(a)
        str_open = ""
        for i in range(len(data_open)):
            str_open = str_open + data_open[i]
    except:
        str_open = ""

    # high
    try:
        df_high = df.loc[df["PRIORITY"].isin(["HIGH"])][
            ["NUMBER", "DESCRIPTION", "STATUS", "DEFECT COUNTERMEASURES"]
        ]

        li_val = df_high.values.tolist()
        data_high = []
        for i in range(len(li_val)):
            a = f"""{1 + i}. {li_val[i][0]}: {li_val[i][1]}\n- Status : {li_val[i][2]}\n- CM      : {li_val[i][3]}\n\n"""
            data_high.append(a)
        str_high = ""
        for i in range(len(data_high)):
            str_high = str_high + data_high[i]
    except:
        str_high = ""

    return f"{period}\n\n*DH FOUND DURING CIL*: {total_found_cil}\n{detail_found_cil}\n\n*DH FOUND*: {total_found}\n{detail_found}\n\n*DH FIX (CLOSED)*: {total_close}\n{detail_close}\n\n*DH SOC*: {total_soc}\n{detail_soc}\n\n**DH OPEN*: {len(data_open)}\n{str_open}\n*DH HIGH*: {len(data_high)}\n{str_high}"


def createText(df: pd.DataFrame) -> str:
    link_up = ""
    list_lu = list(df["WORK CENTER TYPE"].unique())
    for i in range(len(list_lu)):
        link_up = f"{link_up},  {list_lu[i]}"

    df_date = pd.to_datetime(df["REPORTED AT"]).dt.strftime("%d-%m-%Y")
    period = f"{df_date.min()} to {df_date.max()}"

    fhead = f"DH {period} {link_up}"
    lu = str(list(df["LINE"])[0])
    maker = ["Maker " + lu]
    packer = ["Packer " + lu]
    high = ["HIGH"]
    status_open = ["OPEN"]

    def get_main(dataframe: pd.DataFrame, col: str, val: str):
        try:
            return dataframe[col].value_counts()[val]
        except:
            return 0

    main_data = [
        len(df),
        get_main(df, "FOUND DURING", "CIL"),
        get_main(df, "STATUS", "CLOSED"),
        get_main(df, "PRIORITY", "HIGH"),
    ]

    # maker
    is_exist = False
    try:
        df_maker = df.loc[df["WORK CENTER TYPE"].isin(maker)]
        is_exist = True
    except:
        pass

    if is_exist:
        data_maker = [
            len(df_maker),
            get_main(df_maker, "FOUND DURING", "CIL"),
            get_main(df_maker, "STATUS", "CLOSED"),
        ]
    else:
        data_maker = [0, 0, 0]

    # packer
    is_exist = False
    try:
        df_packer = df.loc[df["WORK CENTER TYPE"].isin(packer)]
        is_exist = True
    except:
        pass

    if is_exist:
        data_packer = [
            len(df_packer),
            get_main(df_packer, "FOUND DURING", "CIL"),
            get_main(df_packer, "STATUS", "CLOSED"),
        ]
    else:
        data_packer = [0, 0, 0]

    # open
    is_exist = False
    try:
        df_open = df.loc[df["STATUS"].isin(status_open)][
            ["NUMBER", "DESCRIPTION", "PRIORITY"]
        ]

        li_val = df_open.values.tolist()
        data_open = []
        for i in range(len(li_val)):
            a = f"""{1 + i}. {li_val[i][0]}: {li_val[i][1]}\n"""
            data_open.append(a)
        str_open = ""
        for i in range(len(data_open)):
            str_open = str_open + data_open[i]
    except:
        str_open = ""

    # high
    try:
        df_high = df.loc[df["PRIORITY"].isin(high)][
            ["NUMBER", "DESCRIPTION", "STATUS", "DEFECT COUNTERMEASURES"]
        ]

        li_val = df_high.values.tolist()
        data_high = []
        for i in range(len(li_val)):
            a = f"""{1 + i}. {li_val[i][0]}: {li_val[i][1]}\n- Status : {li_val[i][2]}\n- CM      : {li_val[i][3]}\n\n"""
            data_high.append(a)
        str_high = ""
        for i in range(len(data_high)):
            str_high = str_high + data_high[i]
    except:
        str_high = ""

    txt_to_file = f"""*{fhead}*\n> DH FOUND: {data_maker[0] + data_packer[0]}\n- Maker : {data_maker[0]}\n- Packer: {data_packer[0]}\n\n> DH FOUND DURING CIL: {data_maker[1] + data_packer[1]}\n- Maker : {data_maker[1]}\n- Packer: {data_packer[1]}\n\n> DH FIX (CLOSED): {data_maker[2] + data_packer[2]}\n- Maker : {data_maker[2]}\n- Packer: {data_packer[2]}\n\n> DH OPEN: {len(data_open)}\n{str_open}\n> DH HIGH: {main_data[3]}\n{str_high}"""

    return txt_to_file


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller"""

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
