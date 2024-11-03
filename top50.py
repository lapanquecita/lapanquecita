import numpy as np
import pandas as pd
import plotly.graph_objects as go


# Este diccionario es usado para limpiar los nombres
# de algunos aeropuertos.
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
    df = pd.read_csv("./data.csv")

    # Filtramos por el Año que nos interesa.`
    df = df[df["AÑO / YEAR"] == año]

    # Seleccionamos los aeropuertos que tuvieron tráfico internacional.
    internacional = df[
        (df["TIPO/ TYPE"] == "INTERNACIONAL/ INTERNATIONAL")
        & (df["OPCIONES/ OPTIONS"] == "OPERACIONES/ FLIGHTS")
        & (df["TOTAL/TOTAL"] != 0)
    ]

    # Limpiamos los nombres de los aeropuertos con tráfico internacional.
    internacional = [
        NOMBRES.get(item.title(), item.title())
        for item in internacional["AEROPUERTO / AIRPORT"].unique()
    ]

    # Dependiendo de la opción creamos filtros y textos específicos.
    if opcion == "operaciones":
        df = df[df["OPCIONES/ OPTIONS"] == "OPERACIONES/ FLIGHTS"]
        titulo = f"Los 50 aeropuertos de México con mayor número de operaciones durante el {año}"
        nota = "<b>Notas:</b><br>El 🌎 indica que el aeropuerto recibió tráfico internacional.<br>Una operación puede ser un aterrizaje o un despegue.<br>Las cifras incluyen operaciones nacionales e internacionales."
    elif opcion == "pasajeros":
        df = df[df["OPCIONES/ OPTIONS"] == "PASAJEROS/PASSENGERS"]
        titulo = f"Los 50 aeropuertos de México con mayor número de pasajeros durante el {año}"
        nota = "<b>Notas:</b><br>El 🌎 indica que el aeropuerto recibió tráfico internacional.<br>Las cifras incluyen pasajeros nacionales y extranjeros."

    # Transformamos el DataFrame usando solo las columnas necesarias.
    df = df.pivot_table(
        index="AEROPUERTO / AIRPORT",
        columns="TIPO/ TYPE",
        values="TOTAL/TOTAL",
        aggfunc="sum",
    )

    # Limpiamos el nombre del aeropuerto.
    df.index = df.index.str.title().map(lambda x: NOMBRES.get(x, x))

    # Agregamos un emoji de 🌎 para los aeropuertos con tráfico internacional.
    df.index = df.index.map(lambda x: f"{x} 🌎" if x in internacional else x)

    # Sumamos ambos tipos de operaciones/pasajeros.
    df["total"] = df.sum(axis=1)

    # Calculamos la razón para determinar la posición del texto.
    df["ratio"] = np.log10(df["total"]) / np.log10(df["total"].max())

    df["text_pos"] = df["ratio"].apply(lambda x: "outside" if x <= 0.97 else "inside")

    # Ordenamos los totales de mayor a menor.
    df.sort_values("total", ascending=False, inplace=True)

    # Nos limitamos al top 50.
    df = df.head(50)

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
                text="Fuente: AFAC (2024)",
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
    main(2023, "operaciones", "#fc4103")
    main(2023, "pasajeros", "#fc036b")
