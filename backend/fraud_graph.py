import networkx as nx
from rapidfuzz import fuzz

def build_fraud_graph(documents):
    
    G = nx.Graph()
    for doc in documents:
        doc_id = doc["id"]
        G.add_node(doc_id, type="document", filename=doc["filename"], tamper_score=doc.get("tamper_score"))
       
        for other in documents:
            if doc != other:
                if doc.get("policy_no") == other.get("policy_no"):
                    G.add_edge(doc_id, other["id"], relation="policy_link")
                elif fuzz.ratio(str(doc.get("name", "")), str(other.get("name", ""))) > 90:
                    G.add_edge(doc_id, other["id"], relation="name_sim")
               
    return G


def graph_to_json(G):
    nodes = [{"id": n, **G.nodes[n]} for n in G.nodes]
    edges = [{"source": u, "target": v, "relation": G[u][v].get("relation")} for u,v in G.edges]
    return {"nodes": nodes, "edges": edges}


