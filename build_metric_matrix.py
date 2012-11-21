

import os, sys
import networkx as nx
import numpy

def build_metric_matrix(sampling_path, metric_type):
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
    subsampled_list = [sorted_sample_size_list[i] for i in range(len(sorted_sample_size_list)) if i % 5 == 0]
    
    mx = numpy.zeros(shape=(num_iterations, len(subsampled_list)))
    sample_sizes = numpy.zeros(shape=(len(subsampled_list), 1))
    
    for index, sampling_size in enumerate(subsampled_list):
        print "Sampling percentage " + str(sampling_size)
        path = sampling_path + os.sep + sampling_size
        iterations = os.listdir(sampling_path + os.sep + sampling_size)
        for iteration in iterations:
            print "Iteration " + str(iteration)
            g = nx.read_adjlist(path + os.sep + iteration)

            #calculate metric
            if metric_type == 'cc':
                calc_metric = nx.average_clustering
            else:
                raise Exception( metric_type + " is not a valid metric" )
            metric = calc_metric(g)
            sample_sizes[index] = int(sampling_size)
            mx[int(iteration) - 1, index] = metric #-1 because iterations are 1-indexed
    
    numpy.savetxt(metric_type + "_mx", mx)
    numpy.savetxt(metric_type + "_samples", sample_sizes)
    return mx, sample_sizes

if __name__ == "__main__":
    build_metric_matrix(sys.argv[1], sys.argv[2])
            
            
                   
                   
        
