import enum
import math

import numpy as np


# TODO(Chia Rui): Fix wrong type annotation

class IceMode(enum.IntEnum):
    CYLINDER = 1
    SPHEROID = 2


class IceHabit(enum.IntEnum):
    PLATE = 1
    DENDRITE = 2
    COLUMN = 3
    PLANAR_POLYCRYSTAL = 4
    COLUMN_POLYCRYSTAL = 5
    IRREGULAR_POLYCRYSTAL = 6
    NONE = -1


class IceType(enum.IntEnum):
    # 1 : pristine crystal
    # 2 : rimed crystal
    # 3 : aggregate
    # 4 : rimed aggregate
    # 5 : graupel
    # 6 : hail
    PRISTINE = 1
    RIMED_CRYSTAL = 2
    AGGREGATE = 3
    RIMED_AGGREGATE = 4
    GRAUPEL = 5
    HAIL = 6
    NONE = -1
    # AGGREGATE = 1
    # PRISTINE = 2
    # RIMED_AGGREGATE = 3
    # GRAUPEL = 4
    # RIMED_CRYSTAL = 5
    # NONE = -1


ICE_MAX_DENS = 0.91668 # g cm-3
T_0 = 273.16
P_0 = 1013250.0 # g/s^2/cm
R_D = 287.04e4
R_V = 461.5e4
M_W = 18.016
R_U = 8.31436e7
MR = M_W / R_U

R_DV = R_D / R_V
AMPS_LIQSUPERSAT_TEMP_RANGE = np.arange(start=163.0,step=1.0,stop=314.0)
AMPS_ICESUPERSAT_TEMP_RANGE = np.arange(start=163.0,step=1.0,stop=275.0)

NOK_IGP = 23
A_IGP = np.zeros((NOK_IGP, 4), dtype=float)
B_IGP = np.zeros((NOK_IGP, 4), dtype=float)
X_IGP = np.array([-60.0,-55.0, -50.0, -45.0, -40.0, -35.0, -30.0, -27.0, -25.0, -23.0, -21.0, -20.0, -17.0, -15.0, -12.0, -10.0, -8.0, -6.0, -5.0, -4.0, -3.5, -2.5, -1.5])
assert X_IGP.shape[0] == NOK_IGP

A_IGP[0,:]=( 0.000000e+00 , 0.000000e+00 , -3.000000e-02 , 2.300000e+00)
A_IGP[1,:]=( 0.000000e+00 , 0.000000e+00 , -3.000000e-02 , 2.150000e+00 )
A_IGP[2,:]=( -4.800000e-04 , 2.400000e-03 , -3.000000e-02 , 2.000000e+00 )
A_IGP[3,:]=( 1.586667e-03 , -1.353333e-02 , -4.200000e-02 , 1.850000e+00 )
A_IGP[4,:]=( 1.512821e-03 , -5.897436e-03 , -5.833333e-02 , 1.500000e+00 )
A_IGP[5,:]=( -9.597381e-05 , 8.490998e-04 , -3.846154e-03 , 1.250000e+00 )
A_IGP[6,:]=( -1.176598e-04 , 9.293226e-05 , -2.553191e-03 , 1.240000e+00 )
A_IGP[7,:]=( 2.040230e-03 , -6.494253e-03 , -5.172414e-03 , 1.230000e+00 )
A_IGP[8,:]=( -1.439394e-03 , 3.712121e-03 , -6.666667e-03 , 1.210000e+00 )
A_IGP[9,:]=( -1.597052e-03 , -1.726044e-02 , -9.090909e-03 , 1.200000e+00 )
A_IGP[10,:]=( 4.920791e-01 , -7.947818e-01 , -9.729730e-02 , 1.100000e+00 )

