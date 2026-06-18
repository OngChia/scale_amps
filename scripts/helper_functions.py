import os
import numpy as np
import matplotlib.pyplot as plt


def extract_grouped_data(input_data: list[np.ndarray], seeding_w, split: bool = True):
    updraft_data_mask = np.where(seeding_w >= 0.2)[0]
    nowind_data_mask = np.where((seeding_w  < 0.2) & (seeding_w > -0.2))[0]
    downdraft_data_mask = np.where(seeding_w <= -0.2)[0]

    def _concat_arrays(data_mask: np.ndarray):
        grouped_data = None
        for k in data_mask:
            size = 0
            if isinstance(input_data[k], np.ndarray):
                size = input_data[k].size
            elif isinstance(input_data[k], list):
                size = len(input_data[k])
            elif isinstance(input_data[k], np.float64):
                size = 1
            if size == 1:
                print(input_data[k], np.atleast_1d(input_data[k]))
                current_data = np.squeeze(input_data[k])
                grouped_data = np.concatenate((grouped_data, np.atleast_1d(current_data)), axis=0) if grouped_data is not None else np.atleast_1d(current_data)
            else:
                for i in range(len(input_data[k])):
                    grouped_data = np.concatenate((grouped_data, np.array(input_data[k][i])), axis=0) if grouped_data is not None else np.array(input_data[k][i])
        return grouped_data
    if split:
        updraft_data = _concat_arrays(updraft_data_mask)
        nowind_data = _concat_arrays(nowind_data_mask)
        downdraft_data = _concat_arrays(downdraft_data_mask)
        return (updraft_data, nowind_data, downdraft_data)
    else:
        return _concat_arrays(np.arange(len(input_data)))

def normalize_data(input_data: list[np.ndarray]):
    normalized_data = []
    for item in input_data:
        mean_val = np.nanmean(item)
        normalized_data.append(np.abs(item - mean_val))
    return normalized_data

def all_mean(input_data: np.ndarray, label: str):
    mean_val = np.nanmean(input_data)
    std_val = np.nanstd(input_data)
    print(f"mean and std of {label}: ", mean_val, std_val)
