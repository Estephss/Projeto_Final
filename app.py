import streamlit as st
import home
import page2
import page3

# Inicializa o estado da sessão se necessário
if "query_params" not in st.session_state:
    st.session_state.query_params = {"page": "home"}

# Obtém o parâmetro de consulta 'page'
page = st.session_state.query_params.get("page", "home")

# Carrega a página correspondente
if page == "home":
    home.main()
elif page == "page1":
    page2.main()
elif page == "page2":
    page3.main()