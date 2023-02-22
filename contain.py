import networkx as nx
import networkx.algorithms.community as nx_comm
import matplotlib.pyplot as plt
from networkx.generators.random_graphs import gnm_random_graph
import random as rnd
import time
from SparseShield_NIvsHS.Scripts.SparseShieldSolver import SparseShieldSolver
from SparseShield_NIvsHS.Scripts.NetShieldSolver import NetShieldSolver
import os

def Contain(G,seeds, budget, r, dr):
    nbs=[set(G.neighbors(s))|{s} for s in seeds]
    subs=[G.subgraph(n) for n in nbs]
    agg=nx.compose_all(subs)
    seed_group=next(nx.connected_components(agg))
    while True:
        comms = nx_comm.louvain_communities(G, resolution=r, seed=42)
        intersects = [x for c in comms if (x := (seed_group & c))]
        ratios = [(x, len(x)/len(seed_group)) for x in intersects]
        if len(ratios) >= budget:
            sorted_ratios = sorted(ratios, key=lambda item:item[1], reverse=True)[0:budget]
            return sorted_ratios, r
        else:
            return [], -1
        r += dr

# CONTAIN, NetShield, and SparseShield usage
if __name__ == "__main__":
    for f in  ['tvshow_edges.csv', 'politician_edges.csv', 'government_edges.csv', 'public_figure_edges.csv', 'athletes_edges.csv', 'company_edges.csv', 'new_sites_edges.csv', 'artist_edges.csv', 'artist_edges.csv',]:
        G = nx.read_edgelist(os.path.join("data", f), delimiter=',', create_using=nx.Graph(), nodetype=int)

        deg_sort = sorted([(n, len(list(G.neighbors(n)))) for n in G.nodes()], key=lambda item:item[1], reverse=True)
        seeds = deg_sort[0:int(len(deg_sort)*0.1)]
        seeds = sorted([x[0] for x in seeds])

        s=set(seeds)
        k=len(seeds)
        print(len(G.nodes), len(G.edges))
        
        # How to use CONTAIN
        start_time = time.time()
        ranks, r = Contain(G, seeds=seeds, budget=10, r=1, dr=0.25)
        immunised_nodes = sum([len(x[0]) for x in ranks])
        end_time = time.time()
        print("Contain: budget", k, "time", end_time-start_time, "No. immunised nodes", immunised_nodes)
        print('====================================')

        # Test SparseShield
        start_time = time.time()
        solver = SparseShieldSolver(G, seeds=seeds, k=k)
        nodes = solver.sparse_shield()
        end_time = time.time()
            

        print("SparseShield: budget", k, "time", end_time-start_time, "No. immunised nodes", len(nodes))
        print('====================================')

        # Test SparseShield
        start_time = time.time()
        solver = NetShieldSolver(G, seeds=seeds, k=k)
        nodes = solver.net_shield()
        end_time = time.time()    

        print("NetShield: budget", k, "time", end_time-start_time, "No. immunised nodes", len(nodes))
        print('====================================')
