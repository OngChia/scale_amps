import math
import os
import sys
from datetime import timedelta

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import netCDF4 as nc4
import pandas as pd
import xarray as xr
import numpy as np
import pickle
import re
import csv
import cmcrameri.cm as cmc

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap

from stats_plot import data_state
from stats_plot.plot_functions import plot_3boxes_for_updowndraft_comparison, plot_box_for_updowndraft_comparison
from stats_plot.helper_functions import extract_grouped_data, normalize_data, all_mean


# ----------------------------
# 全局绘图样式（科研展示风格）
# ----------------------------
plt.rcParams.update({
    "font.family": "DejaVu Sans",       # 科研默认字体兼容性好
    "font.size": 13,
    "axes.labelsize": 14,
    "axes.titlesize": 14,
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

def plot(x_data, y_data, x_label, y_label, title, logy: bool=False, set_colorbar: bool = True, ax=None, fig=None):
    output_fig = False
    if ax is None:
        plt.close()
        fig, ax = plt.subplots(figsize=(5.6, 4))   # 比例略宽，便于阅读
        output_fig = True
    
    # 让颜色映射以 0 为中心、上下对称（你的 w 有正有负时特别重要）
    w_for_color = seed_w["min_vertical_wind_speed"].to_numpy()
    absmax = float(np.nanmax(np.abs(w_for_color))) if w_for_color.size else 1.0
    
    # ✅ 优化色带：roma 或 oslo，亮度均匀、科学出版常用
    # cmap = cmc.roma.reversed()
    cmap = CM_W3
    lc = multiline(
        x_data,
        y_data,
        seed_w['min_vertical_wind_speed'],
        ax,
        cmap=cmap,
        lw=1.8,
        alpha=0.85,
    )
    lc.set_clim(-absmax, absmax)

    ax.set_xlabel(x_label, labelpad=4)
    ax.set_ylabel(y_label, labelpad=4)
    fmt_y = mticker.ScalarFormatter(useMathText=True)
    fmt_y.set_scientific(True)
    fmt_y.set_powerlimits((0, 0))
    fmt_y.set_useOffset(True)
    ax.yaxis.set_major_formatter(fmt_y)
    
    # ✅ 优化色标尺寸与字体比例
    if set_colorbar:
        cbar = fig.colorbar(lc, pad=0.03, aspect=30)
        cbar.set_label("Mean seeding W (m s$^{-1}$)", fontsize=14, labelpad=6)
        cbar.ax.tick_params(labelsize=14, width=0.8)
    else:
        fig.set_constrained_layout_pads(w_pad = 0., h_pad = 1.2, hspace = 0., wspace = 0.)
  

    # ✅ 坐标轴范围内边距略放宽
    ax.margins(x=0.02, y=0.05)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(True)

    if logy:
        ax.set_yscale("log")

    formatter = mticker.ScalarFormatter(useMathText=True)
    ax.xaxis.set_major_formatter(formatter)

    if output_fig:
        plt.tight_layout()
        plt.savefig(
            os.path.join(plot_dir, f"figure_plume_{title}.png"),
            dpi=300,
            bbox_inches="tight"
        )


# ----------------------------
# 基础设置
# ----------------------------
dir = os.path.dirname(__file__)
Nice_threshold = 1.e-2
seed_file = "/capstor/store/cscs/userlab/cwd01/cong/plume_data/seeding_mean_wind_speed.csv"
data_files = ["/capstor/store/cscs/userlab/cwd01/cong/plume_data/simulation_" + str(index) + "min_data.pkl" for index in range(20)]
reduced_w_data_files = ["/capstor/store/cscs/userlab/cwd01/cong/plume_data/simulation_" + str(index) + "min_data_for_reduced_w.pkl" for index in range(20)]

# seed_file = "/scratch/mch/cong/plume_data/seeding_mean_wind_speed.csv"
# data_files = ["/scratch/mch/cong/plume_data/no_seeding/simulation_" + str(index) + "min_data.pkl" for index in range(20)]
# reduced_w_data_files = ["/scratch/mch/cong/plume_data/no_seeding/simulation_" + str(index) + "min_data_for_reduced_w.pkl" for index in range(20)]
# data_files = ["/scratch/mch/cong/plume_data/no_seeding/simulation_" + str(index) + "min_data.pkl" for index in range(20)]
# reduced_w_data_files = ["/scratch/mch/cong/plume_data/no_seeding/simulation_" + str(index) + "min_data_for_reduced_w.pkl" for index in range(20)]
# data_files = ["/scratch/mch/cong/plume_data/wbf_off/simulation_" + str(index) + "min_data.pkl" for index in range(20)]
# reduced_w_data_files = ["/scratch/mch/cong/plume_data/wbf_off/simulation_" + str(index) + "min_data_for_reduced_w.pkl" for index in range(20)]

ice_distribution_data = xr.open_zarr("/capstor/store/cscs/userlab/cwd01/cong/plume_data/obs_data/ice_distribution.zarr")
# ice_distribution_data = xr.open_zarr("/scratch/mch/cong/plume_data/obs_data/ice_distribution.zarr")
    
plot_dir = "./plots_plume_statistics"
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

for single_file in data_files:
    print("file name: ", single_file)

seed_w = pd.read_csv(seed_file)
print(seed_w['min_vertical_wind_speed'])


plume_data = data_state.PlumeData(
    data_file_number=len(data_files),
    data_files=data_files,
    reduced_w_data_files=reduced_w_data_files,
    grid_spacing=20.0,
    dtime=12.0,
)
plume_state = plume_data.plume_state

# ----------------------------
# 绘图函数（统一美化）
# ----------------------------
# def multiline(xs, ys, c, ax=None, **kwargs):
#     ax = plt.gca() if ax is None else ax
#     segments = [np.column_stack([x, y]) for x, y in zip(xs, ys)]
#     lc = LineCollection(segments, **kwargs)
#     lc.set_array(np.asarray(c))
#     ax.add_collection(lc)
#     ax.autoscale()
#     return lc


# def plot(x_data, y_data, x_label, y_label, title):
#     plt.close()
#     fig, ax = plt.subplots(figsize=(6, 4))
#     cmap = cmc.batlow
#     lc = multiline(x_data, y_data, seed_w['min_vertical_wind_speed'],
#                    ax=ax, cmap=cmap, lw=1.8, alpha=0.85)

#     ax.set_xlabel(x_label)
#     ax.set_ylabel(y_label)
#     for spine in ["top", "right"]:
#         ax.spines[spine].set_visible(True)

#     axcb = fig.colorbar(lc, pad=0.02, aspect=30)
#     axcb.set_label('Mean seeding W (m s$^{-1}$)', fontsize=10)
#     axcb.ax.tick_params(labelsize=9)

#     plt.tight_layout()
#     plt.savefig(os.path.join(plot_dir, f"figure_plume_{title}.png"), dpi=800)

print("debug 2000m time: ", plume_state.plume_2000m_time)
max_plume_2000m_time = np.max(plume_state.plume_2000m_time)
max_plume_3000m_time = np.max(plume_state.plume_3000m_time)
max_plume_4000m_time = np.max(plume_state.plume_4000m_time)

for k in range(len(data_files)):
    for i, t in enumerate(plume_state.plume_max_time[k]):
        if t > 800:
            print("debug 800 time: ", k, t, i, plume_state.plume_max_loc_y[k][i])
            break
    for i, t in enumerate(plume_state.plume_max_loc_y[k]):
        if t > 2000.0:
            print("debug 2000m loc: ", k, t, i, plume_state.plume_max_time[k][i])
            break
    for i, t in enumerate(plume_state.plume_max_loc_y[k]):
        if t > 3000.0:
            print("debug 3000m loc: ", k, t, i, plume_state.plume_max_time[k][i])
            break
    for i, t in enumerate(plume_state.plume_max_loc_y[k]):
        if t > 4000.0:
            print("debug 4000m loc: ", k, t, i, plume_state.plume_max_time[k][i])
            break

def plot_shade(x_data, y_data, seeding_w, x_label, y_label, title, ax=None, y_scientific=False):
    output_fig = False
    if ax is None:
        plt.close()
        fig, ax = plt.subplots(figsize=(5.6, 4))
        output_fig = True

    filtered_y_data = np.zeros((len(data_files), max_plume_4000m_time), dtype=float)
    filtered_x_data = np.array(x_data[0][:max_plume_4000m_time])
    for k, item in enumerate(y_data):
        filtered_y_data[k] = item[:max_plume_4000m_time]
    min_y_data = np.min(filtered_y_data, axis=0)
    max_y_data = np.max(filtered_y_data, axis=0)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    updraft_data_mask = np.where(seeding_w >= 0.2)[0]
    nowind_data_mask = np.where((seeding_w  < 0.2) & (seeding_w > -0.2))[0]
    downdraft_data_mask = np.where(seeding_w <= -0.2)[0]

    updraft_y_data = filtered_y_data[updraft_data_mask, :]
    nowind_y_data = filtered_y_data[nowind_data_mask, :]
    downdraft_y_data = filtered_y_data[downdraft_data_mask, :]

    ax.margins(x=0.02, y=0.05)
    ax.plot(filtered_x_data, np.mean(updraft_y_data, axis=0), color=COL_UP, linestyle='solid', lw=1.8, label="Updraft") # "#311B92"
    ax.plot(filtered_x_data, np.mean(nowind_y_data, axis=0), color=COL_CALM, linestyle='solid', lw=1.8, label="No wind") # teal: #004D40, deep purple: #311B92, purple: #3809b2
    ax.plot(filtered_x_data, np.mean(downdraft_y_data, axis=0), color=COL_DOWN, linestyle='solid', lw=1.8, label="Downdraft")
    ax.fill_between(filtered_x_data, min_y_data, max_y_data, color="gray", alpha=0.25)
    if "RH" in y_label:
        ax.set_ylim(94, 100.3)
    ax.legend(frameon=False)

    # if y_scientific:
    #     ax.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
    #     ax.get_yaxis().get_offset_text().set_x(-0.175)

    if y_scientific:
        fmt = mticker.ScalarFormatter(useMathText=True)
        fmt.set_powerlimits((0, 0))
        fmt.set_scientific(True)
        fmt.set_useOffset(True)
        
        ax.yaxis.set_major_formatter(fmt)
        # ax.yaxis.get_major_formatter().set_useMathText(True)

    if output_fig:
        plt.tight_layout()
        plt.savefig(os.path.join(plot_dir, f"figure_shade_plume_{title}.png"), dpi=500)


def plot_3trends(input_xdata: np.ndarray, input_ydata: list[np.ndarray], seeding_w, x_label, y_labels, titles, filename):
    fig, ax = plt.subplots(figsize=(14.0, 6.0), ncols=3, nrows=1)
    subplot_title_labels = ['(a)', '(b)', '(c)']
    for i in range(3):
        plot_shade(
            input_xdata,
            input_ydata[i],
            seeding_w,
            x_label=x_label,
            y_label=y_labels[i],
            title=titles[i],
            ax=ax[i],
            y_scientific=True if "rate" in y_labels[i].lower() else False,
        )
        ax[i].set_title(subplot_title_labels[i], loc='left')
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.15)
    plt.savefig(filename, dpi=500, bbox_inches="tight")
    plt.close()
    print(f"  → 保存 {os.path.basename(filename)}")


def plot_9trends(input_xdata: np.ndarray, input_ydata: list[np.ndarray], seeding_w, x_label, y_labels, titles, filename):
    fig, ax = plt.subplots(figsize=(13.0, 11.5), ncols=3, nrows=3)
    count = 0
    subplot_title_labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)', '(g)', '(h)', '(i)']
    for i in range(3):
        for j in range(3):
            plot_shade(
                input_xdata,
                input_ydata[count],
                seeding_w,
                x_label=x_label,
                y_label=y_labels[count],
                title=titles[count],
                ax=ax[i][j],
                y_scientific=True if "rate" in y_labels[count].lower() else False,
            )
            ax[i][j].set_title(subplot_title_labels[count], loc='left')
            count += 1
    for i in range(2):
        for j in range(3):
            ax[i][j].xaxis.set_ticklabels([])
            ax[i][j].set_xlabel("")
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.15)
    plt.savefig(filename, dpi=500, bbox_inches="tight")
    plt.close()
    print(f"  → 保存 {os.path.basename(filename)}")

