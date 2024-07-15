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

    centered_title("Trajetórias, Tempo e Velocidade")

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

    st.write("Este mapa de calor com tempo apresenta a variação do percurso realizado pelo motorista com base no dia e hora do registro dos dados e, além disso, sua velocidade a cada ponto.")
    st.write("Embora não se tenha o valor da velocidade ponto a ponto mostrada no mapa, a simbologia traz uma ideia de sua característica:")
    st.markdown(":arrow_right: Quanto maior o círculo vermelho, maior é a velocidade resgitrada dentro do período de tempo que está sendo mostrado.")
    st.markdown(":arrow_right: Quanto menor o círculo vermelho, menor é a velocidade resgitrada dentro do período de tempo que está sendo mostrado.")
    st.write(":bulb: Para observar com mais clareza, pause a reprodução e aumente o zoom sobre a rota de interesse.")

    # Filtrar os IDs únicos de id_driver
    unique_id_drivers = sorted(gdf['id_driver'].unique())
    selected_id_driver = st.selectbox("Selecione o condutor", options=unique_id_drivers)

    # Filtrar o GeoDataFrame com base no id_driver selecionado
    filtered_gdf = gdf[gdf['id_driver'] == selected_id_driver]

    # Função para extrair coordenadas de LineString
    def extract_coordinates(geometry):
        if geometry.geom_type == 'LineString':
            return list(geometry.coords)
        elif geometry.geom_type == 'MultiLineString':
            return [list(line.coords) for line in geometry]
        else:
            raise ValueError(f"Unsupported geometry type: {geometry.geom_type}")

    # Preparar os dados para o HeatMapWithTime
    heat_data = []
    time_index = []

    # Ordenar os dados por data
    filtered_gdf = filtered_gdf.sort_values('date_d')

    for date in filtered_gdf['date_d'].unique():
        date_data = []
        for idx, row in filtered_gdf[filtered_gdf['date_d'] == date].iterrows():
            coords = extract_coordinates(row.geometry)
            for coord in coords:
                date_data.append([coord[1], coord[0], row['speed']])
        heat_data.append(date_data)
        time_index.append(date.strftime('%Y-%m-%d %H:%M:%S'))
    attr = ('&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>')
    tiles = ('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png')

    # Criar o mapa base
    m2 = folium.Map(location=[-25.4809,-49.2718], tiles = tiles, attr = attr, zoom_start=12)

    # Adicionar o HeatMapWithTime
    hm = HeatMapWithTime(
        data=heat_data,
        index=time_index,
        auto_play=True,
        max_opacity=0.8,
        radius=10,
        gradient={0.1: 'blue', 0.25: 'lime', 0.55: 'orange', 1: 'red'}
    )
    hm.add_to(m2)

    folium_static(m2)

    colored_divider()

    st.write("Este mapa classifica a velocidade no tempo para cada trajetória.")
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