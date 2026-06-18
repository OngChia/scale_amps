import os

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import netCDF4 as nc4
import numpy as np
import xarray as xr

from scale_tools import amps_library as amps, helper_functions as helper


dir = os.path.dirname(__file__)

scale_file_name = "/capstor/store/cscs/userlab/cwd01/cong/scale_amps_data/correct_fixae_ghighres_noice_40min/history"
plot_dir = "./"

if 'fine_ice_bin' in scale_file_name:
    ibin_fine = True
    massbini = amps.massbini_fine
    max_bini = amps.max_bini_fine
else:
    ibin_fine = False
    massbini = amps.massbini
    max_bini = amps.max_bini

### OPEN NETCDF DATA
# create a file object to handle the data inside the file

process_number=32
x_process_number=4
y_process_number=8

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

tlim = len(time)
zlim = len(z)
ylim = len(y)
xlim = len(x)

j_seed = 0
k_seed = 0
for k in range(zlim):
    if z[k] > 300.0+1.e-15:
        k_seed = k
        break
i_seed = []
for i in range(xlim):
    if x[i] >= 949.0 and x[i] <= 1051.0:
        i_seed.append(i)


print("seed_location (x): ", x[i_seed])
print("seed_location (y): ", y[j_seed])
print("seed_location (z): ", z[k_seed])

print("seed_location index (x): ", i_seed)
print("seed_location index (y): ", j_seed)
print("seed_location index (z): ", k_seed)

obs_x_coord = 1000.0 # (925, 975, 1025, 1075, 1125)
obs_y_coord = (2000.0, )
obs_z_coord = (410.0, )
obs_z_lower_coord = (400.0, )
obs_z_upper_coord = (450.1, )
obs_x_index = np.argmin(np.abs(x - obs_x_coord))
obs_y_index = []
for item in obs_y_coord:
    obs_y_index.append(np.argmin(np.abs(y - item)))
obs_z_index, obs_z_lower_index, obs_z_upper_index = [], [], []
for item_no, item in enumerate(obs_z_coord):
    obs_z_index.append(np.argmin(np.abs(z - item)))
    obs_z_lower_index.append(np.argmin(np.abs(z - obs_z_lower_coord[item_no])))
    obs_z_upper_index.append(np.argmin(np.abs(z - obs_z_upper_coord[item_no])))
obs_index = []
for item in obs_y_index:
    obs_index.append((item, obs_x_index))


print("seed_location index (x): ", x[obs_x_index])
print("seed_location index (y): ", y[obs_y_index[0]])
print("seed_location index (z): ", z[obs_z_index[0]])


# -- dimensions are time, z, y, x
print("tlim, zlim, ylim, xlim: ", tlim, zlim, ylim, xlim)

print("LOG -- FINISH READING NETCDF DIMENSIONS")


print("LOG -- START READING NETCDF VARIABLES AND ANALYSIS")


nc4_f = []
for n in range(process_number):
    if n < 10:
        nc4_f.append(nc4.Dataset(scale_file_name+'.pe00000'+str(n)+'.nc', "r"))
    else:
        nc4_f.append(nc4.Dataset(scale_file_name+'.pe0000'+str(n)+'.nc', "r"))




print("LOG -- FINISH READING NETCDF DIMENSIONS")


### INITIALIZE GLOBAL VARIABLES

scale_data = {}
amps_data = {}

print("LOG -- START READING NETCDF VARIABLES AND ANALYSIS")

mean_seed_w = []
seed_time = []
for t in range(tlim):
    if t > 107:
        continue
    print("LOG -- PROGRESS", t)

    helper.read_scale_data(
            nc4_f,
            scale_data,
            amps_data,
            "DENS",
            "T",
            "U",
            "V",
            "W",
            "QV",
            process_number=process_number,
            x_process_number=x_process_number,
            y_process_number=y_process_number,
            z_grid_number=zlim,
            y_grid_number=ylim,
            x_grid_number=xlim,
            time_step=t,
            ibin_fine=ibin_fine,
        )

    mean_seed_w.append(np.mean(scale_data["W"][k_seed, j_seed, i_seed]))
    seed_time.append(time[t] / 60.0)

min1_mean_seed_w = []
t = 0
min1_seed_time = []
for t in range(101):
    min1_seed_time.append(seed_time[t])
    min1_mean_seed_w.append(0.2 * (mean_seed_w[t] + mean_seed_w[t+1] + mean_seed_w[t+2] + mean_seed_w[t+3] + mean_seed_w[t+4]))



print("LOG -- FINISH READING NETCDF")

print("LOG -- START PLOTTING")
 
# ------------------------------------------
# 改进版绘图部分
# ------------------------------------------
def setup_plot_style():
    """论文级绘图风格"""
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update({
        "font.size": 13,
        "font.family": "DejaVu Sans",
        "axes.labelsize": 14,
        "axes.titlesize": 15,
        "axes.linewidth": 1.2,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "lines.linewidth": 2,
        "lines.markersize": 6,
        "legend.frameon": False,
    })
    # sns.set_theme(
    #     style="whitegrid",
    #     font_scale=1.1,
    #     rc={
    #         "axes.edgecolor": "0.25",
    #         "axes.linewidth": 1.2,
    #         "axes.labelsize": 13,
    #         "axes.titlesize": 14,
    #         "lines.linewidth": 1.8,
    #         "lines.markersize": 9,
    #         "legend.frameon": False,
    #         "legend.loc": "best",
    #         "xtick.direction": "in",
    #         "ytick.direction": "in",
    #         "font.family": "serif",
    #         "axes.spines.right": False,
    #         "axes.spines.top": False,
    #         "savefig.dpi": 400,
    #         "grid.linewidth": 0.6,
    #         "grid.alpha": 0.4,
    #     },
    # )

