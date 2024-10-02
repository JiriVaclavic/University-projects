/*
    Soubor:	    parsplit.cpp
    Datum:	    29.3.2023
    Autor:	    Bc. Jiri Vaclavic, xvacla31@stud.fit.vutbr.cz
    Projekt:    PRL, Implementace algoritmu PARALLEL SPLITTING
*/

#include <stdio.h>
#include <stdlib.h>
#include <cstdlib>
#include <ostream>
#include <fstream>
#include "mpi.h"


/** Computing Select sort step 
 *  comparing values with median and splitting
 *  them into separated arrays L, E or G **/
void select_sort_step(int *input_array, int median, int array_length,
                        int *L_length, int *E_length, int *G_length, int *array_L, int *array_E, int *array_G){ 
    for(int i = 0; i < (array_length); i++){

        if(input_array[i] < median){
            array_L[*L_length] = input_array[i];
            (*L_length)++;            
        } else if(input_array[i] == median){
            array_E[*E_length] = input_array[i];
            (*E_length)++;            
        } else{
            array_G[*G_length] = input_array[i];
            (*G_length)++;
        }
    }
}
int main(int argc, char **argv) {

    MPI_Init(&argc, &argv); 

    int rank, size; // rank = process ID, size = number of processes
    MPI_Comm_rank(MPI_COMM_WORLD, &rank); // returns process ID of the processor that called the function
    MPI_Comm_size(MPI_COMM_WORLD, &size); // returns number of processes
    
    int *input_arr = NULL;
    int median, value_count;
    int arr_size = 0;    

    /** Reading array from input file **/
    if (rank == 0){
        median = 0;
        value_count = 0;
        input_arr = (int*) malloc(sizeof(int)*size);
        arr_size = size;
        std::fstream fs;
        fs.open("numbers", std::fstream::in);        
        std::cout << "Vstupni pole: ";
        while (fs.good()) {
            int arr_val = fs.get();            
            if(!fs.good())
                break;
            value_count++;
            if(arr_size < value_count){
                input_arr = (int*) realloc(input_arr, (arr_size+size)*(sizeof(int)));
                arr_size+=size;
            }                
            input_arr[value_count-1] = arr_val;
            std::cout << arr_val << " ";
        }
        std::cout << std::endl;
        fs.close();
        median = input_arr[(value_count/2)-1];

    }
    /** Sharing median and length of sub_array for memory allocation **/
    MPI_Bcast(&value_count, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast(&median, 1, MPI_INT, 0, MPI_COMM_WORLD);
    
    
    int sub_array_size = int(value_count / size);  
    int *sub_array = (int*) malloc(sizeof(int) * sub_array_size);

    /** Sending part of array to all processes **/
    MPI_Scatter(input_arr, sub_array_size, MPI_INT,
                sub_array, sub_array_size, MPI_INT, 0, MPI_COMM_WORLD);
    
    
    int L_length = 0;
    int E_length = 0;
    int G_length = 0;
    /** Allocating memory for all 3 arrays (L = Less than median,
     *  E = Equal to median, G = Greater than median) **/
    int *array_L = (int*) malloc( sub_array_size * sizeof(int));
    int *array_E = (int*) malloc( sub_array_size * sizeof(int));
    int *array_G = (int*) malloc( sub_array_size * sizeof(int));
    
    /** Calculating the step of Select sort algorithm **/
    select_sort_step(sub_array, median, sub_array_size, 
                    &L_length, &E_length, &G_length, array_L, array_E, array_G);    

    
    int *recvcounts1 = NULL;
    int *recvcounts2 = NULL;
    int *recvcounts3 = NULL;

    /** Allocating memory for receive data **/
    if (rank == 0){
        recvcounts1 = (int*) malloc( size * sizeof(int)) ;
        recvcounts2 = (int*) malloc( size * sizeof(int)) ;
        recvcounts3 = (int*) malloc( size * sizeof(int)) ;
    }
        
    /** Gathering lengths of sorted sub_arrays L, E, G from each process **/
    MPI_Gather(&L_length, 1, MPI_INT, recvcounts1, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Gather(&E_length, 1, MPI_INT, recvcounts2, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Gather(&G_length, 1, MPI_INT, recvcounts3, 1, MPI_INT, 0, MPI_COMM_WORLD);

    int *displs1 = NULL;
    int *displs2 = NULL;
    int *displs3 = NULL;

    int *output_array_L = NULL;
    int *output_array_E = NULL;
    int *output_array_G = NULL;

    int totlen1 = 0;
    int totlen2 = 0;
    int totlen3 = 0;

    /** Calculating offset of received data **/
    if (rank == 0) {
        displs1 = (int*) malloc( size * sizeof(int) );
        displs2 = (int*) malloc( size * sizeof(int) );
        displs3 = (int*) malloc( size * sizeof(int) );
        displs1[0] = 0;
        displs2[0] = 0;
        displs3[0] = 0;
        totlen1 += recvcounts1[0];
        totlen2 += recvcounts2[0];
        totlen3 += recvcounts3[0];


        for (int i=1; i<size; i++) {
           totlen1 += recvcounts1[i];
           displs1[i] = displs1[i-1] + recvcounts1[i-1];
           totlen2 += recvcounts2[i];
           displs2[i] = displs2[i-1] + recvcounts2[i-1] ;
           totlen3 += recvcounts3[i];
           displs3[i] = displs3[i-1] + recvcounts3[i-1];
        }

        output_array_L = (int*) malloc(totlen1 * sizeof(int));
        output_array_E = (int*) malloc(totlen2 * sizeof(int));
        output_array_G = (int*) malloc(totlen3 * sizeof(int));            

    }
    
    /** Gathering data from all processes into main(root) process **/
    MPI_Gatherv(array_L, L_length, MPI_INT, output_array_L, recvcounts1, displs1, MPI_INT, 0, MPI_COMM_WORLD);    
    MPI_Gatherv(array_E, E_length, MPI_INT, output_array_E, recvcounts2, displs2, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Gatherv(array_G, G_length, MPI_INT, output_array_G, recvcounts3, displs3, MPI_INT, 0, MPI_COMM_WORLD);    
  
     
    /** Printing out the results in set format **/
    if (rank == 0) {
        printf("---------------------------------------------------------\n");
        printf("L = {");
        for (int i = 0; i < totlen1; i++)
        {            
            if(i == totlen1-1){
                printf("%i",output_array_L[i]);   
            }else{
                printf("%i, ",output_array_L[i]);
            }
        }
        printf("}\n");
        printf("E = {");
        for (int i = 0; i < totlen2; i++)
        {
            if(i == totlen2-1){
                printf("%i",output_array_E[i]);   
            }else{
                printf("%i, ",output_array_E[i]);
            }
        }
        printf("}\n");
        printf("G = {");
        for (int i = 0; i < totlen3; i++)
        {
            if(i == totlen3-1){
                printf("%i",output_array_G[i]);   
            }else{
                printf("%i, ",output_array_G[i]);
            }
        }
        printf("}\n");
        free(recvcounts1);
        free(recvcounts2);
        free(recvcounts3);
        free(displs1);
        free(displs2);
        free(displs3);
        free(input_arr);
        
    }
    free(sub_array);
    free(output_array_L);
    free(output_array_E);
    free(output_array_G);
    MPI_Finalize();
    return 0;
}