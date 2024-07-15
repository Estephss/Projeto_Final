import geopandas as gpd
import pandas as pd
import streamlit as st
import altair as alt
from bokeh.io import output_file, save
from bokeh.models import ColumnDataSource, ColorBar, LinearColorMapper, HoverTool
from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, CARTODBPOSITRON
from bokeh.transform import linear_cmap
from bokeh.layouts import column
from sidebar import configure_sidebar
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

    centered_title("Trajetórias individuais")

    colored_divider()


    @st.cache_resource()
    def get_gdf ():
        return gpd.read_file('trajetorias.geojson')

    gdf = get_gdf()

    # Verificar o CRS atual e transformar para EPSG:3857, se necessário
    if gdf.crs.to_epsg() != 3857:
        gdf = gdf.to_crs(epsg=3857)

    # Extrair informações de ID, velocidade e geometria
    gdf['xs'] = gdf.geometry.apply(lambda geom: list(geom.xy[0]))
    gdf['ys'] = gdf.geometry.apply(lambda geom: list(geom.xy[1]))
    gdf['id'] = gdf['id_trip'].astype(str)
    gdf['id_traj'] = gdf['id_traj'].astype(int)
    gdf['velocidade'] = gdf['speed'].astype(float)

    # Preparando os dados
    data = {
        'id': gdf['id'].tolist(),
        'id_traj': gdf['id_traj'].tolist(),
        'velocidade': gdf['velocidade'].tolist(),
        'xs': gdf['xs'].tolist(),
        'ys': gdf['ys'].tolist()
    }

    # Adicionando a seleção de ID no Streamlit
    unique_ids = sorted(gdf['id'].unique())
    selected_id = st.selectbox("Selecione o condutor e sua viajem", options=unique_ids)

    # Filtrando os dados com base no ID selecionado
    filtered_gdf = gdf[gdf['id'] == selected_id]
    filtered_data = {
        'id': filtered_gdf['id'].tolist(),
        'id_traj': filtered_gdf['id_traj'].tolist(),
        'velocidade': filtered_gdf['velocidade'].tolist(),
        'xs': filtered_gdf['xs'].tolist(),
        'ys': filtered_gdf['ys'].tolist()
    }
    filtered_source = ColumnDataSource(filtered_data)

    # Configuração do mapa de cores
    color_mapper = LinearColorMapper(palette="Plasma256", low=min(data['velocidade']), high=max(data['velocidade']))

    # Criação da figura
    p_map = figure(x_axis_type="mercator", y_axis_type="mercator", title=f"Trajetória de {selected_id}",
                background_fill_color="#040D12", border_fill_color="#040D12")
    tile_provider = get_provider(CARTODBPOSITRON)
    p_map.add_tile(tile_provider)

    hover = HoverTool(
        tooltips=[
            ("ID Trajetória", "@id_traj"),
            ("Velocidade", "@velocidade")
        ],
        point_policy="follow_mouse"
    )
    p_map.add_tools(hover)

    # Configurar a cor dos eixos, grade e título
    p_map.title.text_color = "white"
    p_map.axis.major_label_text_color = "white"
    p_map.axis.axis_label_text_color = "white"
    p_map.axis.major_tick_line_color = "white"
    p_map.axis.minor_tick_line_color = "white"
    p_map.axis.axis_line_color = "white"
    p_map.grid.grid_line_color = None

    # Plotagem das linhas
    p_map.multi_line(xs='xs', ys='ys', source=filtered_source, line_width=4, line_color=linear_cmap('velocidade', 'Plasma256', 
                min(data['velocidade']), max(data['velocidade'])))

    # Adicionando uma barra de cor
    color_bar = ColorBar(color_mapper=color_mapper, location=(0, 0), title='Velocidade',
                        title_text_color="white", major_label_text_color="white", background_fill_color="#040D12")
    p_map.add_layout(color_bar, 'right')

    # Mostrar o mapa no Streamlit
    st.bokeh_chart(p_map)


    colored_divider()
    # Converter GeoDataFrame para DataFrame
    df = filtered_gdf[['id_traj', 'velocidade']].copy()

    # Criação do gráfico de barras com Altair
    chart = alt.Chart(df).mark_bar(color='#9EC8B9').encode(
        x=alt.X('id_traj:O', title='ID da Trajetória', axis=alt.Axis(labelAngle=60)),
        y=alt.Y('velocidade:Q', title='Velocidade', scale=alt.Scale(domain=[0, df['velocidade'].max()])),
    ).properties(
        width=800,
        height=300,
        title=f'Valores de Velocidade para o ID {selected_id}'
    )

    # Mostrar o gráfico no Streamlit
    st.altair_chart(chart, use_container_width=True)


    colored_divider()
    # Selecionando apenas as colunas desejadas e reordenando
    df1 = filtered_gdf[['id_traj', 'id_driver', 'sexo', 'idade', 'categoria', 'categoria_cnh', 'velocidade', 'date_d', 'cidade', 'bairro']].copy()

    # Exibindo o DataFrame
    st.write(df1)

if __name__ == "__main__":
    main()