B_IGP[0,:] = ( 0.0 , 0.0 , 0.0 , 0.7600 )
B_IGP[1,:] = ( 0.0 , 0.0 , 0.0 , 0.7600 )
B_IGP[2,:] = ( 0.0 , 0.0 , 0.0 , 0.7600 )
B_IGP[3,:] = ( 0.0 , 0.0 , 0.0 , 0.7600 )
B_IGP[4,:] = ( 0.0 , 0.0 , 0.0 , 0.7600 )
B_IGP[5,:] = ( 0.0 , 0.0 , 0.0 , 0.7600 )
B_IGP[6,:] = ( 0.0 , 0.0 , 0.0 , 0.7600 )
B_IGP[7,:] = ( 0.0 , 0.0 , 0.0 , 0.7600 )
B_IGP[8,:] = ( 0.0 , 0.0 , 0.0 , 0.7600 )
B_IGP[9,:] = ( 0.0 , 0.0 , 0.0 , 0.7600 )
B_IGP[10,:] = ( 0.0431 , -0.1031 , 0.0 , 0.7600 )

#!c    A_IGP(10,:) = ( -0.0074, 0.0807, -0.3355, 0.8000 )
#    A_IGP(8,:) = ( -0.0027,  0.0293,  0.0, 0.2700 )
#    A_IGP(9,:) = ( -0.0169, 0.0928, 0.1021, 0.4600 )
#    A_IGP(10,:) = ( -0.0200, 0.0798, 0.2702, 0.9000 )

A_IGP[11,:] = (-0.0012,0.0363,-0.2244,0.7000)
A_IGP[12,:] = ( -0.0005, 0.0141, -0.0511, 0.3200 )
A_IGP[13,:] = (  0.0035, 0.0109, -0.0011, 0.2700 )
A_IGP[14,:] = ( -0.0063, 0.0427, 0.1597, 0.4600 )
A_IGP[15,:] = (  0.0212, 0.0051, 0.2552, 0.9000 )
A_IGP[16,:] = ( -0.1109, 0.1320, 0.5294, 1.6000 )
A_IGP[17,:] = (  0.1061, -0.5332, -0.2729, 2.3000 )
A_IGP[18,:] = (  0.2758, -0.2148, -1.0209, 1.6000 )
A_IGP[19,:] = ( -0.0118, 0.6125, -0.6233, 0.6400 )
A_IGP[20,:] = ( -0.2951, 0.5948, -0.0197, 0.4800 )
A_IGP[21,:] = (  0.0550,   -0.0995, 0.1244, 0.7600 )
A_IGP[22,:] = ( -0.0000, 0.0108, 0.0906, 0.8400 )

B_IGP[11:,:] = A_IGP[11:,:]

def create_liquid_bins() -> tuple[np.ndarray, np.ndarray]:
    _massbin = np.zeros(40, dtype=float)
    _massbin_bnd = np.zeros(41, dtype=float)
    c_min = 0.000000000000004188790205
    c_max = 0.0000000654498
    c_maxmass = 0.52359870
    temp1 = c_min
    dbin = (c_max / c_min) ** (0.05)  # 0.1 = 1/10, 0.05 = 1/20
    temp2 = temp1 * dbin
    _massbin_bnd[0] = temp1
    i = 1
    while i <= 20:
        _massbin_bnd[i] = temp2
        _massbin[i - 1] = 0.5 * (temp1 + temp2)  # liquid haze bins
        temp1 = temp2
        temp2 = temp2 * dbin
        i = i + 1
    dbin = (c_maxmass / c_max) ** (0.05)
    temp2 = temp1 * dbin
    i = 21
    while i <= 40:
        _massbin_bnd[i] = temp2
        _massbin[i - 1] = 0.5 * (temp1 + temp2)  # liquid drop bins
        temp1 = temp2
        temp2 = temp2 * dbin
        i = i + 1

    return _massbin, _massbin_bnd


