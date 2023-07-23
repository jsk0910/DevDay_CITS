# --- import modules start ---
# import streamlit 
import streamlit as st
# import data analysis modules
import pandas as pd
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# import mongodb module
import pymongo

# import map visualization module
import folium

# GIS modules
import networkx as nx
import osmnx as ox
import geopandas as gpd

# import another modules
import json
import requests
import math

from src.database import *

# --- import modules end ---

# func: initalize Session State
def initializeApp():
  st.session_state.sessionState = 1
  st.session_state.G = nx.Graph()
  st.session_state.df_code = pd.read_csv('data/감염여부_코드.csv')
  st.session_state.df_hospital = pd.read_csv('data/hospital.csv')
  st.session_state.old_address = None

# func: read Data from Repository
def readData():
  if 'db' not in st.session_state:
    db = connectDB(st.secrets.DBPASS)
    st.session_state.db = db
  else:
    db = st.session_state.db
    
  G = nx.Graph()
  for item in db.code_A.find():
    G = makeGraph(item, G)
  for item in db.code_B.find():
    G = makeGraph(item, G)

  st.session_state.G = G # 세션 저장

  '''
  ## 데이터 불러오기
  df_A = pd.read_csv('data/응급환자_중증도_분류기준.csv', encoding='CP949')
  df_B = pd.read_csv('data/응급환자_중증도_분류기준B.csv')
  df_code = pd.read_csv('data/감염여부_코드.csv')
  df_hospital = pd.read_csv('data/hospital.csv')
  
  ## 데이터 전처리
  df_A.rename(columns={'2단계　': '2단계','Unnamed: 1': '2단계 코드', '3단계　': '3단계', 'Unnamed: 3': '3단계 코드', 'Unnamed: 5': '4단계 코드'}, inplace=True)
  df_A.replace('물질오용', '정신과, 신경과', inplace=True)
  df_A.replace('정신건강', '정신과', inplace=True)
  df_A.replace('코질환', '이비인후과', inplace=True)
  df_A.replace('귀질환', '이비인후과', inplace=True)
  df_A.replace('호흡기', '호흡기과, 흉부내과', inplace=True)
  df_A.replace('심혈관', '심장내과', inplace=True)
  df_A.replace('소화기', '소화기내과', inplace=True)
  df_A.replace('피부', '피부과', inplace=True)
  
  df_B.rename(columns={'2단계　': '2단계', 'Unnamed: 1': '2단계 코드', '3단계　': '3단계', 'Unnamed: 3': '3단계 코드', '4단계　': '4단계', 'Unnamed: 5': '4단계 코드'}, inplace=True)
  df_B.replace('물질오용', '정신과, 신경과', inplace=True)
  df_B.replace('정신건강', '정신과', inplace=True)
  df_B.replace('코질환', '이비인후과', inplace=True)
  df_B.replace('귀질환', '이비인후과', inplace=True)
  df_B.replace('호흡기', '호흡기과, 흉부내과', inplace=True)
  df_B.replace('심혈관', '심장내과', inplace=True)
  df_B.replace('소화기', '소화기내과', inplace=True)
  df_B.replace('피부', '피부과', inplace=True)

  st.session_state.df_A = df_A
  st.session_state.df_B = df_B
  st.session_state.df_code = df_code
  st.session_state.df_hospital = df_hospital
  '''

# func: make graph with NetworkX
def makeGraph(item, G):
  # 진료과 + 응급도 등급으로 도출되도록 변경 필요
  # 그래프에서 관련된 여러 과가 나오도록 변경 필요
  G.add_edge(item['firstCode'] + item['secondCode'] + item['thirdCode'] + item['fourthCode'], item['description'].split(', ')[2] + ' ' + str(item['level']))

def getDepartment():
  mergeCode = st.session_state.mergeCode
  if 'G' in st.session_state:
    G = st.session_state.G
    possible_departments = []

    for code in mergeCode:
      for node in G.nodes:
        if code in node:
          data = list(dict(G_A[node]).keys())
          for d in data:
            d.split(', ')
            for i in d:
              possible_departments.append(d)

    departments = []

    for p in possible_departments:
      data = p.split(', ')
      for d in data:
        if d in departments:
          break
        departments.append(d)
    label = "도출된 진료과는 "
    for i in departments:
      label += i
      label += ", "
    label = label[:-2] + "입니다."
    st.write(label)
    st.session_state.departments = departments
    
def main():
  ## Streamlit App Setting
  st.title('C-ITS')
  st.subheader('Made By SobanGchA (소 방 차)')
  
  age = st.selectbox(
      '환자의 나이를 골라주세요.',
      ('15세 이상의 성인', '15세 미만의 아동'))
  if age == '15세 이상의 성인':
    ageCode = 'A'
  else:
    ageCode = 'B'
    
  step4 = st.text_input('증상의 키워드를 입력하세요.(여러개일 경우, 띄어쓰기로 구분)')
  step4 = step4.split(" ")
  keyword = ""
  for i in step4:
    keyword += str(i)
    keyword += '|'
  '''
  if age == '15세 이상의 성인':
    
    step3_list = df_A[df_A['4단계'].str.contains(keyword[:-1])]
    step3_list_2 = step3_list["3단계"].drop_duplicates()
    step3 = st.multiselect(
      '환자의 응급상황 정보를 선택해주세요.',
      (tuple(step3_list_2.values.tolist())))
    keyword2 = ""
    for i in step3:
      keyword2 += str(i)
      keyword2 += '|'
    step2 = step3_list[step3_list['3단계'].str.contains(keyword2[:-1])]
    mergeCode = "A" + step2["2단계 코드"] + step2["3단계 코드"] + step2["4단계 코드"]
  elif age == '15세 미만의 아동':
    step4 = st.text_input('증상의 키워드를 입력하세요.(여러개일 경우, 띄워쓰기로 구분)')
    step4 = step4.split(" ")
    keyword = ""
    for i in step4:
      keyword += str(i)
      keyword += '|'
    step3_list = df_B[df_B['4단계'].str.contains(keyword[:-1])]
    step3_list_2 = step3_list["3단계"].drop_duplicates()
    step3 = st.multiselect(
      '환자의 응급상황 정보를 선택해주세요.',
      (tuple(step3_list_2.values.tolist())))
    keyword2 = ""
    for i in step3:
      keyword2 += str(i)
      keyword2 += '|'
    step2 = step3_list[step3_list['3단계'].str.contains(keyword2[:-1])]
    mergeCode = "B" + step2["2단계 코드"] + step2["3단계 코드"] + step2["4단계 코드"]
  st.session_state.mergeCode = mergeCode
  getDepartment()
  '''

if __name__ == "__main__":
  st.set_page_config(page_title="C-ITS", layout="wide")
  if 'sessionState' not in st.session_state: # 세션 코드가 없는 경우
    initializeApp() # 앱 초기화
  if 'G' not in st.session_state or 'df_code' not in st.session_state or 'df_hospital' not in st.session_state: # 그래프, 감염여부 코드, 병원 정보 중 하나라도 없는 경우
    readData()
  #df_A = st.session_state.df_A
  #df_B = st.session_state.df_B
  df_code = st.session_state.df_code
  df_hospital = st.session_state.df_hospital
  #if 'G' not in st.session_state:
    #makeGraph()
  main()
