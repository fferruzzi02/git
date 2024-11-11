import streamlit as st
import polars as pl

#todo: parte 2
#scrivi titolo e inserisci dati 
st.title("Emissioni paesi membri dell'unione europea") #titolo 
st.write("Dal 1990 al 2022") 

url = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/sdg_13_10?format=TSV&compressed=true"

#prendo subito tutti i dati e me li salvo, così filtro dopo su una tabella che già ho

#la chiocciola serve per annotare una funzione
@st.cache_data #©osì il risultato della funzione viene salvato nella cache 
def get_data():
    return (pl.read_csv(url, separator="\t")
    .select(
    pl.col("freq,airpol,src_crf,unit,geo\\TIME_PERIOD")
    .str.split(",")
    .list.to_struct(fields=["freq", "airpol",
    "src_crf", "unit", "geo"])
    .alias("combined_info"),
    pl.col("*").exclude("freq,airpol,src_crf,unit,geo\\TIME_PERIOD")
    ).unnest("combined_info")
    .unpivot(index=["freq", "airpol", "src_crf", "unit", "geo"],
    value_name="emissions",
    variable_name="year")
    .with_columns(
    year = pl.col("year").str.replace(" ", "").cast(pl.Int64),
    emissions = pl.col("emissions")
    .str.strip_chars_end(" bep")
    .cast(pl.Float64, strict=True)
    )
    .pivot(on="unit", values="emissions")
    .filter(pl.col("src_crf") == "TOTXMEMONIA"))

data = get_data()

st.write(data) #tabella con tutti i dati 

#todo:parte 3


#grafici filtrati 
"""
st.line_chart(data, x="year", y="T_HAB", color="geo")  #grafico generale

data2022 = data.filter(pl.col("year") == 2022) #dati filtrati per anno

st.bar_chart(data2022, x="geo", y="T_HAB") #istogramma dati filtrati (senza colore)


datait = data.filter(pl.col("geo") == "IT") #dati filtrati per stato 
st.line_chart(datait,x = "year", y ="T_HAB")#grafico dati filtrati

"""

#todo: parte 4
#selezionare con uno slider l’anno su cui si basa il grafico a barre.
#selezionare con un selectbox lo stato da mostrare nel grafico a linee

col1, col2 = st.columns(2)
states = data["geo"].to_list()

year = col1.slider("seleziona anno da 1990 a 2022", 1990, 2022)
st.caption(f"hai selezionato il grafico dell'anno {year}")
st.bar_chart(data.filter(pl.col("year") == year), x = "geo", y="T_HAB")

state = col2.multiselect("seleziona stato", states, default = "IT")
st.caption(f"hai selezionato il grafico dello stato {state}")
st.line_chart(data.filter(pl.col("geo").is_in(state)), x = "year", y = "T_HAB", color="geo")



