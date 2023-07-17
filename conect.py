from neo4j import GraphDatabase

import os


neo4j_host = os.environ.get("NEO4J_HOST")
neo4j_port = os.environ.get("NEO4J_PORT")
neo4j_user = os.environ.get("NEO4J_USER")
neo4j_password = os.environ.get("NEO4J_PASSWORD")
 
  
# Configurar la conexión a Neo4j
driver = GraphDatabase.driver(f"bolt://my-neo4j-container:{neo4j_port}", auth=(neo4j_user, neo4j_password), database="data") 
     
            
  
try:
    with driver.session() as session:
        session.run("CREATE INDEX FOR (a:Accionista) ON (a.ruc)")
except:
    pass
 
try:
    with driver.session() as session:
        session.run("CREATE INDEX FOR (e:Empresa_Publica) ON (e.ruc)")
except:
    pass

def nodes_relations_accion(ruc_buscar): 
    nodes = set()
    edges = set()
    color_node_accionista="red"
    color_node_accionista_proveedor="green"
    def card(valor):
        html=f"""
        
                    <div class="box">
                    
                    <div class="cabecera">
                {valor}
            </div>
            </div>
            """
   
        return html
    mass=5
    with driver.session() as session: 
        result = session.run("""
            MATCH p = (a:Accionista {ruc: $ruc_buscar})-[:INVERSION*]->(a1:Accionista)-[:PROVEEDOR*]->(e:Empresa_Publica)
            RETURN p
        """, ruc_buscar=ruc_buscar)
        
        result_2 = session.run("""
            MATCH p = (a:Accionista {ruc: $ruc_buscar})-[:PROVEEDOR*]->(e:Empresa_Publica)
            RETURN p
        """, ruc_buscar=ruc_buscar)


        if result.peek():
            result=result
            print("Si se encnontraron Datos")
        else:
            result=result_2
            print("Resultados diretos")


        

        for record in result:
            path = record["p"]
            nodes_in_path = [node for node in path.nodes]
            edges_in_path = [rel for rel in path.relationships] 


            for node in nodes_in_path:
                node_id = node.get("ruc", None)
                node_nombre = node.get("nombre", None)
                node_tipo= node.get("tipo", None)
                title=card(node_nombre)
                if node_tipo=='accionistas' and node_id !=ruc_buscar:
                    color=color_node_accionista
                    image='https://cdn-icons-png.flaticon.com/512/6788/6788139.png'
                    size=20
                    node=(node_id,node_nombre,node_tipo,color,title,image,size,mass)
                    nodes.add(node)   
                elif node_id==ruc_buscar:
                    color="orange"
                    image ="https://cdn-icons-png.flaticon.com/512/2113/2113200.png"
                    size=90
                    mass=20
                    node=(node_id,node_nombre,node_tipo,color,title,image,size,mass)
                    nodes.add(node)
                elif node_tipo=='Accionista-Proveedor':
                    color=color_node_accionista_proveedor
                    image='https://cdn-icons-png.flaticon.com/512/6788/6788139.png'
                    size=20
                    node=(node_id,node_nombre,node_tipo,color,title,image,size,mass)
                    nodes.add(node)  
                elif node_tipo=='Proveedor': 
                    color='blue'
                    image='https://cdn-icons-png.flaticon.com/512/7187/7187944.png'
                    size=40
                    node=(node_id,node_nombre,node_tipo,color,title,image,size,mass)
                    nodes.add(node)
                elif node_tipo=='Empresa Pública':
                    color='purple'
                    image='https://cdn-icons-png.flaticon.com/512/7242/7242885.png'
                    size=1
                    node=(node_id,node_nombre,node_tipo,color,title,image,size,mass)
                    nodes.add(node) 
                         
            for rel in edges_in_path:
                edge_id = rel.get("OCID", None)
                ocid = rel.get("OCID", None)
                start_node_id = str(rel.start_node["ruc"])
                end_node_id = str(rel.end_node["ruc"])
                edge_label = rel.type
                Capital = rel.get("Capital", None)
                # Porcentaje = rel.get("Porcentaje", '')
                try:
                    Porcentaje=rel.get(round(rel["Porcentaje"],2),0)
                except:
                    Porcentaje=''
                fecha=rel.get("Fecha", '2015-10-19T00:00:00-05:00')

                edge = (edge_id, start_node_id, end_node_id, edge_label, ocid, fecha,Capital,Porcentaje)
                edges.add(edge)
    
    
    nodes = [{'id': node_id, 'nombre': node_nombre,'tipo':node_tipo,'color':color,'title':title,'shape':'image','image':image,'size':size,'mass': mass} for node_id,node_nombre,node_tipo,color,title,image,size, mass in nodes]
    edges = [{'id': edge_id, 'from': start_node_id, 'to': end_node_id, 'label': edge_label, 'ocid': ocid, 'Fecha': fecha,'Capital':Capital,'Porcentaje':Porcentaje} for edge_id, start_node_id, end_node_id, edge_label, ocid, fecha, Capital, Porcentaje in edges]
   


    return nodes,edges
   
       

