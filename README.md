# Mapa Eletropostos x Frota Plug-in (Brasil)

App Streamlit com mapa hexagonal das 27 UFs comparando a frota de veiculos
plug-in (eletricos + hibridos plug-in) com a quantidade de eletropostos ativos,
em quatro visoes: indice de pressao, frota plug-in, eletropostos ativos e
comparativo direto (frota x postos, com linha de meta 10:1).

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estrutura

- `app.py` — interface Streamlit e construcao dos graficos (Plotly).
- `dados_uf.py` — base de dados por UF e metodologia de calculo/estimativa.
- `.streamlit/config.toml` — tema.

## Dados

Ver o modulo `dados_uf.py` e o rodape do app para fontes e metodologia
(numeros reportados por imprensa especializada + estimativas proporcionais
transparentes para estados sem numero publicado individualmente).
