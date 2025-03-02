import pandas as pd
import plotly.graph_objects as go


# Este diccionario es usado para limpiar los nombres
# de algunos aeropuertos.
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

MESES = [
    "Ene.",
    "Feb.",
    "Mar.",
    "Abr.",
    "May.",
    "Jun.",
    "Jul.",
    "Ago.",
    "Sep.",
    "Oct.",
    "Nov.",
    "Dic.",
]


def main(primer_año, segundo_año, opcion, aeropuerto):
    """
    Crea una gráfica de barras con dos grupos.
    Cada uno corresponde con cada año que se
    desea comparar.

    Parameters
    ----------
    primer_año : int
        El primer año que queremos comparar.

    segundo_año : int
        El segundo año que nos interesa comparar.

    opcion : str
        El tipo de opción, puede ser: OPERACIONES | PASAJEROS

    aeropuerto : str
        El nombre del aeropuerto que nos interesa comparar.

    """

    # Cargamos el dataset de estadísticas operativas.
    df = pd.read_csv("./data.csv", parse_dates=["FECHA"], index_col=0)

    # Filtramos por el aeropuerto que nos interesa.
    df = df[df["AEROPUERTO"] == aeropuerto]

    # Seleccionamos el tipo de opción.
    df = df[df["OPCIONES"] == opcion]

    # Seleccionamos los años.
    df = df[df.index.year.isin([primer_año, segundo_año])]

    # Transformamos el DataFrame para que el índice sean los meses
    # y las columnas los dos años a comparar.
    df = df.pivot_table(
        index=df.index.month,
        columns=df.index.year,
        values="TOTAL",
        aggfunc="sum",
        fill_value=0,
    )

    # Cambiamos los meses a sus nombres.
    df.index = MESES

    # Limpiamos el nombre del aeropuerto.
    aeropuerto = NOMBRES.get(aeropuerto.title(), aeropuerto.title())

    # Vamos a crear dos gráficas de barras sobre el mismo lienzo.
    # Una gráfica para cada año.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[primer_año],
            text=df[primer_año].apply(formatear_texto),
            name=f"<b>{primer_año}</b> (total: <b>{df[primer_año].sum():,.0f}</b>)",
            textposition="outside",
            marker_color="rgb(229, 134, 6)",
            marker_line_width=0,
            textfont_size=16,
            textfont_family="Oswald",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[segundo_año],
            text=df[segundo_año].apply(formatear_texto),
            name=f"<b>{segundo_año}</b> (total: <b>{df[segundo_año].sum():,.0f}</b>)",
            textposition="outside",
            marker_color="rgb(82, 188, 163)",
            marker_line_width=0,
            textfont_size=16,
            textfont_family="Oswald",
        )
    )

    fig.update_xaxes(
        ticks="outside",
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.35,
        mirror=True,
        nticks=12,
    )

    # Detectamos el valor máximo para poder ajustar la
    # escala vertical.
    valor_max = (
        df[primer_año].max()
        if df[primer_año].max() >= df[segundo_año].max()
        else df[segundo_año].max()
    )

    fig.update_yaxes(
        title=f"Total de {opcion} mensuales",
        range=[0, valor_max * 1.07],
        ticks="outside",
        separatethousands=True,
        title_font_size=18,
        tickfont_size=14,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.35,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        legend_orientation="h",
        showlegend=True,
        legend_x=0.5,
        legend_y=1.08,
        legend_xanchor="center",
        legend_yanchor="top",
        legend_font_size=16,
        width=1280,
        height=720,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=18,
        title_text=f"Comparación del número de {opcion.lower()} en el aeropuerto de <b>{aeropuerto}</b> ({primer_año} vs. {segundo_año})",
        title_x=0.5,
        title_y=0.975,
        margin_t=90,
        margin_r=40,
        margin_b=80,
        margin_l=100,
        title_font_size=22,
        plot_bgcolor="#18122B",
        paper_bgcolor="#393053",
        annotations=[
            dict(
                x=0.01,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: AFAC (2025)",
            ),
            dict(
                x=0.5,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes de registro",
            ),
            dict(
                x=1.01,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # El nombre del archivo depende de los parámetros
    # de la función principal.
    fig.write_image(f"./comparacion_{opcion}_{aeropuerto.lower()}.png")


def formatear_texto(x):
    """
    Esta función le da formato a las cifras
    para facilitar su lectura.
    """

    if x >= 1000000:
        return f"{x / 1000000:,.2f}M"
    elif x >= 100000:
        return f"{x / 1000:,.0f}k"
    elif x >= 10000:
        return f"{x / 1000:,.1f}k"
    else:
        return f"{x:,.0f}"


if __name__ == "__main__":
    main(2023, 2024, "PASAJEROS", "ACAPULCO")
    main(2023, 2024, "OPERACIONES", "ACAPULCO")
