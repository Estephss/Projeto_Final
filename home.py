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

    centered_title("Estudo Naturalístico de Direção Braisleiro")

    colored_divider()
    st.write("Este mapa ilustra a extensão do estudo em Curitiba e Região Metropolitana. Com base nisso, o gráfico a seguir apresenta uma contagem de bairros com maior quantidade de rotas.")

    ##Lendo o arquivo 
    @st.cache_resource()
    def get_gdf ():
        return gpd.read_file('trajetorias.geojson').set_index('date_d')

    gdf = get_gdf()

    ##Criando o mapa 

    attr = ('&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>')
    tiles = ('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png')

    m = folium.Map (location = [-25.4809,-49.2718],tiles = tiles, attr = attr, zoom_start = 11)

    ##Estilizando e adiocionando as feições ao mapa

    style = {'color': 'black', 'weight': '0.5'}

    folium.GeoJson(gdf,
                style_function=lambda x: style).add_to(m)

    folium_static(m)

    colored_divider()


    # Criar um DataFrame a partir dos dados

    bc = gdf['bairro'].value_counts()
    df = pd.DataFrame({
        'Bairro': bc.index,
        'Contagem': bc.values})

    # Criar o gráfico de barras com Altair
    chart = alt.Chart(df).mark_bar(color='#9EC8B9').encode(
        x=alt.X('Bairro', sort=None, title='Bairros'),
        y=alt.Y('Contagem', title='Contagem')
    ).properties(
        title='\n\n Contagem de viagens por bairros',
        width=800,  # Largura do gráfico
        height=550  # Altura do gráfico
    ).configure_axis(
        labelAngle=90  # Rotaciona os rótulos do eixo x para melhor visualização
    )

    # Mostrar o gráfico no Streamlit
    st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()