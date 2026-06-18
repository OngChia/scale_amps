import os

import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as patches
import colormaps as cmaps
import numpy as np
import xarray as xr
import cmcrameri.cm as cmc
from mpl_toolkits.axes_grid1 import make_axes_locatable

from scale_tools import amps_library as amps, helper_functions as helper


plt.rcParams.update({
    "font.family": "DejaVu Sans",       # 科研默认字体兼容性好
    "font.size": 16,
    "axes.labelsize": 17,
    "axes.titlesize": 17,
    "axes.linewidth": 1.0,
    "axes.edgecolor": "#222222",
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.top": False,
    "ytick.right": False,
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "xtick.minor.size": 2,
    "ytick.minor.size": 2,
    "xtick.color": "#222222",
    "ytick.color": "#222222",
    "figure.dpi": 100,
    "savefig.dpi": 300,                 # 300dpi足矣
    "savefig.bbox": "tight",
    "legend.fontsize": 9,
    "axes.grid": False,                 # 🚫 不画 grid
})

##### MOVIE FFMPEG COMMAND
# ffmpeg -start_number 40 -framerate 15 -i Nice_%d.png output.mp4

dir = os.path.dirname(__file__)

poly_exist = True

iceaxis_version = 3


# scale_file_name = "/capstor/store/cscs/userlab/cwd01/cong/scale_amps_data/correct_fixae_ghighres_fine_ice_cloud_seeding_0min_z300_1minS10/history"
scale_file_name = "/capstor/store/cscs/userlab/cwd01/cong/scale_amps_data/no_ice_heat_0min/history"
noice_scale_file_name = "/capstor/store/cscs/userlab/cwd01/cong/scale_amps_data/correct_fixae_ghighres_noice_40min/history"
# scale_file_name = "/capstor/scratch/cscs/cong/scale_amps/scale-rm/test/case/cloudmip/seeding_run/history"
# noice_scale_file_name = "/capstor/scratch/cscs/cong/scale_amps/scale-rm/test/case/cloudmip/seeding_no_ice_phy/history"
# input_spinup_file_dir = "/scratch/mch/cong/scale_amps_data/spinup/history_one.pe000000.nc"
plot_dir = "./"

if 'fine_ice' in scale_file_name:
    ibin_fine = True
    massbini = amps.massbini_fine
    max_bini = amps.max_bini_fine
else:
    ibin_fine = False
    massbini = amps.massbini
    max_bini = amps.max_bini

### OPEN NETCDF DATA
# create a file object to handle the data inside the file
# f_spinup = nc4.Dataset(input_spinup_file_dir, "r")

print("\n \n \n")
print("LOG -- START READING NETCDF DIMENSIONS")

process_number=32
x_process_number=4
y_process_number=8
# for cloudmip
# process_number=25
# x_process_number=5
# y_process_number=5

time, x, y, z, fz, dz, fz_3d, dz_3d, grid_volume, y2d, z2d, xx2d, yy2d = helper.read_scale_coordinates(
    scale_file_name,
    process_number=process_number,
    x_process_number=x_process_number,
    y_process_number=y_process_number,
    print_debug=True,
)

x_max = x.max() / 1000.0
y_max = y.max() / 1000.0
z_max = z.max() / 1000.0

xyplane_height = 400.0#450.0
yzplane_x = 1000.0
x_section = np.argmin(np.abs(x - yzplane_x))
z_500m = np.argmin(np.abs(z - xyplane_height))
z_skip = z[::4]
y_skip = y[::4]
x_skip = x[::4]
y2d_skip, z2d_skip = np.meshgrid(y_skip / 1000.0, z_skip / 1000.0)
xx2d_skip, yy2d_skip = np.meshgrid(x_skip / 1000.0, y_skip / 1000.0)

tlim = len(time)
zlim = len(z)
ylim = len(y)
xlim = len(x)

# -- dimensions are time, z, y, x
print("tlim, zlim, ylim, xlim: ", tlim, zlim, ylim, xlim)

print("LOG -- FINISH READING NETCDF DIMENSIONS")


print("LOG -- START READING NETCDF VARIABLES AND ANALYSIS")

plot_timeframe, extra_frame = (20, 40, 60,), 0 # for 1 min, +1 cloudmip

