/*
    Soubor:	    parkmeans.cc
    Datum:	    19.4.2023
    Autor:	    Bc. Jiri Vaclavic, xvacla31@stud.fit.vutbr.cz
    Projekt:    PRL, Implementace algoritmu K-means
*/

#include <iostream>
#include <vector>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <fstream>
#include "mpi.h"

using namespace std;

/*  This function finds the index of the nearest cluster center for a given value */
int getClusterIndex(double x, vector<double>& centroids) {
    int index = 0;
    double minDist = abs(x - centroids[0]);
    for (int i = 1; i < centroids.size(); i++) {
        double dist = abs(x - centroids[i]);
        if (dist < minDist) {
            index = i;
            minDist = dist;
        }
    }
    return index;
}

int main(int argc, char **argv) {
    
    MPI_Init(&argc, &argv); 

    /** rank = process ID, size = number of processes **/
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    /** vector for reading input data **/
    vector<int> input_data;
    int value_count = 0;
    int arr_size;
    int changed = 1;
    ifstream fs("numbers");

    /** Reading array from input file in main process**/
    if (rank == 0){        
        int value_count = 0;
        arr_size = 0;

        fstream fs;
        fs.open("numbers", fstream::in);
        
        while (fs.good()) {
            int arr_val = fs.get();
            
            if (fs.eof()) {
                break;
            }
            if(size == arr_size){
                break;
            }
            value_count++;

            if (arr_size < value_count) {
                input_data.resize(arr_size + 1);
                arr_size = value_count;
            }

            input_data[value_count - 1] = arr_val;
        }
        
        fs.close();

        /** Check if there are enough numbers for each process **/
        if(arr_size < size){
            cout<<"Error: Less numbers than processes"<<endl;
            return 1;
        }
        
    }
    int process_data = 0;

    /** Sending 1 value from input array to all processes **/
    MPI_Scatter(input_data.data(), 1, MPI_INT,
                &process_data, 1, MPI_INT, 0, MPI_COMM_WORLD);
    

    int k = 4;
    vector<double> centroids(k);

    /** Initialize centroids in main the process **/
    if(rank == 0){

        for (int i = 0; i < k; i++) {
            centroids[i] = input_data[i];
        }
    }

    /** Broadcast centroids and changed flag to all processes **/
    MPI_Bcast(centroids.data(), 4, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    MPI_Bcast(&changed, 1, MPI_INT, 0, MPI_COMM_WORLD);
    
    vector<vector<int>> clusters;
    vector<int> index_count;
    if(rank == 0){
        index_count.resize(4);
        clusters.resize(k);
        for (int i = 0; i < k; i++) {
            clusters[i].resize(arr_size);
        }
        
    }
    int it_count = 0;
    /** K-means algorithm **/
    while(changed){
        
        int index = getClusterIndex(process_data, centroids);
        
        vector<int> indexis;
        
        if (rank == 0) {
            it_count++;
            indexis.resize(size);            
            index_count.assign(4, 0);
            for (int i = 0; i < k; i++){
                clusters[i].clear();
                index_count[i] = 0;
            }
                
        }    
        
        MPI_Gather(&index, 1, MPI_INT, indexis.data(), 1, MPI_INT, 0, MPI_COMM_WORLD);
        
        /** Sorting input numbers in clusters by calculated indexes **/
        if(rank == 0){ 
            changed = 0;            
            for(int i = 0; i < arr_size; i++) {
                if(indexis[i] == 0) {
                    index_count[0]++;                
                    clusters[0].push_back(input_data[i]);                    
                }else if(indexis[i] == 1){
                    index_count[1]++;
                    clusters[1].push_back(input_data[i]);
                }else if(indexis[i] == 2){
                    index_count[2]++;
                    clusters[2].push_back(input_data[i]);
                } else{
                    index_count[3]++;
                    clusters[3].push_back(input_data[i]);
                }
            }
            

            /** Reacalculating centroids **/
            for (int i = 0; i < k; i++) {
                if (clusters[i].empty()) continue;

                double sum = 0;
                for (double x : clusters[i]) {
                    sum += x;
                }
                double mean = sum / clusters[i].size();

                if (mean != centroids[i]) {
                    centroids[i] = mean;
                    changed = 1;
                }
            }
            

        }

        /** Waiting for main process to calculate if centroids have changed **/
        MPI_Barrier(MPI_COMM_WORLD);
        MPI_Bcast(centroids.data(), 4, MPI_DOUBLE, 0, MPI_COMM_WORLD);
        MPI_Bcast(&changed, 1, MPI_INT, 0, MPI_COMM_WORLD);
    }
    
    /** Printing out the results in set format **/
    if(rank == 0){
        for (int i = 0; i < k; i++) {
            
            cout << "["<< centroids[i] <<"] ";
            for (int i2 = 0; i2 < index_count[i]; i2++)
            {
                if(i2 < index_count[i]-1){
                    cout<< clusters[i][i2]<< ", " ;
                }else{
                    cout<< clusters[i][i2];
                }
                
            }
            
            cout << endl;            
        }
    }
    MPI_Finalize();
    return 0;
}
