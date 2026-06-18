# -*- coding: utf-8 -*-
"""
fix_point_aspectratio_localcube.py (enhanced)
----------------------------------
从 plume .pkl 文件中提取指定小立方体区域内：
1. ice_acratio → 绘制 aspect ratio stair 图
2. ice_count → 绘制归一化百分比 stair 图
均在 plume 第一轮内时间平均后输出。
"""

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import cmcrameri.cm as cmc

from stats_plot.plot_functions import plot_stair_equalx, plot_2dists, TARGET_XS, TARGET_ZS, DX, DZ, DY, TARGET_Y, NICE_THRESH

# ======================================================
# 路径与参数
# ======================================================
DIR = os.path.realpath(os.path.dirname(__file__))
DATA_DIR = os.path.realpath("/capstor/store/cscs/userlab/cwd01/cong/plume_data")
DATA_DIR_SPECIAL = os.path.realpath("/capstor/store/cscs/userlab/cwd01/cong/plume_data/new_ice_mass/")
OUT_DIR  = os.path.join(DIR, "./plots_z400_x1000/localcube")
os.makedirs(OUT_DIR, exist_ok=True)

colors = cmc.batlow(np.linspace(0.35, 0.75, 4))
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 14,
    "axes.labelsize": 15,
    "axes.titlesize": 15,
    "axes.linewidth": 0.9,
    "axes.edgecolor": "#333333",
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.major.size": 3,
    "ytick.major.size": 3,
})

# ======================================================
# 辅助函数
# ======================================================
# def _wrap_first_cycle_indices(x_list, y_list, z_list, nice_list):
#     """检测 plume 第一轮 timestep 索引"""
#     y_end_cutoff = END_FRAC * Y_DOMAIN_MAX
#     prev_ymax, idx = None, []
#     for t, (x, y, z, nice) in enumerate(zip(x_list, y_list, z_list, nice_list)):
#         x, y, nice = np.asarray(x), np.asarray(y), np.asarray(nice)
#         mask = (np.abs(x - TARGET_X) <= 100) & (nice > NICE_THRESH)
#         if not np.any(mask):
#             continue
#         ymax = np.nanmax(y[mask])
#         if prev_ymax is not None and ymax < prev_ymax * 0.5:
#             break
#         idx.append(t)
#         prev_ymax = ymax
#         if ymax >= y_end_cutoff:
#             break
#     return idx



# ======================================================
# 主计算
# ======================================================
def compute_localcube_mean(ds, var_key):
    """
    从 plume 数据中提取局部立方体的 20-bin 平均值。
    var_key: 'plume_ice_acratio' 或 'plume_ice_count'
    """
    x_list, y_list, z_list = ds["plume_location_x"], ds["plume_location_y"], ds["plume_location_z"]
    nice_list = ds["plume_nice"]
    nice_count_list = ds["plume_ice_count"]
    time_list = ds["plume_time"]
    ice_diameter = np.array(ds["ice_diameter"])
    var_list = ds[var_key]

    # t_indices = _wrap_first_cycle_indices(x_list, y_list, z_list, nice_list)
    # if not t_indices:
    #     print("⚠️ 未找到第一轮 plume。")
    #     return None

    all_mean = np.zeros(ice_diameter.shape, dtype=float)
    total_ice = np.zeros(ice_diameter.shape, dtype=float)
    for t in range(len(time_list)):
        x, y, z, nice, nice_count, var = map(np.asarray, (x_list[t], y_list[t], z_list[t], nice_list[t], nice_count_list[t], var_list[t]))
        if np.max(y) > 3800.0:
            break
        assert x.shape == y.shape == z.shape
        mask_z = np.zeros_like(z, bool)
        mask_x = np.zeros_like(x, bool)
        for zt in TARGET_ZS:
            mask_z |= (np.abs(z - zt) <= DZ)
        for xt in TARGET_XS:
            mask_x |= (np.abs(x - xt) <= DX)
        mask = (
            (np.abs(y - TARGET_Y) <= DY) &
            mask_z &
            mask_x &
            (nice > NICE_THRESH)
        )
        if not np.any(mask):
            continue
        total_ice += np.sum(nice_count[:, mask], axis=1)
        all_mean += np.sum(var[:, mask] * nice_count[:, mask], axis=1)
    if not np.any(all_mean):
        return None, None

    normalized_total_ice = total_ice / np.sum(total_ice)
    return np.where(normalized_total_ice > 0.002, all_mean / total_ice, 0.0), total_ice / np.sum(total_ice)


# ======================================================
# 主程序
# ======================================================
if __name__ == "__main__":
    files = sorted([os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith("data.pkl")])
    print(f"🧊 找到 {len(files)} 个 plume 文件")
    for i, file in enumerate(files):
        if '_9min' in file:
            for f in os.listdir(DATA_DIR_SPECIAL):
                if f.endswith("_data.pkl") and '9min' in f:
                    print("repalcing", file, "with", f)
                    files[i] = os.path.join(DATA_DIR_SPECIAL, f)

    for fname in files:
        exp = fname.split("/")[-1].replace(".pkl", "")
        print(f"\n🎨 处理实验: {exp}")
        with open(fname, "rb") as f:
            ds = pickle.load(f)

        # ---- Aspect ratio ----
        acr_mean, count_mean = compute_localcube_mean(ds, "plume_ice_acratio")
        if acr_mean is not None:
            edges = np.asarray(ds["ice_diameter_boundary"], float)
            if np.nanmax(edges) < 0.01:
                edges *= 1e6
            edges = np.unique(np.sort(edges))
            plot_stair_equalx(acr_mean, edges, "Aspect ratio",
                              os.path.join(OUT_DIR, f"{exp}_aspect_equalx.png"),
                              colors[2]) # "Aspect ratio in local cube"

        # ---- Ice count (%) ----
        if count_mean is not None:
            # 归一化到百分比
            count_pct = 100 * count_mean
            edges = np.asarray(ds["ice_diameter_boundary"], float)
            if np.nanmax(edges) < 0.01:
                edges *= 1e6
            edges = np.unique(np.sort(edges))
            plot_stair_equalx(count_pct, edges, "Ice count (%)",
                              os.path.join(OUT_DIR, f"{exp}_icecount_equalx.png"),
                              colors[1]) # "Ice count in local cube"

        if acr_mean is not None and count_mean is not None:
            count_pct = 100 * count_mean
            edges = np.asarray(ds["ice_diameter_boundary"], float)
            if np.nanmax(edges) < 0.01:
                edges *= 1e6
            edges = np.unique(np.sort(edges))
            plot_2dists(
                [count_pct, acr_mean],
                edges,
                ["Ice count (%)", "Aspect ratio"],
                os.path.join(OUT_DIR, f"{exp}_icecount_and_aspect.png"),
            )
    print(f"\n✅ 所有 stair 图绘制完成！输出目录: {OUT_DIR}")