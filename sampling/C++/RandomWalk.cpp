#include "RandomWalk.h"
#include <time.h>
#include <stdio.h>
#include <iostream>
using namespace std;

PUNGraph RandomWalk::walk(double percent) {
	srand(time(NULL));
  int node_num = graph->GetNodes();
	TIntV all_ids;
	graph->GetNIdV(all_ids);
	target_node_num = ceil(node_num * percent);
  cout << "Sample Target: " << target_node_num << endl;
  sample_g = TUNGraph::New();
  while (sample_g->GetNodes() < target_node_num) {
    int istart = all_ids[rand()%node_num];
    //cout << "Start from node " << istart << endl;
	cout<<"Sampled graph size(target="<<target_node_num<<"): "<<sample_g->GetNodes()<<endl;
    start_journey(istart, all_ids);
  }
	return sample_g;
}

RandomWalk::RandomWalk(PUNGraph g, int cp, int minc) {
	graph = g;
	check_period = cp;
	min_inc = minc;
}

void RandomWalk::start_journey(int istart, const TIntV &all_node_ids) {
	double jumpback_prob = 0.15;
	int last_check_sz = sample_g->GetNodes();
	TUNGraph::TNodeI currentI = graph->GetNI(istart);
	int srcId = istart;
	if (!sample_g->IsNode(istart))
		sample_g->AddNode(istart);
	while (sample_g->GetNodes() < target_node_num) {
		//cout<< sample_g->GetNodes()<<endl;
		for (int i = 0; i < check_period; i++) {
			double prob = (double)rand() / RAND_MAX;
			if (prob < jumpback_prob) {
				currentI = graph->GetNI(istart);
				srcId = istart;
			}
			else {
				int deg = currentI.GetDeg();
				int ineighbor = currentI.GetNbrNId(rand()%deg);
				if (!sample_g->IsNode(ineighbor)) {
					sample_g->AddNode(ineighbor);
					//cout << sample_g->GetNodes() << endl;
				}
				sample_g->AddEdge(srcId, ineighbor);
				srcId = ineighbor;
				currentI = graph->GetNI(ineighbor);
			}
			if (sample_g->GetNodes() >= target_node_num)
				break;
		}
		if (sample_g->GetNodes() - last_check_sz < min_inc)
			break;
		last_check_sz = sample_g->GetNodes();
	}
}
