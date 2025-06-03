#!/bin/bash

module load stack/2024-06
module load openmpi/4.1.6
module load netcdf-c
module load netcdf-fortran
module load hdf5
module load zlib/1.3-mktm5vz

export SCALE_DISABLE_SDM="T"
export SCALE_COMPAT_MPI="T"
export SCALE_ENABLE_OPENMP="T"
export SCALE_SYS=Linux64-gnu-ompi
#export SCALE_NETCDF_INCLUDE="-I/user-environment/linux-sles15-neoverse_v2/nvhpc-24.3/netcdf-fortran-4.6.1-siaau7en4nxc4m42qy73sj34bxi2eq4h/include"
export SCALE_NETCDF_INCLUDE="-I/cluster/software/stacks/2024-06/spack/opt/spack/linux-ubuntu22.04-x86_64_v3/gcc-12.2.0/netcdf-c-4.9.2-3ixjuamuzhaidkuj2wmtlm6rfztexyc7/include -I/cluster/software/stacks/2024-06/spack/opt/spack/linux-ubuntu22.04-x86_64_v3/gcc-12.2.0/netcdf-fortran-4.6.1-3evygqg3zejnd7ysofubj42hl43wb6iw/include -I/cluster/software/stacks/2024-06/spack/opt/spack/linux-ubuntu22.04-x86_64_v3/gcc-12.2.0/hdf5-1.14.3-tznzefvxmerw2cl3vo3t6hxtvxgctwjp/include"
export SCALE_NETCDF_LIB="-L/cluster/software/stacks/2024-06/spack/opt/spack/linux-ubuntu22.04-x86_64_v3/gcc-12.2.0/netcdf-fortran-4.6.1-3evygqg3zejnd7ysofubj42hl43wb6iw/lib -L/cluster/software/stacks/2024-06/spack/opt/spack/linux-ubuntu22.04-x86_64_v3/gcc-12.2.0/netcdf-c-4.9.2-3ixjuamuzhaidkuj2wmtlm6rfztexyc7/lib -L/cluster/software/stacks/2024-06/spack/opt/spack/linux-ubuntu22.04-x86_64_v3/gcc-12.2.0/netcdf-cxx4-4.3.1-lovpndjceza5t4wngu3qix5kbyxcojjg/lib -lnetcdff -lnetcdf -lhdf5_hl -lhdf5"

