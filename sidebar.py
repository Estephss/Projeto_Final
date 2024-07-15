import streamlit as st

def configure_sidebar():
    st.sidebar.image("logo.png", use_column_width=True)
    st.sidebar.header("Navegação:")

    if st.sidebar.button(":house: Inicio"):
        st.session_state.query_params = {"page": "home"}
    if st.sidebar.button(":dash: Velocidade"):
        st.session_state.query_params = {"page": "page1"}
    if st.sidebar.button(":clock4: Velocidade no tempo"):
        st.session_state.query_params = {"page": "page2"}

    st.sidebar.header("Sobre o desenvolvimento:")
    st.sidebar.info(""" :gear: Aplicação desenvolvida por [Estephanie Daiane](https://github.com/Estephss)
                    \n :female-teacher: Orientação: [Silvana Camboim](https://github.com/SilvanaCamboim)
                    """ )
    st.sidebar.info(
            """🌐 Setor de [Ciência da Terra](http://www.terra.ufpr.br/)
            \n 🌍 [Eng. Cartográfica e de Agrimensura](https://cartografica.ufpr.br/)""")

    st.sidebar.write("[![UFPR](http://www.ufpr.br/portalufpr/wp-content/uploads/2015/11/ufpr_logo.jpg)](https://www.ufpr.br/portalufpr/)")

    st.sidebar.header("Sobre o NDS-BR:")
    st.sidebar.info(""" :closed_book: [CEPPUR-UFPR](tecnologia.ufpr.br/ceppur/estudo-naturalistico-de-direcao-brasileiro/)
                    \n :gear: Aplicação web: [Indicadores sobre uso do ceular e cinto de segurança](https://painelndsbr.streamlit.app/)
                    """ )