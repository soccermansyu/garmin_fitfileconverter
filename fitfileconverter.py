#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import datetime
import os
import shutil
import csv
from pathlib import Path

import fitdecode
import pandas as pd
import plotly.express as px
import streamlit as st

current_dir = os.path.dirname(__file__)

def load_fit_tmp(path):
    """
    this is an only sample function
    load fit file and convert to dataframe
    you should change codes below for fit file structure that you expect
    """
#     list_record = []
#     with fitdecode.FitReader(path) as fit:
#         for frame in fit:
#             if isinstance(frame, fitdecode.records.FitDataMessage):
#                 if frame.name == "record":
#                     data = {}
#                     for field in frame.fields:
#                         data[field.name] = field.value
#                         data[field.name + '_units'] = field.units
#                     datas.append(data)
#     df = pd.DataFrame(datas)
#     return df

    datas = []
    with fitdecode.FitReader(path) as fit:
        for frame in fit:

            if isinstance(frame, fitdecode.FitDataMessage):
                if frame.name == 'record':
                    data = {}
                    for field in frame.fields:
                        data[field.name] = field.value
                        #data[field.name + '_units'] = field.units
                    datas.append(data)

# データクレンジング
    df = pd.DataFrame(datas)
    for del_name in df.columns:
        if "unknown" in del_name:
            df =  df.drop(del_name, axis=1)
        else:
            continue
    df = df.drop("position_lat", axis=1)
    df = df.drop("position_long", axis=1)
    df = df.drop("fractional_cadence", axis=1)
    df = df.dropna(how="any")
    df = df.rename(columns={
        'timestamp': '時刻',
        'distance': '累積距離[m]',
        'accumulated_power': 'パワー累積[W]',
        'enhanced_speed': '速度[m/s]',
        'enhanced_altitude': '高度[m]',
        'stance_time':'接地時間[ms]',
        'power': 'パワー[W]',
        'stance_time_balance': '接地バランス(左)[%]',
        'vertical_oscillation': '上下動[m]',
        'stance_time_percent': '接地時間%',
        'vertical_ratio': '上下動率[%]',
        'step_length': 'ストライド[m]',
        'heart_rate': '心拍数[bpm]',
        'cadence': 'ピッチ[歩/分]',
        'temperature': '気温[℃]',
        'activity_type': 'アクティビティタイプ'
    })
    df['ピッチ[歩/分]'] *= 2
    df["時刻"] = pd.to_datetime(df["時刻"]).dt.tz_convert('Asia/Tokyo').astype(str).str[:19]

    if '接地バランス(左)[%]' in df.columns:
        df['接地バランス(右)[%]'] = 100 - df['接地バランス(左)[%]']
        df['上下動[m]'] = df['上下動[m]'] / 1000
        df['ストライド[m]'] = df['ストライド[m]'] / 1000
    
    return df
        
@st.cache
def convert_df(df):
    """
    convert df to csv
    """
    return df.to_csv(index=False).encode('cp932')


def calc_tmp(df):
    """
    this is an only sample function
    you should define process for your purpose
    """
    df = df.loc[0:, :]
    return df

# explanation
# st.title("ガーミン .Fitファイルを.CSV形式へ変換する")
# st.markdown("# アプリケーションの使い方")
# st.markdown("""
# １． ガーミンのランニングウォッチとPCを充電用ケーブルで接続\n
# ２． 「Activity」フォルダから、変換したい.Fitファイルを確認\n
# ３． 以下2通りのどちらかの方法でFitファイルをアップロードする\n
#  - 本アプリケーションのBrowse filesをクリックし変換したいファイルを選択
#  - 変換したいFIｔファイルをドラッグ&ドロップする
# ４． ファイルをアップロードすると変換処理が行われる。少し待機します。\n
# ５． 変換が完了するとDownloadボタンが現れる\n
# ６． Downloadボタンを押してCSVファイルをダウンロードする\n
# ７． PCのダウンロードフォルダにCSVファイルが保存されている\n
# """)

# st.markdown("# アプリケーションについての要望・改善等")
# st.markdown("""
# 本アプリケーションについて、動作不良や要望事項等がありましたら、\n
# 以下リンク先「ランニングを科学する」お問い合わせページから\n
# お問い合わせください。\n
# https://shuichi-running.com/contact/\n
# お待ちしております。\n
# """)

# upload .fit file
uploaded_file = st.file_uploader("upload your .fit file")
if uploaded_file is not None:
    # set path
    data_directory_path = Path(current_dir, "data")
    file_path = Path(data_directory_path, uploaded_file.name)

    # make data directory
    if data_directory_path.exists():
        shutil.rmtree(data_directory_path)
    os.makedirs(data_directory_path)

    # export .file to data directory
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # load fit file and convert to dataframe
    df = load_fit_tmp(file_path)

    # data processing
    df = calc_tmp(df)


    # convert df to csv
    csv = convert_df(df)

    # download
    st.download_button(
        label="Download",
        data=csv,
        file_name='activity_converted.csv',
        mime='text/csv',
    )

