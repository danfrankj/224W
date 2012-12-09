

import os, sys
import networkx as nx
import numpy
from scipy.sparse import csr_matrix
from scipy.io import mmread, mmwrite
from matplotlib.pyplot import hist
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

#def get_kl_divergence(d1, d2):
#    """
#    Given 2 distributions (dicts) d1 and d2, get the KL-divergence between the two
#    The key is the discrete x-value, and the value is the y-value
#    """
#    max_divergence = 0
#    for i in range(max(max(d1), max(d2))):
#        v1 = d1.get(i) or 0
#        v2 = d2.get(i) or 0
#        if abs(v1 - v2) > max_divergence:
#            max_divergence = abs(v1-v2)
#    return max_divergence

#returns dict
def get_degree_distribution(g, array_dim=None) :
    degs = {}
    for n in g.nodes() :
        deg = g.degree(n)
        if deg not in degs :
            degs[ deg ] = 0
        degs[ deg ] += 1
    for key in degs.keys():
        degs[key] /= float(len(g.nodes()))
    if array_dim:
        return [degs.get(i) or 0 for i in range(array_dim)]
    else:
        return [degs.get(i) or 0 for i in range(max(degs)+1)]

#return array
def get_scc_size_distribution(g, array_dim=None):
    scc_list = nx.strongly_connected_components(g)
    scc_size_dist = numpy.zeros(shape=(array_dim or len(scc_list[0])+1))
    for scc in scc_list:
        scc_size_dist[len(scc)] += 1
    for i in range(len(scc_size_dist)):
        scc_size_dist[i] /= float(len(scc_list))
    return scc_size_dist


def get_cc_distribution(g):
    ccs = nx.clustering(g).values()
    cc_dist = numpy.zeros(shape=(101))  #from 0 to 1 in .01 increments
    for cc in ccs:
        cc_dist[int(cc * 100)] += 1
    for i in range(len(cc_dist)):
        cc_dist[i] /= float(len(ccs))
    return cc_dist
        
def dstat(p, q):
    p = p / numpy.sum(p)
    q = q / numpy.sum(q)
    return numpy.max(numpy.abs(numpy.cumsum(p) - numpy.cumsum(q)))
    
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
     
     Outputs:
     --------
     numpy 2-d array : sampling size x iterations -> metric value
     
     numpy 1-d array : array of the sample sizes used for the corresponding index for the rows
     of the 2-d array
     
    """
    str_sample_size_list = os.listdir(sampling_path)
    num_iterations = len(os.listdir(sampling_path + os.sep + str_sample_size_list[0]))
    
    sorted_sample_size_list = sorted(str_sample_size_list, key=lambda x: int(x))
    subsampled_list = [sorted_sample_size_list[i] for i in range(len(sorted_sample_size_list)) if i in [0]]#[0,2,4,6,8,10,12,14,16,18] ]
    
    sample_sizes = numpy.zeros(shape=(len(subsampled_list), 1))
    
    
    #calculate metric on original graph 
    #use len(subsampled_list)+1 to leave space for 100% case
    if metric_type == 'cc':
        baseline_metric = get_cc_distribution(nx.read_edgelist(orig_graph_path))
        mx = numpy.zeros(shape=(num_iterations, len(subsampled_list)+1))
    elif metric_type == 'dd':
        baseline_metric = get_degree_distribution(nx.read_edgelist(orig_graph_path))
        array_dim = len(baseline_metric)
        #mx = numpy.zeros(shape=(num_iterations, len(subsampled_list)+1, array_dim))
        mx = numpy.zeros(shape=(num_iterations, len(subsampled_list)+1))
    elif metric_type == 'scc':
        g = nx.read_edgelist(orig_graph_path)
        baseline_metric = get_scc_size_distribution(g)
        array_dim = len(baseline_metric)
        #mx = numpy.zeros(shape=(num_iterations, len(subsampled_list)+1, array_dim))
        mx = numpy.zeros(shape=(num_iterations, len(subsampled_list)+1))

    
    for index, sampling_size in enumerate(subsampled_list):
        print "Sampling percentage " + str(sampling_size)
        path = sampling_path + os.sep + sampling_size
        iterations = os.listdir(sampling_path + os.sep + sampling_size)
        for iteration in iterations:
            #if int(iteration) > 50:
            #  continue
            print "Iteration " + str(iteration)
            g = nx.read_adjlist(path + os.sep + iteration)

            #calculate metric
            if metric_type == 'cc':
                metric = get_cc_distribution(g)
            elif metric_type == 'dd':
                metric = get_degree_distribution(g, array_dim)
                #get_kl_divergence(degree_dist, baseline_mx)
            elif metric_type == 'scc':
                metric = get_scc_size_distribution(g, array_dim)
                
            else:
                raise Exception( metric_type + " is not a valid metric" )
            sample_sizes[index] = int(sampling_size)
            
            #mx[int(iteration) - 1, index] = metric #-1 because iterations are 1-indexed
            mx[int(iteration) - 1, index] = dstat(metric, baseline_metric)

    """
            #output sparse matrix
            if metric_type == 'dd' or metric_type == 'scc':
                mx_sparse = csr_matrix(mx);
                mm_write('tmp_sparse/' + iteration, mx_sparse)
                
    """
    
    
    for iteration in iterations:
        mx[int(iteration)-1, len(subsampled_list)] = 0; #baseline_metric          

    sample_sizes = numpy.append(sample_sizes, [100])
    numpy.savetxt(metric_type + "_samples", sample_sizes)    
    #if metric_type == 'cc':        
    numpy.savetxt(metric_type + "_mx", mx)
    """
    else:
        mx.tofile(metric_type+"_mx", sep=' ')
        mx.tofile(metric_type+"_mx_bin")
        dim = numpy.array([num_iterations, len(sample_sizes), array_dim])
        dim.tofile(metric_type+"_dim", sep=' ')
    """
    return mx, sample_sizes
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: python build_metric_matrix.py <samples dir> <orig graph path> <metric type (cc, dd, scc)>"
    else:
        build_metric_matrix(sys.argv[1], sys.argv[2], sys.argv[3])

            
            
                   
                   
        
