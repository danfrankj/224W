#include "MetricMatrix.h"
#include <vector>
#include <iostream>
#include <time.h>

using namespace std;
void get_degree_distribution(PUNGraph g, map<int, int> &deg_map);
void get_scc_size_distribution(PUNGraph g, map<int, int> &sccsz_map);
void get_clustering_coefficient_distribution(PUNGraph g, map<int, int> &cc_map);
void cumsum(map<int, int> &metric_map, vector<double> &cumsum);

const MetricFun MetricMatrix::metric_funs[3] = {
							get_clustering_coefficient_distribution,
						    get_scc_size_distribution, 
							get_degree_distribution
};

const string MetricMatrix::METRIC_NAMES[3] = {
		"Clustering Coefficient", 
		"Connected Component Size", 
		"Degree Distribution"
};


void
get_degree_distribution(PUNGraph g, map<int, int> &deg_map) {
	TIntV all_ids;
	g->GetNIdV(all_ids);
	TUNGraph::TNodeI node = g->BegNI();
	TUNGraph::TNodeI end = g->EndNI();
	
	while (true) {
		int deg = node.GetDeg();
		if (deg_map.count(deg) == 0)
			deg_map[deg] = 0;
		deg_map[deg]++;
		if (node == end)
			break;
		node++;
	}
}

void 
get_scc_size_distribution(PUNGraph g, map<int, int> &sccsz_map) {
	TIntPrV prv;
	TSnap::GetSccSzCnt(g, prv);
	TVec<TIntPr>::TIter ipr = prv.BegI();
	TVec<TIntPr>::TIter end = prv.EndI();
	
	while (true) {
		TInt sz;
		TInt count;
		ipr->GetVal(sz, count);
		sccsz_map[sz] = count;
		if (ipr == end)
			break;
		ipr++;
	}
}

void get_clustering_coefficient_distribution
	(PUNGraph g, map<int, int> &cc_map) {
		TIntFltH node_cch;
		TSnap::GetNodeClustCf(g, node_cch);
		THash<TInt, TFlt>::TIter node = node_cch.BegI();
		TFlt mincc = 1, maxcc = -1;
		for (int i = 0; i < 100; i++) {
			cc_map[i] = 0;
		}
		while (!node.IsEnd()) {
			int bin = node.GetDat()*100;
			if (bin <0 || bin > 100) {
				cout << "Clustering Coefficient: something wrong!"<<endl;
				exit(-1);
			}
			bin = min(99, bin);
			cc_map[bin]++;
			node++;
		}
}

void 
cumsum(map<int, int> &metric_map, vector<double> &cumsum) {
	cumsum.clear();
	double sum = 0;
	map<int, int>::iterator iter = metric_map.begin();
	map<int, int>::iterator end = metric_map.end();
	while (iter != end) {
		sum += iter->second;
		cumsum.push_back(sum);
		iter++;
	}
}

double* MetricMatrix::build(int percents[], int npercent, int iterations[], int niter) {
	time_t start, end;
	double* dstats = new double[niter*npercent];
	orig_g = TSnap::LoadEdgeList<PUNGraph>(orig_graph_name.c_str(), 0, 1);
	map<int, int> baseline_metric;
	vector<double> baseline_cumsum;
	vector<double> sample_cumsum;
	time(&start);
	metric_funs[metric](orig_g, baseline_metric);
	cumsum(baseline_metric, baseline_cumsum);
	time(&end);
	std::cout << "Calculating baseline takes: " << difftime(end, start) << " seconds" <<std::endl;
	double baseline_sum, sample_sum;
	baseline_sum = baseline_cumsum[baseline_cumsum.size()-1];
	char c_percent[100], c_iter[100];
	for (int i = 0; i < npercent; i++) {
		cout<<"Calculating dstats for "<<percents[i]<<"% sampling"<<endl;
		itoa(percents[i], c_percent, 10);
		for (int j = 0; j < niter; j++) {
			time(&start);
			itoa(iterations[j], c_iter, 10);
			string sample_path = sample_base_dir + "/" 
				+ c_percent + "/" + c_iter;
			PUNGraph sample_g = TSnap::LoadEdgeList<PUNGraph>
				(sample_path.c_str(), 0, 1);
			map<int, int> sample_metric;
			metric_funs[metric](sample_g, sample_metric);
			cumsum(sample_metric, sample_cumsum);
			sample_sum = sample_cumsum[sample_cumsum.size()-1];
			double max_diff = -1;
			for (int k = 0; k < sample_cumsum.size(); k++) {
				double normalized_diff = 
					abs(baseline_cumsum[k]/baseline_sum-
						sample_cumsum[k]/sample_sum);
				if (normalized_diff > max_diff)
					max_diff = normalized_diff;
			}
			cout<<"max_diff: " <<max_diff<<endl;
			dstats[i*niter+j] = max_diff;
			time(&end);
			std::cout << "Elapsed time: " << difftime(end, start) << " seconds" <<std::endl;
		}
	}
	return dstats;
}

MetricMatrix::MetricMatrix(string orig_graph_name, string sample_base_dir, Metric metric) {
	this->orig_graph_name = orig_graph_name;
	this->sample_base_dir = sample_base_dir;
	this->metric = metric;
}