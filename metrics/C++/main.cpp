#include "MetricMatrix.h"
#include <iostream>
#include <fstream>
using namespace std;
int main(int argc, char** argv) {
	//string sample_base_dir = "C:/Users/Sylvon/CS224W/project/C++/RandomWalk/RandomWalk/samples_enron";
	//string orig_graph_name = "C:/Users/Sylvon/CS224W/project/Email-Enron.txt";
	string sample_base_dir = "C:/Users/Sylvon/CS224W/project/C++/RandomWalk/RandomWalk/samples_dblp";
	string orig_graph_name = "C:/Users/Sylvon/CS224W/project/com-dblp.ungraph.txt";
	string ofile_prefix = "";
	string ofile_subfix = ".metric";
	MetricMatrix::Metric metric = MetricMatrix::ClusteringCoefficient;


	MetricMatrix mat(orig_graph_name, sample_base_dir, metric);
	int percents[] = {1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50,
					  55, 60, 65, 70, 75, 80, 85, 90, 95};
	int iters[100];
	for (int i = 0; i < 100; i++) {
		iters[i] = i;
	}

	int npercent = sizeof(percents) / sizeof(int);
	int niter = sizeof(iters) / sizeof(int);
	cout<<"num of percent:"<<npercent<<endl;
	cout<<"num of iter:"<<niter<<endl;
	double *dstats = mat.build(percents, npercent, iters, niter);

	ofstream of(ofile_prefix + 
				MetricMatrix::METRIC_NAMES[MetricMatrix::ClusteringCoefficient] + 
				ofile_subfix);
	for (int i = 0; i < npercent; i++) {
		for (int j = 0; j < niter; j++) {
			//cout<<dstats[i*niter+j]<<" ";
			of<<dstats[i*niter+j]<<" ";
		}
		of<<"\n";
		//cout<<endl;
		//system("pause");
	}
	delete[] dstats;
	cout<<"Done!!"<<endl;
	system("pause");
}