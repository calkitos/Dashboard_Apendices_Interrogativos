#-----------------------------------------------------------------
#BIBLIOTECAS------------------------------------------------------
#-----------------------------------------------------------------
#pip install streamlit
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def main():
    #-----------------------------------------------------------------
    #DATOS------------------------------------------------------------
    #-----------------------------------------------------------------
    df_busqueda = pd.read_csv('https://raw.githubusercontent.com/calkitos/Dashboard_Apendices_Interrogativos/data/resultados_busqueda_corpus.csv', index_col = 0)
    df_cuenta = pd.read_csv('https://raw.githubusercontent.com/calkitos/Dashboard_Apendices_Interrogativos/data/cuenta_palabras.csv', index_col = 0)
    
    #-----------------------------------------------------------------
    #LIMPIEZA------------------------------------------------------------
    #-----------------------------------------------------------------
    df_busqueda.loc[:, 'Ciudad'] = df_busqueda.loc[:, 'Ciudad'].apply(lambda x: 'México, D.F.' if x == 'México, D. F.' else x)
    df_busqueda.loc[:, 'Sexo'] = df_busqueda.loc[:, 'Sexo'].apply(lambda x: np.nan if x == ' ' else x)
    df_busqueda.loc[:, 'Edad'] = df_busqueda.loc[:, 'Edad'].apply(lambda x: np.nan if x in ['desc', 'desconocido'] else x)
    df_busqueda.loc[:, 'Edad'] = df_busqueda.loc[:, 'Edad'].astype(np.float64)
    df_busqueda.loc[:, 'Educación'] = df_busqueda.loc[:, 'Educación'].apply(lambda x: np.nan if x == 'desconocido' else x)
    df_busqueda.loc[:, 'Educación'] = df_busqueda.loc[:, 'Educación'].apply(lambda x: 'alto' if x == '3' else x)
    df_busqueda.loc[:, 'Grupo de edad'] = df_busqueda.loc[:, 'Grupo de edad'].apply(lambda x: np.nan if x in [' desconocido', 'desconocido'] else x)
    df_busqueda.loc[:, 'Grupo de edad'] = df_busqueda.loc[:, 'Grupo de edad'].apply(lambda x: '1' if x == ' 1' else x)
    df_busqueda.loc[:,'País'] = df_busqueda.loc[:,'País'].apply(lambda x: 'México' if x == 'Mexico' else x)
    
    #-----------------------------------------------------------------
    #APP--------------------------------------------------------------
    #-----------------------------------------------------------------
    def plot_data(ciudad, unidad):
    
        if ciudad is None or unidad is None:
            raise PreventUpdate
    
        else:
    
            filtro1 = df_cuenta[df_cuenta['Ciudad'].isin(ciudad)]
            filtro2 = df_busqueda[df_busqueda['Unidad'].isin(unidad)]
            filtro2 = filtro2[filtro2['Ciudad'].isin(ciudad)]
    
            # Box de promedio por ciudad de cuenta de palabras por entrevista
            fig1 = px.box(filtro1, x = 'Ciudad', y = 'Cuenta de palabras')
    
            # Pay de % de unidad por ciudad
            fig_pies = make_subplots(rows = 1, cols = len(filtro2.loc[:,'Ciudad'].unique()), specs= [[{'type': 'domain'} for i in range(len(filtro2.loc[:,'Ciudad'].unique()))]])
    
            for i, x in enumerate(filtro2.loc[:, ['Unidad', 'Ciudad']].groupby('Ciudad')):
    
                titulo, df = (x[0], x[1])
                df_counts = pd.DataFrame(df.loc[:,'Unidad'].value_counts())
                df_counts = df_counts.reset_index()
    
                labels = df_counts.loc[:, 'Unidad']
                values = df_counts.loc[:, 'count']
    
                fig_pies.add_trace(go.Pie(labels  = labels, values = values, title = titulo, titleposition = 'bottom center'), row = 1, col = i+1)
    
            # Treemap de unidad, ciudad y sexo
            ciudad_unidad_sexo = pd.DataFrame(filtro2.loc[:, ['Ciudad', 'Unidad', 'Sexo']].groupby(['Ciudad', 'Unidad']).value_counts())
            ciudad_unidad_sexo = ciudad_unidad_sexo.reset_index()
    
            tree_fig = px.treemap(ciudad_unidad_sexo, path = [px.Constant('all'), 'Ciudad', 'Unidad', 'Sexo'], values = 'count')
            tree_fig.update_traces(root_color = 'lightblue')
            tree_fig.update_layout(margin = dict(t = 50, l = 25, r = 25, b = 25))
    
            # Figuras de variables PRESEEA
            cuenta_unidadXsexo = pd.DataFrame(filtro2.loc[:, ['Unidad', 'Ciudad', 'Sexo']].groupby(['Ciudad', 'Sexo']).value_counts()).reset_index()
            cuenta_unidadXedad = pd.DataFrame(filtro2.loc[:, ['Unidad', 'Ciudad', 'Grupo de edad']].groupby(['Ciudad', 'Grupo de edad']).value_counts()).reset_index()
            cuenta_unidadXeducacion = pd.DataFrame(filtro2.loc[:, ['Unidad', 'Ciudad', 'Educación']].groupby(['Ciudad', 'Educación']).value_counts()).reset_index()
    
            fig_uXsexo = px.bar(cuenta_unidadXsexo, x = 'Ciudad', y = 'count', pattern_shape = 'Unidad', color = 'Sexo', barmode = 'group')
            fig_uXedad = px.bar(cuenta_unidadXedad, x = 'Ciudad', y = 'count', pattern_shape = 'Unidad', color = 'Grupo de edad', barmode = 'group')
            fig_uXeducacion = px.bar(cuenta_unidadXeducacion, x = 'Ciudad', y = 'count', pattern_shape = 'Unidad', color = 'Educación', barmode = 'group')
    
    
    
            return fig1, fig_pies, tree_fig, fig_uXsexo, fig_uXedad, fig_uXeducacion
    
    st.markdown('''
        # Tablero de apéndices interrogativos
    
        Autor: Carlos Enrique Mora González
        
    ''')
    
    ciudad = st.multiselect(label = 'Selecciona una ciudad', options = ['Guadalajara', 'Mexicali', 'México, D.F.', 'Monterrey', 'Puebla'], default = ['Monterrey', 'México, D.F.'])
    if 'unidad' not in st.session_state:
        st.session_state['unidad'] = ['¿sí?', '¿no?']
    unidad = st.session_state['unidad']
    fig1, fig_pies, tree_fig, fig_uXsexo, fig_uXedad, fig_uXeducacion = plot_data(ciudad, unidad)

    st.markdown('''
        ### Cuenta de palabras por entrevista en cada ciudad
        
        Para realizar comparaciones contextualizadas, creo que un factor importante es conocer el total de palabras de las entrevistas. La siguiente es una gráfica de cajas que muestra la relación del promedio de palabras por entrevista en cada ciudad. Ciudades como Puebla tienen un mayor promedio de palabras que otras como Mexicali. Esto significa que, dentro de un margen razonable, es esperable encontrar más apéndices interrogativos en términos absolutos en la primera ciudad que en la segunda.
    ''')
    st.write(fig1)
    
    st.markdown('''
        ## Aparición de apéndices interrogativos
        A continuación se presentan los resultados estadísticos de aparición de los apéndices interrogativos estudiados (_¿sí?_, _¿no?_, _¿o sí?_ y _¿o no?_). A partir de los metadatos contenidos en los archivos de texto que conforman los documentos de entrevistas de PRESEEA, es posible distinguir no solamente la ciudad donde se utilizó uno u otro, sino también otras variables sociolingüísticas del enunciador, tales como: sexo, nivel de instrucción y edad. Las siguientes gráficas tratan de mantenerse en la línea de las propuestas por Cestero Mancera (2019) para permitir cierto grado de comparación con sus resultados.
    ''')
    st.session_state['unidad'] = st.multiselect(label = 'Selecciona un apéndice interrogativo', options = ['¿sí?', '¿no?', '¿o sí?', '¿o no?'], default = ['¿sí?', '¿no?'])
    
    st.markdown('''
        ### Proporción relativa de la unidad por cada ciudad
        La siguiente gráfica muestra la proporción de las unidades comparadas a partir del total de sus apariciones. Nótese que no refleja un porcentaje del total de palabras de la entrevista ni tampoco del total de apéndices interrogativos; solamente aquéllos que están seleccionados. En general, el apéndice _¿no?_ es abrumadoramente más frecuente que el resto. Por su parte, los apéndices con conjunción disyuntiva _¿o sí?_ y _¿o no?_ son una fracción minoritaria.
    ''')
    st.write(fig_pies)

    st.markdown('''
        ### Proporción de unidades según variables de sexo para cada ciudad
        La siguiente es una gráfica de árbol que compara la proporción de distintas variables anidadas mediante el tamaño de las cajas. Así, una caja dentro de otra representa un subconjunto de la mayor y dos cajas dentro del mismo conjunto son entre sí conjuntos disjuntos.
        En esta gráfica llama la atención el hecho de que las ciudades presentan patrones particulares no sólo respecto al uso de unidades, especialmente _¿sí?_ y _¿no?_, sino también de las proporciones de hombres y mujeres que los usan. Por ejemplo, en Guadalajara, los hombres casi no usan _¿no?_
    ''')
    st.write(tree_fig)
    st.write(fig_uXsexo)
    st.write(fig_uXedad)
    st.write(fig_uXeducacion)

if __name__ == "__main__":
    main()
