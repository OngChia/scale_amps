# Cloudlab documentation

The idealized experiment's setup for the initial condition and run scripts are stored in */scale-rm/test/case/cloudlab/script/*. The domain is 2 km x 4 km (x and y coordinates, respectively). 

## Initial condition 

The initial vertical profiles of the temperature, potential temperature, pressure, wind speed, water vapor, liquid water, and number concentration of liquid water are stored in */scale-rm/test/case/cloudlab/env.txt*. They are read in to generate the initial condition for the model when users run */scale-rm/test/case/cloudlab/script/init.conf*.

## Spin-up 

The experiment uses AMPS for the microphysics parameterization. During the spin-up period, the ice physics is turned off to reduce the computational burden (there is no INP). The spin-up time is 1 hour (although maybe 2 hour is more ideal as the Nliq still decreases slightly at the end of 1h). The run script is stored in */scale-rm/test/case/cloudlab/script/run.conf*. Restart files are generated at the end of this spin-up simulation.

A large-scale subsidence is imposed to maintain the height of the boundary layer. The strength of the subsidence is stored in */scale-rm/test/case/cloudlab/largeScaledForce.txt*. This is read in by */scale-rm/src/user/mod_user.F90* to apply the subsidence forcing at every time step (see also the namelist `PARAM_USER` in *run.conf*)

## Cloud seeding

Another run script */scale-rm/test/case/cloudlab/script/restart_run.conf* is used for the actual seeding simulation that continues from the end of spin-up period. It starts from the restart files generated from the spin-up simulation. The ice physics is turned on in this run script with 40 bins for the ice particle distribution. The timing, injection rate, and the location of the seeding can be adjusted in the namelist `PARAM_USER` in *restart_run.conf*. the seeding code is also located in */scale-rm/src/user/mod_user.F90*, same as the subsidence.


