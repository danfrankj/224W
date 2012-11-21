#include <stdlib.h>
#include <Snap.h>
#include <cmath>
#include <string>
using std::string;

class RandomWalk {
private:
	PUNGraph graph;
	PUNGraph sample_g;
	int check_period;
	int min_inc;
	int target_node_num;
	void start_journey(int istart, const TIntV &all_node_ids);
public:
	PUNGraph walk(double percent);
	RandomWalk(PUNGraph g, int cp, int minc);
};