def create_ice_bins() -> tuple[np.ndarray, list[float], list[float]]:
    _massbini = np.zeros(20, dtype=float)
    _massbini_fine = np.zeros(40, dtype=float)
    c_min = 4.18879020478639e-12
    c_max = 1.0e-6
    dbin, dbin_fine = (c_max / c_min) ** (0.25), (c_max / c_min) ** (0.125)
    
    temp1, temp1_fine = c_min, c_min
    temp2, temp2_fine = temp1 * dbin, temp1_fine * dbin_fine
    i = 1
    while i <= 4:
        _massbini[i - 1] = 0.5 * (temp1 + temp2)  # ice deposition bins
        temp1 = temp2
        temp2 = temp2 * dbin
        i = i + 1
    i = 1
    while i <= 8:
        _massbini_fine[i - 1] = 0.5 * (temp1_fine + temp2_fine)  # ice deposition bins
        temp1_fine = temp2_fine
        temp2_fine = temp2_fine * dbin_fine
        i = i + 1
    
    c_min = c_max
    c_max = 1.0e-2
    dbin, dbin_fine = (c_max / c_min) ** (1.0 / 10.0), (c_max / c_min) ** (1.0 / 20.0)
    temp2, temp2_fine = temp1 * dbin, temp1_fine * dbin_fine
    i = 5
    while i <= 14:
        _massbini[i - 1] = 0.5 * (temp1 + temp2)  # ice collection bins
        temp1 = temp2
        temp2 = temp2 * dbin
        i = i + 1
    i = 5
    while i <= 24:
        _massbini_fine[i - 1] = 0.5 * (temp1_fine + temp2_fine)  # ice collection bins
        temp1_fine = temp2_fine
        temp2_fine = temp2_fine * dbin_fine
        i = i + 1
    
    c_min = c_max
    c_max = 1.0e1
    dbin, dbin_fine = (c_max / c_min) ** (1.0 / 6.0), (c_max / c_min) ** (1.0 / 12.0)
    temp2, temp2_fine = temp1 * dbin, temp1_fine * dbin_fine
    i = 15
    while i <= 20:
        _massbini[i - 1] = 0.5 * (temp1 + temp2)  # ice riming bins
        temp1 = temp2
        temp2 = temp2 * dbin
        i = i + 1
    i = 15
    while i <= 26:
        _massbini_fine[i - 1] = 0.5 * (temp1_fine + temp2_fine)  # ice riming bins
        temp1_fine = temp2_fine
        temp2_fine = temp2_fine * dbin_fine
        i = i + 1

    # determine ice diameter bin
    _diameteribin_bnd = []
    _diameteribin = []
    c_min = 4.18879020478639e-12
    c_max = 1.0e-6
    dbin = (c_max / c_min) ** (0.25)
    temp1 = c_min
    temp2 = temp1 * dbin
    _diameteribin_bnd.append((temp1/0.916/3.1416*6.0)**(1.0/3.0)*10000.0)
    i = 1
    while i <= 4:
        _diameteribin_bnd.append((temp2/0.916/3.1416*6.0)**(1.0/3.0)*10000.0)
        _diameteribin.append((0.5*(temp1+temp2)/0.916/3.1416*6.0)**(1.0/3.0)*10000.0)
        temp1 = temp2
        temp2 = temp2 * dbin
        i = i + 1
    i = 1
    
    c_min = c_max
    c_max = 1.0e-2
    dbin = (c_max / c_min) ** (1.0 / 10.0)
    temp2 = temp1 * dbin
    i = 5
    while i <= 14:
        _diameteribin_bnd.append((temp2/0.916/3.1416*6.0)**(1.0/3.0)*10000.0)
        _diameteribin.append((0.5*(temp1+temp2)/0.916/3.1416*6.0)**(1.0/3.0)*10000.0)
        temp1 = temp2
        temp2 = temp2 * dbin
        i = i + 1
    
    c_min = c_max
    c_max = 1.0e1
    dbin = (c_max / c_min) ** (1.0 / 6.0)
    temp2 = temp1 * dbin
    i = 15
    while i <= 20:
        _diameteribin_bnd.append((temp2/0.916/3.1416*6.0)**(1.0/3.0)*10000.0)
        _diameteribin.append((0.5*(temp1+temp2)/0.916/3.1416*6.0)**(1.0/3.0)*10000.0)
        temp1 = temp2
        temp2 = temp2 * dbin
        i = i + 1
    # _diameteribin_bnd = []
    # _diameteribin = []
    # _diameteribin_bnd.append(0.0)
    # _diameteribin_bnd.append(50.0)
    # _diameteribin.append(25.0)
    # i = 1
    # while True:
    #     _diameteribin_bnd.append(_diameteribin_bnd[i] * 1.25)
    #     _diameteribin.append(0.5 * (_diameteribin_bnd[i] + _diameteribin_bnd[i] * 1.25))
    #     if _diameteribin_bnd[i] * 1.25 > 10000.0:
    #         break
    #     i = i + 1

    return _massbini, _massbini_fine, _diameteribin, _diameteribin_bnd


