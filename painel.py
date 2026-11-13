"""Painel do OuvidorSUS 3 (2023 a 2025).

Para abrir:   streamlit run painel.py
Arquivos necessários na mesma pasta: ouv3_tratado.parquet e br_estados.geojson
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PASTA = Path(__file__).parent
SAIDA = PASTA / "ouv3_tratado.parquet"
if not SAIDA.exists():
    SAIDA = PASTA / "dados" / "ouv3_tratado.parquet"
MAPA = PASTA / "br_estados.geojson"
FONTE_URL = "https://dadosabertos.saude.gov.br/dataset/ouvidorsus"

# ------------------------------------------------------------------ cores
MARINHO = "#12355B"
AMBAR = "#F5A524"
AZUL = "#3E7CC4"
CEU = "#8DB6E8"
VERDE_AZULADO = "#2A9D8F"
CORAL = "#E4572E"
ROXO = "#7A5C99"
CINZA = "#5B6B7F"
TEXTO = "#1B2A3A"
SEQUENCIA = [MARINHO, AMBAR, AZUL, CEU, VERDE_AZULADO, CORAL, ROXO, "#9AA7B8"]
COR_CLASSIFICACAO = {
    "Solicitação": MARINHO,
    "Reclamação": AMBAR,
    "Elogio": VERDE_AZULADO,
    "Denúncia": CORAL,
    "Comunicação de irregularidade": ROXO,
    "Informação": CEU,
    "Sugestão": AZUL,
}
SIGLAS = {"sus", "uti", "cnes", "epi", "cpf", "crm", "sinan", "sisab", "hiv", "aids", "ubs", "upa", "samu"}

st.set_page_config(page_title="Manifestações de Ouvidorias do SUS", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, .stApp, [data-testid="stSidebar"] {font-family: 'Plus Jakarta Sans', sans-serif;}
.stApp {background: #EEF2F8;}
.block-container {padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1320px;}
header[data-testid="stHeader"] {background: transparent;}

/* painel lateral */
[data-testid="stSidebar"] {background: #12355B;}
[data-testid="stSidebar"] label p, [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color: #C9D6EA !important; font-weight: 600;}
[data-testid="stSidebar"] [data-baseweb="select"] > div {background: #FFFFFF; border-radius: 8px; border: none;}
[data-baseweb="tag"] {background: #F5A524 !important;}
[data-baseweb="tag"] span {color: #12355B !important; font-weight: 600;}
.marca {color: #FFFFFF; font-size: 1.5rem; font-weight: 800; line-height: 1.15; margin: 0.2rem 0 0.2rem 0;}
.marca span {display: block; color: #F5A524; font-size: 0.82rem; font-weight: 600; margin-top: 4px;}
.lateral-titulo {color: #FFFFFF; font-weight: 700; font-size: 0.95rem; margin: 1.4rem 0 0.2rem 0; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.18);}
.lateral-nota {color: #9FB4D3; font-size: 0.76rem; line-height: 1.4; margin-top: 1.2rem;}

/* título */
.titulo {color: #12355B; font-size: 2rem; font-weight: 800; margin: 0; line-height: 1.15;}
.subtitulo {color: #5B6B7F; font-size: 0.95rem; margin: 0.35rem 0 1.2rem 0;}

/* aviso de painel não oficial */
.oficial {display: flex; align-items: center; gap: 18px; background: #12355B; border-radius: 14px; padding: 16px 20px; margin: 0 0 1.2rem 0; color: #FFFFFF;}
.oficial .icone {flex: 0 0 42px; height: 42px; border-radius: 50%; background: #F5A524; color: #12355B; font-weight: 800; font-size: 1.35rem; display: flex; align-items: center; justify-content: center;}
.oficial .texto {flex: 1 1 auto; min-width: 0;}
.oficial .aviso-titulo {font-weight: 800; font-size: 1.08rem; color: #FFFFFF; margin: 0 0 3px 0;}
.oficial .aviso-corpo {font-size: 0.9rem; line-height: 1.5; color: #D5E0F0; margin: 0;}
.oficial .aviso-fonte {display: block; font-size: 0.78rem; color: #9FB4D3; margin-top: 6px; word-break: break-all;}
.oficial a.botao {flex: 0 0 auto; background: #F5A524; color: #12355B !important; font-weight: 800; font-size: 0.88rem; padding: 10px 16px; border-radius: 10px; text-decoration: none !important; white-space: nowrap;}
.oficial a.botao:hover {background: #FFB93D;}
@media (max-width: 760px) {.oficial {flex-direction: column; align-items: flex-start;}}
.lateral-nota a {color: #F5A524; font-weight: 600;}
.rodape {color: #5B6B7F; font-size: 0.85rem; text-align: center; margin: 2rem 0 0 0; line-height: 1.6;}
.rodape a {color: #12355B; font-weight: 700;}

/* indicadores */
.kpi {background: #FFFFFF; border: 1px solid #E1E8F2; border-radius: 14px; padding: 16px 18px; min-height: 128px;}
.kpi-destaque {background: #12355B; border-color: #12355B;}
.kpi-rotulo {font-size: 0.78rem; font-weight: 600; color: #5B6B7F;}
.kpi-valor {font-size: 2.05rem; font-weight: 800; color: #12355B; line-height: 1.15; margin-top: 6px;}
.kpi-valor.texto {font-size: 1.2rem; line-height: 1.3; margin-top: 10px;}
.kpi-nota {font-size: 0.8rem; color: #5B6B7F; margin-top: 6px;}
.kpi-nota b {color: #B26A00;}
.kpi-destaque .kpi-rotulo {color: #B9C8DE;}
.kpi-destaque .kpi-valor {color: #FFFFFF;}
.kpi-destaque .kpi-nota {color: #D5E0F0;}
.kpi-destaque .kpi-nota b {color: #F5A524;}

/* cartões de gráfico */
[class*="st-key-cartao"] {background: #FFFFFF; border: 1px solid #E1E8F2; border-radius: 14px; padding: 1rem 1.2rem 0.6rem 1.2rem;}
.cartao-titulo {color: #12355B; font-weight: 700; font-size: 1.02rem; margin: 0;}
.cartao-sub {color: #5B6B7F; font-size: 0.8rem; margin: 2px 0 6px 0;}

/* barras com trilho */
.linha-barra {display: grid; grid-template-columns: minmax(80px, 36%) 1fr auto; align-items: center; gap: 10px; padding: 5px 0; font-size: 0.85rem; color: #1B2A3A;}
.trilho {background: #E6ECF4; border-radius: 99px; height: 10px; overflow: hidden;}
.preenchimento {background: #F5A524; height: 100%; border-radius: 99px;}
.linha-barra.ampla {padding: 10px 0;}
.linha-barra .num {font-weight: 700; color: #12355B; font-variant-numeric: tabular-nums; white-space: nowrap;}

@media (min-width: 900px) {
  .st-key-cartao_mapa, .st-key-cartao_ranking {min-height: 520px;}
}

/* aviso */
.aviso {background: #FFF6E0; border-left: 4px solid #F5A524; border-radius: 8px; padding: 10px 14px; font-size: 0.82rem; color: #4A3A12; margin-top: 8px; line-height: 1.45;}

/* abas */
button[data-baseweb="tab"] {font-weight: 600;}
[data-baseweb="tab-highlight"] {background-color: #F5A524 !important;}
</style>
""",
    unsafe_allow_html=True,
)


