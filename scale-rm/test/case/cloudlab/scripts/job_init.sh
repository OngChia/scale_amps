#!/bin/bash

#SBATCH --ntasks=10
#SBATCH --ntasks-per-node=10
#SBATCH --time=1:00:00
#SBATCH --job-name="init_cloudlab_24"
###SBATCH --mem-per-cpu=1024
###SBATCH --output="LOG"
#SBATCH --error="ERROR_LOG_INIT"
###SBATCH --open-mode=truncate

module load stack/2024-06
module load openmpi/4.1.6
module load netcdf-c
module load netcdf-fortran
module load hdf5
module load zlib/1.3-mktm5vz

export OMP_STACKSIZE=16M

mpirun -n 8 ./scale-rm_init init.conf
