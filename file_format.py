#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2020/6/13 10:04 AM
@author: nzhang
"""

from datetime import datetime
import sys
import pandas as pd
import numpy as np
import streamlit as st
import base64

st.title('标签数据处理')

file_type = st.sidebar.selectbox(
    "呦吼，选择下上传文件的类型",
    ("csv", "xlsx")
)

file_path = st.file_uploader("赶快上传文件吧！", type=file_type)


def read_data(file_path, file_type):
    if file_type == "csv":
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    return df


if file_path:
    df = read_data(file_path, file_type)
    st.write(df)
    st.write("样本量", df.shape[0])

    device_cols = st.multiselect("选择设备列", list(df.columns))

    date_col = st.selectbox("选择日期列", list(df.columns))

    date_format = st.selectbox("日期格式", ["%Y-%m-%d", "%Y%m%d"])
    try:
        df[date_col] = pd.to_datetime(df[date_col], format=date_format)
        st.write("起始日期：", df[date_col].min())
        st.write("结束日期：", df[date_col].max())
        df[date_col] = df[date_col].map(lambda s: datetime.strftime(s, "%Y-%m-%d"))

        col_names = device_cols + [date_col]
        data = df[col_names]
        if len(device_cols) == 2:
            data["device_id"] = np.where(
                data[device_cols[0]].notna(),
                data[device_cols[0]],
                data[device_cols[1]]
            )
        else:
            data["device_id"] = df[device_cols]

        rst = data[["device_id", date_col]]
        rst = rst[rst["device_id"].notna()]
        rst["device_id"] = rst["device_id"].apply(str)
        st.write(rst)
        st.write("有效样本数量", rst.shape[0])

    except ValueError:
        st.error("请确认日期列及其格式")


    def get_table_download_link(df):
        """Generates a link allowing the data in a given panda dataframe to be downloaded
        in:  dataframe
        out: href string
        """
        csv = df.to_csv(index=False, sep="\t")
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
        return href

    st.markdown(get_table_download_link(rst), unsafe_allow_html=True)