import os

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import pandas as pd
import pickle
import xarray as xr
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
# from highlight_text import ax_text

from stats_plot import data_state
from stats_plot.plot_functions import plot_3boxes_for_updowndraft_comparison, plot_2boxes_for_updowndraft_comparison, plot_allcases
from stats_plot.helper_functions import extract_grouped_data

# ----------------------------
# 全局绘图样式（科研展示风格）
# ----------------------------
plt.rcParams.update({
    "font.family": "DejaVu Sans",       # 科研默认字体兼容性好
    "font.size": 15,
    "axes.labelsize": 16,
    "axes.titlesize": 16,
    "axes.linewidth": 1.0,
    "axes.edgecolor": "#222222",
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
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
    "axes.formatter.use_mathtext": True,
})

COL_UP = "#d12734"     # updraft
COL_CALM = "#D5B943"   # no wind
COL_DOWN = "#7fafe1"   # downdraft

# 三色过渡：下降(蓝) → 无风(黄) → 上升(红)
CM_W3 = LinearSegmentedColormap.from_list("w3", [COL_DOWN, COL_CALM, COL_UP], N=256)

LABEL_UP = "Updraft"
LABEL_CALM = "No wind"
LABEL_DOWN = "Downdraft"

def multiline(xs, ys, c, ax=None, **kwargs):
    """Plot lines with different colorings"""
    ax = plt.gca() if ax is None else ax
    segments = [np.column_stack([x, y]) for x, y in zip(xs, ys)]
    lc = LineCollection(segments, **kwargs)
    lc.set_array(np.asarray(c))
    ax.add_collection(lc)
    ax.autoscale()
    return lc


# ----------------------------
# 基础设置
# ----------------------------
dir = os.path.dirname(__file__)
seed_file = "/capstor/store/cscs/userlab/cwd01/cong/plume_data/seeding_mean_wind_speed.csv"
ice_distribution_data = xr.open_zarr("/capstor/store/cscs/userlab/cwd01/cong/plume_data/obs_data/ice_distribution.zarr")

normal_data_files = ["/capstor/store/cscs/userlab/cwd01/cong/plume_data/simulation_" + str(index) + "min_data.pkl" for index in range(20)]
normal_reduced_w_data_files = ["/capstor/store/cscs/userlab/cwd01/cong/plume_data/simulation_" + str(index) + "min_data_for_reduced_w.pkl" for index in range(20)]
wbf_off_data_files = ["/capstor/store/cscs/userlab/cwd01/cong/plume_data/wbf_off/simulation_" + str(index) + "min_data.pkl" for index in range(20)]
wbf_off_reduced_w_data_files = ["/capstor/store/cscs/userlab/cwd01/cong/plume_data/wbf_off/simulation_" + str(index) + "min_data_for_reduced_w.pkl" for index in range(20)]
noseed_data_files = ["/capstor/store/cscs/userlab/cwd01/cong/plume_data/no_seeding/simulation_" + str(index) + "min_data.pkl" for index in range(20)]
noseed_reduced_w_data_files = ["/capstor/store/cscs/userlab/cwd01/cong/plume_data/no_seeding/simulation_" + str(index) + "min_data_for_reduced_w.pkl" for index in range(20)]

plot_dir = "./plots_review/"
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

seed_w = pd.read_csv(seed_file)
print(seed_w['min_vertical_wind_speed'])

if os.path.exists("./temp_plume_data.pkl"):
    print("LOG -- Load plume data from temp file")
    with open("./temp_plume_data.pkl", "rb") as f:
        data = pickle.load(f)
        normal_plume_data, wbf_off_plume_data, noseed_plume_data = data[0], data[1], data[2]
else:
    normal_plume_data = data_state.PlumeData(
        data_file_number=len(normal_data_files),
        data_files=normal_data_files,
        reduced_w_data_files=normal_reduced_w_data_files,
        grid_spacing=20.0,
        dtime=12.0,
    )
    wbf_off_plume_data = data_state.PlumeData(
        data_file_number=len(wbf_off_data_files),
        data_files=wbf_off_data_files,
        reduced_w_data_files=wbf_off_reduced_w_data_files,
        grid_spacing=20.0,
        dtime=12.0,
    )
    noseed_plume_data = data_state.PlumeData(
        data_file_number=len(noseed_data_files),
        data_files=noseed_data_files,
        reduced_w_data_files=noseed_reduced_w_data_files,
        grid_spacing=20.0,
        dtime=12.0,
    )
    with open("./temp_plume_data.pkl", "wb") as f:
        pickle.dump((normal_plume_data, wbf_off_plume_data, noseed_plume_data), f)