# ------------------------------------------------------------- utilidades
def inteiro(n) -> str:
    return f"{int(round(n)):,}".replace(",", ".")


def decimal(x: float, casas: int = 1) -> str:
    return f"{x:.{casas}f}".replace(".", ",")


def rotulo(texto) -> str:
    """Troca MAIÚSCULAS por texto corrido, mantendo siglas e nomes próprios."""
    texto = str(texto)
    if texto in ("Não informado", ""):
        return texto
    if texto.upper() == "WHATSAPP":
        return "WhatsApp"
    palavras = texto.lower().split(" ")
    saida = []
    for p in palavras:
        base = p.strip("()/,-")
        saida.append(p.upper() if base in SIGLAS else p)
    resultado = " ".join(saida)
    resultado = resultado[0].upper() + resultado[1:]
    return resultado.replace("ministério da saúde", "Ministério da Saúde")


@st.cache_data(show_spinner="Carregando os dados...")
def carregar(marca: float) -> pd.DataFrame:
    return pd.read_parquet(SAIDA)


@st.cache_resource
def carregar_mapa():
    if not MAPA.exists():
        return None
    with open(MAPA, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def contar(df: pd.DataFrame, coluna: str, topo: int | None = None, sigla: bool = False) -> pd.DataFrame:
    """Conta manifestações por categoria, da maior para a menor."""
    t = df[coluna].value_counts(dropna=False).rename_axis("categoria").reset_index(name="n")
    t = t[t["n"] > 0].copy()
    t["categoria"] = t["categoria"].astype("object").fillna("Não informado")
    t["rotulo"] = t["categoria"] if sigla else t["categoria"].map(rotulo)
    t = t.sort_values("n", ascending=False).reset_index(drop=True)
    return t.head(topo) if topo else t


def ajustar(fig: go.Figure, altura: int, margem: dict | None = None) -> go.Figure:
    fig.update_layout(
        height=altura,
        margin=margem or dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color=TEXTO, size=12),
        separators=",.",
        hoverlabel=dict(font_family="Plus Jakarta Sans, sans-serif"),
    )
    return fig


