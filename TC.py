import pdfplumber
import streamlit as st
import re
import pandas as pd
from datetime import datetime

st.header("Tempo de Contribuição + RMI")
upload_cnis = st.file_uploader("Importe o CNIS aqui 📥", type="pdf")
vinculos_extraidos = []

if upload_cnis:
    # --- [BLOCO 1: EXTRAÇÃO DO CNIS] ---
    linhas = []
    with pdfplumber.open(upload_cnis) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                linhas.extend(texto.split('\n'))

    idx = 0
    while idx < len(linhas):
        linha = linhas[idx]
        if linha.strip().startswith('Seq.'):
            raw = linhas[idx + 1]
            if idx + 2 < len(linhas) and not linhas[idx + 2].startswith("Remunerações"):
                raw += " " + linhas[idx + 2]

            seq = re.search(r"^\d+", raw)
            nit = re.search(r"\d{3}\.\d{5}\.\d{2}-\d", raw)
            cnpj = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", raw) or re.search(r"\d{2}\.\d{3}\.\d{3}", raw)
            datas = re.findall(r"\d{2}/\d{2}/\d{4}", raw)
            tipo = "Empregado" if "Empregado" in raw else "Outro"
            empresa = ""
            if cnpj:
                partes = raw.split(cnpj.group())
                if len(partes) > 1:
                    empresa = partes[1].split(tipo)[0].strip()
            data_inicio = datas[0] if len(datas) > 0 else ""
            data_fim = datas[1] if len(datas) > 1 else ""
            ult_remun = re.findall(r"\d{2}/\d{4}", raw)
            ult_remun = ult_remun[-1] if ult_remun else ""

            remuneracoes = []
            busca_idx = idx + 1
            while busca_idx < len(linhas) and not linhas[busca_idx].strip().startswith('Remunerações'):
                busca_idx += 1
            if busca_idx < len(linhas) and linhas[busca_idx].strip().startswith('Remunerações'):
                busca_idx += 1
                while busca_idx < len(linhas):
                    l_remu = linhas[busca_idx].strip()
                    if not l_remu or l_remu.startswith('Matrícula do') or l_remu.startswith('Seq.'):
                        break
                    if re.match(r"^\d{2}/\d{4}(\s+[\d.,]+)?", l_remu):
                        matchs = re.findall(r"(\d{2}/\d{4})\s+([\d.,]+)", l_remu)
                        for m in matchs:
                            remuneracoes.append({
                                "competencia": m[0],
                                "valor": m[1].replace('.', '').replace(',', '.')
                            })
                    elif re.match(r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}", l_remu):
                        pass
                    busca_idx += 1

            vinculos_extraidos.append({
                "sequencia": seq.group() if seq else "",
                "NIT": nit.group() if nit else "",
                "CNPJ": cnpj.group() if cnpj else "",
                "empresa": empresa,
                "tipo": tipo,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "ultima_remuneracao": ult_remun,
                "remuneracoes": remuneracoes,
                "raw": raw
            })
            idx = busca_idx
        else:
            idx += 1

    # --- [BLOCO 2: CALCULAR O TEMPO DE CONTRIBUIÇÃO] ---
    def parse_data(data_str):
        try:
            return datetime.strptime(data_str, "%d/%m/%Y")
        except ValueError:
            return None

    total_dias = 0
    for v in vinculos_extraidos:
        inicio = parse_data(v["data_inicio"])
        fim = parse_data(v["data_fim"])
        if inicio and fim:
            dias = (fim - inicio).days + 1
            total_dias += dias
        elif inicio and not fim:
            fim = datetime.today()
            dias = (fim - inicio).days + 1
            total_dias += dias

    anos = total_dias // 365
    meses = (total_dias % 365) // 30
    dias = (total_dias % 365) % 30

    # --- [BLOCO 3: CÁLCULO DA MÉDIA DOS SALÁRIOS] ---
    todas_remuneracoes = []
    for v in vinculos_extraidos:
        for rem in v['remuneracoes']:
            mes, ano_rem = rem['competencia'].split('/')
            if int(ano_rem) > 1994 or (int(ano_rem) == 1994 and int(mes) >= 7):
                todas_remuneracoes.append(float(rem['valor']))

    if vinculos_extraidos:
        df = pd.DataFrame([
            {
                **{k: v for k, v in v.items() if k != "remuneracoes" and k != "raw"},
                "qtd_remuneracoes": len(v["remuneracoes"])
            }
            for v in vinculos_extraidos
        ])

        if todas_remuneracoes:
            media = sum(todas_remuneracoes) / len(todas_remuneracoes)
        else:
            media = 0.0

        st.session_state["vinculos_extraidos"] = vinculos_extraidos
        st.session_state["todas_remuneracoes"] = todas_remuneracoes
        st.session_state["anos"] = anos
        st.session_state["meses"] = meses
        st.session_state["dias"] = dias
        st.session_state["media"] = media

        # --- [Painel de métricas acima da tabela] ---
        st.subheader("Resumo Previdenciário")
        col1, col2, col3 = st.columns(3)
        tempo_formatado = f"{anos}a {meses}m {dias}d"
        col1.metric("Tempo de Contribuição", tempo_formatado)
        col2.metric("Quantidade de Vínculos", len(vinculos_extraidos))
        col3.metric("Média dos Salários", f"R$ {media:,.2f}")
        st.write("")

        # --- [Tabela de vínculos] ---
        st.dataframe(df)

        # --- [Remunerações detalhadas por vínculo] ---
        st.subheader("Remunerações detalhadas por vínculo")
        for i, v in enumerate(vinculos_extraidos):
            with st.expander(f"Vínculo {i+1} | {v['empresa']}"):
                if v["remuneracoes"]:
                    remu_df = pd.DataFrame(v["remuneracoes"])
                    st.dataframe(remu_df)
                else:
                    st.info("Sem remunerações registradas para este vínculo.")

        # --- [Cálculo da RMI] ---
        if todas_remuneracoes:
            tempo = st.number_input("Tempo total de contribuição (anos)", min_value=0, max_value=50, value=anos)
            sexo = st.radio("Sexo", ["Masculino", "Feminino"])
            coef_base = 20 if sexo == "Masculino" else 15
            coef = 60 + 2 * max(0, tempo - coef_base)

            if st.button("Calcular RMI"):
                rmi = media * coef / 100
                st.success(f"Coeficiente aplicado: {coef:.0f}%")
                st.success(f"Renda Mensal Inicial (RMI): R$ {rmi:,.2f}")
        else:
            st.warning("Nenhuma remuneração extraída válida para o cálculo do RMI.")

    else:
        st.warning("Nenhum vínculo foi encontrado no PDF importado.")