# ->->-> BIN INFORMATION

# maximum number of liquid bins
max_binr = 30
max_bini = 20
max_bini_fine = 40

# define liquid bins
_massbin, _massbin_bnd = create_liquid_bins()
massbin = _massbin[:max_binr]
massbin_bnd = _massbin_bnd[: max_binr + 1]
diameterbin = (_massbin[:max_binr] / (3.1416 / 6.0)) ** (1.0 / 3.0) * 10000.0
diameterbin_bnd = (_massbin_bnd[: max_binr + 1] / (3.1416 / 6.0)) ** (1.0 / 3.0) * 10000.0

# define ice bins
massbini, massbini_fine, _diameteribin, _diameteribin_bnd = create_ice_bins()
max_bin_ice_diameter = len(_diameteribin)
diameteribin = np.array(_diameteribin)
diameteribin_bnd = np.array(_diameteribin_bnd)


# AMPS ice category/shape functions
def Iice_habit(icemass, crymass, aggmass, rimmass) -> IceType:
    if rimmass > 0.1 * icemass:
        if aggmass < 0.1 * icemass:
            if rimmass < crymass:
                return IceType.RIMED_CRYSTAL  # rimed crystals
            else:
                return IceType.GRAUPEL  # graupel
        else:
            if rimmass > aggmass:
                return IceType.GRAUPEL  # graupel
            else:
                return IceType.RIMED_AGGREGATE  # rimed aggregates
    else:
        if aggmass < 0.1 * icemass:
            return IceType.PRISTINE  # pristine crystals
        else:
            return IceType.AGGREGATE  # aggregates


def Iice_shape(a_axis, c_axis, d_axis) -> IceHabit:
    if c_axis > a_axis:
        return IceHabit.COLUMN  # columnar crystals
    else:
        if d_axis > 2.0 / 3.0 * a_axis:
            return IceHabit.DENDRITE  # dendrites
        else:
            return IceHabit.PLATE  # hexagonal plates


def Iice_shapePoly(a_axis, c_axis, d_axis, ag_axis, cg_axis, ex_cry) -> IceHabit:
    if ex_cry < 0.5:
        if c_axis > a_axis:
            return IceHabit.COLUMN  # columnar crystals
        else:
            if d_axis > 2.0 / 3.0 * a_axis:
                return IceHabit.DENDRITE  # dendrites
            else:
                return IceHabit.PLATE  # hexagonal plates
    else:
        if a_axis == 0.0 and c_axis == 0.0:
            return IceHabit.NONE
        elif a_axis == 0.0:
            temp = 1.0
        elif c_axis == 0.0:
            temp = -1.0
        else:
            temp = ag_axis / a_axis - cg_axis / c_axis
        if temp >= 0.5:
            return IceHabit.PLANAR_POLYCRYSTAL  # planar polycrystals
        elif temp <= -0.5:
            return IceHabit.COLUMN_POLYCRYSTAL  # columnar polycrystals
        else:
            return IceHabit.IRREGULAR_POLYCRYSTAL  # irregular polycrystals


