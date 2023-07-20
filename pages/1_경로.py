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
  st.write(distance)

  df_distance['distance'] = distance_list
  st.write(df_distance)

  return df_distance

## 최단 경로 시각화
def routeHospital(G, orig, destX, destY):

  # fig, ax = ox.plot_graph(G, node_size=0, edge_linewidth=0.5)

  dest = ox.distance.nearest_nodes(G, X=destX, Y=destY)
  route = ox.shortest_path(G, orig, dest, weight="travel_time")
  r = ox.plot_route_folium(G, route, popup_attribute='length')
  return r

htmlTitle = """
<div><h3>🎈Hello World!</h3></div>
"""
st.markdown(htmlTitle, unsafe_allow_html=True)
## 병원 위치 시각화
address = st.text_input('현재 위치를 입력하세요. (도로명 주소)', '부산광역시 사하구 낙동대로550번길 37')
if 'address' not in st.session_state:
  st.session_state.address = address
else:
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
st.write(df_hospital_distance)

if 'G' not in st.session_state:
  G = ox.graph_from_place('부산, 대한민국', network_type='drive', simplify=False)
  G = ox.speed.add_edge_speeds(G)
  G = ox.speed.add_edge_travel_times(G)
  st.session_state.G = G
if 'orig' not in st.session_state or address != st.session_state.old_address:
  G = st.session_state.G
  orig = ox.distance.nearest_nodes(G, X=center[1], Y=center[0])
  st.session_state.orig = orig

G = st.session_state.G
orig = st.session_state.orig

style = {'color': '#1A19AC', 'weight':'1'}

if 'r' not in st.session_state or address != st.session_state.old_address:
  r = routeHospital(G, orig, 129.18199, 35.173516)
  for _, row in df_hospital.iterrows():
    folium.Marker(location = [row['위도'], row['경도']],
            popup=row['의료기관명'],
            tooltip=row['의료기관명'],
            icon=folium.Icon(color='red',icon='plus')
          ).add_to(r)
    st.session_state.r = r
r = st.session_state.r

st_folium(r, returned_objects=[])

