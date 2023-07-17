from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from neo4j import GraphDatabase
import conect
import info

from neo4j import GraphDatabase

import os


from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# # Configurar CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Permitir cualquier origen. Puedes ajustarlo a tu necesidad específica.
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


neo4j_host = os.environ.get("NEO4J_HOST")
neo4j_port = os.environ.get("NEO4J_PORT")
neo4j_user = os.environ.get("NEO4J_USER")
neo4j_password = os.environ.get("NEO4J_PASSWORD")


# Configurar la conexión a Neo4j
driver = GraphDatabase.driver(f"bolt://my-neo4j-container:{neo4j_port}", auth=(neo4j_user, neo4j_password), database="data") 
  

# driver = GraphDatabase.driver(f"bolt://my-neo4j-container:7687", auth=('neo4j', '12345678'), database="data") 
  

nodes_accion=conect.all_accion()
nodes, edges = conect.consulta()

# Ruta para servir los archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")



@app.get("/")
def read_root():
    try:
        # Leer el contenido del archivo HTML
        with open("static/index.html") as f:
            html_content = f.read()

        # Retornar el contenido del archivo como respuesta HTML
        return HTMLResponse(content=html_content, status_code=200)
    except:
        return HTMLResponse(content="No conect", status_code=500)
      
@app.get("/ac")
def read_root():
    try:
        # Leer el contenido del archivo HTML
        with open("static/grafo_ac.html") as f:
            html_content = f.read()

        # Retornar el contenido del archivo como respuesta HTML
        return HTMLResponse(content=html_content, status_code=200)
    except:
        return HTMLResponse(content="No conect", status_code=500)
    
    
@app.get("/sugerencias")
def obtener_sugerencias(valor: str):
    with driver.session() as session:
        result = session.run("""
            MATCH (n)
            WHERE toLower(n.nombre) CONTAINS toLower($valor) AND n.type = 'PERSONAS NATURALES'
            RETURN n.ruc AS ruc, n.nombre AS sugerencia
            LIMIT 5
        """, valor=valor)
        
        registros = list(result)  # Almacenar los resultados en una lista
        
        sugerencias = [record["sugerencia"] for record in registros]
        ruc = [record["ruc"] for record in registros]
        
        # print(sugerencias)
        # print(ruc)
        print( {"sugerencias": sugerencias, "ruc": ruc})
        
        return {"sugerencias": sugerencias, "ruc": ruc}




@app.get("/ct")
def read_root():
    try:
        # Leer el contenido del archivo HTML
        with open("static/cty.html") as f:
            html_content = f.read()

        # Retornar el contenido del archivo como respuesta HTML
        return HTMLResponse(content=html_content, status_code=200)
    except:
        return HTMLResponse(content="No conect", status_code=500)

@app.get("/d3")
def read_root():
    try:
        # Leer el contenido del archivo HTML
        with open("static/d3.html") as f:
            html_content = f.read()

        # Retornar el contenido del archivo como respuesta HTML
        return HTMLResponse(content=html_content, status_code=200)
    except:
        return HTMLResponse(content="No conect", status_code=500)




@app.get("/data")
def get_data():
    try:
        return {"nodes": nodes, "edges": edges}
    except:
        return {"error": "No conect"}


@app.get("/accion")
def get_data():
    try:
        return {"nodes": nodes_accion}
    except:
        return {"error": "No conect"}



@app.get("/data_accion")
def get_data(valor):
    nodes_accion, edges_accion = conect.nodes_relations_accion(valor)
    data_nodo = info.info_node(valor)
    print(data_nodo)
    try:
        return {"nodes": nodes_accion, "edges": edges_accion , "data_node": data_nodo}
    except:
        return {"error": "No conect"}
    
import json

@app.get("/tablas")
def obtener_sugerencias(valor: str):
    with driver.session() as session:
        result = session.run(
            """
            MATCH p = (a:Accionista {ruc: $valor})-[r:PROVEEDOR]->(e:Empresa_Publica)
            RETURN a.ruc AS Accionista_ruc, a.nombre AS Accionista_nombre, e.ruc AS Empresa_ruc, e.nombre AS Empresa_nombre, r.Monto AS Monto, r.OCID AS OCID

            UNION

            OPTIONAL MATCH (a:Accionista {ruc: $valor})-[:INVERSION*]->(a1:Accionista)-[r:PROVEEDOR]->(e:Empresa_Publica)
            RETURN a1.ruc AS Accionista_ruc, a1.nombre AS Accionista_nombre, e.ruc AS Empresa_ruc, e.nombre AS Empresa_nombre, r.Monto AS Monto, r.OCID AS OCID
            """, valor=valor
        )

        # Procesa el resultado de la consulta
        rows = []
        for record in result:
            row = {
                "RUC Accionista": record["Accionista_ruc"],
                "Nombre": record["Accionista_nombre"],
                "RUC Empresa Pública": record["Empresa_ruc"],
                "Nombre Empresa Pública": record["Empresa_nombre"],
                "Monto": str(record["Monto"]),  # Convertir a string
                "OCID": record["OCID"],
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        df=df.drop_duplicates("OCID").dropna()

        data_grouped = df.drop_duplicates().groupby(['Nombre', 'RUC Accionista', 'Nombre Empresa Pública', 'RUC Empresa Pública']).agg({'Monto': 'sum', 'OCID': 'count'}).reset_index()

        return {"rows": df.to_dict(orient='records'), "data_grouped": data_grouped.to_dict(orient='records')}