ESTBAR = np.exp(
    54.842763 - 6763.22 / AMPS_LIQSUPERSAT_TEMP_RANGE - 4.210*np.log(AMPS_LIQSUPERSAT_TEMP_RANGE) + 
    0.000367 * AMPS_LIQSUPERSAT_TEMP_RANGE + np.tanh(0.0415*(AMPS_LIQSUPERSAT_TEMP_RANGE - 218.8)) * 
    (
        53.878 - 1331.22 / AMPS_LIQSUPERSAT_TEMP_RANGE - 9.44523 * np.log(AMPS_LIQSUPERSAT_TEMP_RANGE) + 
        0.014025*AMPS_LIQSUPERSAT_TEMP_RANGE
    )
)
ESITBAR = np.exp(
    9.550426 - 5723.265 / AMPS_ICESUPERSAT_TEMP_RANGE + 
    3.53068 * np.log(AMPS_ICESUPERSAT_TEMP_RANGE) - 0.00728332 * AMPS_ICESUPERSAT_TEMP_RANGE
)

def amps_liqsupersat(input_pres: np.ndarray, input_temp: np.ndarray, input_qv: np.ndarray):
    # input_pres [bar = 0.1 Pa, F = m a = kg m s-2, Pa = F / A = kg s-2 m-1 = 10 g s-2 cm-1 = 10 bar]
    # input_temp [K]
    # input qv [kg/kg or g/g]
    liq_satpres = np.exp(
        54.842763 - 6763.22 / input_temp - 4.210*np.log(input_temp) + 
        0.000367 * input_temp + np.tanh(0.0415*(input_temp - 218.8)) * 
        (
            53.878 - 1331.22 / input_temp - 9.44523 * np.log(input_temp) + 
            0.014025*input_temp
        )
    )
    liq_supersat = input_pres * input_qv / (R_DV + input_qv) / liq_satpres
    return liq_supersat * 100.0

def amps_icesupersat(input_pres: np.ndarray, input_temp: np.ndarray, input_qv: np.ndarray):
    # input_pres [bar = 0.1 Pa, F = m a = kg m s-2, Pa = F / A = kg s-2 m-1 = 10 g s-2 cm-1 = 10 bar]
    # input_temp [K]
    # input qv [kg/kg or g/g]
    ice_satpres = np.exp(
        9.550426 - 5723.265 / input_temp + 
        3.53068 * np.log(input_temp) - 0.00728332 * input_temp
    )
    ice_supersat = input_pres * input_qv / (R_DV + input_qv) / ice_satpres
    return ice_supersat * 100.0

def amps_est_liqsupersat(temperature: np.ndarray) -> np.ndarray:
    # temperature [K]

    # output: bar = g/s^2/cm
    # phase == 1
    ind = max(0, min(int(temperature) - 162, 148))
    wt = max(min(temperature - float(ind + 162), 1.0), 0.0)
    e_sat = (ESTBAR[ind] * (1.0 - wt) + ESTBAR[ind + 1] * wt) * 10.0
    return e_sat

def amps_est_icesupersat(temperature: np.ndarray) -> np.ndarray:
    # temperature [K]

    # output: bar = g/s^2/cm
    # phase == 2
    ind = max(0, min(int(temperature) - 162, 109))
    wt = max(min(temperature - float(ind + 162), 1.0), 0.0)
    e_sat = (ESITBAR[ind] * (1.0 - wt) + ESITBAR[ind + 1] * wt) * 10.0
    return e_sat


def cal_vapor_pressure(qv, pressure):
    # qv [kg/kg or g/g]
    # pressure [bar = 0.1 Pa, F = m a = kg m s-2, Pa = F / A = kg s-2 m-1 = 10 g s-2 cm-1 = 10 bar]
    vapor_pressure = pressure * qv / (R_DV + qv)
    return vapor_pressure


def cal_vapor_mixing_ratio(vapor_pressure, pressure):
    # vapor_pressure [bar]
    # pressure [bar = 0.1 Pa, F = m a = kg m s-2, Pa = F / A = kg s-2 m-1 = 10 g s-2 cm-1 = 10 bar]
    qv = R_DV * vapor_pressure / (pressure - vapor_pressure)
    return qv


