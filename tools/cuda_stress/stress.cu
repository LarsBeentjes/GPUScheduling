#include <stdio.h>

/*
 * quite simple application to stress a GPU (runs for a couple seconds)
 *
 * compile with: 'nvcc -o stress stress.cu'
 */

__global__
void worker(int size, float *x, float *y)
{
  int i = blockIdx.x * blockDim.x + threadIdx.x;

  if (i < size)
  {
      x[i] = x[i] * y[i];
      x[i] = pow(y[i], x[i]);
      x[i] = log(x[i]);
      x[i] = sqrt(x[i]);
      x[i] = cos(x[i]);
      x[i] = sin(y[i]);
  }
}

int main()
{
    const int SIZE = 1024 * 1024;
    const int ITERATIONS = 1024 * 1024;

    float *x = (float *)malloc(SIZE * sizeof(float));
    float *y = (float *)malloc(SIZE * sizeof(float));

    for (int i = 0; i < SIZE; i++)
    {
        x[i] = 1.0;
        y[i] = (float)i / SIZE;
    }

    float *cuda_x;
    float *cuda_y;

    cudaMalloc(&cuda_x, SIZE * sizeof(float));
    cudaMalloc(&cuda_y, SIZE * sizeof(float));

    cudaMemcpy(cuda_x, x, SIZE * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(cuda_y, y, SIZE * sizeof(float), cudaMemcpyHostToDevice);

    for(int i = 0; i < ITERATIONS; i++)
        worker<<<(SIZE + 255) /  256, 256>>>(SIZE, cuda_x, cuda_y);

    cudaFree(cuda_y);
    cudaFree(cuda_x);
    free(y);
    free(x);

    return 0;
}
