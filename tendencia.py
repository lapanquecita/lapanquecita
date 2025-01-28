"""
Fuente: https://www.gob.mx/afac/acciones-y-programas/estadisticas-280404/
"""

import random
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.seasonal import STL


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
    "DIC/DEC": 12,
}

NOMBRES = {
    "Ciudad De México/Mexico City": "Ciudad de México",
    "Tuxtla Gutierrez (Angel Albino Corzo)": "Tuxtla Gutiérrez",
    "San Cristobal De Las Casas": "San Cristóbal de las Casas",
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
    """
    Iniciamos el script que genera las gráficas de
    pasajeros y operaciones.
    """

    # Cargamos el dataset de la AFAC.
    df = pd.read_csv("./data.csv")

    # Seleccionamos un aeropuerto al azar.
    aeropuertos = df["AEROPUERTO / AIRPORT"].unique()
    aeropuerto = random.choice(aeropuertos)

    # Generamos las series de tiempo del aeropuerto seleccionado.
    data = extraer_series_de_tiempo(df, aeropuerto, "PASAJEROS")
    data2 = extraer_series_de_tiempo(df, aeropuerto, "OPERACIONES")

    # Calculamos las tendencias.
    data["NACIONAL/DOMESTIC_trend"] = STL(data["NACIONAL/DOMESTIC"]).fit().trend
    data["INTERNACIONAL/ INTERNATIONAL_trend"] = (
        STL(data["INTERNACIONAL/ INTERNATIONAL"]).fit().trend
    )

    data2["NACIONAL/DOMESTIC_trend"] = STL(data2["NACIONAL/DOMESTIC"]).fit().trend
    data2["INTERNACIONAL/ INTERNATIONAL_trend"] = (
        STL(data2["INTERNACIONAL/ INTERNATIONAL"]).fit().trend
    )

    # Seleccionamos los últimos 96 meses (8 años).
    meses = 96

    data = data.tail(meses)
    data2 = data2.tail(meses)

    # Limpiamos el nombre del aeropuerto, ya que algunos no vienen con acentos.
    aeropuerto = aeropuerto.title()
    aeropuerto = NOMBRES.get(aeropuerto, aeropuerto)

    # Vamos a crear 4 gráficas de linea, estas serán para pasajeros
    # y operaciones de origen nacional e internacional.
    graficar(
        data["NACIONAL/DOMESTIC"],
        data["NACIONAL/DOMESTIC_trend"],
        aeropuerto,
        "pasajeros",
        "nacionales",
    )

    graficar(
        data["INTERNACIONAL/ INTERNATIONAL"],
        data["INTERNACIONAL/ INTERNATIONAL_trend"],
        aeropuerto,
        "pasajeros",
        "internacionales",
    )

    graficar(
        data2["NACIONAL/DOMESTIC"],
        data2["NACIONAL/DOMESTIC_trend"],
        aeropuerto,
        "operaciones",
        "nacionales",
    )

    graficar(
        data2["INTERNACIONAL/ INTERNATIONAL"],
        data2["INTERNACIONAL/ INTERNATIONAL_trend"],
        aeropuerto,
        "operaciones",
        "internacionales",
    )


def graficar(df, df_tendencia, aeropuerto, tipo, origen):
    """
    Esta función crea dos gráficas de línea, una con las cifras absolutas y una con el promedio móvil.
    """

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df.values,
            name="Cifras absolutas",
            mode="lines",
            line_color="#18ffff",
            opacity=1.0,
            line_width=4,
            line_shape="spline",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_tendencia.index,
            y=df_tendencia.values,
            name="Tendencia (12 periodos)",
            mode="lines",
            line_color="#ffca28",
            opacity=1.0,
            line_width=4,
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
        separatethousands=True,
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
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
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
                text="Fuente: AFAC (2025)",
            ),
            dict(
                x=0.5,
                y=-0.185,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro",
            ),
            dict(
                x=1.01,
                y=-0.185,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./imgs/{tipo}_{origen}.png")


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
        temp_df.index = temp_df.index.map(lambda x: datetime(año, MESES[x], 1))

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