def cal_halfmaxdim_ip(is_mod: IceMode, semi_aip: np.ndarray, semi_cip: np.ndarray) -> np.ndarray:
    if is_mod == IceMode.CYLINDER:
      # assume the cylinder volume
      xlen = np.sqrt(semi_aip * semi_aip + semi_cip * semi_cip)
    elif is_mod == IceMode.SPHEROID:
      # assume the spheroidal volume
      if semi_aip > semi_cip:
        xlen = semi_aip
      else:
        xlen = semi_cip
    return xlen


def cal_inherent_growth_ratio(temperature: float, dt: float, do_dt_adjustment: bool = True) -> float:
    # temperature [K]
    # dt [s]
    temperature = min(0.0, temperature - 273.16)
    
    def _get_cmod_inh(input_temperature: float, input_dt: float):
        #
        # get a coefficient to modifiy gamma to get better length growth.
        #
        a1 = -8.727618e-6
        a2 = 4.806144e-4
        a3 = -9.762830e-3
        a4 = 9.723944e-2
        a5 = 5.013389e-1
        
        if input_temperature > -20.0:
            y = max(0.5,min(1.0, a1 * input_dt**4 + a2 * input_dt**3 + a3 * input_dt**2 + a4 * input_dt + a5))
        else:
            y = 0.5

        return y

    gamma = np.zeros(2, dtype=float)
    if temperature < X_IGP[0]:
        #       write(*,*) "inherent_growth_ratio > Warning! The temperature is &
        #            colder than -30C. Inherent ratio is set to 1."
        #       out=1.0
        #       return
        gamma[1] = (
            (
                A_IGP[0, 0] * (temperature - X_IGP[0] )**3
            ) + (
                A_IGP[0, 1]*( temperature - X_IGP[0] )**2
            ) + (
                A_IGP[0, 2]*( temperature - X_IGP[0] ) + A_IGP[0, 3]
            )
        )
        gamma[0] = (
            (
                B_IGP[0, 0] * ( temperature - X_IGP[0] )**3
            ) + (
                B_IGP[0, 1]*( temperature - X_IGP[0] )**2
            ) + (
                B_IGP[0, 2]*( temperature - X_IGP[0] ) + B_IGP[0, 3]
            )
        )
        return gamma**_get_cmod_inh(temperature, dt) if do_dt_adjustment else gamma
    elif temperature >= X_IGP[NOK_IGP - 1]:
        gamma[1] = (
            (
                A_IGP[NOK_IGP - 1, 0]*( temperature - X_IGP[NOK_IGP - 1] )**3
            ) + (
                A_IGP[NOK_IGP - 1, 1]*( temperature - X_IGP[NOK_IGP - 1])**2
            ) + (
                A_IGP[NOK_IGP - 1, 2]*( temperature - X_IGP[NOK_IGP - 1]) + A_IGP[NOK_IGP - 1, 3]
            )
        )
        gamma[0] = (
            (
                B_IGP[NOK_IGP - 1, 0]*( temperature - X_IGP[NOK_IGP - 1])**3
            ) + (
                B_IGP[NOK_IGP - 1, 1]*( temperature - X_IGP[NOK_IGP - 1])**2
            ) + (
                B_IGP[NOK_IGP - 1, 2]*( temperature - X_IGP[NOK_IGP - 1]) + B_IGP[NOK_IGP - 1, 3]
            )
        )
        return gamma**_get_cmod_inh(temperature, dt) if do_dt_adjustment else gamma

    for i in range(NOK_IGP - 1):
        if X_IGP[i] <= temperature and temperature < X_IGP[i+1]:
            gamma[1] = (
                (
                    A_IGP[i, 0]*( temperature - X_IGP[i] )**3
                ) + (
                    A_IGP[i, 1]*( temperature - X_IGP[i] )**2
                ) + (
                    A_IGP[i, 2]*( temperature - X_IGP[i] ) + A_IGP[i,3]
                )
            )
            gamma[0] = (
                (
                    B_IGP[i, 0]*( temperature - X_IGP[i] )**3
                ) + (
                    B_IGP[i, 1]*( temperature - X_IGP[i] )**2
                ) + (
                    B_IGP[i, 2]*( temperature - X_IGP[i] ) + B_IGP[i,3]
                )
            )
            return gamma**_get_cmod_inh(temperature, dt) if do_dt_adjustment else gamma
    raise ArithmeticError


