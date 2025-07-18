import pandas as pd

concept_map = {
    "Apoyo": {"ARS": "AAN", "USD": "AAI"},
    "Protección": {"ARS": "PVN", "USD": "PVI"},
    "Extensión": {"ARS": "EXT", "USD": "EXTI"},
}

def generate_page_summary(df_total):
    block = {
        "AG + COME": df_total,
        "COME": df_total[df_total["Tipo Cliente"] == "AEROLINEAS"],
        "AG": df_total[df_total["Tipo Cliente"] == "AVIACION GENERAL"]
    }

    rows = []

    for name_block, df in block.items():
        for metric in ["Importe", "Km", "Servicios"]:
            row = {"Bloque": name_block, "Métrica": metric}
            for concept, money_type in concept_map.items():
                for money_type, rate in money_type.items():
                    df_filtro = df[df["Tasa"] == rate]
                    if metric == "Importe":
                        value = df_filtro["Monto"].sum()
                    elif metric == "Km":
                        value = df_filtro["Km"].sum()
                    elif metric == "Servicios":
                        value = df_filtro["Servicios"].sum()
                    else:
                        value = 0
                    row[(concept, money_type)] = value

            # Total por metric
            row[("Total", "ARS")] = (
                row.get(("Apoyo", "ARS"), 0) +
                row.get(("Protección", "ARS"), 0) +
                row.get(("Extensión", "ARS"), 0)
            )
            row[("Total", "USD")] = (
                row.get(("Apoyo", "USD"), 0) +
                row.get(("Protección", "USD"), 0) +
                row.get(("Extensión", "USD"), 0)
            )
            rows.append(row)

    # Convertir a DataFrame
    df_summary = pd.DataFrame(rows)

    # Reordenar columnas
    metrics = df_summary.pop("Métrica")
    block = df_summary.pop("Bloque")
    df_summary.insert(0, "Métrica", metrics)
    df_summary.insert(1, "Bloque", block)

    # Asegurar columnas multinivel estén ordenadas
    columns = [
        ("Apoyo", "ARS"), ("Apoyo", "USD"),
        ("Protección", "ARS"), ("Protección", "USD"),
        ("Extensión", "ARS"), ("Extensión", "USD"),
        ("Total", "ARS"), ("Total", "USD"),
    ]
    df_summary = df_summary[["Métrica", "Bloque"] + columns]

    # Crear MultiIndex para columnas
    multi_columns = [("", "Métrica"), ("", "Bloque")] + columns
    df_summary.columns = pd.MultiIndex.from_tuples(multi_columns)

    return df_summary