def mostrar(fig: go.Figure):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def titulo_cartao(titulo: str, sub: str = ""):
    st.markdown(
        f'<p class="cartao-titulo">{html.escape(titulo)}</p>'
        + (f'<p class="cartao-sub">{html.escape(sub)}</p>' if sub else ""),
        unsafe_allow_html=True,
    )


def barras_trilho(t: pd.DataFrame, amplo: bool = False) -> str:
    """Barras horizontais com trilho cinza, como nos modelos de referência."""
    if t.empty:
        return ""
    maximo = t["n"].max()
    total = t["n"].sum()
    linhas = []
    for _, linha in t.iterrows():
        largura = 100 * linha["n"] / maximo
        percentual = 100 * linha["n"] / total
        linhas.append(
            f'<div class="linha-barra{" ampla" if amplo else ""}">'
            f'<div>{html.escape(str(linha["rotulo"]))}</div>'
            f'<div class="trilho"><div class="preenchimento" style="width:{largura:.1f}%"></div></div>'
            f'<div class="num">{inteiro(linha["n"])} · {decimal(percentual)}%</div>'
            "</div>"
        )
    return "".join(linhas)


def rosquinha(t: pd.DataFrame, altura: int = 300) -> go.Figure:
    cores = [COR_CLASSIFICACAO.get(r, SEQUENCIA[i % len(SEQUENCIA)]) for i, r in enumerate(t["rotulo"])]
    fig = go.Figure(
        go.Pie(
            labels=t["rotulo"],
            values=t["n"],
            hole=0.64,
            sort=False,
            marker=dict(colors=cores, line=dict(color="#FFFFFF", width=2)),
            textinfo="percent",
            textfont=dict(size=12, color="#FFFFFF"),
            hovertemplate="%{label}<br>%{value:,.0f} manifestações (%{percent})<extra></extra>",
        )
    )
    fig.add_annotation(
        text=f"<b>{inteiro(t['n'].sum())}</b><br><span style='font-size:11px;color:{CINZA}'>manifestações</span>",
        showarrow=False,
        font=dict(size=20, color=MARINHO),
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center", yanchor="top", font=dict(size=11)),
        uniformtext_minsize=10,
        uniformtext_mode="hide",
    )
    return ajustar(fig, altura)


# ------------------------------------------------------------------ dados
if not SAIDA.exists():
    st.title("OuvidorSUS 3")
    st.error("A base de dados não foi encontrada. Verifique se o arquivo ouv3_tratado.parquet foi enviado junto com o painel.")
    st.stop()

df = carregar(SAIDA.stat().st_mtime)
primeiro_ano, ultimo_ano = int(df["ano"].min()), int(df["ano"].max())

