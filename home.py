import streamlit as st 
from sidebar import configure_sidebar
from streamlit_folium import folium_static
import pandas as pd 
import folium 
import geopandas as gpd
import numpy as np
import altair as alt
from streamlit.elements import html

def colored_divider(color='#395B64', height=2, margin_top=40, margin_bottom=40):
    st.markdown(
        f"""
        <div style="margin-top:{margin_top}px; margin-bottom:{margin_bottom}px;">
            <div style="background-color:{color};height:{height}px;border-radius:5px;"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

def centered_title(title_text):
    st.markdown(
        f"""
        <h1 style='text-align: center;'>{title_text}</h1>
        """,
        unsafe_allow_html=True
    )


def main():
    configure_sidebar()

    centered_title("Estudo Naturalístico de Direção Brasileiro")

    colored_divider()

    ##Lendo o arquivo 
    @st.cache_resource()
    def get_gdf (arquivo):
        gdf = gpd.read_file(arquivo)
        return gdf

    gdf = get_gdf('hierarquias.geojson')

    gdf2 = get_gdf('limites.geojson')

    # Função para gerar o mapa
    def create_map(gdf, selected_hierarquia_ctb, gdf2):
        attr = ('&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>')
        tiles = ('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png')

        # Filtrando o GeoDataFrame pela seleção do selectbox
        filtered_gdf = gdf[gdf['hierarquia_ctb'] == selected_hierarquia_ctb]

        ##Criando o mapa 
        m = folium.Map (location = [-25.4809,-49.2718],tiles = tiles, attr = attr, zoom_start = 11)

        # Adicionando geometrias ao mapa
        for _, row in filtered_gdf.iterrows():
            color = get_color_for_hierarquia(row['hierarquia_cwb'])
            folium.GeoJson(
                row['geometry'],
                style_function=lambda feature, color=color: {'color': color}, weight = 2,
                tooltip=row['hierarquia_cwb']
            ).add_to(m)
        
        folium.GeoJson(
        gdf2,
        style_function=lambda x: {
            'fillColor': 'none',  # Sem preenchimento
            'color': 'black',  # Cor do contorno
            'weight': 0.5  # Espessura da linha
            }
            ).add_to(m)

        return m


    # Função para obter uma cor para cada string em hierarquia_cwb
    def get_color_for_hierarquia(hierarquia_cwb):
        colors = {
            'NORMAL': '#ff7f00', #1
            'RODOVIA FEDERAL DUPLICADA':'##fb9a99',
            'RODOVIA FEDERAL SIMPLES':'#33a02c',
            'SETORIAL':'#b15928',
            'EXTERNA': '#e31a1c', #2
            'PRIORITÁRIA 1':'#6a3d9a',#4
            'PRIORITÁRIA 2':'#ffff99',
            'OUTRAS VIAS':'#cab2d6',
            'ANEL CENTRAL': '#a6cee3',#4
            'CENTRAL': '#1f78b4',
            'COLETORA 1': '#b2df8a',
            'COLETORA 2': '#33a02c',
            'COLETORA 3': '#fb9a99',
            'LINHÃO': '#fdbf6f',
            'PEDESTRE':'#cab2d6',
            'RODOVIA ESTADUAL DUPLICADA':'#e31a1c',
            'NPI' : 'black',
        }
        return colors.get(hierarquia_cwb)
    

    # Interface do Streamlit
    st.subheader('Hierarquia das vias ')
    st.write("Este mapa apresenta a hierarquia das vias percorridas pelos participantes do estudo")

    # Criando o selectbox
    unique_hierarquias_ctb = gdf['hierarquia_ctb'].unique()
    selected_hierarquia_ctb = st.selectbox('Selecione a hierarquia com base no código de trânsito brasileiro:', unique_hierarquias_ctb)

    # Criando o mapa filtrado
    if selected_hierarquia_ctb:
        mapa = create_map(gdf, selected_hierarquia_ctb, gdf2)
        folium_static(mapa)

    st.subheader('Legenda ')
    st.image('legenda.png')



if __name__ == "__main__":
    main()