def plot_2trends(input_xdata: np.ndarray, input_ydata: list[np.ndarray], xlabel, ylabels, filename):
    fig, ax = plt.subplots(figsize=(10.5, 5), ncols=2, nrows=1)
    count = 0
    subplot_title_labels = ['(a)', '(b)']
    for i in range(2):
        plot(
            input_xdata,
            input_ydata[count],
            x_label=xlabel,
            y_label=ylabels[count],
            title="",
            logy=False,
            set_colorbar=True if i == 1 else False,
            ax=ax[i],
            fig=fig,
        )
        ax[i].set_title(subplot_title_labels[count], loc='left')
        count += 1
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.15)
    plt.savefig(filename, dpi=500, bbox_inches="tight")
    plt.close()
    print(f"  → 保存 {os.path.basename(filename)}")

# ----------------------------
# 绘制各物理量的剖面
# ----------------------------
plot(plume_state.plume_max_time, plume_state.plume_max_loc_x, "Time (s)", "Ice plume X coord. (m)", "loc_x")
plot(plume_state.plume_max_time, plume_state.plume_max_loc_y, "Time (s)", "Ice plume $y$ position (m)", "loc_y")
plot(plume_state.plume_max_time, plume_state.plume_max_loc_z, "Time (s)", "Ice plume altitude (m)", "loc_z")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_col_rate, "Y (m)", "Collision rate (cm$^{-3}$ s$^{-1}$)", "y_col_rate")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_temperature, "Y (m)", "Temperature (C)", "y_temp")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_qice, "Y (m)", "IWC (g m$^{-3}$)", "y_qice")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_qliq, "Y (m)", "LWC (g m$^{-3}$)", "y_qliq")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_qtotal, "Y (m)", "IWC+LWC (g m$^{-3}$)", "y_qtotal")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_qtotal_plus_qv, "Y (m)", "TWC (g m$^{-3}$)", "y_qtotal_plus_qv")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_nice, "Y (m)", "Nice (L$^{-1}$)", "y_nice")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_total_nice, "Y (m)", "Nice", "y_total_nice")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_nagg, "Y (m)", "Nagg (L$^{-1}$)", "y_nagg")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_nliq, "Y (m)", "Nliq (cm$^{-1}$)", "y_nliq")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_dice, "Y (m)", "Dice ($\\mu$m)", "y_dice")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_dliq, "Y (m)", "Dliq ($\\mu$m)", "y_dliq")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_acratio, "Y (m)", "Aspect ratio", "y_acratio")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_rh, "Y (m)", "RH", "y_rh")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_rhi, "Y (m)", "RHI", "y_rhi")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_amps_rh, "Y (m)", "RH", "y_amps_rh")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_amps_rhi, "Y (m)", "RHI", "y_amps_rhi")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_w, "Y (m)", "W (m s$^{-1}$)", "y_w")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_w_bk, "Y (m)", "W (m s$^{-1}$)", "y_w_bk")

plot(plume_state.plume_max_time, plume_state.plume_max_col_rate, "Time (s)", "Collision rate (cm$^{-3}$ s$^{-1}$)", "t_col_rate")
plot(plume_state.plume_max_time, plume_state.plume_max_temperature, "Time (s)", "Temperature (C)", "t_temp")
plot(plume_state.plume_max_time, plume_state.plume_max_qice, "Time (s)", "IWC (g m$^{-3}$)", "t_qice")
plot(plume_state.plume_max_time, plume_state.plume_max_qliq, "Time (s)", "LWC (g m$^{-3}$)", "t_qliq")
plot(plume_state.plume_max_time, plume_state.plume_max_qtotal, "Time (s)", "IWC+LWC (g m$^{-3}$)", "t_qtotal")
plot(plume_state.plume_max_time, plume_state.plume_max_qtotal_plus_qv, "Time (s)", "TWC (g m$^{-3}$)", "t_qtotal_plus_qv")
plot(plume_state.plume_max_time, plume_state.plume_max_nice, "Time (s)", "Nice (L$^{-1}$)", "t_nice")
plot(plume_state.plume_max_time, plume_state.plume_max_total_nice, "Time (s)", "Nice", "t_total_nice")
plot(plume_state.plume_max_time, plume_state.plume_max_nagg, "Time (s)", "Nagg (L$^{-1}$)", "t_nagg")
plot(plume_state.plume_max_time, plume_state.plume_max_nliq, "Time (s)", "Nliq (cm$^{-3}$)", "t_nliq")
plot(plume_state.plume_max_time, plume_state.plume_max_dice, "Time (s)", "Dice ($\\mu$m)", "t_dice")
plot(plume_state.plume_max_time, plume_state.plume_max_dliq, "Time (s)", "Dliq ($\\mu$m)", "t_dliq")
plot(plume_state.plume_max_time, plume_state.plume_max_acratio, "Time (s)", "Aspect ratio", "t_acratio")
plot(plume_state.plume_max_time, plume_state.plume_max_rh, "Time (s)", "RH", "t_rh")
plot(plume_state.plume_max_time, plume_state.plume_max_rhi, "Time (s)", "RHI", "t_rhi")
plot(plume_state.plume_max_time, plume_state.plume_max_amps_rh, "Time (s)", "RH", "t_amps_rh")
plot(plume_state.plume_max_time, plume_state.plume_max_amps_rhi, "Time (s)", "RHI", "t_amps_rhi")
plot(plume_state.plume_max_time, plume_state.plume_max_w, "Time (s)", "W (m s$^{-1}$)", "t_w")
plot(plume_state.plume_max_time, plume_state.plume_max_w_bk, "Time (s)", "W (m s$^{-1}$)", "t_w_bk")
plot(plume_state.plume_max_time, plume_state.plume_max_reduced_w, "Time (s)", "W (m s$^{-1}$)", "t_reduced_w")

plot_2trends(
    plume_state.plume_max_time,
    [plume_state.plume_max_loc_z, plume_state.plume_max_w],
    "Time (s)",
    ["Ice plume altitude (m)", "W (m s$^{-1}$)"],
    os.path.join(plot_dir, "figure_plume_locz_w_trends.png"),
)