# -------------------------------------------------------- painel lateral
with st.sidebar:
    st.markdown(
        '<div class="marca">OuvidorSUS 3<span>Manifestações registradas</span></div>'
        '<div class="lateral-titulo">Filtros</div>',
        unsafe_allow_html=True,
    )
    st.caption("Deixe vazio para incluir todos.")

    def filtro(texto: str, coluna: str, sigla: bool = False):
        opcoes = sorted(df[coluna].dropna().astype(str).unique())
        return st.multiselect(texto, opcoes, format_func=(str if sigla else rotulo), placeholder="Todos")

    anos = st.multiselect("Ano", sorted(df["ano"].unique()), placeholder="Todos")
    classes = filtro("Classificação", "classificacao_manifestacao")
    canais = filtro("Canal de entrada", "canal_entrada")
    esferas = filtro("Esfera da ouvidoria de destino", "esfera_ouvidoria_destino")
    ufs = filtro("UF da ouvidoria de origem", "uf_ouvidoria_origem", sigla=True)
    situacoes = filtro("Situação da manifestação", "status_manifestacao")
    st.markdown(
        f'<div class="lateral-nota"><b>Painel sem caráter oficial.</b> Feito com dados abertos do OuvidorSUS 3, '
        f'disponíveis em <a href="{FONTE_URL}" target="_blank" rel="noopener noreferrer">dadosabertos.saude.gov.br</a>.</div>',
        unsafe_allow_html=True,
    )

mascara = pd.Series(True, index=df.index)
for valores, coluna in (
    (classes, "classificacao_manifestacao"),
    (canais, "canal_entrada"),
    (esferas, "esfera_ouvidoria_destino"),
    (ufs, "uf_ouvidoria_origem"),
    (situacoes, "status_manifestacao"),
):
    if valores:
        mascara &= df[coluna].isin(valores)
base = df[mascara]                      # todos os filtros, menos o ano
dados = base[base["ano"].isin(anos)] if anos else base

# ------------------------------------------------------------- cabeçalho
periodo = f"{primeiro_ano} a {ultimo_ano}"
st.markdown(
    '<h1 class="titulo">Manifestações de Ouvidorias do SUS</h1>'
    f'<p class="subtitulo">Manifestações registradas no OuvidorSUS 3. Dados abertos do Ministério da Saúde, anos de {periodo}.</p>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="oficial"><div class="icone">i</div><div class="texto">'
    '<p class="aviso-titulo">Painel sem caráter oficial</p>'
    '<p class="aviso-corpo">Elaborado com dados abertos do OuvidorSUS 3, publicados pelo Ministério da Saúde. '
    "Não é uma publicação oficial do órgão e não representa o seu posicionamento.</p>"
    f'<span class="aviso-fonte">Fonte: {FONTE_URL.replace("https://", "")}</span></div>'
    f'<a class="botao" href="{FONTE_URL}" target="_blank" rel="noopener noreferrer">Acessar a fonte dos dados &#8599;</a></div>',
    unsafe_allow_html=True,
)

if dados.empty:
    st.warning("Nenhuma manifestação com os filtros escolhidos. Retire algum filtro.")
    st.stop()

# ------------------------------------------------------------ indicadores
total = len(dados)
por_status = contar(dados, "status_manifestacao")
por_classe = contar(dados, "classificacao_manifestacao")
por_canal = contar(dados, "canal_entrada")
por_assunto = contar(dados, "assunto")

concluidas = por_status.loc[por_status["categoria"].str.upper().str.startswith("CONCLU"), "n"].sum()
em_analise = por_status.loc[por_status["categoria"].str.upper().str.contains("AN[ÁA]LISE", regex=True), "n"].sum()
criticas = por_classe.loc[
    por_classe["categoria"].str.upper().str.contains("RECLAMA|DEN[ÚU]NCIA", regex=True), "n"
].sum()

n24, n25 = (base["ano"] == 2024).sum(), (base["ano"] == 2025).sum()
if n24 > 0 and n25 > 0:
    variacao = 100 * (n25 / n24 - 1)
    sinal = "+" if variacao >= 0 else "-"
    nota_total = f"2025 em relação a 2024: <b>{sinal}{decimal(abs(variacao))}%</b>"
else:
    nota_total = "Total do recorte escolhido"


def cartao_kpi(rotulo_: str, valor: str, nota: str, destaque: bool = False, texto: bool = False) -> str:
    classe = "kpi kpi-destaque" if destaque else "kpi"
    classe_valor = "kpi-valor texto" if texto else "kpi-valor"
    return (
        f'<div class="{classe}"><div class="kpi-rotulo">{rotulo_}</div>'
        f'<div class="{classe_valor}">{valor}</div><div class="kpi-nota">{nota}</div></div>'
    )


