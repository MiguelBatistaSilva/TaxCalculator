import pdfplumber
import re
from datetime import datetime

def extrair_vinculos(upload_cnis):
    linhas = []
    with pdfplumber.open(upload_cnis) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                linhas.extend(texto.split('\n'))
    vinculos_extraidos = []
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
    return vinculos_extraidos

def parse_data(data_str):
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        return None

def calcular_tempo_contribuicao(vinculos_extraidos):
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
    return anos, meses, dias

def calcular_media_remuneracoes(vinculos_extraidos):
    todas_remuneracoes = []
    for v in vinculos_extraidos:
        for rem in v['remuneracoes']:
            mes, ano_rem = rem['competencia'].split('/')
            if int(ano_rem) > 1994 or (int(ano_rem) == 1994 and int(mes) >= 7):
                todas_remuneracoes.append(float(rem['valor']))
    if todas_remuneracoes:
        media = sum(todas_remuneracoes) / len(todas_remuneracoes)
    else:
        media = 0.0
    return todas_remuneracoes, media