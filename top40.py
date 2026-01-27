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
    df = pd.read_csv("./data.csv", parse_dates=["PERIODO"])

    # Filtramos por el Año que nos interesa.`
    df = df[df["PERIODO"].dt.year == año]

    # Filtramos por el tipo de opci'on.
    df = df[df["OPCIONES"] == opcion]

    # Transformamos el DataFrame.
    df = df.pivot_table(
        index="AEROPUERTO", columns="TIPO", values="TOTAL", aggfunc="sum", fill_value=0
    )

    # Sumamos ambos tipos de operaciones/pasajeros.
    df["TOTAL"] = df.sum(axis=1)

    # Quitamos aeropuertos con 0 registros.
    df = df[df["TOTAL"] != 0]

    # Limpiamos el nombre del aeropuerto.
    df.index = df.index.str.title().map(lambda x: NOMBRES.get(x, x))

    # Agregamos un emoji de 🌎 para los aeropuertos con tráfico internacional.
    df.index = df.apply(
        lambda x: f"{x.name} 🌎" if x["INTERNACIONAL"] > 0 else x.name, axis=1
    )

    # Calculamos la razón para determinar la posición del texto.
    df["ratio"] = np.log10(df["TOTAL"]) / np.log10(df["TOTAL"].max())
    df["text_pos"] = df["ratio"].apply(lambda x: "outside" if x <= 0.95 else "inside")

    # Ordenamos los totales de mayor a menor.
    df.sort_values("TOTAL", ascending=False, inplace=True)

    # Nos limitamos al top 40.
    df = df.head(40)

    # Dependiendo de la opción creamos filtros y textos específicos.
    if opcion == "OPERACIONES":
        titulo = f"Los 40 aeropuertos de México con mayor número de operaciones durante {año}"
        nota = "<b>Notas:</b><br>El 🌎 indica que el aeropuerto recibió tráfico internacional.<br>Una operación puede ser un aterrizaje o un despegue.<br>Las cifras incluyen operaciones nacionales e internacionales."
    elif opcion == "PASAJEROS":
        titulo = (
            f"Los 40 aeropuertos de México con mayor número de pasajeros durante {año}"
        )
        nota = "<b>Notas:</b><br>El 🌎 indica que el aeropuerto recibió tráfico internacional.<br>Las cifras incluyen pasajeros nacionales y extranjeros."
    elif opcion == "CARGA":
        titulo = f"Los 40 aeropuertos de México con mayor número de operaciones de carga durante {año}"
        nota = "<b>Notas:</b><br>El 🌎 indica que el aeropuerto recibió tráfico internacional.<br>Una operación puede ser un aterrizaje o un despegue.<br>Las cifras incluyen operaciones nacionales e internacionales."

    fig = go.Figure()

    # Creamos una sencilla gráfica de barras horizontales
    # conlos valores antes calculados.
    fig.add_trace(
        go.Bar(
            y=df.index,
            x=df["TOTAL"],
            text=df["TOTAL"],
            texttemplate=" %{text:,.0f} ",
            textposition=df["text_pos"],
            orientation="h",
            marker_color=color,
            marker_line_width=0,
            textfont_family="Oswald",
            textfont_color="#FFFFFF",
            width=0.55,
            marker_cornerradius=50,
        )
    )

    fig.update_xaxes(
        type="log",
        range=[np.log10(df["TOTAL"].min()) // 1, np.log10(df["TOTAL"].max() * 1.02)],
        separatethousands=True,
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
        autorange="reversed",
        ticks="outside",
        ticklen=10,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showgrid=False,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        uniformtext_mode="show",
        uniformtext_minsize=22,
        showlegend=False,
        width=1920,
        height=2400,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=titulo,
        title_x=0.5,
        title_y=0.985,
        margin_t=90,
        margin_r=40,
        margin_b=160,
        margin_l=320,
        title_font_size=36,
        plot_bgcolor="#0F0F0F",
        paper_bgcolor="#232D3F",
        annotations=[
            dict(
                x=0.99,
                y=0,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="bottom",
                align="left",
                bgcolor="#0F0F0F",
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
                text="Fuente: AFAC (enero 2026)",
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
    main(2025, "OPERACIONES", "#ff6d00")
    main(2025, "PASAJEROS", "#00bfa5")
    main(2025, "CARGA", "#f06292")