setup_plot_style()

df = pd.DataFrame(data={"Time": seed_time, "Vertical wind speed": mean_seed_w})
ave1min_df = pd.DataFrame(data={"Time": min1_seed_time, "Vertical wind speed": min1_mean_seed_w})
# seed_df = pd.DataFrame(data={
#     "Time": [2, 4, 9],
#     "seed": [mean_seed_w[10], mean_seed_w[20], mean_seed_w[45]],
#     "Seeding": ["Downdraft (2 min)", "Updraft (4 min)", "Calm (9 min)"],
# })
seeding_label = [str(k)+" min" for k in range(20)]
seed_df = pd.DataFrame(data={
    "Time": [k for k in range(20)],
    "seed": [mean_seed_w[5*k] for k in range(20)],
    "Seeding": seeding_label,
})
ave1min_seed_df = pd.DataFrame(data={
    "Time": [k for k in range(20)],
    "seed": [min1_mean_seed_w[5*k] for k in range(20)],
    "Seeding": seeding_label,
})

# ------------------------------------------
# 绘图
# ------------------------------------------

# ax.plot(seed_time, mean_seed_w, color="#2b6dad",linewidth=1.8)

# ax.set_xlabel("Time")
# ax.set_ylabel("Vertical wind speed")


def w_plot(input_w_df: pd.DataFrame, input_seed_df: pd.DataFrame, title: str, bk_input_w_df: pd.DataFrame = None, bk_input_seed_df: pd.DataFrame = None, restrict_yaxis: bool = False):
    """绘制垂直风速时间序列"""

    plt.close()
    fig, ax = plt.subplots(figsize=(6, 4.2))
    # 主线
    sns.lineplot(
        data=input_w_df,
        x="Time",
        y="Vertical wind speed",
        color="#311B92",
        linewidth=1.8,
        ax=ax,
        zorder=1,
    )
    if bk_input_w_df is not None:
        sns.lineplot(
            data=bk_input_w_df,
            x="Time",
            y="Vertical wind speed",
            color="#2b6dad",
            alpha=0.4,
            linewidth=1.8,
            ax=ax,
            zorder=1,
        )

    ax.spines['bottom'].set_alpha(0.4)
    ax.spines['left'].set_alpha(0.4)
    ax.spines['top'].set_alpha(0.4)
    ax.spines['right'].set_alpha(0.4)
    # 散点
    # palette = {"Downdraft (2 min)": "#2b5da6", "Updraft (4 min)": "#e2764e", "Calm (9 min)": "#4c9c6e"}
    palette = {}
    for k in range(len(seeding_label)):
        palette[seeding_label[k]] = "#000000"
    scatter = sns.scatterplot(
        data=input_seed_df,
        x="Time",
        y="seed",
        hue="Seeding",
        palette=palette,
        s=30,
        edgecolor="white",
        linewidth=1.2,
        ax=ax,
        zorder=2,
    )
    ax.fill_between(np.arange(101), np.full(101,fill_value=-0.2), np.full(101,fill_value=0.2), color="#f3eed9", alpha=0.2, linewidth=0.0)
    ax.fill_between(np.arange(101), np.full(101,fill_value=0.2), np.full(101,fill_value=0.9), color="#d12734", alpha=0.2, linewidth=0.0)
    ax.fill_between(np.arange(101), np.full(101,fill_value=-0.9), np.full(101,fill_value=-0.2), color="#66b1f3", alpha=0.2, linewidth=0.0)
    # website: #d12734 original: #8f462d updraft
    # website: #f3eed9 original: #d8e7b3 no wind
    # website: #66b1f3 original: #3f62ae downdraft

    scatter.legend_.remove()

    # 坐标与标题
    ax.set_xlim(0, 20)
    ax.set_xticks([i*2 for i in range(11)])
    if restrict_yaxis:
        ax.set_ylim(-0.7, 0.7)
        ax.set_yticks(np.linspace(-0.6,0.6,7))
    else:
        ax.set_ylim(-1.0, 1.0)
        ax.set_yticks(np.linspace(-0.9,0.9,7))
    ax.set_xlabel(f"Time (min)", labelpad=6)
    ax.set_ylabel("Vertical wind speed (m s$^{-1}$)", labelpad=6)
    # ax.set_title("Mean vertical wind speed (m s$^{-1}$)\nat seeding grid cells", pad=10)

    # Legend 设置
    # leg = ax.legend(
    #     loc="lower right",
    #     frameon=True,
    #     framealpha=0.9,
    #     prop={'size': 9},
    # )
    # leg.get_frame().set_linewidth(0.8)
    # leg.get_frame().set_edgecolor("#bbbbbb")

    # 网格线与边界
    # ax.grid(True, linestyle="--", alpha=0.3)
    ax.grid(True, linestyle="--", alpha=0.0)
    # for spine in ["top", "right"]:
    #     ax.spines[spine].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, title), dpi=600)
    plt.show()

w_plot(df, seed_df, "figure_seed_w_sns_pretty.png")
w_plot(ave1min_df, ave1min_seed_df, "figure_seed_w_ave1min_sns_pretty.png", restrict_yaxis=True)
w_plot(ave1min_df, ave1min_seed_df, "figure_seed_w_and_w_ave1min_sns_pretty.png", df, seed_df)

ds = xr.Dataset(
    {
        "min_vertical_wind_speed": (("time",), ave1min_seed_df["seed"]),
    },
    coords={
        "time": ave1min_seed_df["Time"],
    },
)
df = ds.to_dataframe()
df.to_csv('seeding_mean_wind_speed.csv')