plot_shade(plume_state.plume_max_time, plume_state.plume_max_loc_z, seed_w["min_vertical_wind_speed"], "Time (s)", "Ice plume altitude (m)", "loc_z")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_col_rate, seed_w["min_vertical_wind_speed"], "Time (s)", "Collision rate (cm$^{-3}$ s$^{-1}$)", "t_col_rate")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_temperature, seed_w["min_vertical_wind_speed"], "Time (s)", "Temperature (C)", "t_temp")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_qice, seed_w["min_vertical_wind_speed"], "Time (s)", "IWC (g m$^{-3}$)", "t_qice")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_qliq, seed_w["min_vertical_wind_speed"], "Time (s)", "LWC (g m$^{-3}$)", "t_qliq")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_qtotal, seed_w["min_vertical_wind_speed"], "Time (s)", "IWC+LWC (g m$^{-3}$)", "t_qtotal")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_qtotal_plus_qv, seed_w["min_vertical_wind_speed"], "Time (s)", "TWC (g m$^{-3}$)", "t_qtotal_plus_qv")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_nice, seed_w["min_vertical_wind_speed"], "Time (s)", "Nice (L$^{-1}$)", "t_nice")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_total_nice, seed_w["min_vertical_wind_speed"], "Time (s)", "Nice", "t_total_nice")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_nagg, seed_w["min_vertical_wind_speed"], "Time (s)", "Nagg (L$^{-1}$)", "t_nagg")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_nliq, seed_w["min_vertical_wind_speed"], "Time (s)", "Nliq (cm$^{-3}$)", "t_nliq")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_dice, seed_w["min_vertical_wind_speed"], "Time (s)", "Dice ($\\mu$m)", "t_dice")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_dliq, seed_w["min_vertical_wind_speed"], "Time (s)", "Dliq ($\\mu$m)", "t_dliq")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_acratio, seed_w["min_vertical_wind_speed"], "Time (s)", "Aspect ratio", "t_acratio")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_rh, seed_w["min_vertical_wind_speed"], "Time (s)", "RH", "t_rh")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_rhi, seed_w["min_vertical_wind_speed"], "Time (s)", "RHI", "t_rhi")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_amps_rh, seed_w["min_vertical_wind_speed"], "Time (s)", "RH", "t_amps_rh")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_amps_rhi, seed_w["min_vertical_wind_speed"], "Time (s)", "RHI", "t_amps_rhi")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_w, seed_w["min_vertical_wind_speed"], "Time (s)", "W (m s$^{-1}$)", "t_w")

# turbulent kinetic energy (Smagorinsky) m2/s2
plot(plume_state.plume_max_loc_y, plume_state.plume_max_tke, "Y (m)", "TKE (m$^{2}$ s$^{-2}$)", "y_tke")
plot(plume_state.plume_max_time, plume_state.plume_max_tke, "Time (s)", "TKE (m$^{2}$ s$^{-2}$)", "t_tke")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_tke, seed_w["min_vertical_wind_speed"], "Time (s)", "TKE (m$^{2}$ s$^{-2}$)", "t_tke")

# activation rate /cm3/s
plot(plume_state.plume_max_loc_y, plume_state.plume_max_cact, "Y (m)", "Act. rate (cm$^{-3}$ s$^{-1}$)", "y_cact")
plot(plume_state.plume_max_time, plume_state.plume_max_cact, "Time (s)", "Act. rate (cm$^{-3}$ s$^{-1}$)", "t_cact", logy=False)
plot_shade(plume_state.plume_max_time, plume_state.plume_max_cact, seed_w["min_vertical_wind_speed"], "Time (s)", "Act. rate (cm$^{-3}$ s$^{-1}$)", "t_cact")
plot(plume_state.plume_max_loc_y, plume_state.plume_max_reduced_cact, "Y (m)", "Reduced act. rate (cm$^{-3}$ s$^{-1}$)", "y_reduced_cact")
plot(plume_state.plume_max_time, plume_state.plume_max_reduced_cact, "Time (s)", "Reduced act. rate (cm$^{-3}$ s$^{-1}$)", "t_reduced_cact")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_reduced_cact, seed_w["min_vertical_wind_speed"], "Time (s)", "Reduced act. rate (cm$^{-3}$ s$^{-1}$)", "t_reduced_cact")


# accumulative diabatic heating J
plot(plume_state.plume_max_loc_y, plume_state.plume_max_accumulated_heat_release, "Y (m)", "Accumulative latent heat (J)", "y_latent_heat")
plot(plume_state.plume_max_time, plume_state.plume_max_accumulated_heat_release, "Time (s)", "Accumulative latent heat (J)", "t_latent_heat")
plot_shade(plume_state.plume_max_time, plume_state.plume_max_accumulated_heat_release, seed_w["min_vertical_wind_speed"], "Time (s)", "Accumulative latent heat (J)", "t_latent_heat")

filtered_reduced_w_data = np.zeros((len(data_files), max_plume_4000m_time), dtype=float)
for k, item in enumerate(plume_state.plume_max_reduced_w):
    filtered_reduced_w_data[k] = item[:max_plume_4000m_time]
filtered_heat_data = np.zeros((len(data_files), max_plume_4000m_time), dtype=float)
for k, item in enumerate(plume_state.plume_max_accumulated_heat_release):
    filtered_heat_data[k] = item[:max_plume_4000m_time]
filtered_test_data = np.zeros((len(data_files), max_plume_4000m_time), dtype=float)
for k, item in enumerate(plume_state.plume_max_qice):
    filtered_test_data[k] = item[:max_plume_4000m_time]
plot(filtered_heat_data, filtered_reduced_w_data, "Accumulative latent heat (J)", "W increment (m s$^{-1}$)", "heat_vs_w_increment")
plot(filtered_test_data, filtered_reduced_w_data, "TEST", "W increment (m s$^{-1}$)", "test_vs_w_increment")


grouped_1000m_xgrid_data = extract_grouped_data(plume_state.plume_1000m_xgrid, seed_w['min_vertical_wind_speed'])
grouped_1000m_zgrid_data = extract_grouped_data(plume_state.plume_1000m_zgrid, seed_w['min_vertical_wind_speed'])
grouped_2000m_xgrid_data = extract_grouped_data(plume_state.plume_2000m_xgrid, seed_w['min_vertical_wind_speed'])
grouped_2000m_zgrid_data = extract_grouped_data(plume_state.plume_2000m_zgrid, seed_w['min_vertical_wind_speed'])
grouped_3000m_xgrid_data = extract_grouped_data(plume_state.plume_3000m_xgrid, seed_w['min_vertical_wind_speed'])
grouped_3000m_zgrid_data = extract_grouped_data(plume_state.plume_3000m_zgrid, seed_w['min_vertical_wind_speed'])
grouped_4000m_xgrid_data = extract_grouped_data(plume_state.plume_4000m_xgrid, seed_w['min_vertical_wind_speed'])
grouped_4000m_zgrid_data = extract_grouped_data(plume_state.plume_4000m_zgrid, seed_w['min_vertical_wind_speed'])
all_1000m_xgrid_data = extract_grouped_data(plume_state.plume_1000m_xgrid, seed_w['min_vertical_wind_speed'], split=False)
all_2000m_xgrid_data = extract_grouped_data(plume_state.plume_2000m_xgrid, seed_w['min_vertical_wind_speed'], split=False)
all_3000m_xgrid_data = extract_grouped_data(plume_state.plume_3000m_xgrid, seed_w['min_vertical_wind_speed'], split=False)
all_4000m_xgrid_data = extract_grouped_data(plume_state.plume_4000m_xgrid, seed_w['min_vertical_wind_speed'], split=False)
normalized_grouped_1000m_xgrid_data = normalize_data(grouped_1000m_xgrid_data)
normalized_grouped_2000m_xgrid_data = normalize_data(grouped_2000m_xgrid_data)
normalized_grouped_3000m_xgrid_data = normalize_data(grouped_3000m_xgrid_data)
normalized_grouped_4000m_xgrid_data = normalize_data(grouped_4000m_xgrid_data)
normalized_grouped_1000m_zgrid_data = normalize_data(grouped_1000m_zgrid_data)
normalized_grouped_2000m_zgrid_data = normalize_data(grouped_2000m_zgrid_data)
normalized_grouped_3000m_zgrid_data = normalize_data(grouped_3000m_zgrid_data)
normalized_grouped_4000m_zgrid_data = normalize_data(grouped_4000m_zgrid_data)
all_mean(all_1000m_xgrid_data, "all_1000m_xgrid_data")
all_mean(all_2000m_xgrid_data, "all_2000m_xgrid_data")
all_mean(all_3000m_xgrid_data, "all_3000m_xgrid_data")
all_mean(all_4000m_xgrid_data, "all_4000m_xgrid_data")
axis_label = [0, 50, 100, 150, 200, 250, 300]
plot_box_for_updowndraft_comparison(grouped_1000m_zgrid_data, ["Updraft", "No wind", "Downdraft"], "Altitude spread (m) at $y = 1$ km", os.path.join(plot_dir, "figure_box_plume_1000m_zgrid.png"))
plot_box_for_updowndraft_comparison(grouped_2000m_zgrid_data, ["Updraft", "No wind", "Downdraft"], "Altitude spread (m) at $y = 2$ km", os.path.join(plot_dir, "figure_box_plume_2000m_zgrid.png"))
plot_box_for_updowndraft_comparison(grouped_3000m_zgrid_data, ["Updraft", "No wind", "Downdraft"], "Altitude spread (m) at $y = 3$ km", os.path.join(plot_dir, "figure_box_plume_3000m_zgrid.png"))
plot_box_for_updowndraft_comparison(grouped_4000m_zgrid_data, ["Updraft", "No wind", "Downdraft"], "Altitude spread (m) at $y = 4$ km", os.path.join(plot_dir, "figure_box_plume_4000m_zgrid.png"))
plot_box_for_updowndraft_comparison(grouped_1000m_xgrid_data, ["Updraft", "No wind", "Downdraft"], "X spread (m) at 1 km", os.path.join(plot_dir, "figure_box_plume_1000m_xgrid.png"))
plot_box_for_updowndraft_comparison(grouped_2000m_xgrid_data, ["Updraft", "No wind", "Downdraft"], "X spread (m) at 2 km", os.path.join(plot_dir, "figure_box_plume_2000m_xgrid.png"))
plot_box_for_updowndraft_comparison(grouped_3000m_xgrid_data, ["Updraft", "No wind", "Downdraft"], "X spread (m) at 3 km", os.path.join(plot_dir, "figure_box_plume_3000m_xgrid.png"))
plot_box_for_updowndraft_comparison(grouped_4000m_xgrid_data, ["Updraft", "No wind", "Downdraft"], "X spread (m) at 4 km", os.path.join(plot_dir, "figure_box_plume_4000m_xgrid.png"))

