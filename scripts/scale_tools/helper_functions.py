import math
import sys
from typing import TypeAlias

import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import netCDF4 as nc4
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
from scale_tools import amps_library as amps

try:
    import cupy as xp
except ImportError:
    import numpy as xp


NDArray: TypeAlias = np.ndarray | xp.ndarray


def as_numpy(array: NDArray) -> np.ndarray:
    if isinstance(array, np.ndarray):
        return np.array(array, copy=True)
    else:
        import cupy as cp

        return cp.asnumpy(array)

SCALE_DATA_NAME = (
    "DENS",
    "PRES",
    "U",
    "V",
    "W",
    "T",
    "PT",
    "P",
    "RH",
    "RHI",
    "QV",
    "QHYD",
    "QICE",
    "QLIQ",
    "TKE_SMG",
    "NU",
    "Ri",
    "Pr"
    "PREC",
    "SFLX_SW_dn",
    "SFLX_LW_dn",
    "RHOH_MP",
    "DENS_t_MP",
    "MOMZ_t_MP",
    "RHOU_t_MP",
    "RHOV_t_MP",
    "QV_t_MP",
    "PREC",
    "SFLX_SW_dn",
    "SFLX_LW_dn",
)

"""
 RHOH_MP(k,i,j) = RHOE_t(k,i,j) &
                  - ( CPtot_t(k,i,j) + log( PRES(k,i,j) / PRE00 ) * ( CVtot(k,i,j) / CPtot(k,i,j) * CPtot_t(k,i,j) - CVtot_t(k,i,j) ) ) &
                  * DENS(k,i,j) * TEMP(k,i,j)
"""
scale_data2d = (
    "PREC",
    "SFLX_SW_dn",
    "SFLX_LW_dn",
)

AMPS_DATA_NAME = (
    "con_amass11",
    "con_amass12",
    "ae_amass11",
    "ae_amass12",
    "ampsl_act",
    "ampscl_act",
    "ampsci_col",
    "ampsci_rim",
    "con_lmass",
    "con_imass",
    "vol_imass",
    "dmax_imass",
    "ice_imass",
    "cry_imass",
    "agg_imass",
    "rim_imass",
    "a_axis",
    "c_axis",
    "ampsci_ddf",
    "collision_bin",
    "collision_conc_bin",
    "freezing_bin",
    "freezing_conc_bin",
    "vapor_bin",
    "eva_bin",
)


def quickSorti(inputArray, start, end):
    if start >= end:
        return

    loop_hdl = True
    # outer_loop = 0
    temp = end - start + 1
    # while (loop_hdl):
    #    temp = temp/2
    #    temp = int(temp)
    #    outer_loop = outer_loop + 1
    #    if (temp < 1):
    #        loop_hdl = False
    outer_loop = int(temp / 2) + 1

    pivots = []
    pivots.append(start)
    pivots.append(end)
    k = 1
    segmentNumber = 1
    while k <= outer_loop:
        kk = 1
        pivot_array = []
        temp1 = 0
        kk_pivot = 1
        while kk <= segmentNumber:
            pivot_index = quickPartitioni(inputArray, pivots[kk_pivot - 1], pivots[kk_pivot])
            if pivot_index - 1 > pivots[kk_pivot - 1]:
                pivot_array.append(pivots[kk_pivot - 1])
                pivot_array.append(pivot_index - 1)
                temp1 = temp1 + 1
            if pivot_index + 1 < pivots[kk_pivot]:
                pivot_array.append(pivot_index + 1)
                pivot_array.append(pivots[kk_pivot])
                temp1 = temp1 + 1
            kk = kk + 1
            kk_pivot = kk_pivot + 2

        segmentNumber = temp1

        if temp1 == 0:
            break

        pivots = []
        for temp in pivot_array:
            pivots.append(temp)
        k = k + 1


def quickPartitioni(inputArray, start, end):
    if start >= end:
        return start

    k = start
    pivot = inputArray[end]
    i = start
    while k < end:
        if inputArray[k] < pivot:
            temp = inputArray[k]
            inputArray[k] = inputArray[i]
            inputArray[i] = temp
            i = i + 1
        k = k + 1
    inputArray[end] = inputArray[i]
    inputArray[i] = pivot
    return i


