# --- import modules start --- #
# import streamlit
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# import another modules
import json
import math
import os
import re

# import map visualization module
import folium
import geopandas as gpd
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# GIS modules
import networkx as nx

# import openai for GPT3.5
import openai
from openai.error import OpenAIError

# import osmnx
import osmnx as ox

# import data analysis modules
import pandas as pd
# import mongodb module
import pymongo

import requests
from src.database import *

# --- import modules end --- #

# func: initalize Session State
def initializeApp():
    st.session_state.sessionState = 1
    st.session_state.df_code = pd.read_csv('data/감염여부_코드.csv')
    st.session_state.df_hospital = pd.read_csv('data/hospital.csv')
    st.session_state.old_address = None
    st.session_state.gpt_answer = []

# func: read MongoDB
def readDB():
    if 'db' not in st.session_state:
        db = connectDB(st.secrets.DBPASS)
        st.session_state.db = db
    else:
        db = st.session_state.db
    
    return db

# func: read Data from Repository
def readData():
    db = readDB()

    if 'G' in st.session_state:
        G = st.session_state.G
    else:
        G = nx.Graph()
    
    for item in db.code_A.find():
        G = makeGraph(item, G)
    for item in db.code_B.find():
        G = makeGraph(item, G)

    st.session_state.G = G # 세션 저장

# func: make graph with NetworkX
def makeGraph(item, G):
    G.add_edge(item['firstCode'] + item['secondCode'] + item['thirdCode'] + item['fourthCode'], item['description'].split(', ')[2] + '|' + str(item['level']) + '|' + item['description'].split(', ')[3])
    return G

# func: get Department from Graph
def getDepartment(possible_departments:list):
    mergeCode = st.session_state.mergeCode
    if 'G' in st.session_state:
        G = st.session_state.G
        for node in G.nodes:
            if mergeCode in node:
                data = list(dict(G[node]).keys())
                return data[0]

