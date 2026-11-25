"""Mapa hexagonal: frota de veiculos plug-in x eletropostos por UF (Brasil)."""

import math

import plotly.graph_objects as go
import streamlit as st

from dados_uf import REGIAO_COLORS, REGIAO_ORDER, META_RAZAO, montar_tabela_uf

st.set_page_config(page_title="Mapa Eletropostos x Frota Plug-in", page_icon="🔌", layout="wide")

TABELA = montar_tabela_uf()

VIEWS = ["Indice de Pressao", "Frota Plug-in", "Eletropostos Ativos", "Comparativo Direto"]

HEX_SIZE = 46


def hex_xy(row: int, col: int) -> tuple[float, float]:
    x = math.sqrt(3) * (col + 0.5 * (row % 2))
    y = -1.5 * row
    return x, y


def diverging_scale(values: list[float], mid: float, low_color: str, mid_color: str, high_color: str):
    vmin, vmax = min(values), max(values)
    if vmax == vmin:
        return [[0, mid_color], [1, mid_color]], vmin, vmax
    frac = (mid - vmin) / (vmax - vmin)
    frac = min(max(frac, 0.001), 0.999)
    return [[0, low_color], [frac, mid_color], [1, high_color]], vmin, vmax


def build_hexmap(metric_key: str, title: str, colorscale, cmin=None, cmax=None, colorbar_title=""):
    siglas, xs, ys, vals, hover = [], [], [], [], []
    for uf, d in TABELA.items():
        x, y = hex_xy(d["hex_row"], d["hex_col"])
        siglas.append(uf)
        xs.append(x)
        ys.append(y)
        vals.append(d[metric_key])
        hover.append(
            f"<b>{d['nome']} ({uf})</b><br>"
            f"Regiao: {d['regiao']}<br>"
            f"Frota plug-in: {d['frota_plugin']:,}".replace(",", ".") + f" ({d['frota_fonte']})<br>"
            f"Eletropostos: {d['eletropostos']:,}".replace(",", ".") + f" ({d['eletropostos_fonte']})<br>"
            f"Razao veic./posto: {d['razao_veic_posto']}:1<br>"
            f"Indice de pressao (meta {META_RAZAO}:1): {d['indice_pressao']}<br>"
            f"Deficit de eletropostos p/ meta: {d['deficit_eletropostos']}"
        )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers+text",
            marker=dict(
                symbol="hexagon",
                size=HEX_SIZE,
                color=vals,
                colorscale=colorscale,
                cmin=cmin,
                cmax=cmax,
                line=dict(color="white", width=1.5),
                colorbar=dict(title=colorbar_title, thickness=14),
            ),
            text=siglas,
            textfont=dict(size=12, color="#1a1a1a", family="Arial Black"),
            hovertext=hover,
            hoverinfo="text",
            showlegend=False,
        )
    )
    fig.update_layout(
        title=title,
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=50, b=10),
        height=640,
    )
    return fig


def build_comparativo():
    fig = go.Figure()
    max_e = max(d["eletropostos"] for d in TABELA.values())
    linha_x = [0, max_e * 1.15]
    linha_y = [0, max_e * 1.15 * META_RAZAO]
    fig.add_trace(
        go.Scatter(
            x=linha_x,
            y=linha_y,
            mode="lines",
            line=dict(color="#999999", width=1.5, dash="dash"),
            name=f"Meta {META_RAZAO}:1",
            hoverinfo="skip",
        )
    )
    for regiao in REGIAO_ORDER:
        estados = [d for d in TABELA.values() if d["regiao"] == regiao]
        if not estados:
            continue
        fig.add_trace(
            go.Scatter(
                x=[d["eletropostos"] for d in estados],
                y=[d["frota_plugin"] for d in estados],
                mode="markers+text",
                marker=dict(
                    size=[8 + d["populacao_mi"] * 1.1 for d in estados],
                    color=REGIAO_COLORS[regiao],
                    line=dict(color="white", width=1),
                ),
                text=[d["sigla"] for d in estados],
                textposition="top center",
                textfont=dict(size=10),
                name=regiao,
                hovertext=[
                    f"<b>{d['nome']} ({d['sigla']})</b><br>"
                    f"Eletropostos: {d['eletropostos']:,}".replace(",", ".")
                    + f"<br>Frota plug-in: {d['frota_plugin']:,}".replace(",", ".")
                    + f"<br>Razao: {d['razao_veic_posto']}:1"
                    for d in estados
                ],
                hoverinfo="text",
            )
        )
    fig.update_layout(
        title="Comparativo direto: frota plug-in vs. eletropostos (acima da linha = acima da meta 10:1)",
        xaxis=dict(title="Eletropostos ativos (escala log)", type="log"),
        yaxis=dict(title="Frota plug-in (escala log)", type="log"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=70, b=10),
        height=640,
    )
    return fig


st.title("🔌 Frota Plug-in x Eletropostos — Mapa Hexagonal do Brasil")
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
    scale, vmin, vmax = diverging_scale(vals, mid=1.0, low_color="#1b7a4a", mid_color="#f2efe9", high_color="#c23b22")
    fig = build_hexmap(
        "indice_pressao",
        "Indice de pressao sobre a infraestrutura (1.0 = meta de 10 veic./posto atingida)",
        scale,
        cmin=vmin,
        cmax=vmax,
        colorbar_title="Indice",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Verde = folga de infraestrutura (abaixo da meta). Vermelho = pressao acima da meta (deficit de eletropostos).")

elif view == "Frota Plug-in":
    fig = build_hexmap(
        "frota_plugin",
        "Frota de veiculos plug-in por UF",
        [[0, "#eaf1fb"], [1, "#1a4d8f"]],
        colorbar_title="Veiculos",
    )
    st.plotly_chart(fig, use_container_width=True)

elif view == "Eletropostos Ativos":
    fig = build_hexmap(
        "eletropostos",
        "Eletropostos ativos por UF",
        [[0, "#e8f8f1"], [1, "#0f6b45"]],
        colorbar_title="Eletropostos",
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    fig = build_comparativo()
    st.plotly_chart(fig, use_container_width=True)

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
    "e um benchmark de referencia adotado pela aplicacao, nao uma meta oficial unica do governo."
)
