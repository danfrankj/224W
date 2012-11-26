import networkx as nx
import os
import sys
import random

def start_journey(sample_g, whole_graph, istart, check_period, 
            min_inc, target_node_num):
  jumpback_prob = 0.15
  last_check_sz = sample_g.number_of_nodes()
  current_node = whole_graph.nodes()[istart]
  while sample_g.number_of_nodes() < target_node_num:
    print sample_g.number_of_nodes(), last_check_sz, min_inc
    for i in range(0, check_period):
      if random.random() < jumpback_prob:
        current_node = whole_graph.nodes()[istart]
      else:
        neighbors = [n for n in nx.all_neighbors(whole_graph, current_node)]
        num_neighbors = len(neighbors)
        if num_neighbors == 0:
          break
        ineighbor = random.randint(0, num_neighbors-1)
        sample_g.add_edge(current_node, neighbors[ineighbor])
        current_node = neighbors[ineighbor]
      if sample_g.number_of_nodes() >= target_node_num:
        break

    if sample_g.number_of_nodes() - last_check_sz < min_inc:
      break 
    else:
      last_check_sz = sample_g.number_of_nodes()

def walk(whole_graph, sample_percent, dlm = '\t'):
  node_num = whole_graph.number_of_nodes()
  print 'Done.', node_num, ' nodes in total'
  target_node_num = node_num * sample_percent
  print 'Target: sample', target_node_num, 'nodes'

  sampled_g = nx.Graph()
  check_period = 500
  min_inc = 500 * 0.3
  while sampled_g.number_of_nodes() < target_node_num:
    istart = random.randint(0, node_num-1)
    print istart
    start_journey(sampled_g, whole_graph, istart, check_period, 
        min_inc, target_node_num)
    print 'sampled size', sampled_g.number_of_nodes()
  
  return sampled_g

def ensure_dir(path): 
  if not os.path.exists(path):
    os.makedirs(path)

if __name__ == '__main__':
  input_graph = sys.argv[1]
  dlm = '\t'
  print 'Reading graph', input_graph 
  whole_graph = nx.read_adjlist(input_graph, delimiter = dlm, create_using=nx.Graph())
  num_sample_iterations = 100;
  sample_percents = range(1, 50, 2)   
  output_dir = 'samples/' 
  for p in sample_percents:
    print p
    percent_dir = output_dir + str(p) + '/'
    ensure_dir(percent_dir)
    for i in range(1, num_sample_iterations+1):
      print i
      output_file = percent_dir + str(i) 
      sample_g = walk(whole_graph, float(p)/100, dlm)
      nx.write_adjlist(sample_g, output_file) 