# plot_timeframe, extra_frame = (20, 40, 65, 80), 0 # for 2 min, +0
# plot_timeframe, extra_frame = (20, 40, 65, 80), 20 # for 6 min, +20
# plot_timeframe, extra_frame = (25, 45, 65, ), 40 # for 9 min, +40
# plot_timeframe, extra_frame = (20, 45, 75, ), 40 # for 8 min, +40


plot_timeframe_bk = [v + extra_frame for v in plot_timeframe]

u_xyplane, u_yzplane = [], []
v_xyplane, v_yzplane = [], []
w_xyplane, w_yzplane = [], []
rhoh_mp_xyplane, rhoh_mp_yzplane = [], []
bk_rhoh_mp_xyplane, bk_rhoh_mp_yzplane = [], []
all_rhoh_mp_xyplane, all_rhoh_mp_yzplane = [], []
all_rd_rhoh_mp_xyplane, all_rd_rhoh_mp_yzplane = [], []
rd_rhoh_mp_xyplane, rd_rhoh_mp_yzplane = [], []
qv_t_mp_xyplane, qv_t_mp_yzplane = [], []
all_w_xyplane, all_w_yzplane = [], []
bk_w_xyplane, bk_w_yzplane = [], []
all_rd_w_xyplane, all_rd_w_yzplane = [], []
rd_w_xyplane, rd_w_yzplane = [], []
iwp_xyplane = []
qice_xyplane, qice_yzplane = [], []
qliq_xyplane, qliq_yzplane = [], []
bk_qliq_xyplane, bk_qliq_yzplane = [], []
rd_qliq_xyplane, rd_qliq_yzplane = [], []
nice_xyplane, nice_yzplane = [], []
dice_xyplane, dice_yzplane = [], []
inp_xyplane, inp_yzplane = [], []
ddf_xyplane, ddf_yzplane = [], []
u_xy_plane, v_xy_plane = [], []
v_yz_plane, w_yz_plane = [], []

rim_xy_plane, rim_xy_plane = [], []
rim_yz_plane, rim_yz_plane = [], []
cry_xy_plane, cry_xy_plane = [], []
cry_yz_plane, cry_yz_plane = [], []
agg_xy_plane, agg_xy_plane = [], []
agg_yz_plane, agg_yz_plane = [], []


nc4_f = []
for n in range(process_number):
    # if n < 10:
    #     nc4_f.append(nc4.Dataset(scale_file_name+'.pe00000'+str(n)+'.nc', "r"))
    # else:
    #     nc4_f.append(nc4.Dataset(scale_file_name+'.pe0000'+str(n)+'.nc', "r"))
    if n < 10:
        nc4_f.append(xr.open_dataset(noice_scale_file_name+'.pe00000'+str(n)+'.nc', engine="netcdf4"))
    else:
        nc4_f.append(xr.open_dataset(noice_scale_file_name+'.pe0000'+str(n)+'.nc', engine="netcdf4"))

for t in range(200):

    scale_data = {}
    amps_data = {}

    if t not in plot_timeframe_bk:
        continue

    helper.read_scale_data(
        nc4_f,
        scale_data,
        amps_data,
        "W",
        "QLIQ",
        "RHOH_MP",
        process_number=process_number,
        x_process_number=x_process_number,
        y_process_number=y_process_number,
        z_grid_number=zlim,
        y_grid_number=ylim,
        x_grid_number=xlim,
        time_step=t,
        ibin_fine=ibin_fine,
    )
    print("LOG -- BK PROGRESS", t)
    bk_w_xyplane.append(scale_data["W"][z_500m, :, :])
    bk_w_yzplane.append(scale_data["W"][:, :, x_section])
    bk_qliq_xyplane.append(scale_data["QLIQ"][z_500m, :, :] * 1000.0)
    bk_qliq_yzplane.append(scale_data["QLIQ"][:, :, x_section] * 1000.0)
    bk_rhoh_mp_xyplane.append(scale_data["RHOH_MP"][z_500m, :, :])
    bk_rhoh_mp_yzplane.append(scale_data["RHOH_MP"][:, :, x_section])
    
# close them to try to remove cache
for n in range(process_number):
    nc4_f[n].close()

