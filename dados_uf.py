"""Dados publicos sobre frota de veiculos plug-in e eletropostos por UF.

FONTES E METODOLOGIA (resumo; ver tambem o rodape do app):

- Eletropostos por UF: numeros reportados para os estados com cobertura mais
  ampla na imprensa especializada (Bright Consulting, via AutoData, jul/2025;
  menor numero de postos do pais via o mesmo levantamento). Total nacional de
  ancora: ABVE/Tupi (set/2025) = 16.880 eletropostos publicos/semipublicos.
  Estados sem numero publicado individualmente foram estimados repartindo o
  saldo nacional remanescente de forma proporcional a populacao (IBGE, estimativa
  2024) -- marcados como "estimado" na tabela do app.

- Frota plug-in (veiculos 100% eletricos + hibridos plug-in, que dependem de
  recarga externa) nacional: Senatran, compilado pela NeoCharge (dez/2025) =
  154.085 eletricos + 200.244 hibridos plug-in = 354.329 veiculos.
  Distribuicao por estado: ranking NeoCharge/Senatran dos 10 maiores estados
  (base 2024) usado como peso relativo e recalibrado proporcionalmente para o
  total nacional de dez/2025 (representando ~80% do total, consistente com a
  concentracao historica nesses 10 estados). Os demais 17 estados dividem o
  saldo remanescente (~20%) proporcionalmente a populacao -- marcados como
  "estimado".

- Meta de referencia 10 veiculos plug-in por eletroposto: benchmark de
  planejamento adotado por esta aplicacao para comparar estados, inspirado em
  faixas discutidas no setor (nao e uma meta oficial unica do governo
  brasileiro).

Como os dados publicos por estado estao fragmentados entre fontes com
metodologias diferentes (vendas x frota circulante, publico x semipublico
etc.), os valores "estimados" sao modelos transparentes, nao contagens
oficiais -- use a coluna de fonte na tabela do app para distinguir.
"""

from __future__ import annotations

NOME_REGIAO = {
    "Norte": "Norte",
    "Nordeste": "Nordeste",
    "Centro-Oeste": "Centro-Oeste",
    "Sudeste": "Sudeste",
    "Sul": "Sul",
}

REGIAO_ORDER = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

REGIAO_COLORS = {
    "Norte": "#2a78d6",
    "Nordeste": "#eb6834",
    "Centro-Oeste": "#1baf7a",
    "Sudeste": "#eda100",
    "Sul": "#e87ba4",
}

# sigla -> (nome, regiao, populacao em milhoes [IBGE, estimativa 2024], (linha, coluna) no grid hexagonal)
UF_INFO = {
    "AC": ("Acre", "Norte", 0.9, (3, 2)),
    "AL": ("Alagoas", "Nordeste", 3.3, (4, 13)),
    "AP": ("Amapa", "Norte", 0.87, (0, 8)),
    "AM": ("Amazonas", "Norte", 4.3, (2, 4)),
    "BA": ("Bahia", "Nordeste", 14.9, (4, 11)),
    "CE": ("Ceara", "Nordeste", 9.3, (2, 12)),
    "DF": ("Distrito Federal", "Centro-Oeste", 3.1, (5, 9)),
    "ES": ("Espirito Santo", "Sudeste", 4.1, (7, 12)),
    "GO": ("Goias", "Centro-Oeste", 7.3, (5, 8)),
    "MA": ("Maranhao", "Nordeste", 7.1, (2, 10)),
    "MT": ("Mato Grosso", "Centro-Oeste", 3.8, (4, 6)),
    "MS": ("Mato Grosso do Sul", "Centro-Oeste", 2.9, (7, 7)),
    "MG": ("Minas Gerais", "Sudeste", 21.3, (6, 10)),
    "PA": ("Para", "Norte", 8.3, (2, 8)),
    "PB": ("Paraiba", "Nordeste", 4.1, (3, 13)),
    "PR": ("Parana", "Sul", 11.8, (8, 8)),
    "PE": ("Pernambuco", "Nordeste", 9.5, (3, 12)),
    "PI": ("Piaui", "Nordeste", 3.3, (3, 11)),
    "RJ": ("Rio de Janeiro", "Sudeste", 16.7, (7, 11)),
    "RN": ("Rio Grande do Norte", "Nordeste", 3.4, (2, 13)),
    "RS": ("Rio Grande do Sul", "Sul", 11.3, (10, 7)),
    "RO": ("Rondonia", "Norte", 1.8, (4, 4)),
    "RR": ("Roraima", "Norte", 0.65, (0, 5)),
    "SC": ("Santa Catarina", "Sul", 8.0, (9, 8)),
    "SP": ("Sao Paulo", "Sudeste", 46.0, (7, 9)),
    "SE": ("Sergipe", "Nordeste", 2.3, (4, 13)),
    "TO": ("Tocantins", "Norte", 1.6, (4, 9)),
}
# corrige colisao SE/AL no grid: SE fica uma coluna a oeste de AL
UF_INFO["SE"] = ("Sergipe", "Nordeste", 2.3, (4, 13))
UF_INFO["AL"] = ("Alagoas", "Nordeste", 3.3, (4, 14))

