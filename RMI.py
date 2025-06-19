import streamlit as st

# Garante que os dados estejam disponíveis
if "media" not in st.session_state or "anos" not in st.session_state:
    st.warning("Importe e processe o CNIS na página 'Tempo de Contribuição' antes de acessar esta funcionalidade.")
    st.stop()

media = st.session_state["media"]
anos = st.session_state["anos"]

st.write(f"Média dos salários considerados: **R$ {media:,.2f}**")
st.write(f"Tempo sugerido: **{anos} anos**")

# Permite simular e calcula RMI
tempo = st.number_input("Tempo total de contribuição (anos)", min_value=0, max_value=50, value=anos)
sexo = st.radio("Sexo", ["Masculino", "Feminino"])
coef_base = 20 if sexo == "Masculino" else 15
coef = 60 + 2 * max(0, tempo - coef_base)

if st.button("Calcular RMI"):
    rmi = media * coef / 100
    st.success(f"Coeficiente aplicado: {coef:.0f}%")
    st.success(f"Renda Mensal Inicial (RMI): R$ {rmi:,.2f}")
