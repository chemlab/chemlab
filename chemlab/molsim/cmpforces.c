#include "cmpforces.h"
#include <math.h>
#include <stdio.h>
#include <omp.h>
#include <stdlib.h>

void printcoords(double *coords, int dim)
{
  int i,j;
  
  printf("*****\n");
  for (i=0; i<dim; i++)
    {
      for (j=0; j<3; j++)
	printf("%e ",coords[i*3+j]);
      printf("\n");
    }
  return;
}

void omplennard_jones(double *coords, double *out, int dim, double sigma, double eps, int periodic, double boxsize) 
{
    int i, j;
    double rsq, rsq7, rsq4, s6, s12, fac;
    double *dist;
#pragma omp parallel for shared(coords, out, sigma, eps, periodic, boxsize) private(i, j, rsq, rsq7, rsq4, s6, s12, fac, dist)
    for (i=0; i<dim; i++) 
      {
    for (j=i+1; j<dim; j++) 
      {
	dist = malloc(sizeof(double)*3);
	
	if (dist == NULL) abort();
	
	dist[0] = coords[j*3] - coords[i*3];
	dist[1] = coords[j*3 + 1] - coords[i*3 + 1];
	dist[2] = coords[j*3 + 2] - coords[i*3 + 2];
	
	if (periodic) 
	  {
	    dist[0] = dist[0] - boxsize * rint(dist[0]/boxsize);
	    dist[1] = dist[1] - boxsize * rint(dist[1]/boxsize);
	    dist[2] = dist[2] - boxsize * rint(dist[2]/boxsize);
	  }
	
	rsq = dist[0]*dist[0] + dist[1]*dist[1] + dist[2]*dist[2];
	rsq4 = rsq*rsq*rsq*rsq;
	rsq7 = rsq4*rsq*rsq*rsq;
	
	s6 = sigma*sigma*sigma*sigma*sigma*sigma;
	s12 = s6*s6;
	fac = -24*eps*(2*(s12/rsq7) - s6/rsq4);
	
	// printf("fac = %e\n sigma = %e\n eps = %e\n rsq = %e\n", fac, sigma, eps, rsq);
        #pragma omp atomic
	out[i*3] += fac*dist[0];
	#pragma omp atomic
	out[i*3 + 1] += fac*dist[1];
	#pragma omp atomic
	out[i*3 + 2] += fac*dist[2];
	
	#pragma omp atomic
	out[j*3] -= fac*dist[0];
	#pragma omp atomic
	out[j*3 + 1] -= fac*dist[1];
	#pragma omp atomic
	out[j*3 + 2] -= fac*dist[2];
	
	free(dist);
      }
    }

}

