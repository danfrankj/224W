#include "RandomWalk.h"
#include <Snap.h>
#include <iostream>
#include <windows.h>
#include <time.h>

void ensure_dir(char* path) {
	CreateDirectory(path, NULL);
}

int main(int argc, const char* argv[]) {
	//char *graph_name = "C:/Users/Sylvon/CS224W/project/Wiki-Vote.txt";
	char *graph_name = "C:/Users/Sylvon/CS224W/project/com-dblp.ungraph.txt";
	PUNGraph g = TSnap::LoadEdgeList<PUNGraph>(graph_name, 0, 1);
	int sample_iters = 100;
	int sample_percents[] = {1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50,
							 55, 60, 65, 70, 75, 80, 85, 90, 95};
	char file_path[1024];
	char percent_dir[1024];
	char *output_dir = "samples/";
	RandomWalk rw(g, 500, 500*0.3);
	time_t start, end;
	for (int p = 0; p < sizeof(sample_percents); p++) {
		time(&start);
		std::cout << "Sampling " << sample_percents[p] << " percent of the graph" << std::endl;
		sprintf(percent_dir, "%s%d/", output_dir, sample_percents[p]);
		ensure_dir(percent_dir);
		for (int i = 0; i < sample_iters; i++) {
			sprintf(file_path, "%s%d", percent_dir, i);
			PUNGraph sample_g = rw.walk(sample_percents[p]/100.);
			TSnap::SaveEdgeList<PUNGraph>(sample_g, file_path, "");
		}
		time(&end);
		std::cout << "Elapsed time: " << difftime(end, start) << " seconds" <<std::endl;
	}
	return 0;
}