nc4_f = []
for n in range(process_number):
    # if n < 10:
    #     nc4_f.append(nc4.Dataset(scale_file_name+'.pe00000'+str(n)+'.nc', "r"))
    # else:
    #     nc4_f.append(nc4.Dataset(scale_file_name+'.pe0000'+str(n)+'.nc', "r"))
    if n < 10:
        nc4_f.append(xr.open_dataset(scale_file_name+'.pe00000'+str(n)+'.nc', engine="netcdf4"))
    else:
        nc4_f.append(xr.open_dataset(scale_file_name+'.pe0000'+str(n)+'.nc', engine="netcdf4"))

# create background windspeed profile
# v_yz_plane_0 = np.mean(f_spinup.variables["V"][0, :, :, x_section], axis=1)  # [::4]
# v_xy_plane_0 = np.mean(f_spinup.variables["V"][0, z_500m, :, :], axis=0)  # [::4]
# f_spinup.close()


output_count = 0
for t in range(tlim):

    scale_data = {}
    amps_data = {}

    if t not in plot_timeframe:
        continue
    
    helper.read_scale_data(
        nc4_f,
        scale_data,
        amps_data,
        "DENS",
        "RHOH_MP",
        "QV_t_MP",
        "T",
        "U",
        "V",
        "W",
        "QLIQ",
        "QHYD",
        "QICE",
        "ampsci_col",
        "ampsci_ddf",
        # "con_amass12",
        # "ae_amass12",
        "con_lmass",
        "con_imass",
        "vol_imass",
        "dmax_imass",
        "ice_imass",
        "cry_imass",
        "agg_imass",
        "rim_imass",
        process_number=process_number,
        x_process_number=x_process_number,
        y_process_number=y_process_number,
        z_grid_number=zlim,
        y_grid_number=ylim,
        x_grid_number=xlim,
        time_step=t,
        ibin_fine=ibin_fine,
    )
    print("LOG -- PROGRESS", t, time[t])

    # horizontal wind speed
    u_xy_plane.append(scale_data["U"][z_500m, ::4, ::4])

    # horizontal wind speed
    v_yz_plane.append(scale_data["V"][::4, ::4, x_section])
    v_xy_plane.append(scale_data["V"][z_500m, ::4, ::4])

    # verticle wind speed
    w_yz_plane.append(scale_data["W"][::4, ::4, x_section])

    Nliq = np.zeros((zlim, ylim, xlim))
    Nice = np.zeros((zlim, ylim, xlim))
    Dliq = np.zeros((zlim, ylim, xlim))
    Dice = np.zeros((zlim, ylim, xlim))

    # liquid and ice number concentrations and effective diameter
    temp1, temp2, temp3 = 0.0, 0.0, 0.0
    temp4, temp5, temp6 = 0.0, 0.0, 0.0
    cloud_mask = np.where(scale_data["QLIQ"] > 1.0e-6, True, False)
    cloud_count = np.count_nonzero(cloud_mask)
    total_Nice = np.sum(amps_data["con_imass"], axis=0) * scale_data["DENS"]
    # ice_mask = np.where(scale_data["QICE"] > 1.0e-6, True, False)
    ice_mask = np.where(total_Nice > 1.0e-3, True, False)
    ice_count = np.count_nonzero(ice_mask)
    Dliq3, Dliq2 = np.zeros_like(Dliq), np.zeros_like(Dliq)
    # Dice3, Dice2 = np.zeros_like(Dice), np.zeros_like(Dice)
    for j in range(len(amps.massbin)):
        Nliq = np.where(cloud_mask, Nliq + amps_data["con_lmass"][j] * scale_data["DENS"], Nliq)
        Dliq3 = np.where(
            cloud_mask, Dliq3 + amps_data["con_lmass"][j] * scale_data["DENS"] * amps.diameterbin[j] ** 3, Dliq3
        )
        Dliq2 = np.where(
            cloud_mask, Dliq2 + amps_data["con_lmass"][j] * scale_data["DENS"] * amps.diameterbin[j] ** 2, Dliq2
        )
    for j in range(len(massbini)):
        Nice = np.where(ice_mask, Nice + amps_data["con_imass"][j] * scale_data["DENS"], Nice)
    for j in range(len(massbini)):
        Dice = np.where(
            ice_mask & (Nice > 0.0), Dice + amps_data["dmax_imass"][j] * amps_data["con_imass"][j] * scale_data["DENS"] / Nice, Dice
        )
    # Dliq = np.where(Dliq2 > 0.0, Dliq3 / Dliq2, 0.0)
    # Dice = np.where(Dice2 > 0.0, Dice3 / Dice2, 0.0)
    # print(Dice.max(), Dice.min())
    
    scale_data["QLIQ"] = scale_data["QLIQ"] * 1000.0 * scale_data["DENS"][:, :, :]
    scale_data["QICE"] = scale_data["QICE"] * 1000.0 * scale_data["DENS"][:, :, :]
    Qliq = np.where(ice_mask, scale_data["QLIQ"], scale_data["QLIQ"])
    qv_t_mp = np.where(ice_mask, scale_data["QV_t_MP"], 0.0)
    rhoh_mp = np.where(ice_mask, scale_data["RHOH_MP"], 0.0)
    u_mask = np.where(ice_mask, scale_data["U"], 0.0)
    v_mask = np.where(ice_mask, scale_data["V"], 0.0)
    w_mask = np.where(ice_mask, scale_data["W"], 0.0)
    
    rim_mask = np.where(ice_mask, np.sum(amps_data["rim_imass"], axis=0) / np.sum(amps_data["ice_imass"], axis=0), 0.0)
    agg_mask = np.where(ice_mask, np.sum(amps_data["agg_imass"], axis=0) / np.sum(amps_data["ice_imass"], axis=0), 0.0)
    cry_mask = np.where(ice_mask, np.sum(amps_data["cry_imass"], axis=0) / np.sum(amps_data["ice_imass"], axis=0), 0.0)

    ice_mask_xyplane = ice_mask[z_500m, :, :]
    ice_mask_yzplane = ice_mask[:, :, x_section]
    all_rd_w_xy = scale_data["W"][z_500m, :, :] - bk_w_xyplane[output_count][:,:]
    all_rd_w_yz = scale_data["W"][:, :, x_section] - bk_w_yzplane[output_count][:,:]
    all_rd_w_xyplane.append(all_rd_w_xy)
    all_rd_w_yzplane.append(all_rd_w_yz)
    rd_w_xyplane.append(np.where(ice_mask_xyplane, all_rd_w_xy, 0.0))
    rd_w_yzplane.append(np.where(ice_mask_yzplane, all_rd_w_yz, 0.0))

    all_rd_rhoh_mp_xy = scale_data["RHOH_MP"][z_500m, :, :] - bk_rhoh_mp_xyplane[output_count][:,:]
    all_rd_rhoh_mp_yz = scale_data["RHOH_MP"][:, :, x_section] - bk_rhoh_mp_yzplane[output_count][:,:]
    all_rd_rhoh_mp_xyplane.append(all_rd_rhoh_mp_xy)
    all_rd_rhoh_mp_yzplane.append(all_rd_rhoh_mp_yz)
    rd_rhoh_mp_xyplane.append(np.where(ice_mask_xyplane, all_rd_rhoh_mp_xy, 0.0))
    rd_rhoh_mp_yzplane.append(np.where(ice_mask_yzplane, all_rd_rhoh_mp_yz, 0.0))

    rim_xy_plane.append(rim_mask[z_500m, :, :])
    rim_yz_plane.append(rim_mask[:, :, x_section])
    cry_xy_plane.append(cry_mask[z_500m, :, :])
    cry_yz_plane.append(cry_mask[:, :, x_section])
    agg_xy_plane.append(agg_mask[z_500m, :, :])
    agg_yz_plane.append(agg_mask[:, :, x_section])
    
    u_xyplane.append(u_mask[z_500m, :, :])
    u_yzplane.append(u_mask[:, :, x_section])
    v_xyplane.append(v_mask[z_500m, :, :])
    v_yzplane.append(v_mask[:, :, x_section])
    w_xyplane.append(w_mask[z_500m, :, :])
    w_yzplane.append(w_mask[:, :, x_section])
    all_w_xyplane.append(scale_data["W"][z_500m, :, :])
    all_w_yzplane.append(scale_data["W"][:, :, x_section])
    all_rhoh_mp_xyplane.append(scale_data["RHOH_MP"][z_500m, :, :])
    all_rhoh_mp_yzplane.append(scale_data["RHOH_MP"][:, :, x_section])
    iwp_xyplane.append(np.sum(scale_data["QICE"][:, :, :] * dz_3d, axis=0))
    qice_xyplane.append(scale_data["QICE"][z_500m, :, :])
    qice_yzplane.append(scale_data["QICE"][:, :, x_section])
    qliq_xyplane.append(Qliq[z_500m, :, :])
    qliq_yzplane.append(Qliq[:, :, x_section])
    rd_qliq_xyplane.append(scale_data["QLIQ"][z_500m, :, :] - bk_qliq_xyplane[output_count][:,:])
    rd_qliq_yzplane.append(scale_data["QLIQ"][:, :, x_section] - bk_qliq_yzplane[output_count][:,:])
    nice_xyplane.append(Nice[z_500m, :, :] * 1000.0)
    nice_yzplane.append(Nice[:, :, x_section] * 1000.0)
    dice_xyplane.append(Dice[z_500m, :, :])
    dice_yzplane.append(Dice[:, :, x_section])
    rhoh_mp_xyplane.append(rhoh_mp[z_500m, :, :])
    rhoh_mp_yzplane.append(rhoh_mp[:, :, x_section])
    qv_t_mp_xyplane.append(qv_t_mp[z_500m, :, :])
    qv_t_mp_yzplane.append(qv_t_mp[:, :, x_section])
    # mean_mass_inp = np.where(amps_data["con_amass12"][z_500m, :, :] > 1.e-5, amps_data["ae_amass12"][z_500m, :, :] / amps_data["con_amass12"][z_500m, :, :], 0.0)
    # inp_xyplane.append(mean_mass_inp)
    # mean_mass_inp = np.where(amps_data["con_amass12"][:, :, x_section] > 1.e-5, amps_data["ae_amass12"][:, :, x_section] / amps_data["con_amass12"][:, :, x_section], 0.0)
    # inp_yzplane.append(mean_mass_inp)
    inp_xyplane.append(np.zeros_like(Dice[z_500m, :, :]))
    inp_yzplane.append(np.zeros_like(Dice[:, :, x_section]))
    # inp_xyplane.append(amps_data["con_amass12"][z_500m, :, :])
    # inp_yzplane.append(amps_data["con_amass12"][:, :, x_section])
    ddf_xyplane.append(amps_data["ampsci_ddf"][z_500m, :, :])
    ddf_yzplane.append(amps_data["ampsci_ddf"][:, :, x_section])
    # ddf_xyplane.append(amps_data["con_amass12"][z_500m, :, :])
    # ddf_yzplane.append(amps_data["con_amass12"][:, :, x_section])

    output_count += 1


