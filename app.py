"""Mapa coropletico: frota de veiculos plug-in x eletropostos por UF (Brasil)."""

import json
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from dados_uf import META_RAZAO, montar_tabela_uf

st.set_page_config(page_title="Mapa Eletropostos x Frota Plug-in", page_icon="🔌", layout="wide")

GEOJSON_PATH = Path(__file__).parent / "brasil_uf.geojson"

VIEWS = ["Indice de Pressao", "Frota Plug-in", "Eletropostos Ativos", "Comparativo Direto"]

# Paleta: diverging azul<->vermelho com meio-termo cinza neutro (nunca verde/vermelho,
# para nao depender da distincao de cor mais dificil para daltonismo); sequenciais de
# matiz unica, azul e laranja, claro->escuro.
DIVERGENTE_BAIXO = "#2a78d6"   # abaixo da meta (folga)
DIVERGENTE_MEIO = "#f0efec"    # neutro, na meta
DIVERGENTE_ALTO = "#e34948"    # acima da meta (pressao)
SEQ_AZUL = [[0, "#cde2fb"], [0.33, "#5598e7"], [0.66, "#256abf"], [1, "#0d366b"]]
SEQ_LARANJA = [[0, "#fce3d2"], [0.33, "#f3a467"], [0.66, "#d9711f"], [1, "#7a3a0f"]]
GRID_COLOR = "#e1e0d9"
MUTED_INK = "#898781"


@st.cache_data
def carregar_geojson() -> dict:
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        return json.load(f)


BR_GEOJSON = carregar_geojson()
TABELA = montar_tabela_uf()


def diverging_scale(values: list[float], mid: float, low_color: str, mid_color: str, high_color: str):
    vmin, vmax = min(values), max(values)
    if vmax == vmin:
        return [[0, mid_color], [1, mid_color]], vmin, vmax
    frac = (mid - vmin) / (vmax - vmin)
    frac = min(max(frac, 0.001), 0.999)
    return [[0, low_color], [frac, mid_color], [1, high_color]], vmin, vmax


def hover_estado(d: dict) -> str:
    return (
        f"<b>{d['nome']} ({d['sigla']})</b><br>"
        f"Regiao: {d['regiao']}<br>"
        f"Frota plug-in: {d['frota_plugin']:,}".replace(",", ".") + f" ({d['frota_fonte']})<br>"
        f"Eletropostos: {d['eletropostos']:,}".replace(",", ".") + f" ({d['eletropostos_fonte']})<br>"
        f"Razao veic./posto: {d['razao_veic_posto']}:1<br>"
        f"Indice de pressao (meta {META_RAZAO}:1): {d['indice_pressao']}<br>"
        f"Deficit de eletropostos p/ meta: {d['deficit_eletropostos']}"
    )


def build_choropleth(metric_key: str, title: str, colorscale, cmin=None, cmax=None, colorbar_title: str = ""):
    siglas = list(TABELA.keys())
    vals = [TABELA[uf][metric_key] for uf in siglas]
    hover = [hover_estado(TABELA[uf]) for uf in siglas]

    fig = go.Figure()
    fig.add_trace(
        go.Choropleth(
            geojson=BR_GEOJSON,
            featureidkey="properties.sigla",
            locations=siglas,
            z=vals,
            colorscale=colorscale,
            zmin=cmin,
            zmax=cmax,
            marker_line_color="white",
            marker_line_width=1,
            colorbar=dict(title=colorbar_title, thickness=14, len=0.75),
            hovertext=hover,
            hoverinfo="text",
        )
    )
    fig.add_trace(
        go.Scattergeo(
            lon=[TABELA[uf]["lon"] for uf in siglas],
            lat=[TABELA[uf]["lat"] for uf in siglas],
            text=siglas,
            mode="text",
            textfont=dict(size=10, color="#0b0b0b", family="Arial Black"),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(0,0,0,0)",
        projection_type="mercator",
    )
    fig.update_layout(
        title=title,
        margin=dict(l=0, r=0, t=50, b=0),
        height=640,
        paper_bgcolor="white",
    )
    return fig


def build_comparativo():
    """Ranking horizontal da razao veic./posto por UF, com linha de meta (delta-to-target)."""
    ordenado = sorted(TABELA.values(), key=lambda d: -d["razao_veic_posto"])
    siglas_labels = [f"{d['sigla']} — {d['nome']}" for d in ordenado]
    razoes = [d["razao_veic_posto"] for d in ordenado]
    hover = [hover_estado(d) for d in ordenado]

    scale, vmin, vmax = diverging_scale(
        razoes, mid=META_RAZAO, low_color=DIVERGENTE_BAIXO, mid_color=DIVERGENTE_MEIO, high_color=DIVERGENTE_ALTO
    )

    # rotulo direto apenas nos extremos (estado mais e menos pressionado) - nunca em todos os pontos
    textos = [""] * len(ordenado)
    textos[0] = f"{razoes[0]}:1"
    textos[-1] = f"{razoes[-1]}:1"

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=razoes,
            y=siglas_labels,
            orientation="h",
            marker=dict(
                color=razoes,
                colorscale=scale,
                cmin=vmin,
                cmax=vmax,
                colorbar=dict(title="Razao", thickness=12, len=0.75),
            ),
            text=textos,
            textposition="outside",
            textfont=dict(size=11),
            cliponaxis=False,
            hovertext=hover,
            hoverinfo="text",
        )
    )
    fig.add_vline(
        x=META_RAZAO,
        line_dash="dash",
        line_color=MUTED_INK,
        line_width=1.5,
        annotation_text=f"Meta {META_RAZAO}:1",
        annotation_position="top",
        annotation_font_color=MUTED_INK,
    )
    fig.update_layout(
        title="Razao veiculos plug-in por eletroposto, por UF (do mais ao menos pressionado)",
        xaxis=dict(title="Veiculos plug-in por eletroposto ativo", gridcolor=GRID_COLOR, zeroline=False),
        yaxis=dict(title="", autorange="reversed", tickfont=dict(size=11), automargin=True),
        bargap=0.3,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=70, t=60, b=40),
        height=920,
    )
    return fig