# class ANSI():
#     def color_text(value):
#         if value > 0.2:
#             code = "31" # red
#         elif value < -0.2:
#             code = "34" # blue
#         else:
#             code = "33" # yellow
#         return "\033[{code}m".format(code=code)

plot_allcases(
    normal_plume_data.plume_state.plume_max_time,
    normal_plume_data.plume_state.plume_max_loc_z,
    wbf_off_plume_data.plume_state.plume_max_time,
    wbf_off_plume_data.plume_state.plume_max_loc_z,
    noseed_plume_data.plume_state.plume_max_time,
    noseed_plume_data.plume_state.plume_max_loc_z,
    seed_w['min_vertical_wind_speed'],
    y_ticks=[0, 100, 200, 300, 400, 500, 600],
    y_lim=[-6, 606],
    y_label="ice plume altitude (m)",
    plot_dir=plot_dir,
    filename="figure_plume_loc_z_in_sensitivity_tests.png"
)
plot_allcases(
    normal_plume_data.plume_state.plume_max_time,
    normal_plume_data.plume_state.plume_max_buoyancy,
    wbf_off_plume_data.plume_state.plume_max_time,
    wbf_off_plume_data.plume_state.plume_max_buoyancy,
    noseed_plume_data.plume_state.plume_max_time,
    noseed_plume_data.plume_state.plume_max_buoyancy,
    seed_w['min_vertical_wind_speed'],
    y_ticks=None,
    y_lim=None,
    y_label="Plume buoyancy",
    plot_dir=plot_dir,
    filename="figure_plume_buoyancy_in_sensitivity_tests.png"
)


(mean_wbf_effect_z_2min, mean_wbf_effect_z_3min, mean_wbf_effect_z_obs, mean_wbf_effect_z_800s) = (np.zeros(len(normal_data_files)) for _ in range(4))
(mean_wbf_to_normal_z_2min, mean_wbf_to_normal_z_3min, mean_wbf_to_normal_z_obs, mean_wbf_to_normal_z_800s) = (np.zeros(len(normal_data_files)) for _ in range(4))
(mean_noseed_to_normal_z_2min, mean_noseed_to_normal_z_3min, mean_noseed_to_normal_z_obs, mean_noseed_to_normal_z_800s) = (np.zeros(len(normal_data_files)) for _ in range(4))
time_index_2min = np.argmin(np.abs(np.array(normal_plume_data.plume_state.plume_max_time[0]) - 120.0))
time_index_3min = np.argmin(np.abs(np.array(normal_plume_data.plume_state.plume_max_time[0]) - 180.0))
time_index_obs = np.argmin(np.abs(np.array(normal_plume_data.plume_state.plume_max_time[0]) - 444.0)) # 444s
time_index_800s = np.argmin(np.abs(np.array(normal_plume_data.plume_state.plume_max_time[0]) - 800.0))
time_indices = [time_index_2min, time_index_3min, time_index_obs, time_index_800s]
mean_wbf_effect_z = [mean_wbf_effect_z_2min, mean_wbf_effect_z_3min, mean_wbf_effect_z_obs, mean_wbf_effect_z_800s]
mean_wbf_to_normal_z = [mean_wbf_to_normal_z_2min, mean_wbf_to_normal_z_3min, mean_wbf_to_normal_z_obs, mean_wbf_to_normal_z_800s]
mean_noseed_to_normal_z = [mean_noseed_to_normal_z_2min, mean_noseed_to_normal_z_3min, mean_noseed_to_normal_z_obs, mean_noseed_to_normal_z_800s]
for t_index, t in enumerate(time_indices):
    for i in range(len(normal_data_files)):
        mean_wbf_effect_z[t_index][i] = (
            normal_plume_data.plume_state.plume_max_loc_z[i][t] - wbf_off_plume_data.plume_state.plume_max_loc_z[i][t]
        ) / (
            normal_plume_data.plume_state.plume_max_loc_z[i][t] - noseed_plume_data.plume_state.plume_max_loc_z[i][t]
        )
        mean_wbf_to_normal_z[t_index][i] = (
            normal_plume_data.plume_state.plume_max_loc_z[i][t] - wbf_off_plume_data.plume_state.plume_max_loc_z[i][t]
        )
        mean_noseed_to_normal_z[t_index][i] = (
            normal_plume_data.plume_state.plume_max_loc_z[i][t] - noseed_plume_data.plume_state.plume_max_loc_z[i][t]
        )
