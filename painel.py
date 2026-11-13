"""Painel do OuvidorSUS 3 (2023 a 2025).

Versão para publicação. Para abrir:   streamlit run painel.py
"""

from __future__ import annotations
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

_PASTA = Path(__file__).parent
# aceita a base na mesma pasta do painel ou dentro de uma pasta chamada dados
SAIDA = next(
    (p for p in (_PASTA / "ouv3_tratado.parquet", _PASTA / "dados" / "ouv3_tratado.parquet") if p.exists()),
    _PASTA / "ouv3_tratado.parquet",
)

AZUL = "#12355B"
PETROLEO = "#1F6F8B"
CINZA = "#8A99A3"

st.set_page_config(page_title="OuvidorSUS 3", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1280px;}
    h1 {font-size: 1.9rem; margin-bottom: 0.2rem;}
    [data-testid="stMetricValue"] {font-size: 1.7rem; color: #12355B;}
    </style>
    """,
    unsafe_allow_html=True,
)


def inteiro(n: float) -> str:
    """Formata número no padrão brasileiro: 1.234.567"""
    return f"{int(n):,}".replace(",", ".")


def percentual(parte: float, total: float) -> str:
    if total == 0:
        return "0,0%"
    return f"{100 * parte / total:.1f}%".replace(".", ",")


@st.cache_data(show_spinner="Carregando os dados...")
def carregar(marca_de_modificacao: float) -> pd.DataFrame:
    return pd.read_parquet(SAIDA)


def contar(df: pd.DataFrame, coluna: str, topo: int | None = None) -> pd.DataFrame:
    """Conta manifestações por categoria, ordenado do maior para o menor."""
    serie = df[coluna].astype("object").fillna("Não informado")
    tabela = serie.value_counts().rename_axis(coluna).reset_index(name="Manifestações")
    return tabela.head(topo) if topo else tabela


def barras(tabela: pd.DataFrame, coluna: str, rotulo: str, altura: int = 360):
    """Gráfico de barras horizontais, com a maior categoria no topo."""
    tabela = tabela.iloc[::-1]
    fig = px.bar(
        tabela,
        x="Manifestações",
        y=coluna,
        orientation="h",
        text="Manifestações",
        labels={coluna: rotulo},
        color_discrete_sequence=[AZUL],
    )
    fig.update_traces(
        texttemplate="%{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}<br>%{x:,.0f} manifestações<extra></extra>",
    )
    fig.update_layout(
        height=altura,
        margin=dict(l=0, r=40, t=10, b=0),
        xaxis_title=None,
        yaxis_title=None,
        xaxis_showgrid=False,
        xaxis_showticklabels=False,
        plot_bgcolor="white",
        separators=",.",
    )
    return fig


# ---------------------------------------------------------------- dados
if not SAIDA.exists():
    st.title("OuvidorSUS 3")
    st.error("A base de dados não foi encontrada. Verifique se o arquivo ouv3_tratado.parquet foi enviado junto com o painel.")
    st.stop()

df = carregar(SAIDA.stat().st_mtime)

# -------------------------------------------------------------- filtros
st.sidebar.header("Filtros")
st.sidebar.caption("Deixe vazio para incluir todos.")


def filtro(rotulo: str, coluna: str):
    opcoes = sorted(df[coluna].dropna().astype(str).unique())
    return st.sidebar.multiselect(rotulo, opcoes)


anos = st.sidebar.multiselect("Ano", sorted(df["ano"].unique()))
classes = filtro("Classificação", "classificacao_manifestacao")
canais = filtro("Canal de entrada", "canal_entrada")
esferas = filtro("Esfera da ouvidoria de destino", "esfera_ouvidoria_destino")
ufs = filtro("UF da ouvidoria de origem", "uf_ouvidoria_origem")
situacoes = filtro("Situação da manifestação", "status_manifestacao")

mascara = pd.Series(True, index=df.index)
for valores, coluna in (
    (anos, "ano"),
    (classes, "classificacao_manifestacao"),
    (canais, "canal_entrada"),
    (esferas, "esfera_ouvidoria_destino"),
    (ufs, "uf_ouvidoria_origem"),
    (situacoes, "status_manifestacao"),
):
    if valores:
        mascara &= df[coluna].isin(valores)
dados = df[mascara]

# ------------------------------------------------------------ cabeçalho
st.title("OuvidorSUS 3: manifestações registradas")
st.caption(
    "Fonte: Portal de Dados Abertos do SUS, Sistema de Ouvidoria do SUS (OuvidorSUS 3), "
    "arquivos de 2023, 2024 e 2025. Painel feito com dados abertos, sem caráter oficial."
)

if dados.empty:
    st.warning("Nenhuma manifestação com os filtros escolhidos. Retire algum filtro.")
    st.stop()

total = len(dados)
concluidas = (dados["status_manifestacao"] == "CONCLUÍDA").sum()
em_analise = (dados["status_manifestacao"] == "EM ANÁLISE").sum()
classe_top = contar(dados, "classificacao_manifestacao").iloc[0]
canal_top = contar(dados, "canal_entrada").iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Manifestações", inteiro(total))
c2.metric("Concluídas", percentual(concluidas, total))
c3.metric(
    "Classificação mais frequente",
    str(classe_top["classificacao_manifestacao"]).capitalize(),
    percentual(classe_top["Manifestações"], total),
    delta_color="off",
)
c4.metric(
    "Canal mais usado",
    str(canal_top["canal_entrada"]).capitalize(),
    percentual(canal_top["Manifestações"], total),
    delta_color="off",
)

# ------------------------------------------------------- evolução mensal
st.subheader("Evolução mensal")
mensal = dados.groupby("mes", observed=True).size().reset_index(name="Manifestações")
fig = px.line(mensal, x="mes", y="Manifestações", markers=True, color_discrete_sequence=[PETROLEO])
fig.update_traces(hovertemplate="%{x|%m/%Y}<br>%{y:,.0f} manifestações<extra></extra>")
fig.update_layout(
    height=340,
    margin=dict(l=0, r=0, t=10, b=0),
    xaxis_title=None,
    yaxis_title=None,
    plot_bgcolor="white",
    yaxis_gridcolor="#E6ECEF",
    separators=",.",
)
fig.update_xaxes(tickformat="%m/%Y")
st.plotly_chart(fig, width="stretch")
st.caption(
    "O OuvidorSUS 3 começou a ser usado em novembro de 2023 e a migração das ouvidorias "
    "ainda está em andamento. Parte do crescimento da série vem de novas ouvidorias "
    "entrando no sistema, e não necessariamente de mais demanda."
)

# ------------------------------------------------------------- gráficos
esq, dir_ = st.columns(2)
with esq:
    st.subheader("Classificação")
    st.plotly_chart(
        barras(contar(dados, "classificacao_manifestacao"), "classificacao_manifestacao", "Classificação"),
        width="stretch",
    )
with dir_:
    st.subheader("Canal de entrada")
    st.plotly_chart(
        barras(contar(dados, "canal_entrada"), "canal_entrada", "Canal"),
        width="stretch",
    )

st.subheader("UF da ouvidoria de origem")
st.plotly_chart(
    barras(contar(dados, "uf_ouvidoria_origem"), "uf_ouvidoria_origem", "UF", altura=720),
    width="stretch",
)

st.subheader("Assuntos mais frequentes")
st.plotly_chart(
    barras(contar(dados, "assunto", topo=15), "assunto", "Assunto", altura=520),
    width="stretch",
)

esq, dir_ = st.columns(2)
with esq:
    st.subheader("Tipo de problema")
    st.plotly_chart(
        barras(contar(dados, "status_problema"), "status_problema", "Tipo de problema"),
        width="stretch",
    )
with dir_:
    st.subheader("Esfera da ouvidoria de destino")
    st.plotly_chart(
        barras(contar(dados, "esfera_ouvidoria_destino"), "esfera_ouvidoria_destino", "Esfera", altura=240),
        width="stretch",
    )

# --------------------------------------------------------------- tabela
with st.expander("Tabela mensal por classificação"):
    tabela = (
        dados.assign(mes=dados["mes"].dt.strftime("%m/%Y"))
        .pivot_table(
            index="mes",
            columns="classificacao_manifestacao",
            values="ano",
            aggfunc="size",
            fill_value=0,
            observed=True,
        )
    )
    tabela["Total"] = tabela.sum(axis=1)
    ordem = pd.to_datetime(tabela.index, format="%m/%Y").argsort()
    tabela = tabela.iloc[ordem]
    st.dataframe(tabela, width="stretch")
    st.download_button(
        "Baixar tabela em CSV",
        tabela.to_csv(sep=";", encoding="utf-8-sig").encode("utf-8-sig"),
        file_name="ouvidorsus3_mensal_por_classificacao.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------- observações
with st.expander("Cuidados com a leitura dos dados"):
    corrigidas = int(df["ano_foi_corrigido"].sum())
    st.markdown(
        f"""
- **Ano da data corrigido.** Em {inteiro(corrigidas)} linhas ({percentual(corrigidas, len(df))}) a
  data original trazia um ano diferente do arquivo, inclusive anos que ainda não chegaram.
  Seguindo a regra definida, todas as linhas de cada arquivo foram consideradas do ano do arquivo,
  mantendo dia e mês.
- **Linhas repetidas mantidas.** Os arquivos não têm número de protocolo, então não é possível
  separar duplicatas de manifestações realmente idênticas.
- **Campos vazios.** Em 2025, cerca de 11% das linhas estão sem assunto e sem tipo de problema.
  Essas linhas aparecem como "Não informado".
- **Sem tempo de resposta.** A base não traz a data de conclusão, então não há como calculá-lo.
- **Tipificação.** As regras de tipificação mudam entre as versões do sistema. Consulte o manual
  do OuvidorSUS 3 ao interpretar assuntos e subassuntos.
"""
    )
