import streamlit as st
from PIL import Image


st.set_page_config(page_title="Home", page_icon=":bar_chart:")

with open('assets/css.css') as f:
  st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)





#image_path = 'C:/Users/luizf/OneDrive/Documentos/repos/FTC/'

image = Image.open('logo.jpg')
st.sidebar.markdown('### Cury Company')
st.sidebar.image(image, width=200)

st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown( """---""" )

st.markdown('##### Cury Company Growth Dashboard')

st.markdown('Growth Dashboard foi construido para acompanhar as métricas de crescimento dos entregadores e dos restaurentes')


st.markdown('### Como utilizar esse Dashboard?')

st.markdown("""
  - Na barra lateral você tem duas opções para poder filtar o Dashboard:
      - Data limite ( O dashboard será filtrado de acordo a data máxima escolhida.)
      - Tipo de Tráfego (Onde o usuário poderá escolher as quatro opções de tráfego.)
      
      
  ### Conteúdo do Dashboard :
    ##### Visão Entregador
    - Acompanhamento das métricas dos entregadores
    
    ##### Visão Restaurantes
    - Indicadores de crescimento dos restaurantes
                
    ##### Visão Empresa
    - Visão Gerencial: Métricas gerais de Comportamento;
    - Visão Tática: Indicadores sobre o crescimento dos pedidos;
    - Visão Geográfica: Quantidade de pedidos  por clientes.""")


