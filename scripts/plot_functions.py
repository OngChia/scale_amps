import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
import matplotlib.ticker as mticker
import cmcrameri.cm as cmc
import xarray as xr

# ======================================================
# 目标区域参数
# ======================================================
TARGET_XS = (990, 1010)
TARGET_Y = 2010
# TARGET_Y = 3510
TARGET_ZS = (410, 430, 450)
# TARGET_ZS = (510, 530, 550)
DX, DY, DZ = 10, 10, 10
NICE_THRESH = 1e-3
Y_DOMAIN_MAX = 3990.0
END_FRAC = 0.98
X_MIN_PLOT = 0
X_MAX_PLOT = 1600



def plot_profile(y, values, xlabel, filename, color="steelblue", obs_data: float = None, obs_data_std: float = None):
    if y is None or values is None or len(y) == 0:
        print(f"⚠️ 跳过 {os.path.basename(filename)}（无有效数据）")
        return

    fig, ax = plt.subplots(figsize=(4.5, 4.2))
    ax.plot(values, y, "o-", color=color, lw=1.8, markersize=5, alpha=0.9)
    if obs_data and obs_data_std is not None:
        ax.errorbar(obs_data, 2000.0, xerr=obs_data_std, fmt='o', color='black', markersize=5)
    elif obs_data is not None:
        ax.plot(obs_data, 2000.0, "o", color='black', markersize=5)

    ax.set_xlabel(xlabel, labelpad=6)
    ax.set_ylabel("y (m)", labelpad=6)

    # ✅ 科学计数法 + LaTeX 风格 ×10⁻⁴
    ax.ticklabel_format(style='sci', axis='x', scilimits=(-3, 3))
    ax.xaxis.offsetText.set_fontsize(10)
    ax.xaxis.offsetText.set_position((1.0, -0.12))
    plt.rcParams['axes.formatter.use_mathtext'] = True  # 用 LaTeX 数学体

    # ✅ 绘制完之后再替换 offset text
    fig.canvas.draw()
    offset_text = ax.xaxis.get_offset_text()
    text = offset_text.get_text()
    if "e" in text:
        # 把 "1e-4" 转成 "×10⁻⁴"
        formatted = text.replace("1e", "×10^").replace("+0", "").replace("-0", "-")
        offset_text.set_text(formatted)

    ax.grid(alpha=0.3, linestyle="--", linewidth=0.6)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(direction="in", length=4, width=1.0)
    ax.margins(y=0.05)

    fig.tight_layout(pad=0.5)
    plt.savefig(filename, dpi=400, bbox_inches="tight")
    plt.close()
    print(f"  → 保存 {os.path.basename(filename)} ✅")


