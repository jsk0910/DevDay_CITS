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

# --- import modules end ---

# func: read Data from Repository
def readData():
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
  df_B.replace('ㅂ귀질환', '이비인후과', inplace=True)
  df_B.replace('호흡기', '호흡기과, 흉부내과', inplace=True)
  df_B.replace('심혈관', '심장내과', inplace=True)
  df_B.replace('소화기', '소화기내과', inplace=True)
  df_B.replace('피부', '피부과', inplace=True)

  st.session_state.df_A = df_A
  st.session_state.df_B = df_B
  st.session_state.df_code = df_code
  st.session_state.df_hospital = df_hospital

# func: make graph with NetworkX
def makeGraph():
  ## 진료과 도출
  G_A = nx.Graph() # 15세 이상에 대한 그래프
  G_B = nx.Graph() # 15세 미만에 대한 그래프
  
  for idx, row in df_A.iterrows():
    G_A.add_edge("A" + row['2단계 코드'] + row['3단계 코드'] + row['4단계 코드'], row['2단계'])
  for idx, row in df_B.iterrows():
    G_B.add_edge("B" + row['2단계 코드'] + row['3단계 코드'] + row['4단계 코드'], row['2단계'])
  
  st.session_state.G_A = G_A
  st.session_state.G_B = G_B

def main():
  ## Streamlit App Setting
  st.title('C-ITS')
  st.subheader('Made By SobanGchA (소 방 차)')
  
  age = st.selectbox(
      '환자의 나이를 골라주세요.',
      ('15세 이상의 성인', '15세 미만의 아동'))
  if age == '15세 이상의 성인':
    step4 = st.text_input('증상의 키워드를 입력하세요.(여러개일 경우, 띄워쓰기로 구분)')
    step4 = step4.split(" ")
    keyword = ""
    for i in step4:
      keyword += str(i)
      keyword += '|'
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
    st.write(mergeCode)
  elif age == '15세 이상의 아동':
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
    st.write(mergeCode)

if __name__ == "__main__":
  if 'df_A' not in st.session_state or 'df_B' not in st.session_state or 'df_code' not in st.session_state or 'df_hospital' not in st.session_state:
    readData()
  df_A = st.session_state.df_A
  df_B = st.session_state.df_B
  df_code = st.session_state.df_code
  df_hospital = st.session_state.df_hospital
  if 'G_A' not in st.session_state or 'G_B' not in st.session_state:
    makeGraph()
  main()
    
  
"""
code = step3

possible_departments = []

if code[0] == "A":
  for node in G_A.nodes:
    if code in node:
      data = list(dict(G_A[node]).keys())
      for d in data:
        d.split(', ')
        for i in d:
          possible_departments.append(d)
elif code[0] == "B":
  for node in G_B.nodes:
    if code in node:
      data = list(dict(G_B[node]).keys())
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

## 병원 도출 함수
def calculate_distance(df): # df: 병원, latlon: 병원의 위경도 좌표, center: 현재 위치
  df_distance = pd.DataFrame()
  distance_list = []
  for i in df['latlon']:
    if i != None:
      i = list(i)
      y = abs(center[0] - float(i[0])) * 111
      x = (math.cos(center[0]) * 6400 * 2 * 3.14 / 360) * abs(center[1] - float(i[1]))
      distance = math.sqrt(x*x + y*y)
      if distance <= 3.0:
        df_distance = pd.concat([df_distance, df[df['latlon'] == tuple(i)]])
        distance_list.append(distance)

  df_distance = df_distance.drop_duplicates()
  df_distance['distance'] = distance_list

  return df_distance
"""
"""
## 병원 위치 시각화
address = st.text_input('현재 위치를 입력하세요. (도로명 주소)', '부산광역시 사하구 낙동대로550번길 37')
# address = input()


center = list(ox.geocode(address))
G = ox.graph_from_place('부산, 대한민국', network_type='drive', simplify=False)
orig = ox.distance.nearest_nodes(G, X=center[1], Y=center[0])
G = ox.speed.add_edge_speeds(G)
G = ox.speed.add_edge_travel_times(G)

## 최단 경로 시각화
def routeHospital(G, orig, destX, destY):

  # fig, ax = ox.plot_graph(G, node_size=0, edge_linewidth=0.5)

  dest = ox.distance.nearest_nodes(G, X=destX, Y=destY)
  route = ox.shortest_path(G, orig, dest, weight="travel_time")
  r = ox.plot_route_folium(G, route, popup_attribute='length')
  return r

style = {'color': '#1A19AC', 'weight':'1'}

r= routeHospital(G, orig, 129.18199, 35.173516)
for _, row in df_hospital.iterrows():
    folium.Marker(location = [row['위도'], row['경도']],
            popup=row['의료기관명'],
            tooltip=row['의료기관명'],
            icon=folium.Icon(color='red',icon='plus')
          ).add_to(r)
"""
