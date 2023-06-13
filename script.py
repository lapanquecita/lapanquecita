"""
Fuente: https://www.gob.mx/afac/acciones-y-programas/estadisticas-280404/
"""

import random
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go


MESES = {
    "ENE/JAN": 1,
    "FEB/FEB": 2,
    "MAR/MAR": 3,
    "ABR/APR": 4,
    "MAY/MAY": 5,
    "JUN/JUN": 6,
    "JUL/JUL": 7,
    "AGO/AUG": 8,
    "SEP/SEP": 9,
    "OCT/OCT": 10,
    "NOV/NOV": 11,
    "DIC/DEC": 12
}

NOMBRES = {
    "Ciudad De México/Mexico City": "Ciudad de México",
    "Tuxtla Gutierrez (Angel Albino Corzo)": "Tuxtla Gutiérrez",
    "San Jose Del Cabo": "San José del Cabo",
    "Merida": "Mérida",
    "Bajio": "Bajío",
    "Santa Lucía": "Santa Lucía (AIFA)",
    "Culiacan": "Culiacán",
    "Minatitlan": "Minatitlán",
    "Torreon": "Torreón",
    "San Luis Potosi": "San Luis Potosí",
    "Cancun": "Cancún",
    "Cd. Del Carmen": "Cd. del Carmen",
    "Mazatlan": "Mazatlán",
    "Cd. Juarez": "Cd. Juárez",
}


def main():

    # Cargamos el dataset de la AFAC.
    df = pd.read_csv("./AFAC.csv")

    # Seleccionamos un aeropuerto al azar.
    aeropuertos = df["AEROPUERTO / AIRPORT"].unique()
    aeropuerto = random.choice(aeropuertos)

    # Generamos las series de tiempo del aeropuerto seleccionado.
    data = extraer_series_de_tiempo(df, aeropuerto, "PASAJEROS")
    data2 = extraer_series_de_tiempo(df, aeropuerto, "OPERACIONES")

    # Aplicamos un suavizado usando la media móvil anual.
    # De esta forma eliminamos el ruido estacional.
    data_movil = data.rolling(12).mean()
    data2_movil = data2.rolling(12).mean()

    # Seleccionamos los últimos 96 meses (8 años).
    meses = -96

    data = data[meses:]
    data2 = data2[meses:]

    data_movil = data_movil[meses:]
    data2_movil = data2_movil[meses:]

    # Limpiamos el nombre del aeropuerto, ya que algunos no vienen con acentos.
    aeropuerto = aeropuerto.title()
    aeropuerto = NOMBRES.get(aeropuerto, aeropuerto)

    # Vamos a crear 4 gráficas de linea, estas serán para pasajeros
    # y operaciones de origen nacional e internacional..
    graficar(data, data_movil, aeropuerto, "pasajeros",
             "nacionales", "NACIONAL/DOMESTIC")
    graficar(data, data_movil, aeropuerto, "pasajeros",
             "internacionales", "INTERNACIONAL/ INTERNATIONAL")
    graficar(data2, data2_movil, aeropuerto, "operaciones",
             "nacionales", "NACIONAL/DOMESTIC")
    graficar(data2, data2_movil, aeropuerto, "operaciones",
             "internacionales", "INTERNACIONAL/ INTERNATIONAL")


def graficar(df, df_movil, aeropuerto, tipo, origen, columna):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[columna],
            name="Valores absolutos",
            mode="lines",
            marker_color="#18ffff",
            opacity=1.0,
            line_width=4,
            line_shape="spline",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_movil.index,
            y=df_movil[columna],
            name="Promedio móvil a 12 periodos",
            mode="lines",
            marker_color="#ffca28",
            opacity=1.0,
            line_width=4,
            line_shape="spline",
        )
    )

    fig.update_xaxes(
        tickformat="%m<br>%Y",
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        gridwidth=0.5,
        mirror=True,
        nticks=20,
    )

    fig.update_yaxes(
        title="Número de registros mensuales",
        title_standoff=6,
        ticks="outside",
        ticklen=10,
        tickcolor="#FFFFFF",
        linewidth=2,
        showgrid=True,
        gridwidth=0.5,
        showline=True,
        mirror=True,
        nticks=20,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        showlegend=True,
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        width=1280,
        height=720,
        font_color="#FFFFFF",
        font_size=16,
        title_text=f"Número de {tipo} {origen} mensuales en el aeropuerto de <b>{aeropuerto}</b>",
        title_x=0.5,
        title_y=0.96,
        margin_t=60,
        margin_l=105,
        margin_r=40,
        margin_b=110,
        title_font_size=22,
        plot_bgcolor="#1A1A2E",
        paper_bgcolor="#16213E",
        annotations=[
            dict(
                x=0.01,
                y=-0.185,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: AFAC (2023)"
            ),
            dict(
                x=0.5,
                y=-0.185,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Fecha de registro (mes y año)"
            ),
            dict(
                x=1.01,
                y=-0.185,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita"
            ),
        ]
    )

    fig.write_image(f"./{tipo}_{origen}.png")


def extraer_series_de_tiempo(df, aeropuerto, tipo):
    """
    Genera series de tiempo de un aeropuerto.
    """

    lista_df = list()

    # Filtrar por aeropuerto y tipo de información.
    df = df[df["AEROPUERTO / AIRPORT"] == aeropuerto]
    df = df[df["OPCIONES/ OPTIONS"].str.contains(tipo)]

    # iteramos sobre cada año disponible.
    for año in df["AÑO / YEAR"].unique():

        # Seleccionamos el año de la iteración.
        temp_df = df[df["AÑO / YEAR"] == año]

        # Agrupamos por tipo de pasajero.
        temp_df = temp_df.groupby("TIPO/ TYPE").sum()

        # Seleccionamos solo las columnas de meses y volteamos el DataFrame
        # para que los meses sean el nuevo índice.
        temp_df = temp_df[MESES.keys()].transpose()

        # Convertimos el índice a DateTimeIndex.
        temp_df.index = temp_df.index.map(
            lambda x: datetime(año, MESES[x], 1))

        # Agregamos el DataFrame temporal a la lista de DataFrames.
        lista_df.append(temp_df)

    # Unimos todos los DataFrames.
    final = pd.concat(lista_df)

    # Agregamos una columna para el total y filtramos los registros en ceros.
    final["total"] = final.sum(axis=1)
    final = final[final["total"] != 0]

    return final


if __name__ == "__main__":

    main()
