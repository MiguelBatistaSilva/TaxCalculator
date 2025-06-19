import streamlit as st

st.header("Cálculo do Fator Previdenciário")

# Verifica se os dados necessários existem no session_state
if (
    "media" not in st.session_state or
    "anos" not in st.session_state
):
    st.warning("Você precisa importar e processar o CNIS na página principal antes de acessar esta funcionalidade.")
    st.stop()

# Sugestão de preenchimento automático com dados já calculados
media = st.session_state["media"]
anos = st.session_state["anos"]

st.write(f"Média dos salários considerados: **R$ {media:,.2f}**")
st.write(f"Tempo total de contribuição sugerido: **{anos} anos**")

# Pede as informações para cálculo do fator
tempo_contribuicao = st.number_input(
    "Tempo de contribuição (anos, pode ser decimal)",
    min_value=0.0, step=0.1, value=float(anos)
)
idade = st.number_input(
    "Idade na DER (anos, pode ser decimal)",
    min_value=0.0, step=0.1
)
expectativa_vida = st.number_input(
    "Expectativa de vida (tabela IBGE, em anos)",
    min_value=0.0, step=0.1
)
aliquota = 0.31  # valor fixo

if st.button("Calcular Fator Previdenciário"):
    if tempo_contribuicao > 0 and idade > 0 and expectativa_vida > 0:
        fator = (
            (tempo_contribuicao * aliquota) / (idade * expectativa_vida)
        ) * (
            1 + (idade * aliquota) / tempo_contribuicao
        )
        st.success(f"Fator Previdenciário: {fator:.5f}")
        valor_final = media * fator
        st.success(f"Valor do benefício com FP: R$ {valor_final:,.2f}")
    else:
        st.warning("Preencha todos os campos com valores válidos.")

st.caption("Obs: A expectativa de vida é conforme tabela anual do IBGE. Se não souber, consulte a tabela referente ao ano da DER (Data de Entrada do Requerimento).")
