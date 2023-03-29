#Imports
import pandas as pd
import io
import plotly.express as px
import folium
from haversine import haversine
from datetime import *
import streamlit as st

from PIL import Image

from streamlit_folium import folium_static
from folium.plugins   import MarkerCluster

import streamlit.components.v1 as components
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


st.set_page_config(page_title="Visao Empresa", page_icon=":bar_chart:", layout="wide")
# ========================
# Obtendo os dados
# ========================

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

def fig1(df1):
      aux1 = df1[['Order_Date', 'ID']].groupby('Order_Date').count().reset_index()
      aux1 = df1[['Order_Date', 'ID']].groupby('Order_Date').count().reset_index()
      aux1['Order_Date'] = pd.to_datetime(aux1['Order_Date'],  format="%d-%m-%Y").dt.date
      #fazendo o grafico
      fig1 = px.bar(aux1, 
                    x='Order_Date', 
                    y='ID',
                    color_discrete_sequence=px.colors.qualitative.T10,
                    text='ID', 
                    #template='plotly_white',
                    labels={'Order_Date': 'Data do Pedido',
                              'ID': 'Quantidade de Pedidos'})
        
      fig1.update_layout(main_config)
      return fig1

def fig2(df1):
      aux3 = df1[['Road_traffic_density', 'ID']].groupby('Road_traffic_density').count().reset_index()
      #aux3 = aux3.loc[aux3['Road_traffic_density']] != 'NaN'
      aux3['entregas_perc'] = aux3['ID'] / aux3['ID'].sum()
      
      fig2 = px.pie(aux3, values = 'entregas_perc', names = 'Road_traffic_density')
      fig2.update_layout(main_config)
                      
      return fig2
def fig3(df1):
    aux4 = df1[['City', 'Road_traffic_density', 'ID']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    aux4 = aux4.loc[aux4['City']!= 'NaN ']
          

    fig3 = px.bar(aux4, x='City', y='ID', color='Road_traffic_density', barmode='group')


    fig3.update_layout(main_config)
    return fig3

def fig4(df1):  
    aux5 = df1['Week_of_Year'] = df1['Order_Date'].dt.strftime('%U')
    aux5 = df1[['ID', 'Week_of_Year']].groupby('Week_of_Year').count().reset_index()
    fig4 = px.line(aux5, x='Week_of_Year', y='ID')
    fig4.update_traces(mode="markers+lines")
    fig4.update_layout(main_config)
    return fig4

def fig5(df1):
    aux5 = df1[['ID', 'Hour_Orderd']].groupby('Hour_Orderd').count().reset_index()
    fig5 = px.bar(aux5, 
                      x='Hour_Orderd', 
                      y='ID',
                      color_discrete_sequence=px.colors.qualitative.T10,
                      text='ID', 
                      #template='plotly_white',
                      labels={'Hour_Orderd': 'Hora',
                                'ID': 'Quantidade de Pedidos'})
          
    fig5.update_layout(main_config)
                            
    return fig5

def density_map(df1):
    aux6 = df1[['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
    aux6 = aux6.groupby(['City', 'Road_traffic_density']).median().reset_index()
    aux = df1[['Delivery_location_latitude', 'Delivery_location_longitude','ID']].groupby(['Delivery_location_latitude', 'Delivery_location_longitude']).count().reset_index()
    
    density_map = folium.Map(location=[df1['Delivery_location_latitude'].mean(),
                  df1['Delivery_location_longitude'].mean()], 
                  zoom_start=3)

    marker_cluster = MarkerCluster().add_to( density_map )
    for name, row in aux.iterrows():
        folium.Marker( [row['Delivery_location_latitude'], row['Delivery_location_longitude'] ], 
                        popup='Quandidade: {}pedidos'.format(int(row['ID']),
                                                             row['Delivery_location_latitude'],
                                                             row['Delivery_location_longitude']) ).add_to( marker_cluster )
    return density_map
# ========================
# Layout Sidebar
# ========================

df1 = clean_data(df)


with open('css.css') as f:
  st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)


st.header('Marketplace - Visão Empresa')
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



# ========================
# Layout no Streamlit
# ========================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
  with st.container():

    st.markdown('##### Pedidos por Dia')
      
    with st.container():  
      fig1 = fig1(df1)
      st.plotly_chart(fig1, theme="streamlit", use_container_width=True,  config=config_graph)#use_container_width=True,

#segunda
# linha
  with st.container():
    col1,col2 = st.columns(2)

    with col1:
      st.markdown('##### Percentual por Tráfego')
      fig2 = fig2(df1)
      st.plotly_chart(fig2, use_container_width=True, config=config_graph)
   

    with col2:
      st.markdown('##### Por Cidade e Trafego')
      with st.container():               
        fig3 = fig3(df1)
        st.plotly_chart(fig3, use_container_width=True, config=config_graph)
    

with tab2:

  st.markdown('##### Quantidade de Pedidos Por Semana')
  with st.container():              
    fig4 = fig4(df1)
    st.plotly_chart(fig4, use_container_width=True, config=config_graph)

  #with st.container(''):
  Container1 = st.container()  
  Container1.markdown('##### Quantidade de Pedidos Por Hora')
  fig5 = fig5(df1)
  Container1.plotly_chart(fig5, theme="streamlit", use_container_width=True,  config=config_graph)#use_container_width=True,



with tab3:
  st.markdown('##### Quantidade de Pedidos Por Residencia')
  with st.container():
    density_map = density_map(df1)
    folium_static(density_map, width=1024,height=600)
    