def consulta():
    nodes = set()
    edges = set()

    with driver.session() as session:
        result = session.run("""
            MATCH p = (a:Accionista {nombre: "1716211758"})-[:CONTRATA*]->(:Empresa_Publica)
            RETURN p
        """)

        for record in result:
            path = record["p"]
            nodes_in_path = [node for node in path.nodes]
            edges_in_path = [rel for rel in path.relationships] 

            for node in nodes_in_path:
                node_id = node.get("nombre", None)
                color1="red"
                color2="green"
                color3="orange"
                if node["tipo"] is None and node["nombre"]!='1716211758':
                    nod=(node_id,color1)
                    nodes.add(nod)
                elif node["tipo"] is None and  node["nombre"]=='1716211758':
                    nod=(node_id,color3)
                    nodes.add(nod)   
                else:
                    nod=(node_id,color2)
                    nodes.add(nod)     

            for rel in edges_in_path:
                edge_id = rel.get("ocid", None)
                start_node_id = str(rel.start_node["nombre"])
                end_node_id = str(rel.end_node["nombre"])
                edge_label = rel.type
                ocid = rel.get("ocid", None)
                fecha = rel.get("fecha", "2015")

                edge = (edge_id, start_node_id, end_node_id, edge_label, ocid, fecha)
                edges.add(edge)

    # Convertir los conjuntos en listas
    nodes = [{'id': node_id, 'label': None,'color':color} for node_id,color in nodes]
    edges = [{'id': edge_id, 'from': start_node_id, 'to': end_node_id, 'label': edge_label, 'ocid': ocid, 'Fecha': fecha} for edge_id, start_node_id, end_node_id, edge_label, ocid, fecha in edges]

   

    return nodes, edges
def all_accion():
    nodes = set()
    color_node_accionista="red"
    color_node_accionista_proveedor="green"
    with driver.session() as session:
        result = session.run("""
            MATCH p = (:Accionista)
            RETURN p
        """)

        for record in result:
            path = record["p"]
            nodes_in_path = [node for node in path.nodes]
            edges_in_path = [rel for rel in path.relationships] 

            for node in nodes_in_path:
                node_id = node.get("ruc", None)
                node_nombre = node.get("nombre", None)
                node_tipo= node.get("tipo", None)
                if node_tipo=='accionistas':
                    color=color_node_accionista
                    node=(node_id,node_nombre,node_tipo,color)
                    nodes.add(node)   
                elif node_tipo=='Accionista-Proveedor':
                    color=color_node_accionista_proveedor
                    node=(node_id,node_nombre,node_tipo,color)
                    nodes.add(node)  
                elif node_tipo=='Proveedor': 
                    color='yellow'
                    node=(node_id,node_nombre,node_tipo,color)
                    nodes.add(node)          
                         
    nodes = [{'id': node_id, 'nombre': node_nombre,'tipo':node_tipo,'color':color} for node_id,node_nombre,node_tipo,color in nodes]
    return nodes
  
    