def cal_capacitance(clen: float, alen: float) -> float:
    # clen [cm]
    # alen [cm]
    phi_ic = clen / alen
    if phi_ic < 1.0:
        # --- in case of oblate spheroids ---
        d = math.sqrt( max(alen**2 - clen**2, 0.0) )
        eps = math.sqrt( 1.0 - phi_ic**2)
        capacitance = d / math.asin(eps)
    elif phi_ic > 1.0:
        # --- in case of prolate spheroids ---
        d = math.sqrt( max(clen**2 - alen**2, 0.0) )
        eps = math.sqrt( 1.0 - 1.0 / phi_ic**2)
        capacitance = d / math.log((1.0 + eps) * phi_ic )
        # capacitance = ( 0.708 + 0.615 * (phi_ic**(-0.76)))*c_len
    else:
        # --- in case of sphere ---
        capacitance = alen
    return capacitance


def cal_diffusivity(temperature: float, pressure: float) -> float:
    # temperature [K]
    # pressure [bar = 0.1 Pa, F = m a = kg m s-2, Pa = F / A = kg s-2 m-1 = 10 g s-2 cm-1 = 10 bar]
    diffusivity = 0.211 * ( ( temperature / T_0 )**1.94) * (P_0 / pressure)
    return diffusivity


def cal_deposition_coef(temperature: float, pressure: float, clen: float, alen: float) -> list[float, float]:
    # temperature [K]
    # pressure [bar = 0.1 Pa, F = m a = kg m s-2, Pa = F / A = kg s-2 m-1 = 10 g s-2 cm-1 = 10 bar]
    # clen [cm]
    # alen [cm]
    coef = [0.0, 0.0]
    fv, fkn = 1.0, 1.0
    coef[0] =  4.0 * math.pi * cal_diffusivity(temperature, pressure) * cal_capacitance(clen, alen) * MR * fv * fkn
    coef[1] = -coef[0]
    return coef


def cal_vapor_deposition_mass_rate(temperature: float, pressure: float, e_sat: float, supersaturation: float, clen: float, alen: float, dt: float):
    # temperature [K]
    # pressure [bar = 0.1 Pa, F = m a = kg m s-2, Pa = F / A = kg s-2 m-1 = 10 g s-2 cm-1 = 10 bar]
    # clen [cm]
    # alen [cm]
    coef = cal_deposition_coef(temperature, pressure, clen, alen)
    # assume that the particle surface temüperature is the same as the ambient temperature
    # d_mean_mass = (coef[0] * e_sat_n_2 / temperature * (s_v_n_2 + 1.0) + coef[1] * get_sat_vapor_pres_lk(2,tmp,ag%estbar,ag%esitbar) / tmp)
    d_mean_mass = (coef[0] * e_sat / temperature * (supersaturation + 1.0) + coef[1] * e_sat / temperature)

    i_tmp_le0 = 0.5 * (1.0 + np.sign(273.16 - temperature))
    den_v_inf = (supersaturation + 1.0) * e_sat / (R_V * temperature)
    den_sv_sfc = e_sat / (R_V * temperature) # assume surface temperature is equal to ambient temperature
    # ex_vden = supersaturation * e_sat / (R_V * temperature)
    ex_vden = den_v_inf - den_sv_sfc
    gamma = cal_inherent_growth_ratio(temperature, dt=dt)
    deposition_density = i_tmp_le0 * (
        max(0.91 * math.exp( -3.0 * max(ex_vden * 1.0e+6 - 0.05, 0.0) / gamma[0]), 1.0e-1) + (
            1.0 - i_tmp_le0
        ) * 0.91
    )
    d_volume = d_mean_mass / deposition_density
    ice_volume = 4.0 / 3.0 * math.pi * clen * alen**2
    d_alen = alen * d_volume / ice_volume / (gamma[0] + 2.0)
    d_clen = clen * d_volume / ice_volume * gamma[0] / (gamma[0] + 2.0)
    return d_mean_mass, d_clen, d_alen


