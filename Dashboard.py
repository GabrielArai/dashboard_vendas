import requests
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout = 'wide')


def formata_numero(valor, prefixo = ''):
    for unidade in ['' ,'mil']:
        if valor < 1000:
            return f"{prefixo} {valor:.2f} {unidade}"
        valor/=1000
    return f"{prefixo} {valor:.2f} milhões"


st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao':str(regiao).lower(), 'ano':ano}
response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# Tabelas
## Receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

## Quantidade de Vendas
vendas_estados = dados.groupby(['Local da compra','lat','lon']).count().reset_index()[['Local da compra','Produto','lat','lon']]
vendas_estados.rename(columns={'Produto':'Qtd Vendas'}, inplace=True)

vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Produto'].count().reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()
vendas_mensal.rename(columns={'Produto':'Qtd Vendas'}, inplace=True)

vendas_categorias = dados.groupby('Categoria do Produto').count().reset_index()[['Categoria do Produto','Produto']]
vendas_categorias.rename(columns={'Produto':'Qtd Vendas'}, inplace=True)

## Vendedores
vendedores = pd.DataFrame(dados.groupby("Vendedor")['Preço'].agg(['sum','count']))



# Gráficos
## Receita
fig_mapa_receita = px.scatter_geo(receita_estados, 
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  size='Preço',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon': False},
                                  title='Receita por Estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers=True,
                             range_y=(0, receita_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados,
                            x='Local da compra',
                            y='Preço',
                            text_auto = True,
                            title='Top Estados (Receita)'
                             )
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title='Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

## Quantidade de Vendas
fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  size='Qtd Vendas',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon': False},
                                  title='Quantidade de Vendas por Estado')

fig_vendas_mensal = px.line(vendas_mensal,
                             x = 'Mes',
                             y = 'Qtd Vendas',
                             markers=True,
                             range_y=(0, vendas_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Quantidade de Vendas Mensal')
fig_vendas_mensal.update_layout(yaxis_title = 'Quantidade de Vendas')

fig_vendas_estados = px.bar(vendas_estados,
                            x='Local da compra',
                            y='Qtd Vendas',
                            text_auto = True,
                            title='Top Estados (Quantidade de Vendas)'
                             )
fig_vendas_estados.update_layout(yaxis_title = 'Quantidade de Vendas')

fig_vendas_categorias = px.bar(vendas_categorias,
                               x='Categoria do Produto',
                               y='Qtd Vendas',
                               text_auto = True,
                               title='Quantidade de Vendas por categoria')
fig_vendas_categorias.update_layout(yaxis_title = 'Quantidade de Vendas')

# Visualização no streamlit
aba1,aba2,aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(round(dados['Preço'].sum(),2), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(round(dados['Preço'].sum(),2), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estados, use_container_width=True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)

with aba3:
    qtd_vendedores = st.number_input("Quantidade de Vendedores", 2, 10, 5)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(round(dados['Preço'].sum(),2), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum',ascending=False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum',ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title= f'Top {qtd_vendedores} Vendedores (Receita)')
        st.plotly_chart(fig_receita_vendedores)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count',ascending=False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count',ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title= f'Top {qtd_vendedores} Vendedores (Vendas)'
                                        )
        st.plotly_chart(fig_vendas_vendedores)