def read_scale_coordinates(
    file_name: str,
    process_number: int,
    x_process_number: int,
    y_process_number: int,
    print_debug: bool = False,
) -> tuple[
    NDArray,
    NDArray,
    NDArray,
    NDArray,
    NDArray,
    NDArray,
    NDArray,
    NDArray,
    NDArray,
    NDArray,
    NDArray,
    NDArray,
]:

    assert process_number == x_process_number * y_process_number

    f = nc4.Dataset(file_name+'.pe000000.nc', "r")
    if f.file_format == "NETCDF4":
        # print(f)
        ### READ DIMENSION VARIABLES
        # time
        time = f.variables["time"][:]
        # z
        z = f.variables["z"][:]
        # fz
        fz = f.variables["FZ"][:]
        # fxg
        fxg = f.variables["FXG"][:]
        # fyg
        fyg = f.variables["FYG"][:]
    else:
        print("ERROR -- NETCDF VERSION NOT SUPPORTED")
        sys.exit(0)

    f.close()

    for n in range(x_process_number):
        ### OPEN NETCDF DATA
        # create a file object to handle the data inside the file
        if n < 10:
            f = nc4.Dataset(file_name+'.pe00000'+str(n)+'.nc', "r")
        else:
            f = nc4.Dataset(file_name+'.pe0000'+str(n)+'.nc', "r")
    
        if f.file_format == "NETCDF4":
            ### READ DIMENSION VARIABLES
            # x
            if n == 0:
                x = f.variables["x"][:]
            else:
                x = xp.concatenate((x, f.variables["x"][:]))

        else:
            print("ERROR -- NETCDF VERSION NOT SUPPORTED")
            sys.exit(0)

        f.close()

    for n in range(process_number):
        ### OPEN NETCDF DATA
        # create a file object to handle the data inside the file
        if n % x_process_number == 0:
            if n < 10:
                f = nc4.Dataset(file_name+'.pe00000'+str(n)+'.nc', "r")
            else:
                f = nc4.Dataset(file_name+'.pe0000'+str(n)+'.nc', "r")
        
            if f.file_format == "NETCDF4":
                ### READ DIMENSION VARIABLES
                # y
                if n == 0:
                    y = f.variables["y"][:]
                else:
                    y = xp.concatenate((y, f.variables["y"][:]))

            else:
                print("ERROR -- NETCDF VERSION NOT SUPPORTED")
                sys.exit(0)

            f.close()
    
    fz_3d = xp.repeat(xp.expand_dims(fz, axis=-1), repeats=y.shape[0], axis=-1)
    fz_3d = xp.repeat(xp.expand_dims(fz_3d, axis=-1), repeats=x.shape[0], axis=-1)

    dz = fz[3 : fz.shape[0] - 2] - fz[2 : fz.shape[0] - 3]
    assert dz.shape[0] == z.shape[0]
    dz_3d = xp.repeat(xp.expand_dims(dz, axis=-1), repeats=y.shape[0], axis=-1)
    dz_3d = xp.repeat(xp.expand_dims(dz_3d, axis=-1), repeats=x.shape[0], axis=-1)

    dx = fxg[3 : fxg.shape[0] - 2] - fxg[2 : fxg.shape[0] - 3]
    dy = fyg[3 : fyg.shape[0] - 2] - fyg[2 : fyg.shape[0] - 3]
    assert dx.shape[0] == x.shape[0]
    assert dy.shape[0] == y.shape[0]
    dx_3d = xp.repeat(xp.expand_dims(dx, axis=0), repeats=y.shape[0], axis=0)
    dx_3d = xp.repeat(xp.expand_dims(dx_3d, axis=0), repeats=z.shape[0], axis=0)
    dy_3d = xp.repeat(xp.expand_dims(dy, axis=-1), repeats=x.shape[0], axis=-1)
    dy_3d = xp.repeat(xp.expand_dims(dy_3d, axis=0), repeats=z.shape[0], axis=0)
    assert dx_3d.shape == dz_3d.shape
    assert dy_3d.shape == dz_3d.shape
    grid_volume = dz_3d * dy_3d *dx_3d

    y_in_yzplane, z_in_yzplane = xp.meshgrid(y / 1000.0, z / 1000.0)
    x_in_xyplane, y_in_xyplane = xp.meshgrid(x / 1000.0, y / 1000.0)

    if print_debug:
        for i in range(x.shape[0]):
            print("X coordinate: ", i, x[i])
        print()
        for i in range(y.shape[0]):
            print("Y coordinate: ", i, y[i])

    return time, x, y, z, fz, dz, fz_3d, dz_3d, grid_volume, y_in_yzplane, z_in_yzplane, x_in_xyplane, y_in_xyplane