def plot_box_for_sim_obs_comparison(box_data: list, labels, ylabel, filename=None, ax=None, logy=False, obs_data: np.ndarray=None):
    import matplotlib.patches as mpatches
    import matplotlib.ticker as mticker

    if ax is None:
        fig, ax = plt.subplots(figsize=(5.0, 4.0))

    # --- 改为高辨识度配色方案 ---
    if obs_data is None:
        color_map = {
            # "300m": "#47b8de",  # 蓝
            "Sim.": "#005945",  # 橙
            # "500m": "#fcfcd4",  # 绿
        }
    else:
        color_map = {
            "Sim.": "#005945",  # 橙
            "Obs.": "#999999",
        }

    box_colors = []
    for lbl in labels:
        for key in color_map:
            if key in lbl:
                box_colors.append(color_map[key])
                break
        else:
            box_colors.append("#999999")

    # --- 绘制 boxplot ---
    medianprops = dict(color="#222222", linewidth=1.6)
    meanprops = dict(marker="o", markerfacecolor="white", markeredgecolor="#444444", markersize=4)

    if obs_data is not None:
        box_data.append(obs_data)

    bp = ax.boxplot(
        box_data,
        patch_artist=True,
        showmeans=True,
        meanprops=meanprops,
        medianprops=medianprops,
        showfliers=False,
        whis=[5, 95],
        widths=0.6,
        boxprops=dict(linewidth=0.8, color="#666666"),
        whiskerprops=dict(linewidth=0.8, color="#666666"),
        capprops=dict(linewidth=0.8, color="#666666"),
    )

    # --- 填充颜色 ---
    for patch, color in zip(bp["boxes"], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
        patch.set_edgecolor("#444444")

    # --- 坐标轴美化 ---
    clean_labels = [lbl.replace("_", " ") for lbl in labels]
    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(clean_labels, rotation=25, ha="right") # , fontsize=10
    ax.set_ylabel(ylabel, labelpad=8)
    # ax.set_title(title, pad=10, fontsize=12, fontweight="semibold")

    if logy:
        ax.set_yscale("log")
    ax.xaxis.set_major_locator(mticker.FixedLocator(range(1, len(labels) + 1)))
    # ax.grid(True, which="major", axis="y", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)
    # ax.tick_params(axis="both") # , labelsize=16
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    # --- legend 动态放置 ---
    legend_patches = [
        mpatches.Patch(facecolor=color_map[k], edgecolor="none", alpha=0.8, label=k.replace("m", " m"))
        for k in color_map
    ]

    # ylim = ax.get_ylim()
    # ax.set_ylim(ylim[0] * 0.8, ylim[1])
    # print("debug ylim: ", ylim, obs_data.min())
    # if obs_data is not None:
    #     if ylim[0] > obs_data.min():
    #         ax.set_ylim(obs_data.min()*0.1, ylim[1])

    # 检查右上角是否有空间，否则放左上角
    try:
        ylim = ax.get_ylim()
        y_med = np.nanmedian([np.nanmedian(d) for d in box_data])
        if np.log10(ylim[1]) - np.log10(y_med) < 1.5:
            # ax.set_ylim(ylim[0], ylim[1]*1.3)
            loc, anchor = "upper left", (0.02, 0.98)
        else:
            loc, anchor = "upper left", (0.98, 0.98)
    except Exception:
        ylim = ax.get_ylim()
        ax.set_ylim(ylim[0], ylim[1]*1.3)
        loc, anchor = "upper left", (0.98, 0.98)

    # ax.legend(
    #     handles=legend_patches,
    #     title="Altitude",
    #     loc=loc,
    #     frameon=False,
    #     fontsize=10,
    #     title_fontsize=10,
    #     bbox_to_anchor=anchor,
    # )

    if filename is not None:
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        plt.savefig(filename, dpi=500, bbox_inches="tight")
        plt.close()
        print(f"  → 保存 {os.path.basename(filename)}")


def plot_4boxes_for_sim_obs_comparison(box_data: list, labels, ylabel, filename, logy=False, obs_data: list=None):
    # fig, ax = plt.subplots(figsize=(14.0, 5.0), ncols=3, nrows=1)
    fig, ax = plt.subplots(figsize=(19.0, 5.0), ncols=4, nrows=1)
    subplot_title_labels = ['(a)', '(b)', '(c)', '(d)']
    # for i in range(3):
    #     ax[i].set_aspect(1.0/ax[i].get_data_ratio(), adjustable='box')
    for i in range(4):
        plot_box_for_sim_obs_comparison(
            [box_data[i], ],
            labels,
            ylabel[i],
            filename=None,
            ax=ax[i],
            logy=logy[i],
            obs_data=obs_data[i],
        )
    for i in range(4):
        ax[i].set_title(subplot_title_labels[i], loc='left', fontsize='medium')
    plt.tight_layout()
    plt.savefig(filename, dpi=500, bbox_inches="tight")
    plt.close()
    print(f"  → 保存 {os.path.basename(filename)}")


def plot_box_for_updowndraft_comparison(box_data: list, labels, ylabel, filename, ax=None, logy=False, y_axis_ticks=None):
    import matplotlib.patches as mpatches
    import matplotlib.ticker as mticker

    if ax is None:
        fig, ax = plt.subplots(figsize=(5.0, 4.0))

    # --- 改为高辨识度配色方案 ---
    assert len(box_data) == len(labels), f"Box data and labels length mismatch! {len(box_data)}, {len(labels)}"
    assert len(labels) == 3, f"labels length is not 3! {len(labels)}"
    color_map = {
        labels[0]: "#d12734",
        labels[1]: "#f3eed9",
        labels[2]: "#66b1f3",
    }
    # website: #d12734 original: #8f462d updraft
    # website: #f3eed9 original: #d8e7b3 no wind
    # website: #66b1f3 original: #3f62ae downdraft
    
    box_colors = []
    for lbl in labels:
        for key in color_map:
            if key in lbl:
                box_colors.append(color_map[key])
                break
        else:
            box_colors.append("#999999")

    # --- 绘制 boxplot ---
    medianprops = dict(color="#222222", linewidth=1.6)
    meanprops = dict(marker="o", markerfacecolor="white", markeredgecolor="#444444", markersize=4)

    bp = ax.boxplot(
        box_data,
        patch_artist=True,
        showmeans=True,
        meanprops=meanprops,
        medianprops=medianprops,
        showfliers=False,
        whis=[5, 95],
        widths=0.6,
        boxprops=dict(linewidth=0.8, color="#666666"),
        whiskerprops=dict(linewidth=0.8, color="#666666"),
        capprops=dict(linewidth=0.8, color="#666666"),
    )

    # --- 填充颜色 ---
    for patch, color in zip(bp["boxes"], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
        patch.set_edgecolor("#444444")

    # --- 坐标轴美化 ---
    clean_labels = [lbl.replace("_", " ") for lbl in labels]
    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(clean_labels, rotation=25, ha="right", fontsize=10)
    ax.set_ylabel(ylabel, labelpad=8)
    # ax.set_title(title, pad=10, fontsize=12, fontweight="semibold")

    if logy:
        ax.set_yscale("log")
    ax.xaxis.set_major_locator(mticker.FixedLocator(range(1, len(labels) + 1)))
    # ax.grid(True, which="major", axis="y", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)
    ax.tick_params(left=True, right=False, axis="y", labelsize=16)
    ax.tick_params(bottom=True, top=False, axis="x", labelsize=16)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    # --- legend 动态放置 ---
    legend_patches = [
        mpatches.Patch(facecolor=color_map[k], edgecolor="none", alpha=0.8, label=k.replace("m", " m"))
        for k in color_map
    ]

    # ylim = ax.get_ylim()
    # ax.set_ylim(ylim[0] * 0.8, ylim[1])
    # print("debug ylim: ", ylim, obs_data.min())
    # if obs_data is not None:
    #     if ylim[0] > obs_data.min():
    #         ax.set_ylim(obs_data.min()*0.1, ylim[1])

    # 检查右上角是否有空间，否则放左上角
    if y_axis_ticks is None:
        try:
            ylim = ax.get_ylim()
            y_med = np.nanmedian([np.nanmedian(d) for d in box_data])
            if np.log10(ylim[1]) - np.log10(y_med) < 1.5:
                # ax.set_ylim(ylim[0], ylim[1]*1.3)
                loc, anchor = "upper left", (0.02, 0.98)
            else:
                loc, anchor = "upper left", (0.98, 0.98)
        except Exception:
            ylim = ax.get_ylim()
            ax.set_ylim(ylim[0], ylim[1]*1.3)
            loc, anchor = "upper left", (0.98, 0.98)
    else:
        ax.set_yticks(y_axis_ticks)
        ax.set_ylim(y_axis_ticks[0] - (y_axis_ticks[-1] - y_axis_ticks[0])*0.05, y_axis_ticks[-1]*1.1)

    # ax.legend(
    #     handles=legend_patches,
    #     title="Altitude",
    #     loc=loc,
    #     frameon=False,
    #     fontsize=10,
    #     title_fontsize=10,
    #     bbox_to_anchor=anchor,
    # )

    if filename is not None:
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        plt.savefig(filename, dpi=500, bbox_inches="tight")
        plt.close()
        print(f"  → 保存 {os.path.basename(filename)}")


def plot_3boxes_for_updowndraft_comparison(box_data: list, labels, ylabel, filename, logy=False, y_axis_ticks=None):
    fig, ax = plt.subplots(figsize=(14.0, 5.0), ncols=3, nrows=1)
    subplot_title_labels = ['(a)', '(b)', '(c)']
    # for i in range(3):
    #     ax[i].set_aspect(1.0/ax[i].get_data_ratio(), adjustable='box')
    for i in range(3):
        plot_box_for_updowndraft_comparison(
            box_data[i],
            labels,
            ylabel[i],
            filename=None,
            ax=ax[i],
            logy=logy[i],
            y_axis_ticks=y_axis_ticks,
        )
    for i in range(3):
        ax[i].set_title(subplot_title_labels[i], loc='left', fontsize='medium')
    plt.tight_layout()
    plt.savefig(filename, dpi=500, bbox_inches="tight")
    plt.close()
    print(f"  → 保存 {os.path.basename(filename)}")


def plot_2boxes_for_updowndraft_comparison(box_data: list, labels, ylabel, filename, logy=False, y_axis_ticks=None):
    fig, ax = plt.subplots(figsize=(10.0, 5.0), ncols=2, nrows=1)
    subplot_title_labels = ['(a)', '(b)']
    # for i in range(3):
    #     ax[i].set_aspect(1.0/ax[i].get_data_ratio(), adjustable='box')
    for i in range(2):
        plot_box_for_updowndraft_comparison(
            box_data[i],
            labels,
            ylabel[i],
            filename=None,
            ax=ax[i],
            logy=logy[i],
            y_axis_ticks=y_axis_ticks,
        )
    for i in range(2):
        ax[i].set_title(subplot_title_labels[i], loc='left', fontsize='medium')
    plt.tight_layout()
    plt.savefig(filename, dpi=500, bbox_inches="tight")
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


# ======================================================
# 绘图（等距横轴）
# ======================================================
def plot_stair_equalx(values, edges, ylabel, out_path, color, ax=None):

    ice_distribution_data = xr.open_zarr("/capstor/store/cscs/userlab/cwd01/cong/plume_data/obs_data/ice_distribution.zarr")
    obs_ice_percentage_count = ice_distribution_data["obs_ice_percentage_count"]
    obs_mean_acratio = ice_distribution_data["obs_mean_acratio"]

    # edges, values = _trim_empty_bins(edges, values)
    # edges, values = _slice_edges_for_plot(edges, values)
    keep_index = _trim_empty_bins(edges, values)
    left_index, right_index = _slice_edges_for_plot(edges[:keep_index+1], values[:keep_index])
    
    obs_data = obs_ice_percentage_count if "count" in ylabel else obs_mean_acratio
    obs_keep_index = _trim_empty_bins(edges, obs_data)
    obs_left_index, obs_right_index = _slice_edges_for_plot(edges[:obs_keep_index+1], obs_data[:obs_keep_index])

    left_index = min(left_index, obs_left_index)
    right_index = max(right_index, obs_right_index)

    x_idx = np.arange(len(values[left_index:right_index-1]) + 1)
    labels = [str(int(v)) for v in edges[left_index:right_index]]

    if ax is None:
        plt.close()
        fig, ax = plt.subplots(figsize=(5.2, 3.8))
    ax.stairs(values[left_index:right_index-1], x_idx, color=color, linewidth=1.6,
              label="Sim.")
    ax.stairs(obs_data[left_index:right_index-1], x_idx, color='black', linewidth=1.6,
              label="Obs.")

    ax.set_xlim(x_idx[0], x_idx[-1])
    ax.set_xlabel("Diameter ($\\mu$m)")
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False)
    ax.set_xticks(np.arange(len(labels)))
    labels[0] = ""
    ax.set_xticklabels(labels, rotation=60, ha="right")
    ax.set_ylim(0, np.nanmax(values[left_index:right_index-1]) * 1.15 if np.isfinite(np.nanmax(values[left_index:right_index-1])) else 1)
    
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if out_path is not None:
        fig.tight_layout()
        fig.savefig(out_path, dpi=500)
        plt.close(fig)
        print(f"  → 保存 {os.path.basename(out_path)} ✅")


def plot_2dists(input_data: list, edges, ylabel, filename, logy=False, obs_data: list=None):
    colors = cmc.batlow(np.linspace(0.35, 0.75, 4))
    fig, ax = plt.subplots(figsize=(10.0, 5.0), ncols=2, nrows=1)
    subplot_title_labels = ['(a)', '(b)']
    for i in range(2):
        plot_stair_equalx(
            input_data[i],
            edges,
            ylabel[i],
            out_path=None,
            # color=colors[1] if "count" in ylabel[i].lower() else colors[2],
            color=colors[2], # "#005945"
            ax=ax[i],
        )
    for i in range(2):
        ax[i].set_title(subplot_title_labels[i], loc='left', fontsize='medium')
    # plt.tight_layout()
    plt.subplots_adjust(wspace=0.3, hspace=0.0)
    plt.savefig(filename, dpi=500, bbox_inches="tight")
    plt.close()
    print(f"  → 保存 {os.path.basename(filename)}")


def plot_allcases(
    normal_plume_time,
    normal_plume_data,
    wbf_off_plume_time,
    wbf_off_plume_data,
    noseed_plume_time,
    noseed_plume_data,
    seeding_w,
    y_ticks: list | None,
    y_lim: list | None,
    y_label,
    plot_dir,
    filename,
):
    plt.rcParams.update({
        "font.family": "DejaVu Sans",       # 科研默认字体兼容性好
        "font.size": 17,
        "axes.labelsize": 18,
        "axes.titlesize": 18,
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
        # "figure.dpi": 100,
        # "savefig.dpi": 300,                 # 300dpi足矣
        "savefig.bbox": "tight",
        "legend.fontsize": 12,
        "axes.grid": False,                 # 🚫 不画 grid
        "axes.formatter.use_mathtext": True,
    })
    panel_count = 20
    nrows, ncols = 5, 4

    fig, ax = plt.subplots(figsize=(21.0, 23.0), ncols=ncols, nrows=nrows)
    axes = ax.flatten()
    # color_seed = []
    # for i in range(panel_count):
    #     fstring = f"{seeding_w[i]:.2f}"
    #     color_seed.append(ANSI.color_text(seeding_w[i]) + fstring) #  + "\033[0m"
    # subplot_title_labels = [f"({chr(ord('a') + i)})   initial seeding w: " + color_seed[i] for i in range(panel_count)]
    w_color = ["red" if w > 0.2 else "blue" if w < -0.2 else "goldenrod" for w in seeding_w]
    subplot_title_prefix = [f"({chr(ord('a') + i)})  initial seeding w: " for i in range(panel_count)]

    line_color = 'black'
    line_style = ('-', '--', '-.')
    for index in range(panel_count):
        # print(index, normal_plume_data.plume_state.plume_max_time[index].shape, normal_plume_data.plume_state.plume_max_loc_z[index].shape)
        axes[index].plot(
            normal_plume_time[index],
            normal_plume_data[index],
            color=line_color,
            linestyle=line_style[0],
            label="Normal seeding",
        )
        axes[index].plot(
            wbf_off_plume_time[index],
            wbf_off_plume_data[index],
            color=line_color,
            linestyle=line_style[1],
            label="WBF-off seeding",
        )
        axes[index].plot(
            noseed_plume_time[index],
            noseed_plume_data[index],
            color=line_color,
            linestyle=line_style[2],
            label="No-ice seeding",
        )
        # ax_text(ax=axes[index], x=0.5, y =1.0, ha="center", s=subplot_title_labels[index], size=15, highlight_textprops=[{"color": "red", "weight": "bold"}])
        # axes[index].set_title(subplot_title_labels[index], loc='left', fontsize='medium')
        # Use two text artists so only the numeric value is colorized.
        prefix_text = axes[index].text(
            0.0,
            1.02,
            subplot_title_prefix[index],
            transform=axes[index].transAxes,
            ha="left",
            va="bottom",
            fontsize="medium",
            color="black",
        )

        # Measure the rendered prefix width and place the value right after it.
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        prefix_bbox = prefix_text.get_window_extent(renderer=renderer)
        value_x = axes[index].transAxes.inverted().transform((prefix_bbox.x1, prefix_bbox.y0))[0]
        # print(index, (prefix_bbox.x1, prefix_bbox.y0), " === ", axes[index].transAxes.inverted().transform((prefix_bbox.x1, prefix_bbox.y0)))

        axes[index].text(
            value_x,
            1.02,
            f"{seeding_w[index]:.2f}",
            transform=axes[index].transAxes,
            ha="left",
            va="bottom",
            fontsize="medium",
            color=w_color[index],
            fontweight="bold",
        )

    if y_lim is not None:
        y_lower_limit, y_upper_limit = y_lim[0], y_lim[1]
    else:
        y_upper_limit, y_lower_limit = -1.e100, 1.e100
        for data_slice in normal_plume_data:
            if np.max(data_slice) > y_upper_limit:
                y_upper_limit = np.max(data_slice)
            if np.min(data_slice) < y_lower_limit:
                y_lower_limit = np.min(data_slice)
        for data_slice in noseed_plume_data:
            if np.max(data_slice) > y_upper_limit:
                y_upper_limit = np.max(data_slice)
            if np.min(data_slice) < y_lower_limit:
                y_lower_limit = np.min(data_slice)
    for i in range(nrows):
        for j in range(ncols):
            ax[i][j].set_xticks([0, 200, 400, 600, 800, 1000])
            ax[i][j].set_xlabel("Time (s)")
            ax[i][j].set_xlim(-10, 1010)
            if y_ticks is not None:
                ax[i][j].set_yticks(y_ticks)
                ax[i][j].set_ylim(y_lower_limit - 0.01 * y_lower_limit, y_upper_limit + 0.01 * y_upper_limit)
            else:
                internal_ticks = np.linspace(y_lower_limit, y_upper_limit, 7)
                ax[i][j].set_yticks(internal_ticks)
                ax[i][j].yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.1f}"))
                ax[i][j].set_ylim(y_lower_limit - 0.001 * y_lower_limit, y_upper_limit + 0.001 * y_upper_limit)
            ax[i][j].set_ylabel(y_label)
            
            # fmt_y = mticker.ScalarFormatter(useMathText=True)
            # fmt_y.set_scientific(True)
            # fmt_y.set_powerlimits((0, 0))
            # fmt_y.set_useOffset(True)
            # ax[i][j].yaxis.set_major_formatter(fmt_y)
            if i < nrows - 1:
                ax[i][j].xaxis.set_ticklabels([])
                ax[i][j].set_xlabel("")
            if j > 0:
                ax[i][j].yaxis.set_ticklabels([])
                ax[i][j].set_ylabel("")
    legend = ax[nrows-1][0].legend(
        loc="center left",
        bbox_to_anchor=(1.0,-0.3),
        frameon=True,
        ncol=3,
        edgecolor="black",
        fontsize=17,
    )
    legend_frame = legend.get_frame()
    # legend_frame.set_color('black')
    legend_frame.set_alpha(0.4)
    full_filename = plot_dir + filename
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.18, wspace=0.18)
    plt.savefig(full_filename, dpi=500, bbox_inches="tight")
    plt.close()
    print(f"  → 保存 {os.path.basename(full_filename)}")
