from neo4j import GraphDatabase

import os


neo4j_host = os.environ.get("NEO4J_HOST")
neo4j_port = os.environ.get("NEO4J_PORT")
neo4j_user = os.environ.get("NEO4J_USER")
neo4j_password = os.environ.get("NEO4J_PASSWORD")
 
  
# Configurar la conexión a Neo4j
driver = GraphDatabase.driver(f"bolt://my-neo4j-container:{neo4j_port}", auth=(neo4j_user, neo4j_password), database="data") 
     
            
  
# # Configurar la conexión a Neo4j
# driver = GraphDatabase.driver(f"bolt://localhost/7687", auth=('neo4j', "12345678"), database="data") 

     
def info_node(ruc_buscar):            
   with driver.session() as session: 
        result = session.run("""
            MATCH (a:Accionista {ruc: $ruc_buscar})
            WHERE a.type = 'PERSONAS NATURALES'
            RETURN a
            LIMIT 1
        """, ruc_buscar=ruc_buscar)
        
        node = result.single()["a"]
        node_dict = dict(node.items())
        return node_dict