plot_box_for_updowndraft_comparison(normalized_grouped_1000m_zgrid_data, ["Updraft", "No wind", "Downdraft"], "Altitude spread (m) at $y = 1$ km", os.path.join(plot_dir, "figure_box_plume_1000m_normalized_zgrid.png"), logy=False, y_axis_ticks=axis_label)
plot_box_for_updowndraft_comparison(normalized_grouped_2000m_zgrid_data, ["Updraft", "No wind", "Downdraft"], "Altitude spread (m) at $y = 2$ km", os.path.join(plot_dir, "figure_box_plume_2000m_normalized_zgrid.png"), logy=False, y_axis_ticks=axis_label)
plot_box_for_updowndraft_comparison(normalized_grouped_3000m_zgrid_data, ["Updraft", "No wind", "Downdraft"], "Altitude spread (m) at $y = 3$ km", os.path.join(plot_dir, "figure_box_plume_3000m_normalized_zgrid.png"), logy=False, y_axis_ticks=axis_label)
plot_box_for_updowndraft_comparison(normalized_grouped_4000m_zgrid_data, ["Updraft", "No wind", "Downdraft"], "Altitude spread (m) at $y = 4$ km", os.path.join(plot_dir, "figure_box_plume_4000m_normalized_zgrid.png"), logy=False, y_axis_ticks=axis_label)
plot_box_for_updowndraft_comparison(normalized_grouped_1000m_xgrid_data, ["Updraft", "No wind", "Downdraft"], "X spread (m) at $y = 1$ km", os.path.join(plot_dir, "figure_box_plume_1000m_normalized_xgrid.png"))
plot_box_for_updowndraft_comparison(normalized_grouped_2000m_xgrid_data, ["Updraft", "No wind", "Downdraft"], "X spread (m) at $y = 2$ km", os.path.join(plot_dir, "figure_box_plume_2000m_normalized_xgrid.png"))
plot_box_for_updowndraft_comparison(normalized_grouped_3000m_xgrid_data, ["Updraft", "No wind", "Downdraft"], "X spread (m) at $y = 3$ km", os.path.join(plot_dir, "figure_box_plume_3000m_normalized_xgrid.png"))
plot_box_for_updowndraft_comparison(normalized_grouped_4000m_xgrid_data, ["Updraft", "No wind", "Downdraft"], "X spread (m) at $y = 4$ km", os.path.join(plot_dir, "figure_box_plume_4000m_normalized_xgrid.png"))
plot_3boxes_for_updowndraft_comparison(
    [normalized_grouped_2000m_zgrid_data, normalized_grouped_3000m_zgrid_data, normalized_grouped_4000m_zgrid_data],
    ["Updraft", "No wind", "Downdraft"],
    ["Altitude spread (m) at $y = 2$ km", "Altitude spread (m) at $y = 3$ km", "Altitude spread (m) at $y = 4$ km"],
    os.path.join(plot_dir, "figure_ice_plume_zspread.png"),
    logy=[False, False, False],
    y_axis_ticks=axis_label
)
plot_3boxes_for_updowndraft_comparison(
    [normalized_grouped_2000m_xgrid_data, normalized_grouped_3000m_xgrid_data, normalized_grouped_4000m_xgrid_data],
    ["Updraft", "No wind", "Downdraft"],
    ["Horizontal spread (m) at $y = 2$ km", "Altitude spread (m) at $y = 3$ km", "Altitude spread (m) at $y = 4$ km"],
    os.path.join(plot_dir, "figure_ice_plume_xspread.png"),
    logy=[False, False, False],
    y_axis_ticks=axis_label
)
plot_box_for_updowndraft_comparison((all_2000m_xgrid_data, all_3000m_xgrid_data, all_4000m_xgrid_data), ["2 km", "3 km", "4 km"], "X spread (m)", os.path.join(plot_dir, "figure_box_plume_all_2to4km_xgrid.png"))

plot_9trends(
    plume_state.plume_max_time,
    [
        plume_state.plume_max_qice, plume_state.plume_max_qliq, plume_state.plume_max_qtotal_plus_qv,
        plume_state.plume_max_nice, plume_state.plume_max_nliq, plume_state.plume_max_dice,
        plume_state.plume_max_dliq, plume_state.plume_max_amps_rh, plume_state.plume_max_col_rate,
    ],
    seed_w['min_vertical_wind_speed'],
    "Time (s)",
    [
        "IWC (g m$^{-3}$)", "LWC (g m$^{-3}$)", "TWC (g m$^{-3}$)",
        "Nice (L$^{-1}$)", "Nliq (cm$^{-3}$)", "Dice ($\\mu$m)",
        "Dliq ($\\mu$m)", "RH", "Collision rate (cm$^{-3}$ s$^{-1}$)",
    ],
    [
        "IWC (g m$^{-3}$)", "LWC (g m$^{-3}$)", "TWC (g m$^{-3}$)",
        "Nice (L$^{-1}$)", "Nliq (cm$^{-3}$)", "Dice ($\\mu$m)",
        "Dliq ($\\mu$m)", "RH", "Collision rate (cm$^{-3}$ s$^{-1}$)",
    ],
    os.path.join(plot_dir, "figure_shade_plume_t_trends.png"),
)

plot_3trends(
    plume_state.plume_max_time,
    [
        plume_state.plume_max_nice, plume_state.plume_max_dice, plume_state.plume_max_qice,
    ],
    seed_w['min_vertical_wind_speed'],
    "Time (s)",
    [
        "ICNC (L$^{-1}$)", "Dice ($\\mu$m)", "IWC (g m$^{-3}$)",
    ],
    [
        "ICNC (L$^{-1}$)", "Dice ($\\mu$m)", "IWC (g m$^{-3}$)",
    ],
    os.path.join(plot_dir, "figure_shade_plume_ice_trends.png"),
)

plot_3trends(
    plume_state.plume_max_time,
    [
        plume_state.plume_max_nliq, plume_state.plume_max_dliq, plume_state.plume_max_amps_rh,
    ],
    seed_w['min_vertical_wind_speed'],
    "Time (s)",
    [
        "CDNC (cm$^{-3}$)", "Dliq ($\\mu$m)", "RH",
    ],
    [
        "CDNC (cm$^{-3}$)", "Dliq ($\\mu$m)", "RH",
    ],
    os.path.join(plot_dir, "figure_shade_plume_liq_trends.png"),
)


grouped_plume_2000m_all_qice = extract_grouped_data(plume_state.plume_2000m_all_qice, seed_w['min_vertical_wind_speed'], split=False)
grouped_plume_2000m_all_nice = extract_grouped_data(plume_state.plume_2000m_all_nice, seed_w['min_vertical_wind_speed'], split=False)

grouped_plume_20_threshold = np.nanpercentile(grouped_plume_2000m_all_qice, 20)
grouped_plume_60_threshold = np.nanpercentile(grouped_plume_2000m_all_qice, 60)
grouped_plume_70_threshold = np.nanpercentile(grouped_plume_2000m_all_qice, 70)
grouped_plume_75_threshold = np.nanpercentile(grouped_plume_2000m_all_qice, 75)
grouped_plume_80_threshold = np.nanpercentile(grouped_plume_2000m_all_qice, 80)
grouped_plume_50_threshold = np.nanpercentile(grouped_plume_2000m_all_qice, 50)

import seaborn as sns
plt.close()
fig, ax = plt.subplots(figsize=(6, 4))
print("debug: ", grouped_plume_2000m_all_qice.shape, np.max(grouped_plume_2000m_all_qice), np.min(grouped_plume_2000m_all_qice))
sns.histplot(grouped_plume_2000m_all_qice, bins=30, kde=False)
ax.axvline(grouped_plume_60_threshold, color="blue", linestyle="dashed", lw=1.5, label="60th percentile")
ax.axvline(grouped_plume_70_threshold, color="red", linestyle="dashed", lw=1.5, label="70th percentile")
ax.axvline(grouped_plume_20_threshold, color="yellow", linestyle="dashed", lw=1.5, label="20th percentile")
ax.axvline(grouped_plume_75_threshold, color="green", linestyle="dashed", lw=1.5, label="75th percentile")
ax.axvline(grouped_plume_80_threshold, color="purple", linestyle="dashed", lw=1.5, label="80th percentile")
# ax.axvline(grouped_plume_50_threshold, color="green", linestyle="dashed", lw=1.5, label="50th percentile")
ax.set_xlabel("IWC between 2 and 4 km (g m$^{-3}$)")
ax.set_ylabel("Grid count")
ax.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
ax.legend(frameon=False)
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, "figure_plume_2_and_4km_all_qice_histogram.png"), dpi=500)

