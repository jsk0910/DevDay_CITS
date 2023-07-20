import streamlit as st
from streamlit_folium import st_folium
from folium import plugins

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

## 최단 경로 시각화
def routeHospital(G, orig, destX, destY):

  # fig, ax = ox.plot_graph(G, node_size=0, edge_linewidth=0.5)

  dest = ox.distance.nearest_nodes(G, X=destX, Y=destY)
  route = ox.shortest_path(G, orig, dest, weight="travel_time")
  r = ox.plot_route_folium(G, route, popup_attribute='length')
  return r

st.write('경로 시각화 부분')
## 병원 위치 시각화
address = st.text_input('현재 위치를 입력하세요. (도로명 주소)', '부산광역시 사하구 낙동대로550번길 37')
df_hospital = st.session_state.df_hospital

center = list(ox.geocode(address))
G = ox.graph_from_place('부산, 대한민국', network_type='drive', simplify=False)
orig = ox.distance.nearest_nodes(G, X=center[1], Y=center[0])
G = ox.speed.add_edge_speeds(G)
G = ox.speed.add_edge_travel_times(G)

style = {'color': '#1A19AC', 'weight':'1'}

r = routeHospital(G, orig, 129.18199, 35.173516)
for _, row in df_hospital.iterrows():
    folium.Marker(location = [row['위도'], row['경도']],
            popup=row['의료기관명'],
            tooltip=row['의료기관명'],
            icon=folium.Icon(color='red',icon='plus')
          ).add_to(r)

plugins.LocateControl().add_to(r)
st_folium(r, returned_objects=[])