for n in range(process_number):
    nc4_f[n].close()

# contour plot function
def fmt(x, pos):
    a, b = "{:.2e}".format(x).split("e")
    b = int(b)
    return r"${} \times 10^{{{}}}$".format(a, b)


def plot_3frames(data_yzplane, contour_data_yzplane, filename, colorbar_label, title):

    plt.close()
    # subplot_labels = ['(a)', '(b)', '(c)']
    # fig, axs = plt.subplot_mosaic(figsize=(18, 5), [subplot_labels])
    # i = 0
    # for label, ax in axs.items():
    #     ax.set_title(title[i])
    #     ax.set_title(label, loc='left', fontsize='medium')
    #     i += 1
    subplot_title_labels = ['(a)', '(b)', '(c)']
    subplot_labels = [0, 1, 2]
    fig, axs = plt.subplots(figsize=(18, 5), ncols=3, nrows=1)

    # colormap = plt.get_cmap("jet")
    # colormap = cmc.roma.reversed()
    colormap = cmaps.batloww.reversed()

    assert data_yzplane.shape[0] == 3
    assert contour_data_yzplane.shape[0] == 3
    data_yzplane_max = np.max(data_yzplane)
    data_yzplane_min = np.min(data_yzplane)
    print("data_yzplane_max:", data_yzplane_max)
    if data_yzplane_min < 0.0:
        print("TWO WAY PLOTTING")
        upper_boundary = max(-data_yzplane_min, data_yzplane_max)
        data_yzplane_max = upper_boundary
        data_yzplane_min = -upper_boundary
        data_yzplane_boundaries = np.linspace(data_yzplane_min, data_yzplane_max, 100)
        data_yzplane_tboundaries = [data_yzplane_min, 0.5 * data_yzplane_min, 0, 0.5 * data_yzplane_max, data_yzplane_max]
        data_yzplane_norm = colors.BoundaryNorm(data_yzplane_boundaries, colormap.N, clip=True)
    else:
        data_yzplane_boundaries = np.linspace(0.0, data_yzplane_max, 100)
        bnd_scale_list = [0, 0.25, 0.5, 0.75, 1.0]
        data_yzplane_tboundaries = [i * data_yzplane_max for i in bnd_scale_list] 
        data_yzplane_norm = colors.BoundaryNorm(data_yzplane_boundaries, colormap.N, clip=True)

    cp = {}
    cpc = {}
    for count, i in enumerate(subplot_labels):
        cp[i] = axs[i].contourf(
            y2d, z2d, data_yzplane[count], cmap=colormap, levels=data_yzplane_boundaries, norm=data_yzplane_norm
        )
        
        cpc[i] = axs[i].contour(y2d, z2d, contour_data_yzplane[count], colors="black", linestyles='solid' ,levels=np.linspace(0.01, np.max(contour_data_yzplane), 5))

    def fmt(x):
        s = f"{x:.1f}"
        if s.endswith("0"):
            s = f"{x:.0f}"
        # return rf"{s} \%" if plt.rcParams["text.usetex"] else f"{s} %"
        return f"{s}"

    for i in subplot_labels:
        axs[i].clabel(cpc[i], cpc[i].levels, fmt=fmt, fontsize=10)

    # for i in range(3):
    #     square = patches.Rectangle((1.990, 0.400), 0.030, 0.050, edgecolor='black', facecolor='none', linewidth=1.2, linestyle='solid')
    #     axs[i].add_patch(square)

    divider1 = make_axes_locatable(axs[subplot_labels[-1]])
    cax1 = divider1.append_axes("right", size="5%", pad=0.1)
    # formatter = ticker.LogFormatter(10, labelOnlyBase=False) 
    cb1 = plt.colorbar(cp[subplot_labels[-1]], ticks=data_yzplane_tboundaries, cax=cax1, label=colorbar_label) #, format=ticker.FuncFormatter(fmt)
    cb_ticks = cb1.ax.get_yticks().tolist()
    for i, item in enumerate(cb_ticks):
        cb_ticks[i] = round(item, 1) # .label.get_text()
    cb1.ax.yaxis.set_ticklabels(cb_ticks)
    cb1.ax.minorticks_off()
    # cb1.ax.tick_params(labelsize=fontsize)
    
    for i in subplot_labels:
        axs[i].set_title(title[i]) # , fontsize=fontsize
        axs[i].set_title(subplot_title_labels[i], loc='left', fontsize='medium')
        axs[i].set_xlim(0, y_max)
        axs[i].set_ylim(0, 1)
        axs[i].set_xticks([0, 1, 2, 3, 4])
        axs[i].set_yticks([0, 0.25, 0.5, 0.75, 1])
        axs[i].set_xlabel("$y$ (km)") # , fontsize=fontsize
        if i == subplot_labels[0]:
            axs[i].set_ylabel("$z$ (km)") # , fontsize=fontsize
        axs[i].tick_params(axis="both", which="major") # , labelsize=fontsize

    for i in subplot_labels:
        if i != subplot_labels[0]:
            axs[i].yaxis.set_ticklabels([])
    # for i in range(3):
    #     axs[i].set_aspect(1.0/axs[i].get_data_ratio(), adjustable='box')
    plt.subplots_adjust(wspace=0.125, hspace=0.0)
    # plt.tight_layout()
    plt.savefig(filename+".png", format="png")


qice_yzplane_array = np.array(qice_yzplane)
qliq_yzplane_array = np.array(qliq_yzplane)
nice_yzplane_array = np.array(nice_yzplane)
w_yzplane_array = np.array(w_yzplane)
plot_3frames(qice_yzplane_array, qliq_yzplane_array, "figure_ice_plume_iwc", "IWC (g m$^{-3}$)", ["t = 4 min", "t = 8 min", "t = 12 min"])
plot_3frames(nice_yzplane_array, qliq_yzplane_array, "figure_ice_plume_nice", "Nice (cm$^{-3}$)", ["t = 4 min", "t = 8 min", "t = 12 min"])
plot_3frames(w_yzplane_array, qliq_yzplane_array, "figure_ice_plume_w", "W (m s$^{-1}$)", ["t = 4 min", "t = 8 min", "t = 12 min"])

print("LOG -- END")
