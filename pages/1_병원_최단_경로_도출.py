import streamlit as st
from streamlit_folium import st_folium

# import data analysis modules
import pandas as pd

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

# func: address to lat, lon
def addr_to_lat_lon(addr):
  url = f"https://dapi.kakao.com/v2/local/search/address.json?query={addr}"
  headers = {"Authorization": "KakaoAK " + st.secrets.KAKAOKEY}
  result = json.loads(str(requests.get(url, headers=headers).text))
  match_first = result['documents'][0]['address']
  return float(match_first['y']), float(match_first['x'])

# 병원 도출 함수
def calculate_distance(df): # df: 병원, latlon: 병원의 위경도 좌표, center: 현재 위치
  df_distance = df
  distance_list = []
  for i, row in df.iterrows():
    if row is not None:
      #i = list(i)
      y = abs(center[0] - float(row['위도'])) * 111
      x = (math.cos(center[0]) * 6400 * 2 * 3.14 / 360) * abs(center[1] - float(row['경도']))
      distance = math.sqrt(x*x + y*y)
      distance_list.append(distance)

  df_distance['distance'] = distance_list

  return df_distance

## 최단 경로 시각화
def routeHospital(G, orig, dest):
  dest1 = ox.distance.nearest_nodes(G, X=dest[0][0], Y=dest[0][1])
  dest2 = ox.distance.nearest_nodes(G, X=dest[1][0], Y=dest[1][1])
  dest3 = ox.distance.nearest_nodes(G, X=dest[2][0], Y=dest[2][1])
  route1 = ox.shortest_path(G, orig, dest1, weight="travel_time")
  route2 = ox.shortest_path(G, orig, dest2, weight="travel_time")
  route3 = ox.shortest_path(G, orig, dest3, weight="travel_time")
  
  r = ox.plot_route_folium(G, route1, popup_attribute='length', zoom=13, color="red")
  r = ox.plot_route_folium(G, route2, route_map=r, popup_attribute='length', zoom=13, color="green")
  r = ox.plot_route_folium(G, route3, route_map=r, popup_attribute='length', zoom=13, color="blue")
  return r

# title
htmlTitle = """
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
      <p style="font-weight: 600; font-size: 20px;">C-ITS 응급환자이송지원시스템</p>
      <p style="font-weight: 600; font-size: 20px;">병원 최단 경로 도출</p>
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

## 병원 위치 시각화
address = st.text_input('현재 위치를 입력하세요. (도로명 주소)', '부산광역시 사하구 낙동대로550번길 37')
if 'address' not in st.session_state:
  st.session_state.address = address
elif address != st.session_state.address:
  st.session_state.old_address = st.session_state.address
  st.session_state.address = address
df_hospital = st.session_state.df_hospital

if 'center' not in st.session_state or address != st.session_state.old_address:
  st.session_state.center = list(addr_to_lat_lon(address))
center = st.session_state.center
if 'df_hospital_distance' not in st.session_state or address != st.session_state.old_address:
  df_hospital_distance = calculate_distance(df_hospital)
  st.session_state.df_hospital_distance = df_hospital_distance
df_hospital_distance = st.session_state.df_hospital_distance

if 'G_map' not in st.session_state:
  G_map = ox.graph_from_place('부산, 대한민국', network_type='drive', simplify=False)
  G_map = ox.speed.add_edge_speeds(G_map)
  G_map = ox.speed.add_edge_travel_times(G_map)
  st.session_state.G_map = G_map
if 'orig' not in st.session_state or address != st.session_state.old_address:
  G_map = st.session_state.G_map
  orig = ox.distance.nearest_nodes(G_map, X=center[1], Y=center[0])
  st.session_state.orig = orig

G_map = st.session_state.G_map
orig = st.session_state.orig

style = {'color': '#1A19AC', 'weight':'1'}
min = df_hospital_distance.sort_values(by="distance")
st.session_state.min = min

if 'departments' in st.session_state:
  departments = st.session_state.departments
  try:
    depart = ""
    for i in departments:
      depart += i
      depart += '|'
    depart += '내과'
    min = min[min['진료과목'].str.contains(depart)]
  except:
    min = st.session_state.min

if 'r' not in st.session_state or address != st.session_state.old_address:
  orig = st.session_state.orig
  r = None
  with st.spinner('경로 계산중...'):
    r = routeHospital(G_map, orig, [[min.iloc[0]['경도'], min.iloc[0]['위도']],[min.iloc[1]['경도'], min.iloc[1]['위도']], [min.iloc[2]['경도'], min.iloc[2]['위도']]])
  for _, row in df_hospital.iterrows():
    folium.Marker(location = [row['위도'], row['경도']],
            popup=row['의료기관명'],
            tooltip=row['의료기관명'],
            icon=folium.Icon(color='red',icon='plus')
          ).add_to(r)
  for i in range(3):
    folium.Marker(location = [min.iloc[i]['위도'], min.iloc[i]['경도']],
                  popup = folium.Popup(f"{min.iloc[i]['의료기관명']}\n전화번호: {min.iloc[i]['전화번호']}\n",
                  width=250),
                  tooltip = min.iloc[i]['의료기관명'],
                  icon=folium.Icon(color='blue', icon='plus')
                 ).add_to(r)
  folium.Marker(location = [center[0], center[1]],
                popup = "출발지",
                tooltip = "출발지",
                icon=folium.Icon(color='green')
               ).add_to(r)
  folium.Marker(location = [df_hospital[df_hospital['의료기관명'] == '부산대학교병원']['위도'], df_hospital[df_hospital['의료기관명'] == '부산대학교병원']['경도']],
                popup = "부산대학교 권역외상센터",
                tooltip = "부산대학교 권역외상센터",
                icon=folium.Icon(color='black', icon='star')
               ).add_to(r)
  st.session_state.r = r
r = st.session_state.r

st_folium(r, width="500px", returned_objects=[])
