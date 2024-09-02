from IPython.core.display import HTML
from neo4j import GraphDatabase
import pyvis

def visualize_result(query_graph, nodes_text_properties):
    visual_graph = pyvis.network.Network(
        notebook=True, 
        cdn_resources='in_line'
    )

    for node in query_graph.nodes:
        node_label = list(node.labels)[0]
        node_text = node[nodes_text_properties[node_label]]
        visual_graph.add_node(node.element_id, node_text, group=node_label)
        
    for relationship in query_graph.relationships:
        visual_graph.add_edge(
            relationship.start_node.element_id,
            relationship.end_node.element_id,
            title=relationship.type
        )
        
    return HTML(visual_graph.generate_html())


employee_threshold=10

def populate_graph(URI, AUTH, DATABASE):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session(database="neo4j") as session:
            records, summary, keys = driver.execute_query(
                "MATCH (n) DETACH DELETE n",
                database_="neo4j"
            )

            team_memmbers = [
                ('Data Science', 'Anthony', 'Lead Data Scientist'), 
                ('Data Science', 'Sophie', 'Data Scientist'), 
                ('Data Science', 'Olivia', 'Data Scientist'),

                ('Hermes', 'Victor', 'Principal Software Engineer'),
                ('Hermes', 'Nathan', 'Software Engineer'),
                ('Hermes', 'Tudor', 'Site Reliability Engineer'),

                ('Phoenix', 'Einari', 'Principal Software Engineer'),
                ('Phoenix', 'Ayesha', 'Software Engineer'),
                ('Phoenix', 'Vodek', 'Software Engineer'),
                ('Phoenix', 'Paul', 'Site Reliability Engineer'),   
            ]
            
            for m in team_memmbers:
                squad_id = session.execute_write(create_tx, m)
                print(f"User {m[1]} added to squad {squad_id}")


def create_tx(tx, data):
    # Create the person
    result = tx.run("""
        MERGE (p:Person {name: $name})
        RETURN p.name AS name
        """, name=data[1]
    )

    # Check if squad exists
    result = tx.run("""
        MATCH (s:Squad)
        WHERE s.id = $squad
        RETURN s.id AS id
        LIMIT 1
    """, squad=data[0])
    
    squad = result.single()
    
    if squad:
        # relate the person to the existing squad
        result = tx.run("""
            MATCH (s:Squad {id: $squad})
            MATCH (p:Person {name: $name})
            MERGE (p)-[r:IN_SQUAD]->(s)
            RETURN s.id AS id
            """, name=data[1], squad=data[0]
        )
    else:
        result = tx.run("""
            MATCH (p:Person {name: $name})
            CREATE (s:Squad {id: $squad, created_date: datetime()})
            MERGE (p)-[r:IN_SQUAD]->(s)
            RETURN s.id AS id
            """, name=data[1], squad=data[0]
        )
        
    return result.single()['id']
    