grouped_plume_20_threshold = np.nanpercentile(grouped_plume_2000m_all_nice, 20)
grouped_plume_60_threshold = np.nanpercentile(grouped_plume_2000m_all_nice, 60)
grouped_plume_70_threshold = np.nanpercentile(grouped_plume_2000m_all_nice, 70)
grouped_plume_75_threshold = np.nanpercentile(grouped_plume_2000m_all_nice, 75)
grouped_plume_80_threshold = np.nanpercentile(grouped_plume_2000m_all_nice, 80)
grouped_plume_50_threshold = np.nanpercentile(grouped_plume_2000m_all_nice, 50)

plt.close()
fig, ax = plt.subplots(figsize=(6, 4))
sns.histplot(grouped_plume_2000m_all_nice, bins=30, kde=False)
ax.axvline(grouped_plume_60_threshold, color="blue", linestyle="dashed", lw=1.5, label="60th percentile")
ax.axvline(grouped_plume_70_threshold, color="red", linestyle="dashed", lw=1.5, label="70th percentile")
ax.axvline(grouped_plume_20_threshold, color="yellow", linestyle="dashed", lw=1.5, label="20th percentile")
ax.axvline(grouped_plume_75_threshold, color="green", linestyle="dashed", lw=1.5, label="75th percentile")
ax.axvline(grouped_plume_80_threshold, color="purple", linestyle="dashed", lw=1.5, label="80th percentile")
# ax.axvline(grouped_plume_50_threshold, color="green", linestyle="dashed", lw=1.5, label="50th percentile")
ax.set_xlabel("Nice between 2 and 4 km (L$^{-1}$)")
ax.set_ylabel("Grid count")
ax.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
ax.legend(frameon=False)
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, "figure_plume_2_and_4km_all_nice_histogram.png"), dpi=500)

# def extract_spread_data(input_z_data: list[np.ndarray], input_x_data: list[np.ndarray]):
#     spread_data = []
#     assert len(input_z_data) == len(input_x_data), f"Input data length mismatch! {len(input_z_data)}, {len(input_x_data)}"
#     for k in range(len(input_z_data)):
#         concat_input_z_data = None
#         for i in range(len(input_z_data[k])):
#             concat_input_z_data = np.concatenate((concat_input_z_data, np.array(input_z_data[k][i])), axis=0) if concat_input_z_data is not None else np.array(input_z_data[k][i])
#         concat_input_x_data = None
#         for i in range(len(input_x_data[k])):
#             concat_input_x_data = np.concatenate((concat_input_x_data, np.array(input_x_data[k][i])), axis=0) if concat_input_x_data is not None else np.array(input_x_data[k][i])
#         temporary = []
#         if len(concat_input_z_data) > 0:
#             x_unique = np.unique(concat_input_x_data)
#             print(k, " unique x: ", x_unique)
#             for item in x_unique:
#                 mask = np.where(concat_input_x_data == item, True, False)
#                 print(mask)
#                 temporary.append(np.max(concat_input_z_data[mask]) - np.min(concat_input_z_data[mask]))
#             spread_data.append(np.array(temporary) if len(temporary) > 0 else np.nan)
#         else:
#             spread_data.append(np.nan)
#     grouped_data = extract_grouped_data(spread_data)
#     return grouped_data


# # ----------------------------
# # 绘制 3000 m 高度的 PSD
# # ----------------------------

def plot_distribution(x_data, y_data, t_data, seeding_w, xlabel, xlim, title: str, ax=None):
    updraft_data_mask = np.where(seeding_w >= 0.2)[0]
    nowind_data_mask = np.where((seeding_w  < 0.2) & (seeding_w > -0.2))[0]
    downdraft_data_mask = np.where(seeding_w <= -0.2)[0]

    nowind_y_data = np.zeros((nowind_data_mask.shape[0], x_data.shape[0]), dtype=float)
    updraft_y_data = np.zeros((updraft_data_mask.shape[0], x_data.shape[0]), dtype=float)
    downdraft_y_data = np.zeros((downdraft_data_mask.shape[0], x_data.shape[0]), dtype=float)
    filtered_y_data = np.zeros((len(data_files), x_data.shape[0]), dtype=float)
    for k in range(nowind_data_mask.shape[0]):
        nowind_y_data[k] = y_data[nowind_data_mask[k]][t_data[nowind_data_mask[k]]]
    for k in range(updraft_data_mask.shape[0]):
        updraft_y_data[k] = y_data[updraft_data_mask[k]][t_data[updraft_data_mask[k]]]
    for k in range(downdraft_data_mask.shape[0]):
        downdraft_y_data[k] = y_data[downdraft_data_mask[k]][t_data[downdraft_data_mask[k]]]
    for k in range(len(data_files)):
        filtered_y_data[k] = y_data[k][t_data[k]]

    filtered_y_data[filtered_y_data < 1.e-14] = np.nan
    nowind_y_data[nowind_y_data < 1.e-14] = np.nan
    updraft_y_data[updraft_y_data < 1.e-14] = np.nan
    downdraft_y_data[downdraft_y_data < 1.e-14] = np.nan

    nowind_mean = np.nanmean(nowind_y_data, axis=0)
    updraft_mean = np.nanmean(updraft_y_data, axis=0)
    downdraft_mean = np.nanmean(downdraft_y_data, axis=0)

    max_psd = np.nanmax(filtered_y_data, axis=0)
    min_psd = np.nanmin(filtered_y_data, axis=0)

    if ax is None:
        plt.close()
        fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x_data, nowind_mean, color=COL_CALM, lw=1.8, linestyle="solid", label="No wind") # "#311B92"
    ax.plot(x_data, updraft_mean, color=COL_UP, lw=1.8, linestyle="solid", label="Updraft")
    ax.plot(x_data, downdraft_mean, color=COL_DOWN, lw=1.8, linestyle="solid", label="Downdraft")
    ax.fill_between(x_data, min_psd, max_psd, color="gray", alpha=0.175)
    ax.set_xscale("log")
    ax.set_yscale("log")
    if "ice" in title:
        def ticks_format(value, index):
            if value in [300, 600]:   
                return '${0:d}$'.format(int(value))
            else:
                # return '${0:d}\\times10^{{{1:d}}}$'.format(int(base), int(exp))
                return ''
        # ax.set_ylim(1.e-9, 1000)
        # ax.set_yticks([1.e-8, 1.e-6, 1.e-4, 1.e-2, 1.e0, 1.e2])
        ax.set_ylim(1.e-4, 100)
        ax.set_yticks([1.e-3, 1.e-1, 1.e1])
        ax.set_xlim(100, 1000)
        # ax.xaxis.set_minor_formatter(mticker.NullFormatter())
        # ax.set_xticks([100, 300, 600, 1000])
        # ax.xaxis.set_major_locator(mticker.LogLocator(subs=(1,2,)))
        # ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
        # locmin = matplotlib.ticker.LogLocator(base=10.0,subs=(0.2,0.4,0.6,0.8),numticks=12)
        # ax.xaxis.set_minor_locator(locmin)
        # ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        
        # ax.xaxis.set_minor_formatter(mticker.FormatStrFormatter("%d"))
        ax.xaxis.set_minor_formatter(mticker.FuncFormatter(ticks_format))
        
        # xlabels = [item.get_text() for item in ax.get_xticklabels(minor=True)]
        # print("DEBUG XLABELS: ", xlabels)
        # xlabels[1] = "300"
        # xlabels[2] = "600"
        # ax.set_xticklabels(xlabels)
    else:
        ax.set_xlim(xlim[0], xlim[1])
        ax.set_xlabel(xlabel)
    # ax.set_xlabel("Liquid diameter ($\\mu$m)")
    ax.set_ylabel("PSD (cm$^{-3}$ µm$^{-1}$)")
    ax.legend(frameon=False, prop={'size': 13})
    if ax is None:
        plt.tight_layout()
        plt.savefig(os.path.join(plot_dir, title), dpi=500)

def plot_3distributions(x_data, y_data, t_data, seeding_w, xlabel, xlim, filename):
    fig, ax = plt.subplots(figsize=(14.0, 5.0), ncols=3, nrows=1)
    subplot_title_labels = ['(a)', '(b)', '(c)']
    # for i in range(3):
    #     ax[i].set_aspect(1.0/ax[i].get_data_ratio(), adjustable='box')
    for i in range(3):
        plot_distribution(
            x_data=x_data,
            y_data=y_data,
            t_data=t_data[i],
            seeding_w=seeding_w,
            xlabel=xlabel,
            xlim=xlim,
            title=filename,
            ax=ax[i],
        )
    ax[0].set_title("$y = 2$ km")
    ax[1].set_title("$y = 3$ km")
    ax[2].set_title("$y = 4$ km")
    for i in range(3):
        ax[i].set_title(subplot_title_labels[i], loc='left', fontsize='medium')
    for i in range(3):
        if i != 0:
            ax[i].yaxis.set_ticklabels([])
            ax[i].set_ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, filename), dpi=500, bbox_inches="tight")
    plt.close()
    print(f"  → 保存 {os.path.basename(filename)}")