colunas = st.columns(5, gap="small")
colunas[0].markdown(cartao_kpi("Manifestações", inteiro(total), nota_total, destaque=True), unsafe_allow_html=True)
colunas[1].markdown(
    cartao_kpi(
        "Concluídas",
        f"{decimal(100 * concluidas / total)}%",
        f"<b>{inteiro(em_analise)}</b> ainda em análise",
    ),
    unsafe_allow_html=True,
)
colunas[2].markdown(
    cartao_kpi(
        "Reclamações e denúncias",
        f"{decimal(100 * criticas / total)}%",
        f"<b>{inteiro(criticas)}</b> manifestações",
    ),
    unsafe_allow_html=True,
)
colunas[3].markdown(
    cartao_kpi(
        "Canal mais usado",
        html.escape(por_canal.loc[0, "rotulo"]),
        f"<b>{decimal(100 * por_canal.loc[0, 'n'] / total)}%</b> das manifestações",
        texto=True,
    ),
    unsafe_allow_html=True,
)
colunas[4].markdown(
    cartao_kpi(
        "Assunto mais frequente",
        html.escape(por_assunto.loc[0, "rotulo"]),
        f"<b>{decimal(100 * por_assunto.loc[0, 'n'] / total)}%</b> das manifestações",
        texto=True,
    ),
    unsafe_allow_html=True,
)

st.write("")

# ------------------------------------------------------------------ anos
AVISO_ANO = (
    '<div class="aviso"><b>Como ler os anos.</b> O ano é o do arquivo publicado no Portal de Dados Abertos. '
    "O arquivo de 2023 cobre apenas o início do uso do OuvidorSUS 3, a partir de novembro. A migração das "
    "ouvidorias para o sistema continua, então parte do crescimento vem de novas ouvidorias entrando, e não "
    "necessariamente de mais demanda.</div>"
)
COR_ANO = {2023: CEU, 2024: AMBAR, 2025: MARINHO}

with st.container(key="cartao_anos"):
    titulo_cartao("Manifestações por ano", "Total de cada ano e como as classificações se distribuem dentro dele")
    ca, cb = st.columns([2, 3], gap="large")
    por_ano = dados.groupby("ano", observed=True).size().reset_index(name="n")
    with ca:
        fig = go.Figure(
            go.Bar(
                x=[str(a) for a in por_ano["ano"]],
                y=por_ano["n"],
                marker_color=[COR_ANO.get(a, CINZA) for a in por_ano["ano"]],
                text=[inteiro(n) for n in por_ano["n"]],
                textposition="outside",
                cliponaxis=False,
                hovertemplate="%{x}<br>%{y:,.0f} manifestações<extra></extra>",
            )
        )
        fig.update_xaxes(showgrid=False, type="category")
        fig.update_yaxes(visible=False)
        fig.update_traces(width=0.55)
        mostrar(ajustar(fig, 330, dict(l=0, r=0, t=24, b=0)))
    with cb:
        cruzado = (
            dados.groupby(["ano", "classificacao_manifestacao"], observed=True)
            .size()
            .unstack(fill_value=0)
        )
        cruzado = cruzado.loc[:, cruzado.sum().sort_values(ascending=False).index]
        cruzado = cruzado.loc[:, cruzado.sum() > 0]
        percentuais = cruzado.div(cruzado.sum(axis=1), axis=0) * 100
        fig = go.Figure()
        for i, coluna in enumerate(cruzado.columns):
            nome = rotulo(coluna)
            fig.add_trace(
                go.Bar(
                    name=nome,
                    y=[str(a) for a in cruzado.index],
                    x=percentuais[coluna],
                    orientation="h",
                    marker_color=COR_CLASSIFICACAO.get(nome, SEQUENCIA[i % len(SEQUENCIA)]),
                    text=[f"{decimal(p, 0)}%" if p >= 5 else "" for p in percentuais[coluna]],
                    textposition="inside",
                    textfont=dict(color="#FFFFFF", size=12),
                    customdata=cruzado[coluna],
                    hovertemplate="%{y}<br>" + nome + ": %{customdata:,.0f} (%{x:.1f}%)<extra></extra>",
                )
            )
        fig.update_layout(barmode="stack", legend=dict(orientation="h", y=-0.08, x=0, font=dict(size=11)))
        fig.update_xaxes(visible=False, range=[0, 100])
        fig.update_yaxes(autorange="reversed", type="category")
        mostrar(ajustar(fig, 330))
    st.markdown(AVISO_ANO, unsafe_allow_html=True)

