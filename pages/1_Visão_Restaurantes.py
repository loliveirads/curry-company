#Imports
import pandas as pd
import io
import plotly.express as px
import folium
from haversine import haversine
from datetime import *
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from PIL import Image

from streamlit_folium import folium_static

import streamlit.components.v1

#Configuraçao padrao dos gráficos
main_config = {
    "hovermode": "x unified",
    "legend": {"yanchor":"top", 
                "y":0.9, 
                "xanchor":"left",
                "x":1,
                "title": {"text": None},
                "font" :{"color":"black"},
                "bgcolor": "rgba(0,0,0,0)"},
    "margin": {"l":5, "r":30, "t":30, "b":20}
}

#para nao aparecer as opçoes na parte de cima dos graficos
config_graph={"displayModeBar": False, "showTips": False}

#Configuraçao da página
st.set_page_config(page_title="Visão Restaurantes", page_icon=":bar_chart:", layout="wide")



#Openning data
df = pd.read_csv('dataset/train.csv')


# ========================
# Funçoes
# ========================
def clean_data(df1):
  df1 = df.copy()
  #Data Cleaning and transforming
  # 1 - Convertendo a coluna Age de texto para numero
  df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN ', :].copy()
        
  df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype('int64')

  # 2 - Convertendo a coluna Ratings de texto para numero decimal
  df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype('float64')

  # 3 - Convertendo a coluna order de texto para data
  df1 = df1.loc[df1[ 'Order_Date'] != 'NaN ', :].copy()
  df1['Order_Date'] = pd.to_datetime(df1['Order_Date'],  format="%d-%m-%Y")


  # 4 - Convertendo a coluna multiple deliveries para numero int
  df1 = df1.loc[df1['multiple_deliveries'] != 'NaN ', :].copy()
  df1['multiple_deliveries'] = df1['multiple_deliveries'].astype('int64')

  #5 - Criando a coluna week of year
  df1['Week_of_Year'] = df1['Order_Date'].dt.strftime('%U')

  #5 Criando a coluna day
  df1['day'] = df1['Order_Date'].dt.day

  #7 - Criando a coluna Hour_orderd
  
  df1 = df1.loc[df1['Time_Orderd'] != 'NaN ', :].copy()
  df1["Hour_Orderd"] = pd.to_datetime(df1["Time_Orderd"], format="%H:%M:%S").dt.hour.astype('int64')
  df1.loc[df1['Hour_Orderd'] == 0, 'Hour_Orderd'] = 24

  #8 - Criando a coluna distance  
  cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

  df1['distance'] = round(df1.loc[:, cols].apply(lambda x: haversine(
                                                            (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1),2)  

  # 5 - Removendo os espaços dentro de strings
  #df1 = df1.reset_index(drop=True) # pois como estamos excluindo as linhas com NaN o index acaba sendo pulado e não conseguimos usar o for

  #for i in range(len(df1)):
  #   df.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()

  df1 = df1.reset_index(drop=True)
  df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
  df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
  df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
  df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
  df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
  df1 = df1.loc[df1['City'] != 'NaN', :].copy()

  df1.loc[:, 'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].apply(lambda x: x.strip('(min) ')[1])
  df1['Time_taken(min)'] = df1['Time_taken(min)'].astype('int64')

  df1 = df1.loc[df1['Time_Orderd'] != 'NaN ', :].copy()
  df1["Hour_Orderd"] = pd.to_datetime(df1["Time_Orderd"], format="%H:%M:%S").dt.hour.astype('int64')
  df1.loc[df1['Hour_Orderd'] == 0, 'Hour_Orderd'] = 24

  df1 = df1.loc[df1[ 'Delivery_location_latitude'] > 1 , :].copy()
  df1 = df1.loc[df1[ 'Delivery_location_longitude'] > 1 , :].copy()

  df1 = df1.reset_index(drop=True)
  #df1 = df.loc[df['Road_traffic_density'] != 'NaN ', :].copy()
  # Visao empresa 
  return df1



def fig7(df1):
        aux3 = df1[['City', 'distance']].groupby('City').mean().reset_index()
        #aux3 = aux3.loc[aux3['Road_traffic_density']] != 'NaN'

        
        fig7 = px.pie(aux3, values = 'distance', names = 'City')
        
        fig7.update_layout(main_config)
        fig7.update_layout(title=f'Distribuiçao da Distancia Média Por Cidade',
                    title_x=0.2,
                    title_y=0.9,
                    plot_bgcolor = 'white',
                    titlefont = {'family': 'Arial','size': 20,'color': 'black'}) # alterando #fonte do gráfico                
        return fig7
        
def fig8(df1):
                    
                    
    aux = df1[['City','Time_taken(min)']].groupby('City')

    aux = aux.agg(
                tempo_medio = pd.NamedAgg('Time_taken(min)', 'mean'),
                desvio_padrão = pd.NamedAgg('Time_taken(min)', 'std'))
    #df_grouped = df_grouped.sort_values('avg_price',ascending = False)
    aux = aux.sort_values(['tempo_medio'], ascending= False).reset_index()
    aux = aux.round(2)
    fig8 = px.bar(aux, 
                    x='City', 
                    y='tempo_medio',
                    color_discrete_sequence=px.colors.qualitative.T10,
                    text='tempo_medio',
                    error_y='desvio_padrão',
                    #template='plotly_white',
                    labels={'tempo_medio': 'Tempo Médio',
                            'City': 'Cidade'},
                    hover_data=["tempo_medio", "desvio_padrão"])
            
    fig8.update_layout(main_config)
    fig8.update_layout(title='Por Cidade',
                       title_x=0.2,
                    title_y=0.9,
                    plot_bgcolor = 'white',
                    titlefont = {'family': 'Arial','size': 20,'color': 'black'}) # alterando #fonte do gráfico 
    return fig8


def fig9(df1):
    aux = df1[['City','Road_traffic_density','Time_taken(min)']].groupby(['City','Road_traffic_density'])

    aux = aux.agg(tempo_medio = pd.NamedAgg('Time_taken(min)', 'mean'),
                 desvio_padrão = pd.NamedAgg('Time_taken(min)', 'std'))
    #df_grouped = df_grouped.sort_values('avg_price',ascending = False)
    aux = aux.sort_values(['tempo_medio'], ascending= False).reset_index()
                    
    fig9 = px.sunburst(aux, 
                       path=['City','Road_traffic_density'], 
                       values='desvio_padrão',
                       color='desvio_padrão',
                       color_continuous_scale='RdBU',
                       color_continuous_midpoint=np.average(aux['desvio_padrão']))
    #color_discrete_sequence=px.colors.qualitative.T10)
    #template='plotly_white',
    #labels={'tempo_medio': 'Tempo Médio',
            #'City': 'Cidade'},
            #hover_data=["tempo_medio", "desvio_padrão"])
            
    fig9.update_layout(main_config)
    fig9.update_layout(title=' Por tipo de Cidade e Transito',
                       title_x=0.2,
                    title_y=0.9,
                    plot_bgcolor = 'white',
                    titlefont = {'family': 'Arial','size': 20,'color': 'black'}) # alterando #fonte do gráfico                            
    return fig9

def fig10(df1):
        aux = df1[['City','Type_of_order','Time_taken(min)']].groupby(['City','Type_of_order'])

        aux = aux.agg(
            tempo_medio = pd.NamedAgg('Time_taken(min)', 'mean'),
            desvio_padrão = pd.NamedAgg('Time_taken(min)', 'std'))
        #df_grouped = df_grouped.sort_values('avg_price',ascending = False)
        aux = aux.sort_values(['tempo_medio'], ascending= False).reset_index()
        aux = aux.round(2)

        fig10 = px.bar(aux, 
                    x='City', 
                    y='tempo_medio',
                    color = 'Type_of_order',
                    color_discrete_sequence=px.colors.qualitative.T10,
                    text='tempo_medio',
                    text_auto='auto',
                    error_y='desvio_padrão',
                    #template='plotly_white',
                    labels={'tempo_medio': 'Tempo Médio',
                              'City': 'Cidade'},
                    hover_data=["tempo_medio", "desvio_padrão"],
                    barmode='group',)
                    #title='Tempo Médio por Tipo de Cidade e Tipo de Transito')
        
        fig10.update_layout(main_config)
        fig10.update_layout(title_text='Por Tipo de Cidade e Tipo de Pedido',
                            title_x=0.2,
                    title_y=0.9,
                    plot_bgcolor = 'white',
                    titlefont = {'family': 'Arial','size': 20,'color': 'black'}) # alterando #fonte do gráfico
        
        return fig10
# ========================
# Layout Sidebar
# ========================

df1 = clean_data(df)


with open('assets/css.css') as f:
  st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)


st.header('Marketplace - Visão Restaurantes')
st.markdown( """---""" )

#image_path = 'C:/Users/luizf/OneDrive/Documentos/repos/FTC/'

image = Image.open('logo.jpg')
st.sidebar.markdown('### Cury Company')
st.sidebar.image(image, width=200)

st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown( """---""" )

max_date = datetime.strptime(df['Order_Date'].max(), '%d-%m-%Y')
min_date = datetime.strptime(df['Order_Date'].min(), '%d-%m-%Y')
date_options = st.sidebar.slider(
    'Selecione um valor máximo:',
    value=max_date,
    min_value=min_date,
    max_value=max_date,
    format='DD-MM-YYYY')

st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect(
    'Quais as Condições de Transito',
    df1['Road_traffic_density'].unique(),
    default=df1['Road_traffic_density'].unique()
    )


#Filtro do data

#df1 = df1[df1['Order_Date']] < date_options
df1 = df1.loc[df1['Order_Date'] < date_options, :]

#Filtro de Transito
df1 = df1.loc[df1['Road_traffic_density'].isin(traffic_options) , :]

# ========================
# Layout Header
# ========================



tab1 = st.tabs('Visão Gerencial')

with tab1:
    with st.container():
        st.markdown('##### Métricas')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            with st.container():
                total_entregadores = df1["ID"].count()
                st.write('Total de Pedidos Realizados')

                st.metric(f'', total_entregadores, delta=None)

        with col2:
            with st.container():
                distancia_media = round(df1['distance'].mean(),2)
                st.write('Distancia Média em Metros')

                st.metric(f'', distancia_media )

        with col3:
            with st.container():
                aux = df1.loc[df1['Festival'] == 'Yes ', :]
                tempo_medio = round(aux['Time_taken(min)'].mean(),2)
                st.write(' Tempo Médio C/Festival')
                
                st.metric(f'', tempo_medio )

        with col4:
            with st.container():
                aux = df1.loc[df1['Festival'] == 'Yes ', :]
                desvio_padrao = round(aux['Time_taken(min)'].std(),2)
                st.write('Desvio Padrão C/Festival')
    
                st.metric(f'', desvio_padrao )

        with col5:
            with st.container():
                aux = df1.loc[df1['Festival'] == 'No ', :]
                tempo_medio = round(aux['Time_taken(min)'].mean(),2)
                st.write('Tempo Médio S/Festival')

                st.metric(f'', tempo_medio )

        with col6:
            with st.container():
                aux = df1.loc[df1['Festival'] == 'No ', :]
                desvio_padrao = round(aux['Time_taken(min)'].std(),2)
                st.write('Desvio Padrão S/Festival')
    
                st.metric(f'', desvio_padrao )
    

    with st.container():
        st.markdown('##### Distribuiçao da Distancia Média')
        fig7 = fig7(df1)

        st.plotly_chart(fig7, use_container_width=True, config=config_graph)
    
  
    
    with st.container():
        st.markdown('##### Tempo Médio de Entrega')
        col1, col2 = st.columns(2)
        with col1:
            with st.container():
                with st.container():
                    fig8 = fig8(df1)       

                    st.plotly_chart(fig8, theme="streamlit", use_container_width=True,  config=config_graph)#use_container_width=True,
        
        
        with col2:
            with st.container():
                with st.container():
                    
                    fig9 = fig9(df1)
                    st.plotly_chart(fig9, theme="streamlit", use_container_width=True,  config=config_graph)#use_container_width=True,
    
   

    with st.container():
        #st.title('Tempo Médio por Tipo de Cidade e Tipo de Transito')
        fig10 =fig10(df1)
        
        st.plotly_chart(fig10, theme="streamlit", use_container_width=True,  config=config_graph)#use_container_width=True,
