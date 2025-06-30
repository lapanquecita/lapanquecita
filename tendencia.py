"""
Fuente: https://www.gob.mx/afac/acciones-y-programas/estadisticas-280404/
"""

import random

import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.seasonal import STL


NOMBRES = {
    "Ciudad De México": "Ciudad de México",
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
    df = pd.read_csv("./data.csv", parse_dates=["FECHA"])

    # Seleccionamos un aeropuerto al azar.
    aeropuertos = df["AEROPUERTO"].unique()
    aeropuerto = random.choice(aeropuertos)

    # Filtramos el DataFrame con el aeropuerto seleccionado.
    df = df[df["AEROPUERTO"] == aeropuerto]

    # Quitamos valores en cero.
    df = df[df["TOTAL"] != 0]

    # Transformamos el DataFrame para generar series de tiempo para
    # pasajeros y operaciones por mes.
    # En caso de no haber registros interncionales, los creamos en cero.
    pasajeros = df[df["OPCIONES"] == "PASAJEROS"].pivot_table(
        index="FECHA", columns="TIPO", values="TOTAL", aggfunc="sum", fill_value=0
    )

    if "INTERNACIONAL" not in pasajeros.columns:
        pasajeros["INTERNACIONAL"] = 0

    operaciones = df[df["OPCIONES"] == "OPERACIONES"].pivot_table(
        index="FECHA", columns="TIPO", values="TOTAL", aggfunc="sum", fill_value=0
    )

    if "INTERNACIONAL" not in operaciones.columns:
        operaciones["INTERNACIONAL"] = 0

    # Calculamos las tendencias. Nuestra frecuencia es mensual, se usarán 12 periodos en automático.
    pasajeros["NACIONAL_trend"] = STL(pasajeros["NACIONAL"]).fit().trend
    pasajeros["INTERNACIONAL_trend"] = STL(pasajeros["INTERNACIONAL"]).fit().trend

    operaciones["NACIONAL_trend"] = STL(operaciones["NACIONAL"]).fit().trend
    operaciones["INTERNACIONAL_trend"] = STL(operaciones["INTERNACIONAL"]).fit().trend

    # Seleccionamos los últimos 120 meses (10 años).
    meses = 120

    pasajeros = pasajeros.tail(meses)
    operaciones = operaciones.tail(meses)

    # Limpiamos el nombre del aeropuerto, ya que algunos no vienen con acentos.
    aeropuerto = aeropuerto.title()
    aeropuerto = NOMBRES.get(aeropuerto, aeropuerto)

    # Vamos a crear 4 gráficas de linea, estas serán para pasajeros
    # y operaciones de origen nacional e internacional.
    graficar(
        pasajeros["NACIONAL"],
        pasajeros["NACIONAL_trend"],
        aeropuerto,
        "pasajeros",
        "nacionales",
    )

    graficar(
        pasajeros["INTERNACIONAL"],
        pasajeros["INTERNACIONAL_trend"],
        aeropuerto,
        "pasajeros",
        "internacionales",
    )

    graficar(
        operaciones["NACIONAL"],
        operaciones["NACIONAL_trend"],
        aeropuerto,
        "operaciones",
        "nacionales",
    )

    graficar(
        operaciones["INTERNACIONAL"],
        operaciones["INTERNACIONAL_trend"],
        aeropuerto,
        "operaciones",
        "internacionales",
    )


def graficar(df, df_tendencia, aeropuerto, tipo, origen):
    """
    Esta función crea un lienzo con dos gráficas de línea,
    una con las cifras absolutas y otra con la tendencia.
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
        tickformat="s",
        title_standoff=15,
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
        legend_borderwidth=2,
        legend_bordercolor="#FFFFFF",
        showlegend=True,
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Número de {tipo} {origen} mensuales en el aeropuerto de <b>{aeropuerto}</b>",
        title_x=0.5,
        title_y=0.97,
        margin_t=80,
        margin_l=160,
        margin_r=40,
        margin_b=160,
        title_font_size=36,
        plot_bgcolor="#1A1A2E",
        paper_bgcolor="#16213E",        
        annotations=[
            dict(
                x=0.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: AFAC (2025)",
            ),
            dict(
                x=0.5,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro",
            ),
            dict(
                x=1.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./imgs/{tipo}_{origen}.png")


if __name__ == "__main__":
    main()