def plot_9distributions(x_data, y_data_1, y_data_2, y_data_3, t_data, seeding_w, xlabel, xlim, filename):
    fig, ax = plt.subplots(figsize=(15.0, 15.0), ncols=3, nrows=3)
    flat_ax = ax.flatten()
    subplot_title_labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)', '(g)', '(h)', '(i)']
    for i in range(9):
        if i < 3:
            y_data = y_data_1
        elif i < 6:
            y_data = y_data_2
        else:
            y_data = y_data_3
        t_now = t_data[i % 3]
        plot_distribution(
            x_data=x_data,
            y_data=y_data,
            t_data=t_now,
            seeding_w=seeding_w,
            xlabel=xlabel,
            xlim=xlim,
            title=filename,
            ax=flat_ax[i],
        )
    flat_ax[0].set_title("$y = 2$ km, $z = 350$m")
    flat_ax[1].set_title("$y = 3$ km, $z = 350$m")
    flat_ax[2].set_title("$y = 4$ km, $z = 350$m")
    flat_ax[3].set_title("$y = 2$ km, $z = 450$m")
    flat_ax[4].set_title("$y = 3$ km, $z = 450$m")
    flat_ax[5].set_title("$y = 4$ km, $z = 450$m")
    flat_ax[6].set_title("$y = 2$ km, $z = 550$m")
    flat_ax[7].set_title("$y = 3$ km, $z = 550$m")
    flat_ax[8].set_title("$y = 4$ km, $z = 550$m")
    for i in range(9):
        flat_ax[i].set_title(subplot_title_labels[i], loc='left', fontsize='medium')
    for i in range(9):
        if i % 3 != 0:
            flat_ax[i].yaxis.set_ticklabels([])
            flat_ax[i].set_ylabel("")
        if i < 6:
            flat_ax[i].xaxis.set_ticklabels([])
            flat_ax[i].set_xlabel("")
            flat_ax[i].xaxis.set_minor_formatter(mticker.NullFormatter())
    # plt.subplots_adjust(hspace=0.15, wspace=0.05)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, filename), dpi=500, bbox_inches="tight")
    plt.close()
    print(f"  → 保存 {os.path.basename(filename)}")


def _trim_empty_bins(edges, values, min_keep_nonzero=5):
    """裁掉末尾空 bin"""
    edges = np.asarray(edges, float)
    values = np.asarray(values, float)
    if np.all(~np.isfinite(values)) or np.nanmax(values) <= 0:
        return edges, values
    nz = np.where(np.isfinite(values) & (values > 0.1))[0]
    if len(nz) == 0:
        return edges, values
    last = nz[-1]
    keep = max(last + 1, min_keep_nonzero)
    if keep < len(values):
        edges = edges[:keep + 1]
        values = values[:keep]
        return keep
    else:
        return len(values)
    # return edges, values

X_MIN_PLOT = 0
X_MAX_PLOT = 1600

def _slice_edges_for_plot(edges, values, xmin=X_MIN_PLOT, xmax=X_MAX_PLOT):
    """限制绘图范围"""
    edges = np.asarray(edges, float)
    values = np.asarray(values, float)
    left = np.searchsorted(edges, xmin, side="left")
    right = np.searchsorted(edges, xmax, side="right")
    left = max(0, min(left, len(edges) - 2))
    right = max(left + 2, min(right, len(edges)))
    # return edges[left:right], values[left:right - 1]
    return left, right

def plot_stair_equalx(values, obs_data, edges, left_index, right_index, x_idx, ylabel, legend_label, ylim, out_path, color, plot_obs=False, put_legend=False, ax=None):

    labels = [str(int(v)) for v in edges[left_index:right_index]]

    if ax is None:
        plt.close()
        fig, ax = plt.subplots(figsize=(5.2, 3.8))
    ax.stairs(values[left_index:right_index-1], x_idx, color=color, linewidth=1.6,
              label=legend_label)
    if plot_obs:
        ax.stairs(obs_data[left_index:right_index-1], x_idx, color='black', linewidth=1.6,
                label="Obs.")

    ax.set_xlim(x_idx[0], x_idx[-1])
    ax.set_xlabel("Diameter ($\\mu$m)")
    ax.set_ylabel(ylabel)
    if put_legend:
        ax.legend(frameon=False)
    ax.set_xticks(np.arange(len(labels)))
    labels[0] = ""
    ax.set_xticklabels(labels, rotation=60, ha="right")
    ax.set_ylim(0, ylim)
    
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if out_path is not None:
        fig.tight_layout()
        fig.savefig(out_path, dpi=500)
        plt.close(fig)
        print(f"  → 保存 {os.path.basename(out_path)} ✅")


def plot_3stairs_equalx(values, obs_data, edges, left_index, right_index, x_idx, ylabel, legend_label, ylim, out_path, color, plot_obs=False, put_legend=False, ax=None):

    labels = [str(int(v)) for v in edges[left_index:right_index]]

    if ax is None:
        plt.close()
        fig, ax = plt.subplots(figsize=(5.2, 3.8))
    ax.stairs(values[left_index:right_index-1], x_idx, color=color, linewidth=1.6,
              label=legend_label)
    if plot_obs:
        ax.stairs(obs_data[left_index:right_index-1], x_idx, color='black', linewidth=1.6,
                label="Obs.")

    ax.set_xlim(x_idx[0], x_idx[-1])
    ax.set_xlabel("Diameter ($\\mu$m)")
    ax.set_ylabel(ylabel)
    if put_legend:
        ax.legend(frameon=False)
    ax.set_xticks(np.arange(len(labels)))
    labels[0] = ""
    ax.set_xticklabels(labels, rotation=60, ha="right")
    ax.set_ylim(0, ylim)
    
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if out_path is not None:
        fig.tight_layout()
        fig.savefig(out_path, dpi=500)
        plt.close(fig)
        print(f"  → 保存 {os.path.basename(out_path)} ✅")


def plot_upnodown_dists(edge_data, x_data, y_data, t_data, seeding_w, ylabel, filename: str):
    assert len(t_data) == 3, "Length of time data is not 3!"
    
    updraft_data_mask = np.where(seeding_w >= 0.2)[0]
    nowind_data_mask = np.where((seeding_w  < 0.2) & (seeding_w > -0.2))[0]
    downdraft_data_mask = np.where(seeding_w <= -0.2)[0]

    nowind_y_data = np.zeros((3, nowind_data_mask.shape[0], x_data.shape[0]), dtype=float)
    updraft_y_data = np.zeros((3, updraft_data_mask.shape[0], x_data.shape[0]), dtype=float)
    downdraft_y_data = np.zeros((3, downdraft_data_mask.shape[0], x_data.shape[0]), dtype=float)
    for t, time_now in enumerate(t_data):
        for k in range(nowind_data_mask.shape[0]):
            nowind_y_data[t, k] = y_data[nowind_data_mask[k]][time_now[nowind_data_mask[k]]]
        for k in range(updraft_data_mask.shape[0]):
            updraft_y_data[t, k] = y_data[updraft_data_mask[k]][time_now[updraft_data_mask[k]]]
        for k in range(downdraft_data_mask.shape[0]):
            downdraft_y_data[t, k] = y_data[downdraft_data_mask[k]][time_now[downdraft_data_mask[k]]]

    total_nowind_y_data = np.sum(nowind_y_data, axis=1)
    total_updraft_y_data = np.sum(updraft_y_data, axis=1)
    total_downdraft_y_data = np.sum(downdraft_y_data, axis=1)
    
    total_sum_nowind = np.nansum(total_nowind_y_data, axis=1)
    total_sum_updraft = np.nansum(total_updraft_y_data, axis=1)
    total_sum_downdraft = np.nansum(total_downdraft_y_data, axis=1)
    for t in range(3):
        total_nowind_y_data[t] = total_nowind_y_data[t] / total_sum_nowind[t] * 100
        total_updraft_y_data[t] = total_updraft_y_data[t] / total_sum_updraft[t] * 100
        total_downdraft_y_data[t] = total_downdraft_y_data[t] / total_sum_downdraft[t] * 100
    # total_nowind_y_data = total_nowind_y_data / total_sum_nowind * 100
    # total_updraft_y_data = total_updraft_y_data / total_sum_updraft * 100
    # total_downdraft_y_data = total_downdraft_y_data / total_sum_downdraft * 100
    
    # for t in range(3):
    #     print(t)
    #     for k in range(x_data.shape[0]):
    #         print(f"  Diameter bin: {x_data[k]:.5f} µm - {total_updraft_y_data[t,k]:.5f} {total_nowind_y_data[t,k]:.5f} {total_downdraft_y_data[t,k]:.5f}")
    
    fig, ax = plt.subplots(figsize=(14.0, 6.0), ncols=3, nrows=1)
    # colors = cmc.batlow(np.linspace(0.35, 0.75, 4))
    colors = [
        "#d12734",
        "#005945", #"#f3eed9",
        "#66b1f3",
    ]
    
    obs_ice_percentage_count = ice_distribution_data["obs_ice_percentage_count"]
    obs_mean_acratio = ice_distribution_data["obs_mean_acratio"]

    # edges, values = _trim_empty_bins(edges, values)
    # edges, values = _slice_edges_for_plot(edges, values)
    obs_data = obs_ice_percentage_count
    obs_keep_index = _trim_empty_bins(edge_data, obs_data)
    obs_left_index, obs_right_index = _slice_edges_for_plot(edge_data[:obs_keep_index+1], obs_data[:obs_keep_index])
    keep_index = _trim_empty_bins(edge_data, total_updraft_y_data[2])
    left_index, right_index = _slice_edges_for_plot(edge_data[:keep_index+1], total_updraft_y_data[2,:keep_index])
    left_index = min(left_index, obs_left_index)
    right_index = max(right_index, obs_right_index)
    x_idx = np.arange(len(total_updraft_y_data[2,left_index:right_index-1]) + 1)
    print(obs_keep_index, obs_left_index, obs_right_index)
    print(keep_index, left_index, right_index)
    print(x_idx)
    ylim = np.nanmax(total_updraft_y_data[2,left_index:right_index-1]) * 1.15 if np.isfinite(np.nanmax(total_updraft_y_data[2,left_index:right_index-1])) else 1

    legend_label = ("Updraft", "No wind", "Downdraft")
    for t in range(3):
        i = 0
        for input_data in (total_updraft_y_data[t], total_nowind_y_data[t], total_downdraft_y_data[t]):
            plot_stair_equalx(
                input_data,
                obs_data,
                edge_data,
                left_index,
                right_index,
                x_idx,
                "Ice count percentage",
                legend_label[i],
                ylim=ylim,
                out_path=None,
                # color=colors[1] if "count" in ylabel[i].lower() else colors[2],
                color=colors[i], # "#005945"
                plot_obs=False,
                put_legend=i==2,
                ax=ax[t],
            )
            i += 1
    subplot_title_labels = ['(a)', '(b)', '(c)']
    ax[0].set_title("$y = 2$ km")
    ax[1].set_title("$y = 3$ km")
    ax[2].set_title("$y = 4$ km")
    for i in range(3):
        ax[i].set_title(subplot_title_labels[i], loc='left', fontsize='medium')
    for i in range(3):
        if i != 0:
            ax[i].yaxis.set_ticklabels([])
            ax[i].set_ylabel("")
    plt.tight_layout()
    plt.savefig(filename, dpi=500, bbox_inches="tight")
    plt.close()
    print(f"  → 保存 {os.path.basename(filename)}")

