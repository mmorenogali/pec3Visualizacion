# Importamos las librerías:
import pandas as pd
import os
import numpy as np
import datetime

# Carga de Dades diàries per comarca:
ddComarca = pd.read_csv(os.path.join(
    "Data", "Raw", "Dades_di_ries_de_COVID-19_per_comarca.csv"))


# Carga de Dosis administrades per comarca:
daComarca = pd.read_csv(os.path.join(
    "Data", "Raw", "Vacunaci__per_al_COVID-19__dosis_administrades_per_comarca.csv"))


# Carga de registros de casos por municipio y sexo:
rcMunicipio = pd.read_csv(os.path.join(
    "Data", "Raw", "Registre_de_casos_de_COVID-19_a_Catalunya_per_municipi_i_sexe.csv"))


# En primer lugar deberemos agrupar los datos de municipio en comarcas,
# para poder unir las demás tablas. De este modo, tendremos la misma
# granularidad geográfica en los datos.
rcMunicipio = rcMunicipio[["TipusCasData","ComarcaCodi","ComarcaDescripcio",
                           "SexeCodi","SexeDescripcio","TipusCasDescripcio",
                           "NumCasos"]]
rcComarca = rcMunicipio.groupby(["TipusCasData","ComarcaCodi","ComarcaDescripcio",
                           "SexeCodi","SexeDescripcio","TipusCasDescripcio"])["NumCasos"].sum()

# Pasamos el groupby a un dataframe de nuevo
rcComarca = rcComarca.reset_index()

# Y ahora renombramos las columnas de los distintos datasets para que sean
# coherentes entre ellos. No cambiaremos los nombres que ya se comparten entre
# datasets y son coherentes.
ddComarca = ddComarca.rename(columns = {
    "NOM":"Comarca",
    "CODI":"Comarca_Codi",
    "GRUP_EDAT":"Edat",
    "EXITUS":"Defuncions"})

# Y pasamos los nombres a CamelCase:
ddComarca.columns = ["".join(i.capitalize() for i in c.split("_")) for c in ddComarca.columns]



# El dataset de Dosis administradas:
daComarca = daComarca.rename(columns = {"RECOMPTE":"Dosis_Administrades",
                                        "CASOS_CONFIRMAT":"Positius"})

# Y pasamos los nombres a CamelCase:
daComarca.columns = ["".join(i.capitalize() for i in c.split("_")) for c in daComarca.columns]

# Por último, el dataset de registro de casos por Comarca:
rcComarca = rcComarca.rename(columns = {"TipusCasDescripcio":"Test",
                                        "RECOMPTE":"Positius",
                                        "TipusCasData":"Data",
                                        "ComarcaDescripcio":"Comarca"})
rcComarca.columns = ["".join(i.capitalize() for i in c.split("_")) for c in rcComarca.columns]

# En el dataset de dades diàries de Covid-19 per comarca, la variable
# Sexo y Grup_Edat tiene el valor "Tots" cuando se trata de una persona
# en una residencia. Es decir, en realidad no se tienen datos en estos
# casos. Por este motivo, definiremos como nulos estos registros:
ddComarca["Sexe"] = np.where(ddComarca["Residencia"] == "Si",
                                      "",
                                      ddComarca["Sexe"])

ddComarca["Edat"] = np.where(ddComarca["Residencia"] == "Si",
                                      "",
                                      ddComarca["Edat"])

# Agrupamos por edad:
conditions = [
    daComarca["Edat"] == "0 a 14",
    daComarca["Edat"] == "15 a 19",
    daComarca["Edat"] == "20 a 24",
    daComarca["Edat"] == "25 a 29",
    daComarca["Edat"] == "30 a 34",
    daComarca["Edat"] == "35 a 39",
    daComarca["Edat"] == "40 a 44",
    daComarca["Edat"] == "45 a 49",
    daComarca["Edat"] == "50 a 54",
    daComarca["Edat"] == "55 a 59",
    daComarca["Edat"] == "60 a 64",
    daComarca["Edat"] == "65 a 69",
    daComarca["Edat"] == "70 a 74",
    daComarca["Edat"] == "75 a 79",
    daComarca["Edat"] == "80 o més"]

choices = ["Menors de 15",
           "Entre 15 i 64",
           "Entre 15 i 64",
           "Entre 15 i 64",
           "Entre 15 i 64",
           "Entre 15 i 64",
           "Entre 15 i 64",
           "Entre 15 i 64",
           "Entre 15 i 64",
           "Entre 15 i 64",
           "Entre 15 i 64",
           "Entre 65 i 74",
           "Entre 65 i 74",
           "Majors de 74",
           "Majors de 74"
           ]

# Aplicamos las condiciones:
daComarca["Edat"] = np.select(conditions,choices)


# Volvemos a realizar un groupby para poder comparar:
ddComarca = ddComarca.groupby(["Comarca","ComarcaCodi","Data",
                               "Sexe","Edat","Residencia"])[
                                   ["Pcr","IngressosTotal","IngressosCritic",
                                    "IngressatsTotal","IngressatsCritic",
                                    "Defuncions"]].sum()
                               
ddComarca = ddComarca.reset_index()



# Redefinimos las fechas de todas las tablas para hacer coincidir con el formato
# YYYY-MM-DD
ddComarca["Data"] = pd.to_datetime(ddComarca["Data"], format =  "%d/%m/%Y").dt.strftime("%Y-%m-%d")
daComarca["Data"] = pd.to_datetime(daComarca["Data"], format =  "%d/%m/%Y").dt.strftime("%Y-%m-%d")
rcComarca["Data"] = pd.to_datetime(rcComarca["Data"], format =  "%d/%m/%Y").dt.strftime("%Y-%m-%d")

# Creamos un diccionario de la forma comarca:provincia
diccionario = daComarca[["Comarca","Provincia"]]
diccionario = diccionario.drop_duplicates()
dictComarcaProvincia = diccionario.set_index("Comarca")["Provincia"].to_dict()



# Añadimos la provincia a los datasets que no la tienen:
ddComarca["Provincia"] = ddComarca["Comarca"]

ddComarca = ddComarca.replace({"Provincia":dictComarcaProvincia})

rcComarca["Provincia"] = rcComarca["Comarca"]

rcComarca = rcComarca.replace({"Provincia":dictComarcaProvincia})


# En este punto tenemos los datos preparados para realizar la visualización
# Los guardamos en un csv:

# Datos diarios por comarca
ddComarca.to_csv(os.path.join("Data","ddComarca.csv"), sep = ",", index = False)

# Dosis administradas por comarca
daComarca.to_csv(os.path.join("Data","daComarca.csv"), sep = ",", index = False)

# Registro casos por comarca
rcComarca.to_csv(os.path.join("Data","rcComarca.csv"), sep = ",", index = False)

# Y los unimos en una misma hoja para trabajar con el dashboard de excel:
dashboardExcel = ddComarca.append([daComarca, rcComarca], sort = False)

dashboardExcel.to_excel(os.path.join("Data","dashboardExcel.xlsx"),
                        sheet_name = "dashboardData", encoding = "utf8",
                        )