def cal_zhang_vapor_deposition_mass_rate(temperature: float, pressure: float, e_sat: float, supersaturation: float, clen: float, alen: float, dt: float):
    zhy_b = 2.045
    zhy_a = 0.0487 # 1000.0 * 0.0487 * 0.01**zhy_b
    zhy_a_dens = 0.0487
    zhy_dens_max = 0.7962
    # temperature [K]
    # pressure [bar = 0.1 Pa, F = m a = kg m s-2, Pa = F / A = kg s-2 m-1 = 10 g s-2 cm-1 = 10 bar]
    # clen [cm]
    # alen [cm]
    xlen = 2.0 * cal_halfmaxdim_ip(IceMode.CYLINDER, alen, clen)
    ice_density = 0.001 * 6.0 * zhy_a_dens * (xlen * 0.01)**(zhy_b - 3.0) / math.pi / (clen / alen)**2
    if ice_density > zhy_dens_max:
        print(xlen, clen / alen, ice_density)
        # h_factor = 2.0 * math.pi * zhy_dens_max * xlen * (alen + gamma[0] * clen / alen)
        # fall back to the original calculation
        return cal_vapor_deposition_mass_rate(temperature, pressure, e_sat, supersaturation, clen, alen, dt)
    else:
        coef = cal_deposition_coef(temperature, pressure, clen, alen)
        # assume that the particle surface temüperature is the same as the ambient temperature
        # d_mean_mass = (coef[0] * e_sat_n_2 / temperature * (s_v_n_2 + 1.0) + coef[1] * get_sat_vapor_pres_lk(2,tmp,ag%estbar,ag%esitbar) / tmp)
        d_mean_mass = (coef[0] * e_sat / temperature * (supersaturation + 1.0) + coef[1] * e_sat / temperature)
        gamma = cal_inherent_growth_ratio(temperature, dt=dt)

        h_factor = 10.0 * 2.0 * zhy_a * (xlen * 0.01)**zhy_b * alen / clen * (
            (
                # 2.0 * zhy_b / (xlen * 0.01)**2 * (alen**2 / clen * 0.01 + gamma[0])
                2.0 * zhy_b / (xlen * 0.01)**2 * alen**2 / clen * 0.01 * (gamma[0] * (clen / alen)**2 + 1.0)
            ) - (
                (gamma[0] - 1.0) / (clen * 0.01)
            )
        )
        d_alen = d_mean_mass / h_factor
        d_clen = gamma[0] * clen / alen * d_alen
        return d_mean_mass, d_clen, d_alen


"""
r_m = sqrt(g%MS(i,n)%semi_a**2+g%MS(i,n)%semi_c**2)
function get_fkn(th_var,phase,r0) result(fkn)
    ! NOTE:
    ! this should be the same as get_mod_diffusivity.
    !
    type (Thermo_Var)  :: th_var
    real(PS), intent(in)   :: r0
    integer :: phase
    real(PS) :: beta
    ! deposition coefficient, thickness of a bc
    real(PS),parameter :: beta_w=0.036
    real(PS),parameter :: beta_i1=0.5,beta_i2=0.006
    real(PS),parameter :: delta=1.0e-5    
    real(PS) :: fkn

    if(phase==1) then
       beta=beta_w
    else
       beta=beta_i1
    end if
    ! +++ calculate kinetic effect +++
    fkn = r0/(r0+delta)+(th_var%D_v/beta/r0)*&
         sqrt(2.0_PS*PI/R_v/th_var%T)
    fkn = 1.0_PS/fkn
  end function get_fkn
"""