# grouped_mean_wbf_effect_z_2min = extract_grouped_data(mean_wbf_effect_z_2min, seed_w['min_vertical_wind_speed'])
grouped_mean_wbf_effect_z_3min = extract_grouped_data(mean_wbf_effect_z_3min, seed_w['min_vertical_wind_speed'])
grouped_mean_wbf_effect_z_obs = extract_grouped_data(mean_wbf_effect_z_obs, seed_w['min_vertical_wind_speed'])
grouped_mean_wbf_effect_z_800s = extract_grouped_data(mean_wbf_effect_z_800s, seed_w['min_vertical_wind_speed'])
# grouped_mean_wbf_to_normal_z_2min = extract_grouped_data(mean_wbf_to_normal_z_2min, seed_w['min_vertical_wind_speed'])
grouped_mean_wbf_to_normal_z_3min = extract_grouped_data(mean_wbf_to_normal_z_3min, seed_w['min_vertical_wind_speed'])
grouped_mean_wbf_to_normal_z_obs = extract_grouped_data(mean_wbf_to_normal_z_obs, seed_w['min_vertical_wind_speed'])
grouped_mean_wbf_to_normal_z_800s = extract_grouped_data(mean_wbf_to_normal_z_800s, seed_w['min_vertical_wind_speed'])
# grouped_mean_noseed_to_normal_z_2min = extract_grouped_data(mean_noseed_to_normal_z_2min, seed_w['min_vertical_wind_speed'])
grouped_mean_noseed_to_normal_z_3min = extract_grouped_data(mean_noseed_to_normal_z_3min, seed_w['min_vertical_wind_speed'])
grouped_mean_noseed_to_normal_z_obs = extract_grouped_data(mean_noseed_to_normal_z_obs, seed_w['min_vertical_wind_speed'])
grouped_mean_noseed_to_normal_z_800s = extract_grouped_data(mean_noseed_to_normal_z_800s, seed_w['min_vertical_wind_speed'])

plot_3boxes_for_updowndraft_comparison(
    [grouped_mean_wbf_effect_z_3min, grouped_mean_wbf_effect_z_obs, grouped_mean_wbf_effect_z_800s],
    ["Updraft", "No wind", "Downdraft"],
    ["$\Delta z_{WBF} / \Delta z_{NOICE}$ at $t = 3$ min", "$\Delta z_{WBF} / \Delta z_{NOICE}$ at $t = 7$ min", "$\Delta z_{WBF} / \Delta z_{NOICE}$ at $t = 13$ min"],
    os.path.join(plot_dir, "figure_ice_plume_wbf_z_fraction_3min.png"),
    logy=[False, False, False],
    y_axis_ticks=[0, 0.25, 0.5, 0.75, 1.0],
)
plot_3boxes_for_updowndraft_comparison(
    [grouped_mean_wbf_to_normal_z_3min, grouped_mean_wbf_to_normal_z_obs, grouped_mean_wbf_to_normal_z_800s],
    ["Updraft", "No wind", "Downdraft"],
    ["(Z_ICE - Z_WBF) at $t = 3$ min", "(Z_ICE - Z_WBF) at $t = 7$ min", "(Z_ICE - Z_WBF) at $t = 13$ min"],
    os.path.join(plot_dir, "figure_ice_plume_wbf_z_diff_3min.png"),
    logy=[False, False, False],
    y_axis_ticks=[0, 50, 100, 150, 200],
)
plot_3boxes_for_updowndraft_comparison(
    [grouped_mean_noseed_to_normal_z_3min, grouped_mean_noseed_to_normal_z_obs, grouped_mean_noseed_to_normal_z_800s],
    ["Updraft", "No wind", "Downdraft"],
    ["(Z_NOICE - Z_WBF) at $t = 3$ min", "(Z_NOICE - Z_WBF) at $t = 7$ min", "(Z_NOICE - Z_WBF) at $t = 13$ min"],
    os.path.join(plot_dir, "figure_ice_plume_noseed_z_diff_3min.png"),
    logy=[False, False, False],
    y_axis_ticks=[0, 50, 100, 150, 200],
)


plot_2boxes_for_updowndraft_comparison(
    [grouped_mean_wbf_effect_z_obs, grouped_mean_wbf_effect_z_800s],
    ["Updraft", "No wind", "Downdraft"],
    ["$R_{\\mathrm{WBF}}$ at $t = 444$ s", "$R_{\\mathrm{WBF}}$ at $t = 800$ s"],
    os.path.join(plot_dir, "figure_ice_plume_wbf_z_fraction.png"),
    logy=[False, False],
    y_axis_ticks=[0, 0.25, 0.5, 0.75, 1.0],
)

print("LOG -- END")
