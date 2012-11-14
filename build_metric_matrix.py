"""
assume file structure
randomwalk
 / 30 (sampling percentage)
   / 1 (iteration of random walk)
   / 2
 / 40
 / 50
 ...
 / 90
 
"""

import os, sys
import networkx as nx
import numpy

def build_metric_matrix(sampling_path):
    sampling_sizes = os.listdir(sampling_path)
    num_iterations = len(os.listdir(sampling_path + os.sep + sampling_sizes[0]))
    
    """
    metric matrix
                    
    sampling size x iterations -> metric value
    """
    mx = numpy.zeros(shape=(len(sampling_sizes), num_iterations))
    sample_sizes = numpy.zeros(shape=(len(sampling_sizes), 1))
    for index, sampling_size in enumerate(sampling_sizes):
        path = sampling_path + os.sep + sampling_size
        iterations = os.listdir(sampling_path + os.sep + sampling_size)
        for iteration in iterations:
            graph_fd = open(path + os.sep + iteration)
            g = nx.Graph()
            
            #read graph
            inline = graph_fd.readline()
            while (inline != ''):
                if (not inline.startswith("#")):
                    nodes = inline.strip().split()
                    g.add_edge(int(nodes[0]), int(nodes[1]))
                    inline = graph_fd.readline()
                    
            #calculate metric
            metric = nx.average_clustering(g)
            sample_sizes[index] = int(sampling_size)
            mx[index, int(iteration)] = metric
            
    print mx
    return mx

if __name__ == "__main__":
    build_metric_matrix(sys.argv[1])
            
            
                   
                   
        
