#Imports
import pandas as pd
import io
import plotly.express as px
import folium
from haversine import haversine
from datetime import *
import streamlit as st
import plotly.graph_objects as go

from PIL import Image

from streamlit_folium import folium_static

import streamlit.components.v1



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

config_graph={"displayModeBar": False, "showTips": False}


st.set_page_config(page_title="Visão Entregadores", page_icon=":bar_chart:", layout="wide")


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


def fig11(df1):
                 

    aux = df1[['Delivery_person_ID','Delivery_person_Ratings']].groupby('Delivery_person_ID')

    aux = aux.agg(media_avaliação = pd.NamedAgg('Delivery_person_Ratings', 'mean'),
                  qtde_entregas = pd.NamedAgg('Delivery_person_Ratings', 'count'))
    #df_grouped = df_grouped.sort_values('avg_price',ascending = False)
    aux = aux.sort_values(['qtde_entregas', 'media_avaliação'], ascending= False).reset_index().round(2)
       
    top = aux.head(20)
    top = top.sort_values(['qtde_entregas', 'media_avaliação'], ascending= True).reset_index()

    fig11 = px.bar(top, 
                    x='qtde_entregas',
                    y='Delivery_person_ID',
                    color_discrete_sequence=px.colors.qualitative.T10,
                    #template='plotly_white',
                    labels={'Delivery_person_ID': 'ID Entregador',
                            'qtde_entregas': 'Quantidade de Entregas'},
                    hover_data=["media_avaliação", "qtde_entregas"],
                    text='qtde_entregas')
                
    fig11.update_layout(main_config)
    fig11.update_xaxes(showticklabels=False)
    
    return fig11


def fig12(df1):

    aux = df1[['Delivery_person_ID','Delivery_person_Ratings']].groupby('Delivery_person_ID')
    aux = aux.agg(media_avaliação = pd.NamedAgg('Delivery_person_Ratings', 'mean'),
                  qtde_entregas = pd.NamedAgg('Delivery_person_Ratings', 'count'))
    #df_grouped = df_grouped.sort_values('avg_price',ascending = False)
    aux = aux.sort_values(['media_avaliação', 'qtde_entregas'], ascending= False).reset_index().round(2)
    top = aux.head(20)
    top = top.sort_values(['media_avaliação', 'qtde_entregas'], ascending= True).reset_index()
        

    fig12 = px.bar(top, 
                 x='media_avaliação', 
                 y='Delivery_person_ID',
                 color_discrete_sequence=px.colors.qualitative.T10,
                 #template='plotly_white',
                 labels={'Delivery_person_ID': 'ID Entregador',
                        'media_avaliação': 'Média de Avaliação'},
                 hover_data=["media_avaliação", "qtde_entregas"],
                 text='media_avaliação')
                
    fig12.update_layout(main_config)
    fig12.update_xaxes(showticklabels=False)               
    
    return fig12


# ========================
# Layout Sidebar
# ========================
df1 = clean_data(df)

with open('assets/css2.css') as f:
  st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)



st.header('Marketplace - Visão Entregadores')
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
    'Selecione um valor máximo',
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




  #primeira linha
# TOP KPI's

total_entregas = df1["ID"].count()
media_avaliaçao = round(df1["Delivery_person_Ratings"].mean(), 1)
star_rating = ":star:" * int(round(media_avaliaçao, 0))
total_entregadores = len(df1["Delivery_person_ID"].unique())
with st.container():

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container():
            st.markdown("###### Total de Entregas:")
            st.markdown(f"#### {total_entregas:,}")
    with col2:
        with st.container():
            st.markdown("###### Média Avaliação:")
            st.markdown(f'#### {media_avaliaçao}{star_rating}')
            
    with col3:
        with st.container():
            st.markdown("###### Total Entregadores:")
            st.markdown(f"#### {total_entregadores}")





with st.container():

    st.markdown( """---""" )

    st.markdown('##### Média de Entrega por Entregador')


    col1, col2, col3 = st.columns(3, gap='large')

    #col 1, linha 1
    with col1:
            
        with st.container():
                
                
            aux5_1 = df1[['Week_of_Year', 'ID']].groupby('Week_of_Year').count().reset_index()
            aux5_2 = df1[['Delivery_person_ID', 'Week_of_Year']].groupby('Week_of_Year').nunique().reset_index()
            aux5 = pd.merge(aux5_1, aux5_2, how='inner')
            aux5['media_entregas'] = (aux5['ID'] / aux5['Delivery_person_ID']).round(2)
            maxima = aux5['Week_of_Year'].max()
            ultima_semana = aux5.loc[aux5['Week_of_Year'] == maxima, 'media_entregas'].iloc[0].round(2)
            media = aux5['media_entregas'].mean()
            diferença = ( ultima_semana / media).round(3)
            diferença_percentual=((diferença - 1)*100).round(3)
            st.metric(f'Ultima Semana', ultima_semana,f'{diferença_percentual}%')
                
                
    with col2:
        with st.container():
                
            aux5_1 = df1[['day', 'ID']].groupby('day').count().reset_index()
            aux5_2 = df1[['day', 'Delivery_person_ID']].groupby('day').nunique().reset_index()
            aux5 = pd.merge(aux5_1, aux5_2, how='inner')
            aux5['media_entregas'] = (aux5['ID'] / aux5['Delivery_person_ID']).round(2)
            maxima = aux5['day'].max()
            ultimo_dia = aux5.loc[aux5['day'] == maxima, 'media_entregas'].iloc[0].round(2)
            media = aux5['media_entregas'].mean()
            diferença = ( ultimo_dia / media).round(3)
            diferença_percentual=((diferença - 1)*100).round(3)
            st.metric(f'Ultimo dia', ultimo_dia,f'{diferença_percentual}%')
                


    with col3:
        with st.container():
                
            aux5_1 = df1[['Hour_Orderd', 'ID']].groupby('Hour_Orderd').count().reset_index()
            aux5_2 = df1[['Delivery_person_ID', 'Hour_Orderd']].groupby('Hour_Orderd').nunique().reset_index()
            aux5 = pd.merge(aux5_1, aux5_2, how='inner')
            aux5['media_entregas'] = (aux5['ID'] / aux5['Delivery_person_ID']).round(2)
            maxima = aux5['Hour_Orderd'].max()
            ultima_hora = aux5.loc[aux5['Hour_Orderd'] == maxima, 'media_entregas'].iloc[0].round(2)
            media = aux5['media_entregas'].mean()
            diferença = ( ultima_hora / media).round(3)
            diferença_percentual=((diferença - 1)*100).round(3)
            st.metric(f'Ultima hora',ultima_hora ,f'{diferença_percentual}%')
            

    st.markdown( """---""" )
    
    #segunda linha
    with st.container():
        st.markdown('##### Top 20 Entregadores')
        col1, col2 = st.columns(2)

        with col1:
            with st.container():
                fig11 = fig11(df1)

                st.plotly_chart(fig11, theme="streamlit", use_container_width=True,  config=config_graph)#use_container_width=True,



        with col2:
            with st.container():
                fig12 = fig12(df1)

                st.plotly_chart(fig12, theme="streamlit", use_container_width=True,  config=config_graph)#use_container_width=True,