st.title("🔌 Frota Plug-in x Eletropostos — Mapa do Brasil")
st.caption(
    "Comparativo por UF entre a frota de veiculos plug-in (eletricos + hibridos plug-in) "
    "e a quantidade de eletropostos ativos, com indice de pressao em relacao a uma meta "
    "de referencia de 10 veiculos por eletroposto."
)

total_frota = sum(d["frota_plugin"] for d in TABELA.values())
total_postos = sum(d["eletropostos"] for d in TABELA.values())
razao_nacional = round(total_frota / total_postos, 1)
estados_acima_meta = sum(1 for d in TABELA.values() if d["indice_pressao"] > 1)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Frota plug-in (Brasil)", f"{total_frota:,}".replace(",", "."))
c2.metric("Eletropostos ativos (Brasil)", f"{total_postos:,}".replace(",", "."))
c3.metric("Razao nacional (veic./posto)", f"{razao_nacional}:1", help=f"Meta de referencia: {META_RAZAO}:1")
c4.metric("UFs acima da meta", f"{estados_acima_meta} de 27")

view = st.radio("Visao", VIEWS, horizontal=True)

if view == "Indice de Pressao":
    vals = [d["indice_pressao"] for d in TABELA.values()]
    scale, vmin, vmax = diverging_scale(
        vals, mid=1.0, low_color=DIVERGENTE_BAIXO, mid_color=DIVERGENTE_MEIO, high_color=DIVERGENTE_ALTO
    )
    fig = build_choropleth(
        "indice_pressao",
        "Indice de pressao sobre a infraestrutura (1.0 = meta de 10 veic./posto atingida)",
        scale,
        cmin=vmin,
        cmax=vmax,
        colorbar_title="Indice",
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)
    st.caption("Azul = folga de infraestrutura (abaixo da meta). Vermelho = pressao acima da meta (deficit de eletropostos).")

elif view == "Frota Plug-in":
    fig = build_choropleth(
        "frota_plugin",
        "Frota de veiculos plug-in por UF",
        SEQ_AZUL,
        colorbar_title="Veiculos",
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

elif view == "Eletropostos Ativos":
    fig = build_choropleth(
        "eletropostos",
        "Eletropostos ativos por UF",
        SEQ_LARANJA,
        colorbar_title="Eletropostos",
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

else:
    fig = build_comparativo()
    st.plotly_chart(fig, use_container_width=True, theme=None)
    st.caption("Barras acima da linha pontilhada representam UFs com mais veiculos por posto do que a meta de referencia.")

with st.expander("Ver tabela completa por UF"):
    linhas = sorted(TABELA.values(), key=lambda d: -d["frota_plugin"])
    st.dataframe(
        [
            {
                "UF": d["sigla"],
                "Estado": d["nome"],
                "Regiao": d["regiao"],
                "Frota plug-in": d["frota_plugin"],
                "Fonte (frota)": d["frota_fonte"],
                "Eletropostos": d["eletropostos"],
                "Fonte (postos)": d["eletropostos_fonte"],
                "Razao veic./posto": d["razao_veic_posto"],
                "Indice de pressao": d["indice_pressao"],
                "Deficit p/ meta": d["deficit_eletropostos"],
            }
            for d in linhas
        ],
        use_container_width=True,
        hide_index=True,
    )

st.markdown("---")
st.caption(
    "**Metodologia e fontes:** eletropostos reportados por Bright Consulting/AutoData (jul/2025) "
    "e total nacional ABVE/Tupi (set/2025, 16.880 pontos); frota plug-in nacional via Senatran, "
    "compilado pela NeoCharge (dez/2025, 354.329 veiculos BEV+PHEV), com distribuicao estadual "
    "baseada no ranking NeoCharge/Senatran dos 10 maiores estados. Estados sem numero publicado "
    "individualmente foram estimados por proporcionalidade populacional (IBGE) sobre o saldo "
    "nacional remanescente — ver coluna de fonte na tabela. A meta de 10 veiculos por eletroposto "
    "e um benchmark de referencia adotado pela aplicacao, nao uma meta oficial unica do governo. "
    "Fronteiras estaduais: click_that_hood (CC0), geometria simplificada."
)