def read_scale_data(
    f: list[nc4.Dataset],
    scale_data_dict: dict,
    amps_data_dict: dict,
    *output_data_name: str,
    process_number: int,
    x_process_number: int,
    y_process_number: int,
    z_grid_number: int,
    y_grid_number: int,
    x_grid_number: int,
    time_step: int,
    ibin_fine: bool = False,
) -> None:

    if ibin_fine:
        max_bini = amps.max_bini_fine
    else:
        max_bini = amps.max_bini

    assert y_grid_number % y_process_number == 0, f" number of y processes {y_grid_number} must be divided by total y grid number {y_process_number}"
    assert x_grid_number % x_process_number == 0, f" number of x processes {x_grid_number} must be divided by total x grid number {x_process_number}"
    y_local_grid_number = int(y_grid_number / y_process_number)
    x_local_grid_number = int(x_grid_number / x_process_number)
    assert len(f) == process_number
    
    if len(scale_data_dict) == 0:
        for data_name in output_data_name:
            assert data_name in SCALE_DATA_NAME or data_name in AMPS_DATA_NAME, f"{data_name} not in SCALE_DATA_NAME or AMPS_DATA_NAME"
            if data_name in SCALE_DATA_NAME:
                if data_name in scale_data2d:
                    scale_data_dict[data_name] = xp.zeros((y_grid_number, x_grid_number), dtype=float)
                else:
                    scale_data_dict[data_name] = xp.zeros((z_grid_number, y_grid_number, x_grid_number), dtype=float)
    if len(amps_data_dict) == 0:
        for data_name in output_data_name:
            assert data_name in SCALE_DATA_NAME or data_name in AMPS_DATA_NAME, f"{data_name} not in SCALE_DATA_NAME or AMPS_DATA_NAME"
            if data_name in AMPS_DATA_NAME:
                if 'lmass' in data_name:
                    amps_data_dict[data_name] = xp.zeros((amps.max_binr, z_grid_number, y_grid_number, x_grid_number), dtype=float)
                elif ('imass' in data_name) or ('bin' in data_name) or ('axis' in data_name):
                    amps_data_dict[data_name] = xp.zeros((max_bini, z_grid_number, y_grid_number, x_grid_number), dtype=float)
                else:
                    amps_data_dict[data_name] = xp.zeros((z_grid_number, y_grid_number, x_grid_number), dtype=float)

    assert process_number == x_process_number * y_process_number
    for n in range(process_number):
        ### OPEN NETCDF DATA
        # create a file object to handle the data inside the file
        # if n < 10:
        #     f = nc4.Dataset(file_name+'.pe00000'+str(n)+'.nc', "r")
        # else:
        #     f = nc4.Dataset(file_name+'.pe0000'+str(n)+'.nc', "r")
        i = n % x_process_number
        j = int(n / x_process_number)
        for data_name in output_data_name:
            if data_name in SCALE_DATA_NAME:
                if data_name != "QICE":
                    if data_name in scale_data2d:
                        scale_data_dict[data_name][j*y_local_grid_number:(j+1)*y_local_grid_number, i*x_local_grid_number:(i+1)*x_local_grid_number] = f[n].variables[data_name][time_step, :, :]
                    else:
                        scale_data_dict[data_name][:, j*y_local_grid_number:(j+1)*y_local_grid_number, i*x_local_grid_number:(i+1)*x_local_grid_number] = f[n].variables[data_name][time_step, :, :, :]
            elif data_name in AMPS_DATA_NAME:
                if 'lmass' in data_name:
                    for bin in range(amps.max_binr):
                        variable_name = data_name + str(bin + 1)
                        amps_data_dict[data_name][bin, :, j*y_local_grid_number:(j+1)*y_local_grid_number, i*x_local_grid_number:(i+1)*x_local_grid_number] = f[n].variables[variable_name][time_step, :, :, :]
                elif 'imass' in data_name or 'axis' in data_name:
                    if "dmax" not in data_name:
                        for bin in range(max_bini):
                            variable_name = data_name + str(bin + 1)
                            amps_data_dict[data_name][bin, :, j*y_local_grid_number:(j+1)*y_local_grid_number, i*x_local_grid_number:(i+1)*x_local_grid_number] = f[n].variables[variable_name][time_step, :, :, :]
                elif 'bin' in data_name:
                    for bin in range(max_bini):
                        variable_name = data_name + str(bin + 41)
                        amps_data_dict[data_name][bin, :, j*y_local_grid_number:(j+1)*y_local_grid_number, i*x_local_grid_number:(i+1)*x_local_grid_number] = f[n].variables[variable_name][time_step, :, :, :]
                else:
                    amps_data_dict[data_name][:, j*y_local_grid_number:(j+1)*y_local_grid_number, i*x_local_grid_number:(i+1)*x_local_grid_number] = f[n].variables[data_name][time_step, :, :, :]

    if "QICE" in output_data_name:
        assert "QLIQ" in output_data_name and "QHYD" in output_data_name, "QLIQ and QHYD must be present to compute QICE"
        scale_data_dict["QICE"] = scale_data_dict["QHYD"] - scale_data_dict["QLIQ"]

    if "dmax_imass" in output_data_name:
        assert "vol_imass" in output_data_name, "vol_imass must be present to compute dmax_imass"
        # a_axis = xp.zeros((max_bini, z_grid_number, y_grid_number, x_grid_number), dtype=float)
        # c_axis = xp.zeros((max_bini, z_grid_number, y_grid_number, x_grid_number), dtype=float)
        # for n in range(process_number):
        #     i = n % x_process_number
        #     j = int(n / x_process_number)
        #     for bin in range(max_bini):
        #         variable_name = "a_axis" + str(bin + 1)
        #         a_axis[bin, :, j*y_local_grid_number:(j+1)*y_local_grid_number, i*x_local_grid_number:(i+1)*x_local_grid_number] = f[n].variables[variable_name][time_step, :, :, :]
        #         variable_name = "c_axis" + str(bin + 1)
        #         c_axis[bin, :, j*y_local_grid_number:(j+1)*y_local_grid_number, i*x_local_grid_number:(i+1)*x_local_grid_number] = f[n].variables[variable_name][time_step, :, :, :]
        # calculate maximum dimension
        # TODO, this is only an approximation
        # for bin in range(max_bini):
        #     mask = ((amps_data_dict[con_name][bin] > 0.0) & (a_axis[bin] > 0.0))
        #     mask1 = (mask & (c_axis[bin] / a_axis[bin] > 1.0))
        #     mask2 = (mask & (a_axis[bin] / a_axis[bin] <= 1.0))
        #     amps_data_dict["dmax_imass"][bin] = xp.where(mask1, (amps_data_dict[vol_name][bin] / amps_data_dict[con_name][bin] * 6.0 / math.pi) ** (1.0 / 3.0) * 10000.0, 0.0)
        #     amps_data_dict["dmax_imass"][bin] = xp.where(mask1, (amps_data_dict[vol_name][bin] / amps_data_dict[con_name][bin] * 6.0 / math.pi) ** (1.0 / 3.0) * 10000.0, amps_data_dict["dmax_imass"][bin])
        #                if (ice_type == 4) then
        #                   if (alpha_im > 1.0E0) then
        #                      csm = ((vcs/(4.0E0/3.0E0*pi))**(1.0E0/3.0E0))
        #                      asm = csm/alpha_im
        #                      local_Dmax = 2.0E0*csm*10000.0E0
        #                   else
        #                      asm = ((vcs/(4.0E0/3.0E0*pi))**(1.0E0/3.0E0))
        #                      csm = asm*alpha_im
        #                      local_Dmax = 2.0E0*asm*10000.0E0
        #                   endif
        #                else
        #                   asm = ((vcs/(4.0E0/3.0E0*pi))**(1.0/3.0))/sqrt(1.0E0 + alpha_im**2)
        #                   csm = asm*alpha_im
        #                   local_Dmax = 2.0E0*asm*sqrt(1.0E0 + alpha_im**2)*10000.0E0
        #                endif
        for bin in range(max_bini):
            vol_name = "vol_imass"
            con_name = "con_imass"
            amps_data_dict["dmax_imass"][bin] = xp.where(amps_data_dict[con_name][bin] > 0.0, (amps_data_dict[vol_name][bin] / amps_data_dict[con_name][bin] * 6.0 / math.pi) ** (1.0 / 3.0) * 10000.0, 0.0)
            # amps_data_dict["dmax_imass"][bin] = (amps_data_dict[vol_name][bin] / amps_data_dict[con_name][bin] * 6.0 / math.pi) ** (1.0 / 3.0) * 10000.0
            # print("debug: ", bin, amps_data_dict["dmax_imass"][bin].max(), amps_data_dict[vol_name][bin].max(), amps_data_dict[con_name][bin].max())

    return



