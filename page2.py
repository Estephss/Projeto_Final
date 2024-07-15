import geopandas as gpd
import pandas as pd
import streamlit as st
import altair as alt
from bokeh.io import output_file, save
from bokeh.models import ColumnDataSource, ColorBar, LinearColorMapper, HoverTool,BasicTicker, FixedTicker
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

# Função para mapear a velocidade para a cor correspondente
def get_color(velocidade):
    if 0 < velocidade <= 20:
        return "#1a9850"
    elif 20 < velocidade <= 40:
        return "#91cf60"
    elif 40 < velocidade <= 60:
        return "#d9ef8b"
    elif 60 < velocidade <= 80:
        return "#fee08b"
    elif 80 < velocidade <= 100:
        return "#fc8d59"
    elif 100 < velocidade <= 120:
        return "#d73027"
    else:
        return "#b2182b"

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


    # Adiciona a cor correspondente a cada linha no DataFrame
    filtered_gdf['color'] = filtered_gdf['velocidade'].apply(get_color)

    # Criaçndo o mapa
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

    # Função para extrair coordenadas
    def extract_coordinates(geom):
        if geom.geom_type == 'LineString':
            return [list(geom.coords.xy[0]), list(geom.coords.xy[1])]
        elif geom.geom_type == 'MultiLineString':
            xs, ys = [], []
            for part in geom:
                xs.extend(part.coords.xy[0])
                ys.extend(part.coords.xy[1])
            return [xs, ys]
        else:
            return [[], []]

    # Extraindo coordenadas
    xs, ys = zip(*filtered_gdf['geometry'].apply(extract_coordinates))
    source = ColumnDataSource(data={
        'xs': xs,
        'ys': ys,
        'color': filtered_gdf['color'].tolist(),
        'velocidade': filtered_gdf['velocidade'].tolist(),
        'id_traj': filtered_gdf['id_traj'].tolist()
    })

    # Configuração do mapa de cores para a barra de cores
    color_mapper = LinearColorMapper(palette=["#1a9850", "#91cf60", "#d9ef8b", "#fee08b", "#fc8d59", "#d73027", "#b2182b"], 
                                    low=0, high=140)

    # Adicionando a barra de cores
    color_bar = ColorBar(color_mapper=color_mapper, ticker=FixedTicker(ticks=[0, 20, 40, 60, 80, 100, 120, 140]), location=(0, 0), title='Velocidade',
                        title_text_color="white", major_label_text_color="white", background_fill_color="#040D12")
    p_map.add_layout(color_bar, 'right')

    # Plotagem das linhas
    p_map.multi_line(xs='xs', ys='ys', source=source, line_width=4, line_color='color')

    # Mostrar o mapa no Streamlit
    st.bokeh_chart(p_map)


    colored_divider()

    # Converter GeoDataFrame para DataFrame
    df = filtered_gdf[['id_traj', 'velocidade']].copy()

    # Mapeamento das cores para Altair
    color_scale = ["#1a9850", "#91cf60", "#d9ef8b", "#fee08b", "#fc8d59", "#d73027", "#b2182b"]
    
    # Criando o gráfico

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('id_traj:O', title='ID da Trajetória', axis=alt.Axis(labelAngle=60)),
        y=alt.Y('velocidade:Q', title='Velocidade', scale=alt.Scale(domain=[0, df['velocidade'].max()])),
        color=alt.Color('velocidade:Q', scale=alt.Scale(domain=[min(data['velocidade']), max(data['velocidade'])], range=color_scale), legend=None)   
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