import numpy as np
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


def main(año, opcion, color):
    """
    Genera una gráfica de barras con el top 50
    de registros.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    opcion : str
        El tipo de opción, puede ser: operaciones | pasajeros

    color : str
        El color de las barras en formato hexadecimal.

    """

    # Cargamos el dataset de estadísticas operativas.
    df = pd.read_csv("./data.csv", parse_dates=["FECHA"])

    # Filtramos por el Año que nos interesa.`
    df = df[df["FECHA"].dt.year == año]

    # Obtenemos aeropuertos con tráfico internacional.
    internacional = (
        df[(df["OPCIONES"] == "OPERACIONES") & (df["TIPO"] == "INTERNACIONAL")]
        .groupby("AEROPUERTO")
        .sum(numeric_only=True)
    )
    internacional = internacional[internacional["TOTAL"] != 0].index.tolist()

    # Transformamos el DataFrame.
    df = df.pivot_table(
        index="AEROPUERTO", columns="TIPO", values="TOTAL", aggfunc="sum", fill_value=0
    )

    # Agregamos un emoji de 🌎 para los aeropuertos con tráfico internacional.
    # Aprovechamos para limpiar el nombre del aeropuerto.
    df.index = df.index.map(
        lambda x: f"{NOMBRES.get(x.title(), x.title())} 🌎"
        if x in internacional
        else NOMBRES.get(x.title(), x.title())
    )

    # Sumamos ambos tipos de operaciones/pasajeros.
    df["total"] = df.sum(axis=1)

    # Calculamos la razón para determinar la posición del texto.
    df["ratio"] = np.log10(df["total"]) / np.log10(df["total"].max())
    df["text_pos"] = df["ratio"].apply(lambda x: "outside" if x <= 0.97 else "inside")

    # Ordenamos los totales de mayor a menor.
    df.sort_values("total", ascending=False, inplace=True)

    # Nos limitamos al top 50.
    df = df.head(50)

    # Dependiendo de la opción creamos filtros y textos específicos.
    if opcion == "OPERACIONES":
        titulo = f"Los 50 aeropuertos de México con mayor número de operaciones durante el {año}"
        nota = "<b>Notas:</b><br>El 🌎 indica que el aeropuerto recibió tráfico internacional.<br>Una operación puede ser un aterrizaje o un despegue.<br>Las cifras incluyen operaciones nacionales e internacionales."
    elif opcion == "PASAJEROS":
        titulo = f"Los 50 aeropuertos de México con mayor número de pasajeros durante el {año}"
        nota = "<b>Notas:</b><br>El 🌎 indica que el aeropuerto recibió tráfico internacional.<br>Las cifras incluyen pasajeros nacionales y extranjeros."

    fig = go.Figure()

    # Creamos una sencilla gráfica de barras horizontales
    # conlos valores antes calculados.
    fig.add_trace(
        go.Bar(
            y=df.index,
            x=df["total"],
            text=df["total"],
            texttemplate=" %{text:,.0f} ",
            textposition=df["text_pos"],
            orientation="h",
            marker_color=color,
            marker_line_width=0,
            textfont_size=18,
            textfont_family="Oswald",
            textfont_color="#FFFFFF",
        )
    )

    fig.update_xaxes(
        type="log",
        range=[np.log10(df["total"].min()) // 1, np.log10(df["total"].max() * 1.02)],
        separatethousands=True,
        tickfont_size=14,
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        gridwidth=0.35,
        mirror=True,
        nticks=20,
    )

    # Para hacer la letra más grande utilizamos
    # las propiedades de uniformtext.
    fig.update_yaxes(
        autorange="reversed",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.35,
        showgrid=False,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        uniformtext_mode="show",
        uniformtext_minsize=18,
        showlegend=False,
        width=1280,
        height=1600,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=18,
        title_text=titulo,
        title_x=0.5,
        title_y=0.985,
        margin_t=60,
        margin_r=40,
        margin_b=80,
        margin_l=220,
        title_font_size=26,
        plot_bgcolor="#18122B",
        paper_bgcolor="#393053",
        annotations=[
            dict(
                x=0.99,
                y=-0.01,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="bottom",
                align="left",
                bgcolor="#18122B",
                bordercolor="#FFFFFF",
                borderwidth=1.5,
                borderpad=7,
                font_size=16,
                text=nota,
            ),
            dict(
                x=0.01,
                y=-0.05,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: AFAC (2025)",
            ),
            dict(
                x=0.53,
                y=-0.05,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Total de registros anuales (escala logarítmica)",
            ),
            dict(
                x=1.01,
                y=-0.05,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./{opcion}_{año}.png")


if __name__ == "__main__":
    main(2024, "OPERACIONES", "#fc4103")
    main(2024, "PASAJEROS", "#fc036b")
