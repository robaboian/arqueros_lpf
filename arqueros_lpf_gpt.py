import streamlit as st
import LanusStats as ls
import pandas as pd
from mplsoccer import PyPizza


def main():
    # Inicializa el scraper
    fbref = ls.Fbref()

    # Obtén los datos
    df1 = fbref.get_player_season_stats(
        'keepersadv', 'Primera Division Argentina')
    df2 = fbref.get_player_season_stats(
        'keepers', 'Primera Division Argentina')

    # Selecciona las columnas relevantes de df2
    df2 = df2[['Player', 'Min', 'SoTA', 'Saves', 'CS', 'MP']]

    # Fusiona los DataFrames en base a la columna 'Player'
    arqueros = pd.merge(df1, df2, on='Player', how='inner')

    # Función para renombrar columnas duplicadas
    def rename_duplicated_columns(df):
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index.values.tolist()] = [dup + '_' +
                                                             str(i) if i != 0 else dup for i in range(sum(cols == dup))]
        df.columns = cols

    rename_duplicated_columns(arqueros)

    # Reorganiza y renombra columnas
    arqueros = arqueros[['Player', 'Squad', 'Born', 'Min', '90s', 'GA', 'PSxG', 'SoTA', 'PSxG/SoT', 'Saves',
                         'CS', 'Att (GK)', 'AvgLen', 'AvgLen_1', 'Stp', '#OPA']]

    rename_dict = {
        'Player': 'Jugador',
        'Squad': 'Equipo',
        'Born': 'Nacimiento',
        'Min': 'Minutos',
        'GA': 'GC',
        'SoTA': 'Remates (arco)',
        'Saves': 'Atajadas',
        'CS': 'Valla invicta',
        'Att (GK)': 'Pases intentados',
        'AvgLen': 'Distancia promedio de pase',
        'AvgLen_1': 'Distancia promedio de saque de arco',
        'Stp': 'Centros cortados',
        '#OPA': 'Acciones defensivas fuera del área'
    }

    arqueros.rename(columns=rename_dict, inplace=True)

    # Limpieza y conversión de datos
    arqueros['Minutos'] = arqueros['Minutos'].str.replace(
        ',', '', regex=False).astype(int)

    # Conversión de columnas a tipos correctos
    arqueros[['Nacimiento', 'Minutos', 'GC', 'Remates (arco)', 'Atajadas', 'Valla invicta',
              'Pases intentados', 'Centros cortados', 'Acciones defensivas fuera del área']] = \
        arqueros[['Nacimiento', 'Minutos', 'GC', 'Remates (arco)', 'Atajadas', 'Valla invicta',
                  'Pases intentados', 'Centros cortados', 'Acciones defensivas fuera del área']].astype(int)

    arqueros[['90s', 'PSxG', 'PSxG/SoT', 'Distancia promedio de pase', 'Distancia promedio de saque de arco']] = \
        arqueros[['90s', 'PSxG', 'PSxG/SoT', 'Distancia promedio de pase',
                  'Distancia promedio de saque de arco']].astype(float)

    # Calcula 'Goles evitados'
    arqueros['Goles evitados'] = arqueros['PSxG'] - arqueros['GC']

    # Elimina duplicados
    arqueros = arqueros.drop_duplicates()

    # Condiciones para eliminar filas específicas
    condiciones_a_eliminar = (
        (arqueros['Jugador'] == 'Ezequiel Centurión') & (arqueros['Equipo'] == 'River Plate') & (arqueros['Minutos'] == 810) |
        (arqueros['Jugador'] == 'Ezequiel Centurión') & (arqueros['Equipo'] == 'River Plate') & (arqueros['Minutos'] == 90) |
        (arqueros['Jugador'] == 'Ezequiel Centurión') & (arqueros['Equipo'] == 'Independiente Rivadavia') & (arqueros['Minutos'] == 90) |
        (arqueros['Jugador'] == 'Nahuel Losada') & (arqueros['Equipo'] == 'Belgrano') & (arqueros['Minutos'] == 540) |
        (arqueros['Jugador'] == 'Nahuel Losada') & (
            arqueros['Equipo'] == 'Lanús') & (arqueros['Minutos'] == 450)
    )

    arqueros = arqueros[~condiciones_a_eliminar]

    # Reinicia el índice
    arqueros = arqueros.reset_index(drop=True)
    arqueros['Minutos'] = arqueros['Minutos'].astype(str).str.replace(',', '')

    arqueros['Minutos'] = arqueros['Minutos'].astype(int)

    arqueros = arqueros[arqueros['Minutos'] > 180]
    # Calcula métricas por 90 minutos
    arqueros90 = pd.DataFrame()
    arqueros90['Jugador'] = arqueros['Jugador']
    arqueros90['Equipo'] = arqueros['Equipo']
    arqueros90['Nacimiento'] = arqueros['Nacimiento']
    arqueros90['Minutos'] = arqueros['Minutos']
    arqueros90['90s'] = arqueros['90s']
    arqueros90['Goles en contra'] = arqueros['GC'] / arqueros['90s']
    arqueros90['PSxG'] = arqueros['PSxG'] / arqueros['90s']
    arqueros90['Remates (al arco) en contra'] = arqueros['Remates (arco)'] / \
        arqueros['90s']
    arqueros90['Atajadas'] = arqueros['Atajadas'] / arqueros['90s']
    arqueros90['Pases intentados'] = arqueros['Pases intentados'] / \
        arqueros['90s']
    arqueros90['Distancia promedio de pase'] = arqueros['Distancia promedio de pase']
    arqueros90['Distancia promedio de saque de arco'] = arqueros['Distancia promedio de saque de arco']
    arqueros90['Centros cortados'] = arqueros['Centros cortados'] / \
        arqueros['90s']
    arqueros90['Acciones defensivas fuera del área'] = arqueros['Acciones defensivas fuera del área'] / arqueros['90s']
    arqueros90['Goles evitados'] = arqueros['Goles evitados'] / arqueros['90s']

    arqueros90 = arqueros90.round(2)

    # Crea el DataFrame con los datos normalizados
    arqueros100 = pd.DataFrame()
    arqueros100['Jugador'] = arqueros['Jugador']
    arqueros100['Equipo'] = arqueros['Equipo']
    arqueros100['Nacimiento'] = arqueros['Nacimiento']
    arqueros100['Minutos'] = arqueros['Minutos']
    arqueros100['90s'] = arqueros['90s']
    arqueros100['Goles en contra'] = (
        arqueros90['Goles en contra'].rank(pct=True) * 100).astype(int)
    arqueros100['PSxG'] = (arqueros90['PSxG'].rank(pct=True) * 100).astype(int)
    arqueros100['Remates (al\narco) en contra'] = (
        arqueros90['Remates (al arco) en contra'].rank(pct=True) * 100).astype(int)
    arqueros100['Atajadas'] = (
        arqueros90['Atajadas'].rank(pct=True) * 100).astype(int)
    arqueros100['Pases intentados'] = (
        arqueros90['Pases intentados'].rank(pct=True) * 100).astype(int)
    arqueros100['Distancia promedio\nde pase'] = (
        arqueros90['Distancia promedio de pase'].rank(pct=True) * 100).astype(int)
    arqueros100['Distancia promedio\nde saque de arco'] = (
        arqueros90['Distancia promedio de saque de arco'].rank(pct=True) * 100).astype(int)
    arqueros100['Centros cortados'] = (
        arqueros90['Centros cortados'].rank(pct=True) * 100).astype(int)
    arqueros100['Acciones defensivas\nfuera del área'] = (
        arqueros90['Acciones defensivas fuera del área'].rank(pct=True) * 100).astype(int)
    arqueros100['Goles evitados'] = (
        arqueros90['Goles evitados'].rank(pct=True) * 100).astype(int)

    st.header("Pizza Plot de arqueros de la Liga Profesional de Fútbol 2024")
    st.write("###### Los datos fueron normalizados cada 90' y luego estandarizados en percentiles. Debajo del gráfico pueden encontrar la tabla para poder contextualizar la información. Se descartaron a los jugadores que no sumaron más de 180 minutos.")
    st.write("Un percentil es una medida estadística para comparar resultados, nos permite saber cómo está situado un valor en función de una muestra.")

    st.write("###### X: @robaboian_")

    arquero_nombre = st.selectbox(
        'Arqueros:', arqueros100['Jugador'].sort_values().unique(), index=None)

    # Filtrar los datos del arquero seleccionado
    arquero = arqueros100[arqueros100['Jugador'] == arquero_nombre]

    if arquero.empty:
        st.write(
            "Por favor, seleccione un arquero de la lista para que pueda visualizarse el gráfico.")
        return

    # Convertir datos del arquero a una serie de enteros
    datosradar = ['Goles en contra', 'PSxG', 'Remates (al\narco) en contra', 'Atajadas', 'Pases intentados',
                  'Distancia promedio\nde pase', 'Distancia promedio\nde saque de arco',
                  'Centros cortados', 'Acciones defensivas\nfuera del área', 'Goles evitados']

    valores = arquero[datosradar].values.flatten()

    # Asegurarse de que los valores sean enteros
    valores = valores.astype(int)  # Si los valores pueden ser flotantes
    valores = valores.tolist()  # Convertir a lista de flotantes si es necesario

    pizza = PyPizza(
        params=datosradar,
        background_color='#FFFFFF',
        straight_line_color='#000000',
        straight_line_lw=2,
        last_circle_lw=2,
        last_circle_ls='-',
        last_circle_color='#000000',
        other_circle_lw=1,
        other_circle_color='#000000',
        other_circle_ls='--')

    fig, ax = pizza.make_pizza(
        figsize=(20, 20),
        values=valores,
        kwargs_slices=dict(facecolor="#1ec180",
                           edgecolor="#000000", zorder=2, linewidth=2),
        kwargs_params=dict(color="#000000", fontsize=25,
                           weight='bold', va="center"),
        kwargs_values=dict(color="#000000", fontsize=20, weight='bold', zorder=6, bbox=dict(
            edgecolor="#04f5ff", facecolor="#04f5ff",
            boxstyle="round,pad=0.2", lw=2)),
        param_location=105)
    
    st.pyplot(fig)

    st.write("###### Referencias:")
    st.write("###### PSxG: Índice de expectativa de gol post-remate. Referencia a la peligrosidad de los remates al arco recibidos. | Goles evitados: Se calcula por la diferencia entre los goles en contra y el PSxG.")

    st.markdown(
    """
    Me gustaría agradecer a [Lanus Stats](https://www.youtube.com/@LanusStats/videos) y a [McKay Johns](https://www.youtube.com/@McKayJohns) por sus aportes a la comunidad.
    """)
    
    st.subheader("Estadísticas de los arqueros estandarizadas cada 90'")
    st.dataframe(arqueros90)

   

    
    



if __name__ == "__main__":
    main()