st.write("")

# ------------------------------------------------------------ mapa e UFs
esq, dir_ = st.columns([3, 2], gap="medium")
por_uf = contar(dados, "uf_ouvidoria_origem", sigla=True)
por_uf = por_uf[por_uf["categoria"] != "Não informado"]

with esq:
    with st.container(key="cartao_mapa"):
        titulo_cartao("Manifestações por UF", "UF da ouvidoria de origem, em volume absoluto, sem ajuste pela população")
        geo = carregar_mapa()
        if geo is None:
            st.info("Para ver o mapa, envie o arquivo br_estados.geojson junto com o painel.")
        else:
            fig = px.choropleth(
                por_uf,
                geojson=geo,
                locations="categoria",
                featureidkey="properties.sigla",
                color="n",
                color_continuous_scale=["#EAF1FB", CEU, AZUL, MARINHO],
            )
            fig.update_traces(
                marker_line_color="#FFFFFF",
                marker_line_width=0.8,
                hovertemplate="%{location}<br>%{z:,.0f} manifestações<extra></extra>",
            )
            fig.update_geos(fitbounds="locations", visible=False)
            if "DF" in por_uf["categoria"].values:
                n_df = int(por_uf.loc[por_uf["categoria"] == "DF", "n"].iloc[0])
                fig.add_trace(
                    go.Scattergeo(
                        lon=[-47.9],
                        lat=[-15.8],
                        mode="markers",
                        marker=dict(
                            size=15,
                            color=[n_df],
                            coloraxis="coloraxis",
                            line=dict(color="#FFFFFF", width=1.5),
                        ),
                        hovertemplate=f"DF<br>{inteiro(n_df)} manifestações<extra></extra>",
                        showlegend=False,
                    )
                )
            fig.update_layout(
                coloraxis_colorbar=dict(title=None, thickness=10, len=0.6, tickfont=dict(size=10)),
            )
            mostrar(ajustar(fig, 420))

with dir_:
    with st.container(key="cartao_ranking"):
        titulo_cartao("UFs com mais manifestações", "As 10 maiores")
        st.markdown(barras_trilho(por_uf.head(10), amplo=True), unsafe_allow_html=True)

st.write("")

# ------------------------------------------------------------- rosquinhas
c1, c2, c3 = st.columns(3, gap="medium")
with c1:
    with st.container(key="cartao_classificacao"):
        titulo_cartao("Classificação")
        mostrar(rosquinha(por_classe, 340))
with c2:
    with st.container(key="cartao_situacao"):
        titulo_cartao("Situação")
        mostrar(rosquinha(por_status, 340))
with c3:
    with st.container(key="cartao_esfera"):
        titulo_cartao("Esfera de destino")
        mostrar(rosquinha(contar(dados, "esfera_ouvidoria_destino"), 340))

st.write("")

# ------------------------------------------------------- canal e problema
c1, c2 = st.columns(2, gap="medium")
with c1:
    with st.container(key="cartao_canal"):
        titulo_cartao("Canal de entrada", "Os 8 mais usados")
        st.markdown(barras_trilho(por_canal.head(8)), unsafe_allow_html=True)
