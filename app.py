# data
import pandas as pd
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import json
import requests
import math

# mongodb
import pymongo

# map
import folium

# GIS
import networkx as nx
import osmnx as ox
import geopandas as gpd

df_A = pd.read_csv('/content/drive/MyDrive/데브데이2023/01 개발파일/data/응급환자_중증도_분류기준.csv', encoding='CP949')
df_B = pd.read_csv('/content/drive/MyDrive/데브데이2023/01 개발파일/data/응급환자_중증도_분류기준B.csv')
df_code = pd.read_csv('/content/drive/MyDrive/데브데이2023/01 개발파일/data/감염여부_코드.csv')