# func: main UI
def main():
    # Streamlit App Setting
    db = readDB()
    openai.api_key = st.secrets.GPT_KEY

    # Title
    htmlTitle="""
    <!-- Font Awesome -->
    <link
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    rel="stylesheet"/>
    <!-- Google Fonts -->
    <link
    href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
    rel="stylesheet"/>
    <!-- MDB -->
    <link
    href="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/6.4.0/mdb.min.css"
    rel="stylesheet"/>
    <!-- MDB -->
    <script
    type="text/javascript"
    src="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/6.4.0/mdb.min.js"></script>
    <div class="container title">
        <p style="font-weight: 900; font-size: 30px;">C-ITS 응급환자이송지원시스템&nbsp;<span class="badge badge-primary">prototype</span></p>
        <p style="font-weight: 600; font-size: 20px; color: #242DFC">환자 정보 입력</p>
    </div>
    <style type="text/css">
        @font-face {
            font-family: 'Pretendard-Regular';
            src: url('https://cdn.jsdelivr.net/gh/Project-Noonnu/noonfonts_2107@1.1/Pretendard-Regular.woff') format('woff');
            font-weight: 400;
            font-style: normal;
        }
        .container {
            font-family: 'Pretendard-Regular';
        }
    </style>
    """
    st.markdown(htmlTitle, unsafe_allow_html=True)

    # 나이 선택
    age = st.selectbox(
        '환자의 나이를 골라주세요.',
        ('15세 이상의 성인', '15세 미만의 아동'))
    if age == '15세 이상의 성인':
        ageCode = 'A'
    else:
        ageCode = 'B'
    
    # step4
    step4 = st.text_input('증상의 키워드를 입력하세요.(여러개일 경우, 띄어쓰기로 구분)')

    if step4 != "" and ('oldStep' not in st.session_state or step4 != st.session_state.oldStep):
        st.session_state.gpt_answer = []
        step4 = step4.split(" ")
        st.session_state.oldStep = step4
        keyword = ""
        keyword = "|".join(step4)

        if ageCode == 'A':
            response = db.code_A.find({"description": {"$regex": keyword[1:-1], "$options": "i"}})
            st.session_state.response = response

        if ageCode == 'B':
            response = db.code_B.find({"description": {"$regex": keyword[1:-1], "$options": "i"}})
            st.session_state.response = response

        step3_list2 = []
        step3_list = []
        for key in response:
            step3_list.append(key)
            step3_list2.append(key['description'].split(', ')[2])

        # step3
        key = tuple(set(step3_list2))
        step3 = st.multiselect(
            '환자의 응급상황 정보를 선택해주세요.',
            (key))
        keyword2 = ""
        keyword2 = "|".join(step3)

        if step3 != []:
            with st.spinner('증상 도출 중...'):
                #step2
                step2_list = []
                for k in step3_list:
                    if re.findall(keyword2, k['description']) != []:
                        step2_list.append(k)

                # 진료과 도출
                if 'possible_departments' not in st.session_state:
                    st.session_state.possible_departments = []
                possible_departments = []
                for k in step2_list:
                    st.session_state.mergeCode = k['firstCode'] + k['secondCode'] + k['thirdCode'] + k['fourthCode']
                    possible_departments.append(getDepartment(possible_departments))
                st.session_state.possible_departments = set(possible_departments)

            # 진료과 출력
            html1 = """
                <div class="container">
                    <p>각 증상과 응급도 입니다.</p>
                    <p><small>*응급도는 1~5이며 1이 가장 응급 상황입니다.</small></p>
                </div>
                """
            st.write(html1, unsafe_allow_html=True)

            kindOfdepart = []
            html2 = "<table class='table'><thead><tr><th scope='col'>증상 종류</th><th scope='col'>상세 증상</th><th scope='col'>응급도 코드</th></tr></thead><tbody>"
            for i in st.session_state.possible_departments:
                kindOfdepart.append(i.split('|')[0] + '|' + i.split('|')[2])
                emerCode = int(i.split('|')[1])
                html2 += "<tr class='" + f"{'table-warning' if emerCode > 2 else 'table-danger'}"+"'>" + f"<th scope='row'>{i.split('|')[0]}</th><td>{i.split('|')[2]}</td><td>{i.split('|')[1]}</tr>"
        
            html2 += "</tbody></table>"
            st.write(html2, unsafe_allow_html=True)
            kindOfdepart = set(kindOfdepart)
            firstCodeOfDepart = []

            # GPT 진료과 도출
            gpt_answer = st.session_state.gpt_answer

            if gpt_answer == [] or gpt_answer[0] == "Error":
                with st.spinner('진료과 도출 중...'):
                    try:
                        model = "gpt-3.5-turbo"
                        j = 0
                        for i in kindOfdepart:
                            j += 1
                            if i.split('|')[0] not in firstCodeOfDepart:
                                firstCodeOfDepart.append(i.split('|')[0])
                                query = i.replace('|', ', ') + "증상이 있는 환자는 어느 과에서 진료를 받아야 해?"
                                messages = [
                                    {"role": "user", "content": query}
                                ]
                                response = None
                                response = openai.ChatCompletion.create(
                                    model="gpt-3.5-turbo",
                                    messages=messages
                                )
                                gpt_answer.append(response.choices[0].message.content)
                            if j == 3:
                                break
                    except OpenAIError as e:
                        st.write(e)
                        gpt_answer.append("Error")

            dep = []
            for g in gpt_answer:
                if g != "Error":
                    dep.append(re.compile(r'[가-힣]+과+').findall(g))

            dept = []
            for d in dep:
                dept.append(set(d))

            st.session_state.dept = dept

            # next button
            if st.button('적합한 병원 경로 확인하기'):
                switch_page("병원_최단_경로_도출")

if __name__ == "__main__":
    st.set_page_config(page_title="C-ITS", layout="wide")
    if 'sessionState' not in st.session_state: # 세션 코드가 없는 경우
        initializeApp() # 앱 초기화
    
    # Set Data
    if 'G' not in st.session_state or 'df_code' not in st.session_state or 'df_hospital' not in st.session_state: # 그래프, 감염여부 코드, 병원 정보 중 하나라도 없는 경우
        readData()
    df_code = st.session_state.df_code
    df_hospital = st.session_state.df_hospital

    main()
