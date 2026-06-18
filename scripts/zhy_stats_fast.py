# -*- coding: utf-8 -*-
"""
fix_point_statistics_plot_z400_profile.py
--------------------------------
沿 y 方向剖面绘图（仅使用 x≈1000±20 m, z≈400±30 m 且 ice>0 的格点）
"""

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import re
import xarray as xr
import pandas as pd

from stats_plot.plot_functions import plot_profile, plot_box_for_sim_obs_comparison, plot_4boxes_for_sim_obs_comparison

# ----------------------------
# 路径配置
# ----------------------------
DIR = os.path.realpath(os.path.dirname(__file__))
print(f"📂 工作目录: {DIR}")
# DATA_DIR = os.path.abspath(os.path.join(DIR, "./data/plots"))
DATA_DIR = os.path.realpath("/capstor/store/cscs/userlab/cwd01/cong/plume_data")
DATA_DIR_SPECIAL = os.path.realpath("/capstor/store/cscs/userlab/cwd01/cong/plume_data/new_ice_mass/")
PLOT_ROOT = os.path.join(DIR, "./plots_z400_x1000")
PER_EXP_DIR = os.path.join(PLOT_ROOT, "per_experiment")
os.makedirs(PER_EXP_DIR, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 17,
    "axes.labelsize": 18,
    "axes.titlesize": 18,
    "axes.linewidth": 0.8,
    "axes.edgecolor": "#333333",
    "xtick.direction": "in",
    "ytick.direction": "in",
    "grid.color": "#dddddd",
    "grid.linestyle": "--",
    "grid.linewidth": 0.5,
    "legend.fontsize": 9,
    "lines.linewidth": 1.4,
})


obs_col_rate_data = pd.read_csv('/capstor/store/cscs/userlab/cwd01/cong/plume_data/obs_data/SM054_col_rate.csv')
obs_col_rate = obs_col_rate_data['obs_col_rate']
observation_data = xr.open_zarr("/capstor/store/cscs/userlab/cwd01/cong/plume_data/obs_data/liq_ice_count_and_col_rate.zarr")
obs_ice_count = observation_data["obs_ice_count"]
obs_liq_count = observation_data["obs_liq_count"]
obs_liq_content = observation_data["obs_liq_content"]

# ======================================================
# 辅助函数
# ======================================================
def parse_label(name: str):
    """提取文件名中的实验标签"""
    base = os.path.basename(name).replace("_data.pkl", "")
    duration = re.search(r"(\d+min)", base)
    altitude = re.search(r"altitude(\d+m)", base)
    duration = duration.group(1) if duration else "unknown"
    altitude = altitude.group(1) if altitude else "unknown"
    return f"{duration}_{altitude}"


def setup_plot_style():
    plt.rcParams.update({
        "axes.linewidth": 0.8,
        "axes.edgecolor": "#333333",
        "grid.color": "#dddddd",
        "grid.linestyle": "--",
        "grid.linewidth": 0.5,
    })


