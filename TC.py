import streamlit as st
import pandas as pd
import cnis

upload_cnis = st.file_uploader("Importe o CNIS aqui 📥", type="pdf")

if upload_cnis:
    vinculos_extraidos = cnis.extrair_vinculos(upload_cnis)
    anos, meses, dias = cnis.calcular_tempo_contribuicao(vinculos_extraidos)
    todas_remuneracoes, media = cnis.calcular_media_remuneracoes(vinculos_extraidos)

    # Salva os dados no session_state
    st.session_state["vinculos_extraidos"] = vinculos_extraidos
    st.session_state["anos"] = anos
    st.session_state["meses"] = meses
    st.session_state["dias"] = dias
    st.session_state["media"] = media
    st.session_state["todas_remuneracoes"] = todas_remuneracoes

# Checa se os dados já foram processados (mesmo sem upload atual)
if "vinculos_extraidos" in st.session_state:
    st.subheader("Resumo Previdenciário")
    col1, col2, col3 = st.columns(3)
    tempo_formatado = f"{st.session_state['anos']}a {st.session_state['meses']}m {st.session_state['dias']}d"
    col1.metric("Tempo de Contribuição", tempo_formatado)
    col2.metric("Quantidade de Vínculos", len(st.session_state["vinculos_extraidos"]))
    col3.metric("Média dos Salários", f"R$ {st.session_state['media']:,.2f}")

    df = pd.DataFrame([
        {
            **{k: v for k, v in v.items() if k != "remuneracoes" and k != "raw"},
            "qtd_remuneracoes": len(v["remuneracoes"])
        }
        for v in st.session_state["vinculos_extraidos"]
    ])
    st.dataframe(df)
else:
    st.info("Por favor, importe o CNIS para visualizar o resumo previdenciário.")


if "vinculos_extraidos" in st.session_state:
    if st.button("🧹 Limpar"):
        # Lista de chaves a serem limpas do session_state
        for k in [
            "vinculos_extraidos", "todas_remuneracoes", "anos",
            "meses", "dias", "media"
        ]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()