plot_distribution(plume_data.liq_diameter_bnd, plume_state.plume_max_liq_psd, plume_state.plume_2000m_time, seed_w['min_vertical_wind_speed'], "Liquid diameter ($\\mu$m)", (0.1, 100), "figure_plume_2000m_liq_psd")
plot_distribution(plume_data.liq_diameter_bnd, plume_state.plume_max_liq_psd, plume_state.plume_3000m_time, seed_w['min_vertical_wind_speed'], "Liquid diameter ($\\mu$m)", (0.1, 100), "figure_plume_3000m_liq_psd")
plot_distribution(plume_data.liq_diameter_bnd, plume_state.plume_max_liq_psd, plume_state.plume_4000m_time, seed_w['min_vertical_wind_speed'], "Liquid diameter ($\\mu$m)", (0.1, 100), "figure_plume_4000m_liq_psd")
plot_distribution(plume_data.ice_diameter_bnd, plume_state.plume_max_ice_psd, plume_state.plume_2000m_time, seed_w['min_vertical_wind_speed'], "Ice diameter ($\\mu$m)", (100, 1000), "figure_plume_2000m_ice_psd")
plot_distribution(plume_data.ice_diameter_bnd, plume_state.plume_max_ice_psd, plume_state.plume_3000m_time, seed_w['min_vertical_wind_speed'], "Ice diameter ($\\mu$m)", (100, 1000), "figure_plume_3000m_ice_psd")
plot_distribution(plume_data.ice_diameter_bnd, plume_state.plume_max_ice_psd, plume_state.plume_4000m_time, seed_w['min_vertical_wind_speed'], "Ice diameter ($\\mu$m)", (100, 1000), "figure_plume_4000m_ice_psd")

plot_3distributions(
    plume_data.ice_diameter_bnd,
    plume_state.plume_max_ice_psd,
    [plume_state.plume_2000m_time, plume_state.plume_3000m_time, plume_state.plume_4000m_time],
    seed_w['min_vertical_wind_speed'],
    "Ice diameter ($\\mu$m)",
    (100, 1000),
    "figure_ice_psd.png",
)

plot_9distributions(
    plume_data.ice_diameter_bnd,
    plume_state.plume_max_ice_psd_350,
    plume_state.plume_max_ice_psd_450,
    plume_state.plume_max_ice_psd_550,
    [plume_state.plume_2000m_time, plume_state.plume_3000m_time, plume_state.plume_4000m_time],
    seed_w['min_vertical_wind_speed'],
    "Ice diameter ($\\mu$m)",
    (100, 1000),
    "figure_ice_psd_at_fixed_altitudes.png",
)

for psd in ("plume_max_ice_psd_300", "plume_max_ice_psd_350", "plume_max_ice_psd_400", "plume_max_ice_psd_450", "plume_max_ice_psd_500", "plume_max_ice_psd_550"):
    temp_filename = f"figure_ice_psd_{psd[-3:]}.png"
    plot_3distributions(
        plume_data.ice_diameter_bnd,
        getattr(plume_state, psd),
        [plume_state.plume_2000m_time, plume_state.plume_3000m_time, plume_state.plume_4000m_time],
        seed_w['min_vertical_wind_speed'],
        "Ice diameter ($\\mu$m)",
        (100, 1000),
        temp_filename,
    )

plt.rcParams.update({
    "xtick.top": False,
    "ytick.right": False,
})

plot_upnodown_dists(
    plume_data.ice_diameter_bnd,
    plume_data.ice_diameter,
    plume_state.plume_max_ice_count,
    [plume_state.plume_2000m_time, plume_state.plume_3000m_time, plume_state.plume_4000m_time],
    seed_w['min_vertical_wind_speed'],
    "Ice diameter ($\\mu$m)", os.path.join(plot_dir, "figure_plume_2_to_4km_ice_count_psd")
)

for count in ("plume_max_ice_count_300", "plume_max_ice_count_350", "plume_max_ice_count_400", "plume_max_ice_count_450", "plume_max_ice_count_500", "plume_max_ice_count_550"):
    temp_filename = f"figure_plume_2_to_4km_psd_{count[-3:]}.png"
    plot_upnodown_dists(
        plume_data.ice_diameter_bnd,
        plume_data.ice_diameter,
        getattr(plume_state, count),
        [plume_state.plume_2000m_time, plume_state.plume_3000m_time, plume_state.plume_4000m_time],
        seed_w['min_vertical_wind_speed'],
        "Ice diameter ($\\mu$m)", os.path.join(plot_dir, temp_filename)
    )
# # -------- Liquid PSD --------
# plt.close()
# fig, ax = plt.subplots(figsize=(6, 4))
# ax.plot(liq_diameter_bnd, mean_updraft_liq_psd, color="indianred", lw=1.8, label="Median")
# ax.plot(liq_diameter_bnd, mean_updraft_liq_psd, color="indianred", lw=1.8, label="Median")
# ax.fill_between(liq_diameter_bnd, min_updraft_liq_psd, max_updraft_liq_psd,
#                 color="indianred", alpha=0.25, label="Range")
# ax.set_xscale("log")
# ax.set_xlim(0.1, 100)
# ax.set_xlabel("Liquid diameter ($\\mu$m)")
# ax.set_ylabel("PSD (cm$^{-3}$ µm$^{-1}$)")
# ax.legend(frameon=False)
# plt.tight_layout()
# plt.savefig(os.path.join(plot_dir, "figure_plume_3000m_liq_psd.png"), dpi=800)

# # -------- Ice PSD --------
# plt.close()
# fig, ax = plt.subplots(figsize=(6, 4))
# ax.plot(ice_diameter_bnd, mean_updraft_ice_psd, color="black", lw=1.8, label="Median")
# ax.fill_between(ice_diameter_bnd, min_updraft_ice_psd, max_updraft_ice_psd,
#                 color="steelblue", alpha=0.3, label="Range")
# ax.set_xscale("log")
# ax.set_yscale("log")
# ax.set_xlim(10, 1000)
# ax.set_ylim(1e-8, 1e3)
# ax.set_xlabel("Ice diameter ($\\mu$m)")
# ax.set_ylabel("PSD (cm$^{-3}$ µm$^{-1}$)")
# ax.legend(frameon=False)
# plt.tight_layout()
# plt.savefig(os.path.join(plot_dir, "figure_plume_3000m_ice_psd.png"), dpi=800)


plt.close()
fig, ax = plt.subplots(figsize=(6, 4))
filtered_reduced_w_data = np.zeros((len(data_files), max_plume_3000m_time), dtype=float)
for k, item in enumerate(plume_state.plume_max_reduced_w):
    filtered_reduced_w_data[k] = item[:max_plume_3000m_time]
filtered_heat_data = np.zeros((len(data_files), max_plume_3000m_time), dtype=float)
for k, item in enumerate(plume_state.plume_max_accumulated_heat_release):
    filtered_heat_data[k] = item[:max_plume_3000m_time]