def compute_profile_with_ice_mask(
    x_list, y_list, z_list,
    var_list, ice_list,
    x_targets=(1000,), dx=10,
    z_targets=(410, 430, 450), dz=10,
    dy=100,
    nice_thresh=1e-2,
    y_domain_max=3990.0,
    end_frac=0.98,
    debug=True,
):
    """
    只累积 plume 的第一轮；并打印每个 timestep 在 x–z 窗口内
    第一次出现 ice 的 y 范围（未裁剪）以及参与统计的 y 范围（裁剪后）。
    """
    y_end_cutoff = end_frac * y_domain_max
    all_y, all_v = [], []
    reached_end = False
    prev_ymax = None
    first_seen_t = None  # 第一次看到 plume 的时刻

    for t_idx, (x, y, z, v, ice) in enumerate(zip(x_list, y_list, z_list, var_list, ice_list)):
        if reached_end:
            break

        x, y, z, v, ice = map(np.asarray, (x, y, z, v, ice))
        assert x.shape == z.shape == y.shape

        # 组合 z 窗口
        mask_z = np.zeros_like(z, dtype=bool)
        for zt in z_targets:
            mask_z |= (np.abs(z - zt) <= dz)
        mask_x = np.zeros_like(x, dtype=bool)
        for xt in x_targets:
            mask_x |= (np.abs(x - xt) <= dx)

        # —— “未裁剪”的 plume 掩码：只看 x/z 与 ice 阈值，用来判断 plume 是否出现 & wrap —— #
        raw_mask = (
            np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
            # & (x >= target_x - dx) & (x <= target_x + dx)
            & mask_x
            & mask_z
            & (ice > nice_thresh)
        )

        if not np.any(raw_mask):
            # 这个时刻在切片里还没有 plume
            continue

        # 记录第一次看到 plume 的时刻和 y 范围
        if first_seen_t is None:
            first_seen_t = t_idx

        y_raw = y[raw_mask]
        y_raw_min = float(np.nanmin(y_raw))
        y_raw_max = float(np.nanmax(y_raw))

        # —— “裁剪后”的统计掩码：再加上 y 限制 —— #
        use_mask = raw_mask & (y > 0.0) & (y <= y_end_cutoff)

        if not np.any(use_mask):
            # 有 plume，但都被 y 限制裁掉了（例如 wrap 到 0 附近）
            if debug:
                print(f"[t={t_idx:03d}] plume(raw) y=[{y_raw_min:.1f},{y_raw_max:.1f}] -> after-cut: empty")
            continue

        y_this = y[use_mask]
        v_this = v[use_mask]

        # 调试输出：这个时刻参与统计的 y 范围和样本数
        if debug:
            print(
                f"[t={t_idx:03d}] plume(raw) y=[{y_raw_min:.1f},{y_raw_max:.1f}]  "
                f"used y=[{np.nanmin(y_this):.1f},{np.nanmax(y_this):.1f}], n={y_this.size}"
            )

        all_y.append(y_this)
        all_v.append(v_this)

        # ---- wrap-around 检测（用未裁剪的 ymax） ----
        ymax_now = y_raw_max
        if prev_ymax is not None and ymax_now < prev_ymax * 0.5:
            if debug:
                print(f"⛔ wrap-around detected at t={t_idx:03d}: ymax {prev_ymax:.0f} → {ymax_now:.0f}. stop.")
            reached_end = True
            break
        prev_ymax = ymax_now

        # ---- 到达顶部 cutoff 也停止 ----
        if y_raw_max >= y_end_cutoff:
            if debug:
                print(f"⛔ reach top at t={t_idx:03d}: y_raw_max={y_raw_max:.0f} ≥ {y_end_cutoff:.0f}. stop.")
            reached_end = True
            break

    if not all_y:
        if debug:
            print("⚠️ 没有任何 timestep 进入统计（可能 plume 未形成或全部被裁剪）。")
        return None, None, None

    # 汇总后再做 y 分箱
    all_y = np.concatenate(all_y)
    all_v = np.concatenate(all_v)

    if debug:
        print(f"📊 累积（第一轮）样本: {all_y.size} 个, y范围=[{np.nanmin(all_y):.1f},{np.nanmax(all_y):.1f}] m; "
              f"first plume at t={first_seen_t}")

    y_min, y_max = np.nanmin(all_y), np.nanmax(all_y)
    bins = np.arange(y_min, y_max + dy, dy)
    if len(bins) < 2:
        bins = np.array([y_min, y_min + dy])
    y_center = 0.5 * (bins[:-1] + bins[1:])

    v_mean, v_std = [], []
    for i in range(len(bins) - 1):
        sel = (all_y >= bins[i]) & (all_y < bins[i + 1])
        if np.any(sel):
            vals = np.abs(all_v[sel])
            v_mean.append(np.nanmean(vals))
            v_std.append(np.nanstd(vals))
        else:
            v_mean.append(np.nan)
            v_std.append(np.nan)
    sel = (all_y >= 2000.0) & (all_y < 2050.0)
    if np.any(sel):
        vals_2000m = np.abs(all_v[sel])
    else:
        vals_2000m = None
    return y_center, np.array(v_mean), np.array(v_std), vals_2000m


