import streamlit as st

st.set_page_config(layout="wide")

col1, col2 = st.columns([3, 1])

with col1:
    # Inicializa o estado de sessão
    if "role" not in st.session_state:
        st.session_state.role = None

    # Funções de login/logout
    def login():
        st.title("Tax Calculator")
        escolha = st.selectbox("Escolha o cálculo:", [None, "Cálculo de Benefícios"])
        if st.button("Acessar"):
            st.session_state.role = escolha
            st.rerun()

    def logout():
        st.session_state.role = None
        st.rerun()

    # Recupera o papel atual
    role = st.session_state.role

    # Definição das páginas
    login_page = st.Page(login,title="Tax Calculator",icon="🔑")
    logout_page = st.Page(logout,title="Sair",icon="🚪")

    # Cálculo de Benefícios
    timec_page = st.Page("TC.py", title="Tempo de Contribuição", icon="💵", default=(role == "Cálculo de Benefícios"))
    rmi_page = st.Page("RMI.py", title="Renda Mensal Inicial", icon="⚖️", default=False)
    wagesbond_page = st.Page("WagesBond.py", title="Remunerações", icon="📊", default=False)

    #Outro


    # Monta o dicionário de navegação
    page_dict = {}
    if role == "Cálculo de Benefícios":
        # agrupa as duas sub-páginas e o logout
        page_dict["Cálculo de Benefícios"] = [timec_page, rmi_page, wagesbond_page, logout_page]

    # Executa a navegação (login ou menu de cálculo)
    if page_dict:
        pg = st.navigation(page_dict)
    else:
        pg = st.navigation([login_page])

    pg.run()

with col2:
    st.write("")  # espaço reservado para logo ou outros elementos
