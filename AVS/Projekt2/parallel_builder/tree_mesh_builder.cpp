/**
 * @file    tree_mesh_builder.cpp
 *
 * @author  Jiri Vaclavic <xvacla31@stud.fit.vutbr.cz>
 *
 * @brief   Parallel Marching Cubes implementation using OpenMP tasks + octree early elimination
 *
 * @date    16.12.2022
 **/

#include <iostream>
#include <math.h>
#include <limits>

#include "tree_mesh_builder.h"

TreeMeshBuilder::TreeMeshBuilder(unsigned gridEdgeSize)
    : BaseMeshBuilder(gridEdgeSize, "Octree")
{

}
unsigned TreeMeshBuilder::recursiveCube(const Vec3_t<float> &position, const ParametricScalarField &field, size_t cubeSize, int arr[][8]) {

    unsigned totalTriangles = 0;

    if(cubeSize > 1) {
        /* MIDPOINT CALCULATED */
        Vec3_t<float> midP((position.x + cubeSize/2)*mGridResolution, (position.y + cubeSize/2)*mGridResolution, (position.z + cubeSize/2)*mGridResolution);

        float f = mIsoLevel  + (sqrt(3)/2)*(cubeSize*mGridResolution);

        if(evaluateFieldAt(midP, field) > f)
            return 0;

        /* 8 TASKS GENERATED */
        for(int i = 0; i < 8; i++){
            #pragma omp task shared(totalTriangles)
            {                
                int x = arr[0][i];
                int y = arr[1][i];
                int z = arr[2][i];
                Vec3_t<float> cube(position.x + x*(cubeSize/2), position.y + y*(cubeSize/2), position.z + z*(cubeSize/2));

                unsigned tmp = recursiveCube(cube, field, cubeSize/2, arr); 
                totalTriangles += tmp;   
            }
        }

    } else {
        totalTriangles += buildCube(position, field);
    }

    #pragma omp taskwait
    return totalTriangles;
}
unsigned TreeMeshBuilder::marchCubes(const ParametricScalarField &field)
{
    // Suggested approach to tackle this problem is to add new method to
    // this class. This method will call itself to process the children.
    // It is also strongly suggested to first implement Octree as sequential
    // code and only when that works add OpenMP tasks to achieve parallelism.
    unsigned totalTriangles = 0;
    Vec3_t<float> cubeOffset(0, 0, 0);        
    int arr[3][8] = {{0,0,0,0,1,1,1,1},{0,0,1,1,0,0,1,1},{0,1,0,1,0,1,0,1}};
    #pragma omp parallel
    {
      #pragma omp single
        {
            totalTriangles = recursiveCube(cubeOffset, field, mGridSize, arr);
        }        
    }
    return totalTriangles;
}

float TreeMeshBuilder::evaluateFieldAt(const Vec3_t<float> &pos, const ParametricScalarField &field)
{
    const Vec3_t<float> *pPoints = field.getPoints().data();
    const unsigned count = unsigned(field.getPoints().size());

    float value = std::numeric_limits<float>::max();
    //#pragma omp parallel for reduction(min:value)
    for(unsigned i = 0; i < count; ++i)
    {
        float distanceSquared  = (pos.x - pPoints[i].x) * (pos.x - pPoints[i].x);
        distanceSquared       += (pos.y - pPoints[i].y) * (pos.y - pPoints[i].y);
        distanceSquared       += (pos.z - pPoints[i].z) * (pos.z - pPoints[i].z);
        value = std::min(value, distanceSquared);
    }
    return sqrt(value);
}

void TreeMeshBuilder::emitTriangle(const Triangle_t &triangle)
{
    // NOTE: This method is called from "buildCube(...)"!

    // Store generated triangle into vector (array) of generated triangles.
    // The pointer to data in this array is return by "getTrianglesArray(...)" call
    // after "marchCubes(...)" call ends.
    #pragma omp critical
    {
        mTriangles.push_back(triangle);
    }
}
