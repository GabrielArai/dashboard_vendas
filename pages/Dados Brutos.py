import requests
import time
import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache_data
def coverte_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def msg_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon="✅")
    time.sleep(5)
    sucesso.empty()

st.set_page_config(layout = 'wide')

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as Colunas', list(dados.columns), list(dados.columns))

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do Produto'):
    produto = st.multiselect('Selecione os Produtos', dados['Produto'].unique(), dados['Produto'].unique())
with st.sidebar.expander('Categoria do Produto'):
    categoria = st.multiselect('Selecione a Categoria', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
with st.sidebar.expander('Preço do Produto'):
    preco = st.slider('Selecione o Preço', 0, 5000, (0,5000))
with st.sidebar.expander('Frete do Produto'):
    frete = st.slider('Selecione o Frete', 0, 500, (0,500))
with st.sidebar.expander('Data da Compra'):
    data = st.date_input('Selecione a Data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
with st.sidebar.expander('Vendedor'):
    vendedor = st.multiselect('Selecione o Vendedor', dados['Vendedor'].unique(), dados['Vendedor'].unique())
with st.sidebar.expander('Local da Compra'):
    local = st.multiselect('Selecione o Local da Compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())
with st.sidebar.expander('Avaliação da Compra'):
    avaliacao = st.multiselect('Selecione a Avaliação da Compra', dados['Avaliação da compra'].unique(), dados['Avaliação da compra'].unique())
with st.sidebar.expander('Tipo de Pagamento'):
    tipo_pagamento = st.multiselect('Selecione o Tipo de Pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())
with st.sidebar.expander('Quantidade de Parcelas'):
    parcelas = st.multiselect('Selecione a Quantidade de Parcelas', dados['Quantidade de parcelas'].unique(), dados['Quantidade de parcelas'].unique())

query = """
Produto in @produto and \
`Categoria do Produto` in @categoria and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data[0] <= `Data da Compra` <= @data[1] and \
Vendedor in @vendedor and \
`Local da compra` in @local and \
`Avaliação da compra` in @avaliacao and \
`Tipo de pagamento` in @tipo_pagamento and \
`Quantidade de parcelas` in @parcelas
"""

dados_filt = dados.query(query)
dados_filt = dados_filt[colunas]

st.dataframe(dados_filt)

st.markdown(f'A tabela possui :blue[{dados_filt.shape[0]}] linhas e :blue[{dados_filt.shape[1]}] colunas')

st.markdown("Escreva um nome para o seu arquivo:")
col1,col2 = st.columns(2)
with col1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    nome_arquivo += '.csv'
with col2:
    st.download_button('Fazer o download da tabela em csv', data = coverte_csv(dados_filt), file_name = nome_arquivo, mime = 'text/csv', on_click = msg_sucesso())
