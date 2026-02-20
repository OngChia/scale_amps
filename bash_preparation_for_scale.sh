#!/bin/bash

#module load stack/2024-06
#module load openmpi/4.1.6
#module load netcdf-c
#module load netcdf-fortran
#module load hdf5
#module load zlib/1.3-mktm5vz

export SCALE_DISABLE_SDM="T"
export SCALE_COMPAT_MPI="T"
export SCALE_ENABLE_OPENMP="T"
#export SCALE_SYS=Linux64-gnu-ompi
export SCALE_SYS=Linux64-nvidia
export SCALE_NETCDF_INCLUDE="-I/user-environment/linux-sles15-neoverse_v2/nvhpc-25.1/netcdf-c-4.9.2-h7unw26sxi3eelxrzcxhd5smgrcb36iv/include -I/user-environment/linux-sles15-neoverse_v2/nvhpc-25.1/netcdf-fortran-4.6.1-hephn4sau5altyim3nrqs733czftlup4/include -I/user-environment/linux-sles15-neoverse_v2/nvhpc-25.1/hdf5-1.14.3-k4pxtegzxrw52n5pbd2ct5efsuzbcuif/include"
export SCALE_NETCDF_LIB="-L/user-environment/linux-sles15-neoverse_v2/nvhpc-25.1/netcdf-c-4.9.2-h7unw26sxi3eelxrzcxhd5smgrcb36iv/lib64 -L/user-environment/linux-sles15-neoverse_v2/nvhpc-25.1/netcdf-cxx4-4.3.1-7odwypxtfnbnn4xfytazptqamtmqu6zm/lib64 -L/user-environment/linux-sles15-neoverse_v2/nvhpc-25.1/netcdf-fortran-4.6.1-hephn4sau5altyim3nrqs733czftlup4/lib -L/user-environment/linux-sles15-neoverse_v2/nvhpc-25.1/hdf5-1.14.3-k4pxtegzxrw52n5pbd2ct5efsuzbcuif/lib -lnetcdff -lnetcdf -lhdf5_hl -lhdf5"
#export SCALE_NETCDF_INCLUDE="-I/cluster/software/stacks/2024-06/spack/opt/spack/linux-ubuntu22.04-x86_64_v3/gcc-12.2.0/netcdf-c-4.9.2-3ixjuamuzhaidkuj2wmtlm6rfztexyc7/include -I/cluster/software/stacks/2024-06/spack/opt/spack/linux-ubuntu22.04-x86_64_v3/gcc-12.2.0/netcdf-fortran-4.6.1-3evygqg3zejnd7ysofubj42hl43wb6iw/include -I/cluster/software/stacks/2024-06/spack/opt/spack/linux-ubuntu22.04-x86_64_v3/gcc-12.2.0/hdf5-1.14.3-tznzefvxmerw2cl3vo3t6hxtvxgctwjp/include"
#export SCALE_NETCDF_LIB="-L/cluster/software/stacks/2024-06/spack/opt/spack/linux-ubuntu22.04-x86_64_v3/gcc-12.2.0/netcdf-fortran-4.6.1-3evygqg3zejnd7ysofubj42hl43wb6iw/lib -L/cluster/software/stacks/2024-06/spack/opt/spack/linux-ubuntu22.04-x86_64_v3/gcc-12.2.0/netcdf-c-4.9.2-3ixjuamuzhaidkuj2wmtlm6rfztexyc7/lib -L/cluster/software/stacks/2024-06/spack/opt/spack/linux-ubuntu22.04-x86_64_v3/gcc-12.2.0/netcdf-cxx4-4.3.1-lovpndjceza5t4wngu3qix5kbyxcojjg/lib -lnetcdff -lnetcdf -lhdf5_hl -lhdf5"