ELETROPOSTOS_REPORTADOS = {
    "SP": 4500,
    "RJ": 1400,
    "RS": 1159,
    "MG": 1154,
    "SC": 1100,
    "PR": 1027,
    "RR": 5,
    "AC": 6,
    "AP": 6,
}
ELETROPOSTOS_NACIONAL = 16880

# Ranking NeoCharge/Senatran (base 2024) usado como peso relativo entre os 10 maiores estados.
FROTA_PESO_BASE = {
    "SP": 47101,
    "MG": 10386,
    "RJ": 10183,
    "SC": 9704,
    "PR": 9312,
    "RS": 7704,
    "DF": 6947,
    "GO": 5180,
    "BA": 4949,
    "ES": 3787,
}
FROTA_NACIONAL = 354329  # Senatran/NeoCharge dez/2025: 154.085 BEV + 200.244 PHEV
FROTA_TOP10_SHARE = 0.80  # parcela nacional atribuida aos 10 estados do ranking

META_RAZAO = 10  # meta de referencia: 10 veiculos plug-in por eletroposto


def _distribuir_proporcional(saldo: float, estados: list[str]) -> dict[str, int]:
    pop_total = sum(UF_INFO[uf][2] for uf in estados)
    valores = {uf: (UF_INFO[uf][2] / pop_total) * saldo for uf in estados}
    inteiros = {uf: round(v) for uf, v in valores.items()}
    return inteiros


def _montar_eletropostos() -> dict[str, dict]:
    todos = list(UF_INFO.keys())
    conhecidos = ELETROPOSTOS_REPORTADOS
    restantes = [uf for uf in todos if uf not in conhecidos]
    saldo = ELETROPOSTOS_NACIONAL - sum(conhecidos.values())
    estimados = _distribuir_proporcional(saldo, restantes)
    out = {}
    for uf in todos:
        if uf in conhecidos:
            out[uf] = {"valor": conhecidos[uf], "fonte": "reportado"}
        else:
            out[uf] = {"valor": estimados[uf], "fonte": "estimado"}
    return out


def _montar_frota() -> dict[str, dict]:
    todos = list(UF_INFO.keys())
    top10 = list(FROTA_PESO_BASE.keys())
    restantes = [uf for uf in todos if uf not in top10]

    alvo_top10 = FROTA_NACIONAL * FROTA_TOP10_SHARE
    peso_total = sum(FROTA_PESO_BASE.values())
    fator = alvo_top10 / peso_total
    valores_top10 = {uf: round(FROTA_PESO_BASE[uf] * fator) for uf in top10}

    saldo_restante = FROTA_NACIONAL - sum(valores_top10.values())
    estimados = _distribuir_proporcional(saldo_restante, restantes)

    out = {}
    for uf in top10:
        out[uf] = {"valor": valores_top10[uf], "fonte": "reportado (estimado por ranking regional)"}
    for uf in restantes:
        out[uf] = {"valor": estimados[uf], "fonte": "estimado"}
    return out


def montar_tabela_uf() -> dict[str, dict]:
    """Retorna, para cada UF, frota plug-in, eletropostos, fontes e metricas derivadas."""
    eletropostos = _montar_eletropostos()
    frota = _montar_frota()
    tabela = {}
    for uf, (nome, regiao, pop, hexpos) in UF_INFO.items():
        f = frota[uf]["valor"]
        e = eletropostos[uf]["valor"]
        razao = f / e if e else float("inf")
        indice_pressao = razao / META_RAZAO
        eletropostos_necessarios = max(0, round(f / META_RAZAO) - e)
        tabela[uf] = {
            "sigla": uf,
            "nome": nome,
            "regiao": regiao,
            "populacao_mi": pop,
            "hex_row": hexpos[0],
            "hex_col": hexpos[1],
            "frota_plugin": f,
            "frota_fonte": frota[uf]["fonte"],
            "eletropostos": e,
            "eletropostos_fonte": eletropostos[uf]["fonte"],
            "razao_veic_posto": round(razao, 1),
            "indice_pressao": round(indice_pressao, 2),
            "deficit_eletropostos": eletropostos_necessarios,
        }
    return tabela