def plot_qice2_qliq_2d(
    data: NDArray,
    qliq: NDArray,
    w: NDArray,
    y2d: NDArray,
    z2d: NDArray,
    y_max: int,
    x_section: int,
    step: int,
) -> None:
    bluemap = plt.get_cmap("Blues")
    redmap = plt.get_cmap("Reds")

    # contour plot function
    def fmt(x, pos):
        a, b = "{:.2e}".format(x).split("e")
        b = int(b)
        return r"${} \times 10^{{{}}}$".format(a, b)

    plt.close()
    fig, axs = plt.subplots(ncols=2, figsize=(18, 9))
    fig.subplots_adjust(wspace=0.2)

    qliq_max = qliq[:, :, x_section].max() + 1.0e-14
    qliq_boundaries = xp.linspace(0, qliq_max, 100)
    qliq_tboundaries = [0, 0.25 * qliq_max, 0.5 * qliq_max, 0.75 * qliq_max, qliq_max]
    qliq_norm = colors.BoundaryNorm(qliq_boundaries, bluemap.N, clip=True)

    data_max = data[:, :, x_section].max() + 1.0e-14
    data_boundaries = xp.linspace(0, data_max, 100)
    data_tboundaries = [0, 0.25 * data_max, 0.5 * data_max, 0.75 * data_max, data_max]
    data_norm = colors.BoundaryNorm(data_boundaries, redmap.N, clip=True)

    # cboundaries = xp.linspace(-1,1,11)
    w_min = w[:, :, x_section].min() - 1.0e-14
    w_max = w[:, :, x_section].max() + 1.0e-14
    cboundaries = [
        w_min,
        0.75 * w_min,
        0.5 * w_min,
        0.25 * w_min,
        0,
        0.25 * data_max,
        0.5 * data_max,
        0.75 * data_max,
        data_max,
    ]

    cp1 = axs[0].contourf(
        y2d, z2d, qliq[:, :, x_section], cmap=bluemap, levels=qliq_boundaries, norm=qliq_norm
    )
    cp2 = axs[1].contourf(
        y2d, z2d, data[:, :, x_section], cmap=redmap, levels=data_boundaries, norm=data_norm
    )
    axs[0].contour(y2d, z2d, w[:, :, x_section], colors="black", levels=cboundaries)
    # axs[1].contour(y,z,ww,colors='black',levels=cboundaries)

    fontsize = 18

    divider1 = make_axes_locatable(axs[0])
    cax1 = divider1.append_axes("right", size="5%", pad=0.1)
    cb1 = plt.colorbar(cp1, ticks=qliq_tboundaries, cax=cax1, format=ticker.FuncFormatter(fmt))
    divider2 = make_axes_locatable(axs[1])
    cax2 = divider2.append_axes("right", size="5%", pad=0.1)
    cb2 = plt.colorbar(cp2, ticks=data_tboundaries, cax=cax2, format=ticker.FuncFormatter(fmt))
    # cb1 = plt.colorbar(cp1,format=ticker.FuncFormatter(fmt),ticks=nice_tboundaries)
    cb1.ax.tick_params(labelsize=fontsize)
    cb2.ax.tick_params(labelsize=fontsize)

    axs[0].set_xlim(0, y_max)
    axs[0].set_ylim(0, 1)
    axs[0].set_xticks([0, 1, 2, 3, 4])
    axs[0].set_yticks([0, 0.25, 0.5, 0.75, 1])
    axs[0].set_xlabel("y (km)", fontsize=fontsize)
    axs[0].set_ylabel("z (km)", fontsize=fontsize)
    axs[0].tick_params(axis="both", which="major", labelsize=fontsize)
    axs[0].set_title("Liquid water content (g kg$^{-3}$)", fontsize=fontsize)

    axs[1].set_xlim(0, y_max)
    axs[1].set_ylim(0, 1)
    axs[1].set_xticks([0, 1, 2, 3, 4])
    axs[1].set_yticks([0, 0.25, 0.5, 0.75, 1])
    axs[1].set_xlabel("y (km)", fontsize=fontsize)
    # axs[1].set_ylabel("z (km)",fontsize=fontsize)
    axs[1].axes.yaxis.set_ticklabels([])
    axs[1].tick_params(axis="both", which="major", labelsize=fontsize)
    axs[1].set_title("Ice water content (g kg$^{-3}$)", fontsize=fontsize)

    # axs[0].set_aspect(1.0/axs[0].get_data_ratio(),adjustable='box')
    # axs[1].set_aspect(1.0/axs[1].get_data_ratio(),adjustable='box')
    plt.savefig("figure_qliq_qice2d_" + str(step) + ".png", format="png", dpi=500)