min_reduced_w_data = np.min(filtered_reduced_w_data, axis=0)
max_reduced_w_data = np.max(filtered_reduced_w_data, axis=0)
updraft_data_mask = np.where(seed_w['min_vertical_wind_speed'] >= 0.2)[0]
nowind_data_mask = np.where((seed_w['min_vertical_wind_speed']  < 0.2) & (seed_w['min_vertical_wind_speed'] > -0.2))[0]
downdraft_data_mask = np.where(seed_w['min_vertical_wind_speed'] <= -0.2)[0]
updraft_reduced_w_data = filtered_reduced_w_data[updraft_data_mask, :]
nowind_reduced_w_data = filtered_reduced_w_data[nowind_data_mask, :]
downdraft_reduced_w_data = filtered_reduced_w_data[downdraft_data_mask, :]
updraft_heat_data = filtered_heat_data[updraft_data_mask, :]
nowind_heat_data = filtered_heat_data[nowind_data_mask, :]
downdraft_heat_data = filtered_heat_data[downdraft_data_mask, :]
ax.plot(updraft_heat_data, updraft_reduced_w_data, 'o', color='indianred')
ax.plot(nowind_heat_data, nowind_reduced_w_data, 'o', color='yellowgreen')
ax.plot(downdraft_heat_data, downdraft_reduced_w_data, 'o', color='blue')
for k in range(updraft_heat_data.shape[0]):
    ax.plot(updraft_heat_data[k], updraft_reduced_w_data[k], '-', color='indianred')
for k in range(nowind_heat_data.shape[0]):
    ax.plot(nowind_heat_data[k], nowind_reduced_w_data[k], '-', color='yellowgreen')
for k in range(downdraft_heat_data.shape[0]):
    index = downdraft_data_mask[k]
    # print("   ===   ", k, seed_w['min_vertical_wind_speed'][index])
    # for i in range(downdraft_heat_data.shape[1]):
    #     print(downdraft_heat_data[k][i], downdraft_reduced_w_data[k][i])
    ax.plot(downdraft_heat_data[k], downdraft_reduced_w_data[k], '-', color='blue')
ax.legend(frameon=False)

plt.tight_layout()
plt.savefig(os.path.join(plot_dir, f"figure_heat_and_w.png"), dpi=500)


plt.close()
fig, ax = plt.subplots(figsize=(6, 4))
def extract_double_list(mask, xdata, zdata) -> tuple[np.ndarray, np.ndarray]:
    output_x_data, output_z_data = None, None
    for k in range(len(data_files)):
        if k in mask:
            for i in range(len(xdata[k])):
                output_x_data = np.concatenate((output_x_data, np.array(xdata[k][i])), axis=0) if output_x_data is not None else np.array(xdata[k][i])
            for i in range(len(zdata[k])):
                output_z_data = np.concatenate((output_z_data, np.array(zdata[k][i])), axis=0) if output_z_data is not None else np.array(zdata[k][i])
    return output_x_data, output_z_data
updraft_x_data, updraft_z_data = extract_double_list(updraft_data_mask, plume_state.plume_2000m_xgrid, plume_state.plume_2000m_zgrid)
nowind_x_data, nowind_z_data = extract_double_list(nowind_data_mask, plume_state.plume_2000m_xgrid, plume_state.plume_2000m_zgrid)
downdraft_x_data, downdraft_z_data = extract_double_list(downdraft_data_mask, plume_state.plume_2000m_xgrid, plume_state.plume_2000m_zgrid)
ax.plot(updraft_x_data, updraft_z_data, 'o', color='indianred')
ax.plot(nowind_x_data, nowind_z_data, 'o', color='yellowgreen')
ax.plot(downdraft_x_data, downdraft_z_data, 'o', color='blue')
updraft_data, updraft_xedges, updraft_yedges = np.histogram2d(updraft_x_data, updraft_z_data)
nowind_data, nowind_xedges, nowind_yedges = np.histogram2d(nowind_x_data, nowind_z_data)
downdraft_data, downdraft_xedges, downdraft_yedges = np.histogram2d(downdraft_x_data, downdraft_z_data)
# ax.contourf(updraft_data, extent=[updraft_xedges[0], updraft_xedges[-1], updraft_yedges[0], updraft_yedges[-1]], colors='indianred', linewidths=1.5, alpha=0.4)
# ax.contourf(nowind_data, extent=[nowind_xedges[0], nowind_xedges[-1], nowind_yedges[0], nowind_yedges[-1]], colors='yellowgreen', linewidths=1.5, alpha=0.4)
# ax.contourf(downdraft_data, extent=[downdraft_xedges[0], downdraft_xedges[-1], downdraft_yedges[0], downdraft_yedges[-1]], colors='blue', linewidths=1.5, alpha=0.4)

ax.legend(frameon=False)

plt.tight_layout()
plt.savefig(os.path.join(plot_dir, f"figure_plume_region_at_2000m.png"), dpi=500)


# for summary table

def print_summary(data, title):
    updraft_data_mask = np.where(seed_w['min_vertical_wind_speed'] >= 0.2)[0]
    nowind_data_mask = np.where((seed_w['min_vertical_wind_speed']  < 0.2) & (seed_w['min_vertical_wind_speed'] > -0.2))[0]
    downdraft_data_mask = np.where(seed_w['min_vertical_wind_speed'] <= -0.2)[0]

    nowind_data = np.zeros(nowind_data_mask.shape[0], dtype=float)
    updraft_data = np.zeros(updraft_data_mask.shape[0], dtype=float)
    downdraft_data = np.zeros(downdraft_data_mask.shape[0], dtype=float)
    for k in range(nowind_data_mask.shape[0]):
        nowind_data[k] = data[nowind_data_mask[k]][plume_state.plume_2000m_time[nowind_data_mask[k]]]
    for k in range(updraft_data_mask.shape[0]):
        updraft_data[k] = data[updraft_data_mask[k]][plume_state.plume_2000m_time[updraft_data_mask[k]]]
    for k in range(downdraft_data_mask.shape[0]):
        downdraft_data[k] = data[downdraft_data_mask[k]][plume_state.plume_2000m_time[downdraft_data_mask[k]]]

    print(title, " 2000m", np.nanmean(plume_state.plume_2000m_time))
    print("Nowind mean std:", np.nanmean(nowind_data), np.nanstd(nowind_data))
    print("Updraft mean std:", np.nanmean(updraft_data), np.nanstd(updraft_data))
    print("Downdraft mean std:", np.nanmean(downdraft_data), np.nanstd(downdraft_data))

    nowind_data = np.zeros(nowind_data_mask.shape[0], dtype=float)
    updraft_data = np.zeros(updraft_data_mask.shape[0], dtype=float)
    downdraft_data = np.zeros(downdraft_data_mask.shape[0], dtype=float)
    for k in range(nowind_data_mask.shape[0]):
        nowind_data[k] = data[nowind_data_mask[k]][plume_state.plume_3000m_time[nowind_data_mask[k]]]
    for k in range(updraft_data_mask.shape[0]):
        updraft_data[k] = data[updraft_data_mask[k]][plume_state.plume_3000m_time[updraft_data_mask[k]]]
    for k in range(downdraft_data_mask.shape[0]):
        downdraft_data[k] = data[downdraft_data_mask[k]][plume_state.plume_3000m_time[downdraft_data_mask[k]]]

    print(title, " 3000m", np.nanmean(plume_state.plume_3000m_time))
    print("Nowind mean std:", np.nanmean(nowind_data), np.nanstd(nowind_data))
    print("Updraft mean std:", np.nanmean(updraft_data), np.nanstd(updraft_data))
    print("Downdraft mean std:", np.nanmean(downdraft_data), np.nanstd(downdraft_data))

    nowind_data = np.zeros(nowind_data_mask.shape[0], dtype=float)
    updraft_data = np.zeros(updraft_data_mask.shape[0], dtype=float)
    downdraft_data = np.zeros(downdraft_data_mask.shape[0], dtype=float)
    for k in range(nowind_data_mask.shape[0]):
        nowind_data[k] = data[nowind_data_mask[k]][plume_state.plume_4000m_time[nowind_data_mask[k]]]
    for k in range(updraft_data_mask.shape[0]):
        updraft_data[k] = data[updraft_data_mask[k]][plume_state.plume_4000m_time[updraft_data_mask[k]]]
    for k in range(downdraft_data_mask.shape[0]):
        downdraft_data[k] = data[downdraft_data_mask[k]][plume_state.plume_4000m_time[downdraft_data_mask[k]]]

    print(title, " 4000m", np.nanmean(plume_state.plume_4000m_time))
    print("Nowind mean std:", np.nanmean(nowind_data), np.nanstd(nowind_data))
    print("Updraft mean std:", np.nanmean(updraft_data), np.nanstd(updraft_data))
    print("Downdraft mean std:", np.nanmean(downdraft_data), np.nanstd(downdraft_data))

    print()



# print_summary(plume_max_nice, "nice")
# print_summary(plume_max_nliq, "nliq")
# print_summary(plume_max_dice, "dice")
# print_summary(plume_max_dliq, "dliq")
# print_summary(plume_max_qice, "iwc")
# print_summary(plume_max_qliq, "lwc")
# print_summary(plume_max_col_rate, "col_rate")

print("LOG -- END")

