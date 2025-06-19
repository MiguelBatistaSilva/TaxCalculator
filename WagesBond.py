import streamlit as st
import pandas as pd

if "vinculos_extraidos" not in st.session_state:
    st.warning("Importe e processe o CNIS na página 'Tempo de Contribuição' antes de acessar esta funcionalidade.")
    st.stop()

vinculos_extraidos = st.session_state["vinculos_extraidos"]

for i, v in enumerate(vinculos_extraidos):
    with st.expander(f"Vínculo {i+1} | {v['empresa']}"):
        if v["remuneracoes"]:
            remu_df = pd.DataFrame(v["remuneracoes"])
            st.dataframe(remu_df)
        else:
            st.info("Sem remunerações registradas para este vínculo.")
