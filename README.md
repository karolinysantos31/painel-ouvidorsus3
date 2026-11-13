# Manifestações de Ouvidorias do SUS

> **Painel sem caráter oficial.** Feito com dados abertos do OuvidorSUS 3, publicados pelo Ministério da Saúde. Não é uma publicação oficial do órgão e não representa o seu posicionamento.

**Painel:** https://painel-ouvidorsus3-5dqzsnbxj9n7qy9prapp3nd.streamlit.app/
**Fonte dos dados:** https://dadosabertos.saude.gov.br/dataset/ouvidorsus

## O que é

Painel interativo com as manifestações registradas no OuvidorSUS 3, sistema de ouvidoria do SUS, de 2023 a 2025. São mais de 784 mil registros, com filtros por ano, classificação, canal de entrada, esfera de destino, UF e situação.

## O que o painel mostra

- Indicadores: total de manifestações, percentual de concluídas, percentual de reclamações e denúncias, canal mais usado e assunto mais frequente
- Manifestações por ano e distribuição das classificações dentro de cada ano
- Mapa do Brasil por UF da ouvidoria de origem, com ranking das 10 maiores
- Classificação, situação e esfera de destino
- Canal de entrada e tipo de problema
- Assuntos e subassuntos em blocos proporcionais

## Como os dados foram tratados

- **Fonte:** três arquivos CSV anuais do Portal de Dados Abertos do SUS (OuvidorSUS 3, 2023, 2024 e 2025).
- **Ano:** o ano de cada manifestação é o do arquivo publicado. Em 480.144 linhas (61,2%), o ano escrito na data era diferente do ano do arquivo, inclusive anos que ainda não chegaram. Por isso, o painel não usa a data completa e não traz gráficos por mês.
- **Colunas mantidas:** apenas categorias e o ano (classificação, canal de entrada, esfera de destino, UF de origem, situação, assunto, subassunto e tipo de problema). Não há dados que identifiquem pessoas.
- **Base do painel:** `ouv3_tratado.parquet`, com 784.993 linhas.

## Limitações

- Nenhuma data da base cai depois do dia 12 de um mês, o que indica problema de origem ou cobertura parcial de cada mês.
- O arquivo de 2023 cobre apenas o início do uso do sistema, a partir de novembro. A migração das ouvidorias para o OuvidorSUS 3 continua, então o aumento entre os anos não indica, por si só, mais demanda.
- Os arquivos não têm número de protocolo. Linhas idênticas foram mantidas, porque não é possível separá-las de manifestações realmente iguais.
- A base não traz data de conclusão, então não há tempo de resposta.
- O mapa mostra o volume absoluto por UF, sem ajuste pela população.
- Em parte das linhas faltam assunto, subassunto e tipo de problema. Elas aparecem como "Não informado".
- As regras de tipificação mudam entre as versões do sistema. Consulte o manual do OuvidorSUS 3 para interpretar assuntos e subassuntos.

## Tecnologias

Python, Pandas, Plotly, Streamlit e PyArrow. Hospedado no Streamlit Community Cloud.

## Arquivos

| Arquivo | Função |
|---|---|
| `painel.py` | Código do painel |
| `ouv3_tratado.parquet` | Base tratada |
| `br_estados.geojson` | Contornos dos estados, usados no mapa |
| `requirements.txt` | Bibliotecas necessárias |

## Como rodar no computador

Requer Python 3.10 ou mais recente.

```
pip install -r requirements.txt
streamlit run painel.py
```

## Aviso

Painel independente, feito com dados abertos, sem caráter oficial. Os números refletem a base publicada e as regras de tratamento descritas acima.
