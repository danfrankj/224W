

import os, sys
import networkx as nx
import numpy

array_dim = 0
#def get_kl_divergence(d1, d2):
#    """
#    Given 2 distributions d1 and d2, get the KL-divergence between the two
#    The index is the discrete x-value, and the value is the y-value
#    """
#    max_divergence = 0
#    for i in range(min(len(d1), len(d2))):
#        if abs(d1[i] - d2[i]) > max_divergence:
#            max_divergence = abs(d1[i] - d2[i])
#    
#    if len(d1) < len(d2):
#        for i in range(len(d1), len(d1)):
#            if abs(d2[i]) > max_divergence:
#                max_divergence = abs(d2[i])
#    else:
#        for i in range(len(d2), len(d1)):
#            if abs(d1[i]) > max_divergence:
#                max_divergence = abs(d1[i])
#    return max_divergence

def get_kl_divergence(d1, d2):
    """
    Given 2 distributions (dicts) d1 and d2, get the KL-divergence between the two
    The key is the discrete x-value, and the value is the y-value
    """
    max_divergence = 0
    for i in range(max(max(d1), max(d2))):
        v1 = d1.get(i) or 0
        v2 = d2.get(i) or 0
        if abs(v1 - v2) > max_divergence:
            max_divergence = abs(v1-v2)
    return max_divergence

def get_degree_distribution(g) :
    degs = {}
    for n in g.nodes() :
        deg = g.degree(n)
        if deg not in degs :
            degs[ deg ] = 0
        degs[ deg ] += 1
    for key in degs.keys():
        degs[key] /= float(len(g.nodes()))
    return degs

def get_scc_size_distribution(g):
    scc_list = nx.strongly_connected_components(g)
    max_scc_size = len(scc_list[0])
    scc_size_dist = numpy.zeros(shape=(max_scc_size+1))
    for scc in scc_list:
        scc_size_dist[len(scc)] += 1
    return scc_size_dist
    
def build_metric_matrix(sampling_path, orig_graph_path, metric_type):
    """
    Example usage:
    python build_metric_matrix.py ./randomwalk cc
    
    assuming directory structure
    randomwalk (sampling procedure)
     / 30 (sampling percentage)
       / 1 (iteration of random walk)
       / 2
     / 40
     / 50
     ...
     / 90
     
     Parameters:
     -----------
     sampling_path: path to the top level sampling procedure folder, which would be
     "randomwalk" in the example directory structure above
     
     metric_type: string corresponding to the graph property we're considering. Ex. "cc" for
     clustering coefficient
     
     Returns:
     --------
     numpy 2-d array : sampling size x iterations -> metric value
     
     numpy 1-d array : array of the sample sizes used for the corresponding index for the rows
     of the 2-d array
     
    """
    str_sample_size_list = os.listdir(sampling_path)
    num_iterations = len(os.listdir(sampling_path + os.sep + str_sample_size_list[0]))
    
    sorted_sample_size_list = sorted(str_sample_size_list, key=lambda x: int(x))
    subsampled_list = [sorted_sample_size_list[i] for i in range(len(sorted_sample_size_list)) if i in [1] ]
    
    sample_sizes = numpy.zeros(shape=(len(subsampled_list), 1))
    
    
    #calculate metric on original graph 
    #use len(subsampled_list)+1 to leave space for 100% case
    if metric_type == 'cc':
        baseline_metric = nx.average_clustering(nx.read_edgelist(orig_graph_path))
        mx = numpy.zeros(shape=(num_iterations, len(subsampled_list)+1))
    elif metric_type == 'dd':
        orig_dd = get_degree_distribution(nx.read_edgelist(orig_graph_path))
        max_degree = max(orig_dd)
        array_dim = max_degree+1
        baseline_metric = [orig_dd.get(i) or 0 for i in range(array_dim)]
        mx = numpy.zeros(shape=(num_iterations, len(subsampled_list)+1, array_dim)) 
    elif metric_type == 'scc':
        scc_list = nx.strongly_connected_components(nx.read_edgelist(orig_graph_path))
        max_scc_size = len(scc_list[0])
        array_dim = max_scc_size+1
        baseline_metric = numpy.zeros(shape=(array_dim))
        for scc in scc_list:
            baseline_metric[len(scc)] += 1
        mx = numpy.zeros(shape=(num_iterations, len(subsampled_list)+1, array_dim))
    
    for index, sampling_size in enumerate(subsampled_list):
        print "Sampling percentage " + str(sampling_size)
        path = sampling_path + os.sep + sampling_size
        iterations = os.listdir(sampling_path + os.sep + sampling_size)
        for iteration in iterations:
            if int(iteration) > 50:
              continue
            print "Iteration " + str(iteration)
            g = nx.read_adjlist(path + os.sep + iteration)

            #calculate metric
            if metric_type == 'cc':
                metric = nx.average_clustering(g)
            elif metric_type == 'dd':
                degree_dist = get_degree_distribution(g)
                metric = [degree_dist.get(i) or 0 for i in range(array_dim)]
                #get_kl_divergence(degree_dist, baseline_mx)
            elif metric_type == 'scc':
                scc_list = nx.strongly_connected_components(g)
                metric = numpy.zeros(shape=(array_dim))
                for scc in scc_list:
                    metric[len(scc)] += 1
                
            else:
                raise Exception( metric_type + " is not a valid metric" )
            sample_sizes[index] = int(sampling_size)
            mx[int(iteration) - 1, index] = metric #-1 because iterations are 1-indexed
    
    
    for iteration in iterations:
        mx[int(iteration)-1, len(subsampled_list)] = baseline_metric          

    sample_sizes = numpy.append(sample_sizes, [100])
    numpy.savetxt(metric_type + "_samples", sample_sizes)    
    if metric_type == 'cc':        
      numpy.savetxt(metric_type + "_mx", mx)
    else:
      mx.tofile(metric_type+"_mx", sep=' ')
      mx.tofile(metric_type+"_mx_bin")
      dim = numpy.array([num_iterations, len(sample_sizes), array_dim])
      dim.tofile(metric_type+"_dim", sep=' ')

    return mx, sample_sizes

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: python build_metric_matrix.py <samples dir> <orig graph path> <metric type (cc, dd, scc)>"
    else:
        build_metric_matrix(sys.argv[1], sys.argv[2], sys.argv[3])

            
            
                   
                   
        
