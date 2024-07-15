import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap, HeatMapWithTime
import branca.colormap as cm
from sidebar import configure_sidebar


def colored_divider(color='#395B64', height=2, margin_top=20, margin_bottom=40):
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

    centered_title("Trajetórias e Velocidades")

    colored_divider()

    st.write("Este mapa de calor apresenta o volume de trajetórias na área de estudo. Nas regiões com coloração mais avermelhada, tem-se mais rotas realizadas.")

    ##Lendo o arquivo 
    @st.cache_data
    def get_gdf ():
        return gpd.read_file('trajetorias.geojson')

    gdf = get_gdf()

    gdf['date_d'] = pd.to_datetime(gdf['date_d'])

    ##Criando o mapa 

    attr = ('&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>')
    tiles = ('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png')

    # Preparar os dados para o heatmap
    heat_data = []
    for line, speed in zip(gdf.geometry, gdf['speed']):
        if line.geom_type == 'LineString':
            for point in line.coords:
                heat_data.append([point[1], point[0], speed])
        elif line.geom_type == 'MultiLineString':
            for linestring in line:
                for point in linestring.coords:
                    heat_data.append([point[1], point[0], speed])

    # Criar o mapa base
    m1 = folium.Map(location=[-25.4809,-49.2718], tiles = tiles, attr = attr, zoom_start=11, max_zoom=15)

    # Adicionar o heatmap
    HeatMap(heat_data, radius=3, blur=1.5).add_to(m1)

    # Exibir o mapa no Streamlit
    folium_static(m1)

    colored_divider()

    st.write("Este mapa classifica a velocidade agregada no tempo para cada trajetória.")
    st.write(":bulb: Para observar com mais clareza, aumente o zoom sobre a região interesse.")

    # Criar uma função para definir a cor com base na velocidade
    def get_color(speed):
        if 0 <speed < 11.51:
            return '#fff5f0'
        elif 11.52< speed < 26.72:
            return '#fcbea5'
        elif 26.73 < speed < 42.63:
            return '#fb7050'
        elif 42.64 < speed < 64.84:
            return '#d32020'
        elif 64.85< speed < 131:
            return '#67000d'
        else:
            return 'gray'


    m1 = folium.Map(location=[-25.4809,-49.2718], tiles = tiles, attr = attr, zoom_start=11, max_zoom=15)

    # Criação do colormap
    colormap = cm.StepColormap(
        colors=['#fff5f0', '#fcbea5', '#fb7050', '#d32020', '#67000d'],
        vmin=0, vmax=131,
        index=[0, 12, 27, 43, 65, 131],
        caption='Velocidade (km/h)'
    )
    colormap.add_to(m1)

    # Iterar sobre as linhas do GeoDataFrame para adicionar linhas coloridas ao mapa
    for idx, row in gdf.iterrows():
        speed = row['speed']  # Substitua 'speed' pelo nome do seu campo de velocidade
        geometry = row['geometry']

        # Converter a geometria para o formato GeoJSON para adicionar ao mapa Folium
        geojson_data = geometry.__geo_interface__

        # Criar um folium.PolyLine com a cor baseada na velocidade
        folium.PolyLine(
            locations=[(lat, lon) for lon, lat in geometry.coords],
            color=get_color(speed),
            tooltip=f"Velocidade: {speed}",
            weight=2
        ).add_to(m1)



    # Exibir o mapa Folium no Streamlit
    folium_static(m1)

if __name__ == "__main__":
    main()