def plot2d(
    data: NDArray,
    w: NDArray,
    q: NDArray,
    y2d: NDArray,
    z2d: NDArray,
    xx2d: NDArray,
    yy2d: NDArray,
    title: str,
    unit: str,
    x_max: int,
    y_max: int,
    x_section: int,
    z_section: int,
    step: int,
    is_plus_minus_data: bool = False,
    is_plot_from_zero: bool = True,
) -> None:
    bluemap = plt.get_cmap("Blues")
    redmap = plt.get_cmap("Reds")

    # contour plot function
    def fmt(x, pos):
        a, b = "{:.2e}".format(x).split("e")
        b = int(b)
        return r"${} \times 10^{{{}}}$".format(a, b)

    plt.close()
    fig, axs = plt.subplots(ncols=2, figsize=(18, 9))
    fig.subplots_adjust(wspace=0.55)

    # data_path = xp.sum(data, axis=0)
    data_path = data[z_section]

    data_max = data[:, :, x_section].max() + 1.0e-14
    data_min = data[:, :, x_section].min() - 1.0e-14
    if is_plus_minus_data:
        assert data_max * data_min < 0.0
        if xp.abs(data_max) > xp.abs(data_min):
            data_min = -data_max
        else:
            data_max = -data_min
        data_boundaries = xp.linspace(data_min, data_max, 100)
        data_tboundaries = [
            data_min,
            0.75 * data_min,
            0.5 * data_min,
            0.25 * data_min,
            0.25 * data_max,
            0.5 * data_max,
            0.75 * data_max,
            data_max,
        ]
    else:
        if is_plot_from_zero:
            if data_max > 1.0e-13:
                data_boundaries = xp.linspace(0.0, data_max, 100)
                data_tboundaries = [0, 0.25 * data_max, 0.5 * data_max, 0.75 * data_max, data_max]
            else:
                data_boundaries = xp.linspace(data_min, 0.0, 100)
                data_tboundaries = [data_min, 0.75 * data_min, 0.5 * data_min, 0.25 * data_min, 0]
        else:
            data_boundaries = xp.linspace(data_min, data_max, 100)
            data_tboundaries = xp.linspace(data_min, data_max, 5)
    data_norm = colors.BoundaryNorm(data_boundaries, redmap.N, clip=True)

    data_path_max = data_path.max() + 1.0e-14
    data_path_min = data_path.min() - 1.0e-14
    if is_plus_minus_data:
        assert data_path_max * data_path_min < 0.0
        if xp.abs(data_path_max) > xp.abs(data_path_min):
            data_path_min = -data_path_max
        else:
            data_path_max = -data_path_min
        data_path_boundaries = xp.linspace(data_path_min, data_path_max, 100)
        data_path_tboundaries = [
            data_path_min,
            0.75 * data_path_min,
            0.5 * data_path_min,
            0.25 * data_path_min,
            0.25 * data_path_max,
            0.5 * data_path_max,
            0.75 * data_path_max,
            data_path_max,
        ]
    else:
        if is_plot_from_zero:
            if data_path_max > 1.0e-13:
                data_path_boundaries = xp.linspace(0.0, data_path_max, 100)
                data_path_tboundaries = [
                    0,
                    0.25 * data_path_max,
                    0.5 * data_path_max,
                    0.75 * data_path_max,
                    data_path_max,
                ]
            else:
                data_path_boundaries = xp.linspace(data_path_min, 0.0, 100)
                data_path_tboundaries = [
                    data_path_min,
                    0.75 * data_path_min,
                    0.5 * data_path_min,
                    0.25 * data_path_min,
                    0,
                ]
        else:
            data_path_boundaries = xp.linspace(data_path_min, data_path_max, 100)
            data_path_tboundaries = xp.linspace(data_path_min, data_path_max, 5)
    data_path_norm = colors.BoundaryNorm(data_path_boundaries, redmap.N, clip=True)

    w_min = w[:, :, x_section].min()
    w_max = w[:, :, x_section].max()
    if w_min * w_max < 0.0:
        # w_cboundaries = [w_min, 0.75*w_min, 0.5*w_min, 0.25*w_min, 0, 0.25*data_max, 0.5*data_max, 0.75*data_max, data_max]
        w_cboundaries = [
            w_min,
            0.75 * w_min,
            0.5 * w_min,
            0.25 * w_min,
            0.25 * w_max,
            0.5 * w_max,
            0.75 * w_max,
            w_max,
        ]
    else:
        w_cboundaries = [-1.0e-14, 0.0, 1.0e-14]

    q_max = q[:, :, x_section].max() + 1.0e-14
    q_cboundaries = [0.25 * q_max, 0.5 * q_max, 0.75 * q_max, q_max]

    cp1 = axs[0].contourf(
        y2d, z2d, data[:, :, x_section], cmap=bluemap, levels=data_boundaries, norm=data_norm
    )
    cp2 = axs[1].contourf(
        xx2d, yy2d, data_path, cmap=redmap, levels=data_path_boundaries, norm=data_path_norm
    )
    axs[0].contour(y2d, z2d, w[:, :, x_section], colors="black", levels=w_cboundaries)
    axs[0].contour(y2d, z2d, q[:, :, x_section], colors="orange", levels=q_cboundaries)

    q_max = q[z_section].max() + 1.0e-14
    q_cboundaries = [0.25 * q_max, 0.5 * q_max, 0.75 * q_max, q_max]
    axs[1].contour(xx2d, yy2d, q[z_section], colors="black", levels=q_cboundaries)

    fontsize = 18

    divider1 = make_axes_locatable(axs[0])
    cax1 = divider1.append_axes("right", size="5%", pad=0.1)
    cb1 = plt.colorbar(cp1, ticks=data_tboundaries, cax=cax1, format=ticker.FuncFormatter(fmt))
    divider2 = make_axes_locatable(axs[1])
    cax2 = divider2.append_axes("right", size="5%", pad=0.1)
    cb2 = plt.colorbar(cp2, ticks=data_path_tboundaries, cax=cax2, format=ticker.FuncFormatter(fmt))
    # cb1 = plt.colorbar(cp1,format=ticker.FuncFormatter(fmt),ticks=nice_tboundaries)
    cb1.ax.tick_params(labelsize=fontsize)
    cb2.ax.tick_params(labelsize=fontsize)

    axs[0].set_xlim(0, y_max)
    axs[0].set_ylim(0, 1)
    axs[0].set_xticks([0, 1, 2, 3, 4])
    axs[0].set_yticks([0, 0.25, 0.5, 0.75, 1])
    axs[0].set_xlabel("y (km)", fontsize=fontsize)
    axs[0].set_ylabel("z (km)", fontsize=fontsize)
    axs[0].tick_params(axis="both", which="major", labelsize=fontsize)
    axs[0].set_title(title + " " + unit + " at yz plane", fontsize=fontsize)

    axs[1].set_xlim(0, x_max)
    axs[1].set_ylim(0, y_max)
    axs[1].set_xticks([0, 1, 2])
    axs[1].set_yticks([0, 1, 2, 3, 4])
    axs[1].set_xlabel("x (km)", fontsize=fontsize)
    axs[1].set_ylabel("y (km)", fontsize=fontsize)
    # axs[1].axes.yaxis.set_ticklabels([])
    axs[1].tick_params(axis="both", which="major", labelsize=fontsize)
    axs[1].set_title(title + " " + unit, fontsize=fontsize)

    # axs[0].set_aspect(1.0/axs[0].get_data_ratio(),adjustable='box')
    # axs[1].set_aspect(1.0/axs[1].get_data_ratio(),adjustable='box')
    plt.savefig(title + "_" + str(step) + ".png", format="png", dpi=500)