# ======================================================
# 主循环
# ======================================================
pkl_files = sorted([
    os.path.join(DATA_DIR, f)
    for f in os.listdir(DATA_DIR)
    if f.endswith("_data.pkl")
])
for i, file in enumerate(pkl_files):
    if '_9min' in file:
        for f in os.listdir(DATA_DIR_SPECIAL):
            if f.endswith("_data.pkl") and '9min' in f:
                print("repalcing", file, "with", f)
                pkl_files[i] = os.path.join(DATA_DIR_SPECIAL, f)

print(f"🧊 找到 {len(pkl_files)} 个 plume 文件")

for f in pkl_files:
    # if '_9min' not in f:
    #     continue
    with open(f, "rb") as handle:
        ds = pickle.load(handle)

    label = parse_label(f)
    print(f"\n🎨 绘制实验: {label}")

    out_dir = os.path.join(PER_EXP_DIR, label)
    os.makedirs(out_dir, exist_ok=True)

    # ---- 仅统计 ice>0 的格点 ----
    y_col, col_med, _, col_2000m = compute_profile_with_ice_mask(
        ds["plume_location_x"], ds["plume_location_y"], ds["plume_location_z"],
        ds["plume_col_rate"], ds["plume_nice"],
        x_targets=(990, 1010), dx=10, z_targets=(410, 430, 450), dz=10
    )
    y_ice, ice_med, _, ice_2000m = compute_profile_with_ice_mask(
        ds["plume_location_x"], ds["plume_location_y"], ds["plume_location_z"],
        ds["plume_nice"], ds["plume_nice"],
        x_targets=(990, 1010), dx=10, z_targets=(410, 430, 450), dz=10
    )
    y_liq, liq_med, _, liq_2000m = compute_profile_with_ice_mask(
        ds["plume_location_x"], ds["plume_location_y"], ds["plume_location_z"],
        ds["plume_nliq"], ds["plume_nice"],
        x_targets=(990, 1010), dx=10, z_targets=(410, 430, 450), dz=10
    )
    y_lwc, lwc_med, _, lwc_2000m = compute_profile_with_ice_mask(
        ds["plume_location_x"], ds["plume_location_y"], ds["plume_location_z"],
        ds["plume_qliq"], ds["plume_nice"],
        x_targets=(990, 1010), dx=10, z_targets=(410, 430, 450), dz=10
    )
    y_temp, temp_med, _, temp_2000m = compute_profile_with_ice_mask(
        ds["plume_location_x"], ds["plume_location_y"], ds["plume_location_z"],
        ds["plume_temp"], ds["plume_nice"],
        x_targets=(990, 1010), dx=10, z_targets=(410, 430, 450), dz=10
    )

    # ---- 绘图 ----
    # plot_profile(y_col, col_med, "Collision rate (cm⁻³ s⁻¹)",
    #              f"{label}: Collision rate (x≈1000, z≈400 m, ice>0)",
    #              os.path.join(out_dir, "col_rate_profile.png"))
    # plot_profile(y_ice, ice_med, "Ice conc. (cm⁻³)",
    #              f"{label}: Ice concentration (x≈1000, z≈400 m, ice>0)",
    #              os.path.join(out_dir, "ice_conc_profile.png"))
    # plot_profile(y_liq, liq_med, "Liquid conc. (cm⁻³)",
    #              f"{label}: Liquid concentration (x≈1000, z≈400 m, ice>0)",
    #              os.path.join(out_dir, "liq_conc_profile.png"))
    # plot_profile(y_lwc, lwc_med, "LWC (g m⁻³)",
    #              f"{label}: LWC (x≈1000, z≈400 m, ice>0)",
    #              os.path.join(out_dir, "lwc_profile.png"))
    # plot_profile(y_temp, temp_med, "Temperature (K)",
    #              f"{label}: Temperature (x≈1000, z≈400 m, ice>0)",
    #              os.path.join(out_dir, "temp_profile.png"))
    # print("std: ", np.nanstd(obs_col_rate), np.nanstd(obs_ice_count)/1000.0, np.nanstd(obs_liq_count), np.nanstd(obs_liq_content))

    setup_plot_style()

    plot_profile(
        y_col, col_med,
        "Collision rate (cm⁻³ s⁻¹)",
        os.path.join(out_dir, "col_rate_profile.png"),
        color="steelblue",
        obs_data=np.nanmean(obs_col_rate),
    )
    if col_2000m is not None:
        mask = np.where(obs_col_rate > 1.e-14, True, False)
        filtered_obs_col_rate = obs_col_rate[mask]
        plot_box_for_sim_obs_comparison(
            [col_2000m, ],
            ("Sim.", "Obs."),
            "Collision rate (cm⁻³ s⁻¹)",
            os.path.join(out_dir, "col_rate_box.png"),
            ax= None,
            logy=True,
            obs_data=filtered_obs_col_rate,
        )

    plot_profile(
        y_ice, ice_med*1000.0,
        "Ice conc. (L$^{-1}$)",
        os.path.join(out_dir, "ice_conc_profile.png"),
        color="steelblue",
        obs_data=np.nanmean(obs_ice_count),
    )
    if ice_2000m is not None:
        plot_box_for_sim_obs_comparison(
            [ice_2000m*1000.0, ],
            ("Sim.", "Obs."),
            "Ice conc. (L$^{-1}$)",
            os.path.join(out_dir, "ice_conc_box.png"),
            ax= None,
            logy=False,
            obs_data=obs_ice_count,
        )

    plot_profile(
        y_liq, liq_med,
        "Liquid conc. (cm⁻³)",
        os.path.join(out_dir, "liq_conc_profile.png"),
        color="steelblue",
        obs_data=np.nanmean(obs_liq_count),
    )
    if liq_2000m is not None:
        plot_box_for_sim_obs_comparison(
            [liq_2000m, ],
            ("Sim.", "Obs."),
            "Liquid conc. (cm⁻³)",
            os.path.join(out_dir, "liq_conc_box.png"),
            ax= None,
            logy=False,
            obs_data=obs_liq_count,
        )

    plot_profile(
        y_lwc, lwc_med,
        "LWC (g m⁻³)",
        os.path.join(out_dir, "lwc_profile.png"),
        color="steelblue",
        obs_data=np.nanmean(obs_liq_content),
    )
    if lwc_2000m is not None:
        plot_box_for_sim_obs_comparison(
            [lwc_2000m, ],
            ("Sim.", "Obs."),
            "LWC (g m⁻³)",
            os.path.join(out_dir, "lwc_box.png"),
            ax= None,
            logy=False,
            obs_data=obs_liq_content,
        )

    if ice_2000m is not None and liq_2000m is not None and lwc_2000m is not None and col_2000m is not None:
        plot_4boxes_for_sim_obs_comparison(
            [ice_2000m*1000.0, liq_2000m, lwc_2000m, col_2000m, ],
            ("Sim.", "Obs."),
            ("ICNC (L$^{-1}$)", "CDNC (cm⁻³)", "LWC (g m⁻³)", "Collision rate (cm⁻³ s⁻¹)"),
            os.path.join(out_dir, "figure_model_validation.png"),
            logy=[False, False, False, True],
            obs_data=(obs_ice_count, obs_liq_count, obs_liq_content, filtered_obs_col_rate),
        )

    plot_profile(
        y_temp, temp_med,
        "Temperature (K)",
        os.path.join(out_dir, "temp_profile.png")
    )

print(f"\n✅ 所有绘图完成！输出目录: {PLOT_ROOT}")