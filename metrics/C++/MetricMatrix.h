#include <Snap.h>
#include <map>
#include <string>
using namespace std;

typedef void (*MetricFun)(PUNGraph g, map<int, int> &);

class MetricMatrix {
public:
	static enum Metric{ClusteringCoefficient=0, 
		ConnectedComponentSize, DegreeDistribution};
	static const string METRIC_NAMES[3];
private:
	PUNGraph orig_g;
	string sample_base_dir;
	string orig_graph_name;
	Metric metric;

	static const MetricFun metric_funs[3];
public:
	double* build(int percents[], int npercent, int iterations[], int niter);

	MetricMatrix(string orig_graph_name, string sample_base_dir, Metric metric);
};