def nice_qliq_plot2d(
    v_yz_plane: NDArray,
    w_yz_plane: NDArray,
    u_xy_plane: NDArray,
    v_xy_plane: NDArray,
    v_yz_plane_0: NDArray,
    v_xy_plane_0: NDArray,
    nice: NDArray,
    qliq: NDArray,
    y2d: NDArray,
    z2d: NDArray,
    y2d_skip: NDArray,
    z2d_skip: NDArray,
    xx2d: NDArray,
    yy2d: NDArray,
    xx2d_skip: NDArray,
    yy2d_skip: NDArray,
    x_max: int,
    y_max: int,
    x_section: int,
    z_section: int,
    time: float,
    t: int,
    nice_xyplane_limit: float,
    nice_yzplane_limit: float,
) -> None:
    # Evaluate an existing colormap from 0.5 (midpoint) to 1 (upper end)
    redmap = plt.get_cmap("bwr")
    redmap_colors = redmap(xp.linspace(0.5, 1, redmap.N // 2))

    # Create a new colormap from those colors
    redmap = LinearSegmentedColormap.from_list("Upper Half", redmap_colors)

    v_yz_plane_0_expand = xp.expand_dims(v_yz_plane_0, axis=0)
    v_xy_plane_0_expand = xp.expand_dims(v_xy_plane_0, axis=0)
    v_xy_plane_0_expand = xp.repeat(v_xy_plane_0_expand, repeats=v_xy_plane.shape[0], axis=0)
    v_yz_plane_0_expand = xp.repeat(v_yz_plane_0_expand, repeats=v_yz_plane.shape[0], axis=0)

    # contour plot function
    def fmt(x, pos):
        a, b = "{:.2e}".format(x).split("e")
        b = int(b)
        return r"${} \times 10^{{{}}}$".format(a, b)

    plt.close()
    fig, axs = plt.subplots(ncols=2, figsize=(18, 9))
    fig.subplots_adjust(wspace=0.55)

    nice_xyplane = nice[z_section]
    nice_yzplane = nice[:, :, x_section]
    qliq_xyplane = qliq[z_section]
    qliq_yzplane = qliq[:, :, x_section]

    nice_xyplane_boundaries = xp.linspace(0.0, nice_xyplane_limit, 100)
    nice_yzplane_boundaries = xp.linspace(0.0, nice_yzplane_limit, 100)
    nice_xyplane_tboundaries = [
        0,
        0.25 * nice_xyplane_limit,
        0.5 * nice_xyplane_limit,
        0.75 * nice_xyplane_limit,
        nice_xyplane_limit,
    ]
    nice_yzplane_tboundaries = [
        0,
        0.25 * nice_yzplane_limit,
        0.5 * nice_yzplane_limit,
        0.75 * nice_yzplane_limit,
        nice_yzplane_limit,
    ]
    nice_xyplane_norm = colors.BoundaryNorm(nice_xyplane_boundaries, redmap.N, clip=True)
    nice_yzplane_norm = colors.BoundaryNorm(nice_yzplane_boundaries, redmap.N, clip=True)

    qliq_xyplane_max = qliq_xyplane.max()
    qliq_yzplane_max = qliq_yzplane.max()
    qliq_xyplane_cboundaries = [
        0.25 * qliq_xyplane_max,
        0.5 * qliq_xyplane_max,
        0.75 * qliq_xyplane_max,
        qliq_xyplane_max,
    ]
    qliq_yzplane_cboundaries = [
        0.25 * qliq_yzplane_max,
        0.5 * qliq_yzplane_max,
        0.75 * qliq_yzplane_max,
        qliq_yzplane_max,
    ]

    cp1 = axs[0].contourf(
        y2d, z2d, nice_yzplane, cmap=redmap, levels=nice_yzplane_boundaries, norm=nice_yzplane_norm
    )
    cp2 = axs[1].contourf(
        xx2d,
        yy2d,
        nice_xyplane,
        cmap=redmap,
        levels=nice_xyplane_boundaries,
        norm=nice_xyplane_norm,
    )
    axs[0].quiver(y2d_skip, z2d_skip, v_yz_plane, w_yz_plane)  #  - v_yz_plane_0_expand
    qliq_contours = axs[0].contour(
        y2d, z2d, qliq_yzplane, colors="black", levels=qliq_yzplane_cboundaries
    )
    axs[0].clabel(qliq_contours, inline=1, fontsize=10)
    axs[1].quiver(xx2d_skip, yy2d_skip, u_xy_plane, v_xy_plane)  #  - v_xy_plane_0_expand

    fontsize = 18

    divider1 = make_axes_locatable(axs[0])
    cax1 = divider1.append_axes("right", size="5%", pad=0.1)
    cb1 = plt.colorbar(
        cp1, ticks=nice_yzplane_tboundaries, cax=cax1
    )  # ,format=ticker.FuncFormatter(fmt)
    divider2 = make_axes_locatable(axs[1])
    cax2 = divider2.append_axes("right", size="5%", pad=0.1)
    cb2 = plt.colorbar(
        cp2, ticks=nice_xyplane_tboundaries, cax=cax2
    )  # ,format=ticker.FuncFormatter(fmt)
    # cb1 = plt.colorbar(cp1,format=ticker.FuncFormatter(fmt),ticks=nice_tboundaries)
    cb1.ax.tick_params(labelsize=fontsize)
    cb2.ax.tick_params(labelsize=fontsize)

    axs[0].set_xlim(0, y_max)
    axs[0].set_ylim(0, 1)
    axs[0].set_xticks([0, 1, 2, 3, 4])
    axs[0].set_yticks([0, 0.25, 0.5, 0.75, 1])
    axs[0].set_xlabel("y (km)", fontsize=fontsize)
    axs[0].set_ylabel("z (km)", fontsize=fontsize)
    axs[0].tick_params(axis="both", which="major", labelsize=fontsize)
    axs[0].set_title(
        "Nice (cm-3) at X=500 m, t = 18:"
        + str(int(time / 60))
        + ":"
        + str(int(time) - 60 * int(time / 60)),
        fontsize=fontsize,
    )

    axs[1].set_xlim(0, x_max)
    axs[1].set_ylim(0, y_max)
    axs[1].set_xticks([0, 1, 2])
    axs[1].set_yticks([0, 1, 2, 3, 4])
    axs[1].set_xlabel("x (km)", fontsize=fontsize)
    axs[1].set_ylabel("y (km)", fontsize=fontsize)
    # axs[1].axes.yaxis.set_ticklabels([])
    axs[1].tick_params(axis="both", which="major", labelsize=fontsize)
    axs[1].set_title(
        "Nice (cm-3) at Z=500 m, t = 18:"
        + str(int(time / 60))
        + ":"
        + str(int(time) - 60 * int(time / 60)),
        fontsize=fontsize,
    )

    # axs[0].set_aspect(1.0/axs[0].get_data_ratio(),adjustable='box')
    # axs[1].set_aspect(1.0/axs[1].get_data_ratio(),adjustable='box')
    plt.savefig("Nice_" + str(t) + ".png", format="png")


def qice_qliq_plot2d(
    v_yz_plane: NDArray,
    w_yz_plane: NDArray,
    u_xy_plane: NDArray,
    v_xy_plane: NDArray,
    v_yz_plane_0: NDArray,
    v_xy_plane_0: NDArray,
    qice: NDArray,
    qliq: NDArray,
    y2d: NDArray,
    z2d: NDArray,
    y2d_skip: NDArray,
    z2d_skip: NDArray,
    xx2d: NDArray,
    yy2d: NDArray,
    xx2d_skip: NDArray,
    yy2d_skip: NDArray,
    x_max: int,
    y_max: int,
    x_section: int,
    z_section: int,
    time: float,
    t: int,
    qice_xyplane_limit: float,
    qice_yzplane_limit: float,
) -> None:
    # Evaluate an existing colormap from 0.5 (midpoint) to 1 (upper end)
    redmap = plt.get_cmap("bwr")
    redmap_colors = redmap(xp.linspace(0.5, 1, redmap.N // 2))

    # Create a new colormap from those colors
    redmap = LinearSegmentedColormap.from_list("Upper Half", redmap_colors)

    v_yz_plane_0_expand = xp.expand_dims(v_yz_plane_0, axis=0)
    v_xy_plane_0_expand = xp.expand_dims(v_xy_plane_0, axis=0)
    v_xy_plane_0_expand = xp.repeat(v_xy_plane_0_expand, repeats=v_xy_plane.shape[0], axis=0)
    v_yz_plane_0_expand = xp.repeat(v_yz_plane_0_expand, repeats=v_yz_plane.shape[0], axis=0)

    # contour plot function
    def fmt(x, pos):
        a, b = "{:.2e}".format(x).split("e")
        b = int(b)
        return r"${} \times 10^{{{}}}$".format(a, b)

    plt.close()
    fig, axs = plt.subplots(ncols=2, figsize=(18, 9))
    fig.subplots_adjust(wspace=0.55)

    qice_xyplane = qice[z_section]
    qice_yzplane = qice[:, :, x_section]
    qliq_xyplane = qliq[z_section]
    qliq_yzplane = qliq[:, :, x_section]

    qice_xyplane_boundaries = xp.linspace(0.0, qice_xyplane_limit, 100)
    qice_yzplane_boundaries = xp.linspace(0.0, qice_yzplane_limit, 100)
    qice_xyplane_tboundaries = [
        0,
        0.25 * qice_xyplane_limit,
        0.5 * qice_xyplane_limit,
        0.75 * qice_xyplane_limit,
        qice_xyplane_limit,
    ]
    qice_yzplane_tboundaries = [
        0,
        0.25 * qice_yzplane_limit,
        0.5 * qice_yzplane_limit,
        0.75 * qice_yzplane_limit,
        qice_yzplane_limit,
    ]
    qice_xyplane_norm = colors.BoundaryNorm(qice_xyplane_boundaries, redmap.N, clip=True)
    qice_yzplane_norm = colors.BoundaryNorm(qice_yzplane_boundaries, redmap.N, clip=True)

    qliq_xyplane_max = qliq_xyplane.max()
    qliq_yzplane_max = qliq_yzplane.max()
    qliq_xyplane_cboundaries = [
        0.25 * qliq_xyplane_max,
        0.5 * qliq_xyplane_max,
        0.75 * qliq_xyplane_max,
        qliq_xyplane_max,
    ]
    qliq_yzplane_cboundaries = [
        0.25 * qliq_yzplane_max,
        0.5 * qliq_yzplane_max,
        0.75 * qliq_yzplane_max,
        qliq_yzplane_max,
    ]

    cp1 = axs[0].contourf(
        y2d, z2d, qice_yzplane, cmap=redmap, levels=qice_yzplane_boundaries, norm=qice_yzplane_norm
    )
    cp2 = axs[1].contourf(
        xx2d,
        yy2d,
        qice_xyplane,
        cmap=redmap,
        levels=qice_xyplane_boundaries,
        norm=qice_xyplane_norm,
    )
    axs[0].quiver(y2d_skip, z2d_skip, v_yz_plane, w_yz_plane)  #  - v_yz_plane_0_expand
    qliq_contours = axs[0].contour(
        y2d, z2d, qliq_yzplane, colors="black", levels=qliq_yzplane_cboundaries
    )
    axs[0].clabel(qliq_contours, inline=1, fontsize=10)
    axs[1].quiver(xx2d_skip, yy2d_skip, u_xy_plane, v_xy_plane)  #  - v_xy_plane_0_expand

    fontsize = 18

    divider1 = make_axes_locatable(axs[0])
    cax1 = divider1.append_axes("right", size="5%", pad=0.1)
    cb1 = plt.colorbar(
        cp1, ticks=qice_yzplane_tboundaries, cax=cax1
    )  # ,format=ticker.FuncFormatter(fmt)
    divider2 = make_axes_locatable(axs[1])
    cax2 = divider2.append_axes("right", size="5%", pad=0.1)
    cb2 = plt.colorbar(
        cp2, ticks=qice_xyplane_tboundaries, cax=cax2
    )  # ,format=ticker.FuncFormatter(fmt)
    # cb1 = plt.colorbar(cp1,format=ticker.FuncFormatter(fmt),ticks=qice_tboundaries)
    cb1.ax.tick_params(labelsize=fontsize)
    cb2.ax.tick_params(labelsize=fontsize)

    axs[0].set_xlim(0, y_max)
    axs[0].set_ylim(0, 1)
    axs[0].set_xticks([0, 1, 2, 3, 4])
    axs[0].set_yticks([0, 0.25, 0.5, 0.75, 1])
    axs[0].set_xlabel("y (km)", fontsize=fontsize)
    axs[0].set_ylabel("z (km)", fontsize=fontsize)
    axs[0].tick_params(axis="both", which="major", labelsize=fontsize)
    axs[0].set_title(
        "Qice (g kg-1) at X=1000 m, t = 18:"
        + str(int(time / 60))
        + ":"
        + str(int(time) - 60 * int(time / 60)),
        fontsize=fontsize,
    )

    axs[1].set_xlim(0, x_max)
    axs[1].set_ylim(0, y_max)
    axs[1].set_xticks([0, 1, 2])
    axs[1].set_yticks([0, 1, 2, 3, 4])
    axs[1].set_xlabel("x (km)", fontsize=fontsize)
    axs[1].set_ylabel("y (km)", fontsize=fontsize)
    # axs[1].axes.yaxis.set_ticklabels([])
    axs[1].tick_params(axis="both", which="major", labelsize=fontsize)
    axs[1].set_title(
        "Qice (g kg-1) at Z=550 m, t = 18:"
        + str(int(time / 60))
        + ":"
        + str(int(time) - 60 * int(time / 60)),
        fontsize=fontsize,
    )

    # axs[0].set_aspect(1.0/axs[0].get_data_ratio(),adjustable='box')
    # axs[1].set_aspect(1.0/axs[1].get_data_ratio(),adjustable='box')
    plt.savefig("Qice_" + str(t) + ".png", format="png")
