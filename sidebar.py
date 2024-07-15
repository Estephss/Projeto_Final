import streamlit as st
import base64

def load_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()

def configure_sidebar():
    st.sidebar.image("logo.png", width=300)
    st.sidebar.header("Navegação:")

    if st.sidebar.button(":house: Inicio"):
        st.session_state.query_params = {"page": "home"}
    if st.sidebar.button(":motorway: Trajetórias"):
        st.session_state.query_params = {"page": "page1"}
    if st.sidebar.button(":dash: Velocidades"):
        st.session_state.query_params = {"page": "page2"}

    st.sidebar.header("Sobre o desenvolvimento:")
    st.sidebar.info(""" :gear: Aplicação desenvolvida por [Estephanie Daiane](https://github.com/Estephss)
                    \n :female-teacher: Orientação: [Silvana Camboim](https://github.com/SilvanaCamboim)
                    """ )
    
    st.sidebar.header("Sobre a instituição de ensino:")

    st.sidebar.info(
            """🌐 Setor de [Ciência da Terra](http://www.terra.ufpr.br/)""")


    # Caminho para a imagem local
    image_path = "logocarto.png"

    # URL para ser redirecionado ao clicar na imagem
    url = "https://cartografica.ufpr.br/"

    # Carregar a imagem e convertê-la em base64
    image_base64 = load_image(image_path)

    # HTML para a imagem com um link
    html_code = f'''
    <a href="{url}" target="_blank">
        <img src="data:image/png;base64,{image_base64}" width="280>
    </a>
    '''
    st.sidebar.info(
            """Curso de Engenharia Cartográfica e de Agrimensura""")
    # Exibir a imagem com o link na barra lateral
    st.sidebar.markdown(html_code, unsafe_allow_html=True)

    st.sidebar.markdown("\n")

    st.sidebar.write("\n [![UFPR](http://www.ufpr.br/portalufpr/wp-content/uploads/2015/11/ufpr_logo.jpg)](https://www.ufpr.br/portalufpr/)")

    st.sidebar.header("Sobre o NDS-BR:")
    st.sidebar.info(""" :closed_book: [CEPPUR-UFPR](tecnologia.ufpr.br/ceppur/estudo-naturalistico-de-direcao-brasileiro/)
                    \n :blue_car: [OBSERVATÓRIO](https://www.onsv.org.br/)
                    \n :gear: Aplicação web: [Indicadores sobre uso do ceular e cinto de segurança](https://painelndsbr.streamlit.app/)
                    """ )
