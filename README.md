# Mapa Eletropostos x Frota Plug-in (Brasil)

App Streamlit com mapa coropletico geografico real das 27 UFs (fronteiras
GeoJSON) comparando a frota de veiculos plug-in (eletricos + hibridos plug-in)
com a quantidade de eletropostos ativos, em quatro visoes: indice de pressao
(escala divergente azul-cinza-vermelho), frota plug-in e eletropostos ativos
(escalas sequenciais azul/laranja), e comparativo direto (ranking em barras
horizontais da razao veic./posto por UF, com linha de meta 10:1).

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estrutura

- `app.py` — interface Streamlit e construcao dos graficos (Plotly `go.Choropleth` + `go.Bar`).
- `dados_uf.py` — base de dados por UF e metodologia de calculo/estimativa.
- `brasil_uf.geojson` — fronteiras estaduais (click_that_hood, CC0), simplificadas.
- `.streamlit/config.toml` — tema.

## Dados

Ver o modulo `dados_uf.py` e o rodape do app para fontes e metodologia
(numeros reportados por imprensa especializada + estimativas proporcionais
transparentes para estados sem numero publicado individualmente).