with c2:
    with st.container(key="cartao_problema"):
        titulo_cartao("Tipo de problema", "Os 8 mais frequentes")
        st.markdown(barras_trilho(contar(dados, "status_problema", topo=8)), unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------------- assuntos
with st.container(key="cartao_assuntos"):
    titulo_cartao("Assuntos e subassuntos", "O tamanho de cada bloco mostra o volume. Os 25 subassuntos maiores aparecem separados.")
    if "subassunto1" in dados.columns:
        t = (
            dados.groupby(["assunto", "subassunto1"], observed=True, dropna=False)
            .size()
            .reset_index(name="n")
        )
        t = t[t["n"] > 0].copy()
        t["assunto"] = t["assunto"].astype("object").fillna("Não informado")
        t["subassunto1"] = t["subassunto1"].astype("object").fillna("Não informado")
        t = t.sort_values("n", ascending=False).reset_index(drop=True)
        t.loc[t.index >= 25, "subassunto1"] = "Demais subassuntos"
        t = t.groupby(["assunto", "subassunto1"], as_index=False)["n"].sum()
        t["Assunto"] = t["assunto"].map(rotulo)
        t["Subassunto"] = t["subassunto1"].map(rotulo)
        caminho = ["Assunto", "Subassunto"]
    else:
        t = contar(dados, "assunto").rename(columns={"rotulo": "Assunto"})
        caminho = ["Assunto"]
    fig = px.treemap(t, path=caminho, values="n", color="Assunto", color_discrete_sequence=SEQUENCIA)
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{value:,.0f}",
        hovertemplate="%{label}<br>%{value:,.0f} manifestações<extra></extra>",
        marker=dict(line=dict(color="#FFFFFF", width=2)),
        textfont=dict(family="Plus Jakarta Sans, sans-serif", size=13),
        tiling=dict(pad=3),
    )
    mostrar(ajustar(fig, 520))

st.write("")

# ---------------------------------------------------------------- tabela
with st.expander("Tabela anual por classificação"):
    tabela = (
        dados.groupby(["ano", "classificacao_manifestacao"], observed=True)
        .size()
        .unstack(fill_value=0)
    )
    tabela = tabela.loc[:, tabela.sum().sort_values(ascending=False).index]
    tabela = tabela.loc[:, tabela.sum() > 0]
    tabela.index = [str(a) for a in tabela.index]
    tabela.index.name = "Ano"
    tabela.columns = [rotulo(c) for c in tabela.columns]
    tabela["Total"] = tabela.sum(axis=1)
    st.dataframe(tabela, width="stretch")
    st.download_button(
        "Baixar tabela em CSV",
        tabela.to_csv(sep=";", encoding="utf-8-sig").encode("utf-8-sig"),
        file_name="ouvidorsus3_anual_por_classificacao.csv",
        mime="text/csv",
    )

# ------------------------------------------------------------ observações
with st.expander("Cuidados com a leitura dos dados"):
    corrigidas = int(df["ano_foi_corrigido"].sum())
    st.markdown(
        f"""
- **Só o ano é usado.** A data completa da manifestação foi descartada. Na base, nenhuma data cai depois do
  dia 12 de um mês, e em {inteiro(corrigidas)} linhas ({decimal(100 * corrigidas / len(df))}%) o ano escrito na data
  era diferente do ano do arquivo, inclusive anos que ainda não chegaram. Por isso, o ano de cada manifestação é
  o do arquivo publicado, e não há gráficos por mês.
- **Ano de 2023 incompleto.** O arquivo de 2023 cobre só o início do uso do OuvidorSUS 3, a partir de novembro.
  Comparar 2023 com os outros anos não mostra crescimento de demanda.
- **Linhas repetidas mantidas.** Os arquivos não têm número de protocolo, então não é possível separar
  duplicatas de manifestações realmente idênticas.
- **Campos vazios.** Em parte das linhas faltam assunto, subassunto e tipo de problema. Elas aparecem como
  "Não informado".
- **Sem tempo de resposta.** A base não traz a data de conclusão, então não há como calculá-lo.
- **Mapa.** Mostra o volume absoluto por UF da ouvidoria de origem, sem ajuste pela população. Estados com mais
  habitantes tendem a ter mais manifestações.
- **Tipificação.** As regras de tipificação mudam entre as versões do sistema. Consulte o manual do OuvidorSUS 3
  ao interpretar assuntos e subassuntos.
"""
    )

st.markdown(
    '<div class="rodape"><b>Painel sem caráter oficial.</b> Produzido com dados abertos do OuvidorSUS 3, '
    f'Ministério da Saúde: <a href="{FONTE_URL}" target="_blank" rel="noopener noreferrer">{FONTE_URL.replace("https://", "")}</a></div>',
    unsafe_allow_html=True,
)
