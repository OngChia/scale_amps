from typing import Any
import functools
import dataclasses
import pickle
import numpy as np

NICE_THRESHOLD = 1.e-2
R_D = 287.04e4
R_V = 461.5e4
R_DV = R_D / R_V

def make_list(num: int):
    return [[] for _ in range(num)]

@dataclasses.dataclass
class PlumeState:
    plume_max_time: list
    plume_max_loc_x: list
    plume_max_loc_y: list
    plume_max_loc_z: list
    plume_max_rh: list
    plume_max_rhi: list
    plume_max_buoyancy: list
    plume_max_amps_rh: list
    plume_max_amps_rhi: list
    plume_max_w: list
    plume_max_w_bk: list
    plume_max_incloud_w: list
    plume_max_reduced_w: list
    plume_max_qtotal: list
    plume_max_qtotal_plus_qv: list
    plume_max_qv_t: list
    plume_max_pot_temperature: list
    plume_max_temperature: list
    plume_max_ice_count: list
    plume_max_ice_count_300: list
    plume_max_ice_count_350: list
    plume_max_ice_count_400: list
    plume_max_ice_count_450: list
    plume_max_ice_count_500: list
    plume_max_ice_count_550: list
    plume_max_qice: list
    plume_max_qliq: list
    plume_max_dice: list
    plume_max_dliq: list
    plume_max_nice: list
    plume_max_total_nice: list
    plume_max_nagg: list
    plume_max_nliq: list
    plume_max_tke: list
    plume_max_cact: list
    plume_max_reduced_cact: list
    plume_max_col_rate: list
    plume_max_acratio: list
    plume_max_ice_psd: list
    plume_max_ice_psd_300: list
    plume_max_ice_psd_350: list
    plume_max_ice_psd_400: list
    plume_max_ice_psd_450: list
    plume_max_ice_psd_500: list
    plume_max_ice_psd_550: list
    plume_max_liq_psd: list
    plume_max_accumulated_heat_release: list
    temporary_plume_max_accumulated_heat_release: list
    plume_1000m_xgrid: list
    plume_1000m_zgrid: list
    plume_2000m_xgrid: list
    plume_2000m_zgrid: list
    plume_3000m_xgrid: list
    plume_3000m_zgrid: list
    plume_4000m_xgrid: list
    plume_4000m_zgrid: list
    plume_2000m_time: np.ndarray
    plume_3000m_time: np.ndarray
    plume_4000m_time: np.ndarray
    plume_2000m_all_qice: list
    plume_3000m_all_qice: list
    plume_4000m_all_qice: list
    plume_2000m_all_nice: list
    plume_3000m_all_nice: list
    plume_4000m_all_nice: list


@dataclasses.dataclass
class PlumeData:
    
    data_file_number: int
    data_files: list[str]
    reduced_w_data_files: list[str]
    grid_spacing: float # grid cell spacing, unit is m
    dtime: float # model time step, unit is s
    liq_diameter_bnd: np.ndarray = dataclasses.field(init=False)
    ice_diameter: np.ndarray = dataclasses.field(init=False)
    ice_diameter_bnd: np.ndarray = dataclasses.field(init=False)
    plume_state: PlumeState = dataclasses.field(init=False)
    
    @functools.cached_property
    def grid_volume(self) -> float:
        return self.grid_spacing ** 3
    
    def __post_init__(self):
        assert self.data_file_number > 0, f"Data file number must be greater than 0, got {self.data_file_number}"
        assert len(self.data_files) == self.data_file_number, f"Expected {self.data_file_number} data files, got {len(self.data_files)}"
        assert len(self.reduced_w_data_files) == self.data_file_number, f"Expected {self.data_file_number} reduced w data files, got {len(self.reduced_w_data_files)}"
        def _set_attr(var_name: str, var: list | np.ndarray): 
            object.__setattr__(
                self,
                var_name,
                var,
            )
        def get_name(var: Any):
            name = [k for k, v in locals().items() if v is var][0]
            return name

        object.__setattr__(self, "grid_volume", self.grid_spacing ** 3)

        with open(self.data_files[0], "rb") as openfile:
            data = pickle.load(openfile)
            liq_diameter_bnd = np.array(data["liquid_diameter_boundary"])
            ice_diameter = np.array(data["ice_diameter"])
            ice_diameter_bnd = np.array(data["ice_diameter_boundary"])
            object.__setattr__(self, "liq_diameter_bnd", liq_diameter_bnd)
            object.__setattr__(self, "ice_diameter", ice_diameter)
            object.__setattr__(self, "ice_diameter_bnd", ice_diameter_bnd)

        plume_max_time = make_list(self.data_file_number)
        plume_max_loc_x = make_list(self.data_file_number)
        plume_max_loc_y = make_list(self.data_file_number)
        plume_max_loc_z = make_list(self.data_file_number)
        plume_max_buoyancy = make_list(self.data_file_number)
        plume_max_rh = make_list(self.data_file_number)
        plume_max_rhi = make_list(self.data_file_number)
        plume_max_amps_rh = make_list(self.data_file_number)
        plume_max_amps_rhi = make_list(self.data_file_number)
        plume_max_w = make_list(self.data_file_number)
        plume_max_w_bk = make_list(self.data_file_number)
        plume_max_incloud_w = make_list(self.data_file_number)
        plume_max_reduced_w = make_list(self.data_file_number)
        plume_max_qtotal = make_list(self.data_file_number)
        plume_max_qtotal_plus_qv = make_list(self.data_file_number)
        plume_max_qv_t = make_list(self.data_file_number)
        plume_max_pot_temperature = make_list(self.data_file_number)
        plume_max_temperature = make_list(self.data_file_number)
        plume_max_ice_count = make_list(self.data_file_number)
        plume_max_qice = make_list(self.data_file_number)
        plume_max_qliq = make_list(self.data_file_number)
        plume_max_dice = make_list(self.data_file_number)
        plume_max_dliq = make_list(self.data_file_number)
        plume_max_nice = make_list(self.data_file_number)
        plume_max_total_nice = make_list(self.data_file_number)
        plume_max_nagg = make_list(self.data_file_number)
        plume_max_nliq = make_list(self.data_file_number)
        plume_max_tke = make_list(self.data_file_number)
        plume_max_cact = make_list(self.data_file_number)
        plume_max_reduced_cact = make_list(self.data_file_number)
        plume_max_col_rate = make_list(self.data_file_number)
        plume_max_acratio = make_list(self.data_file_number)
        plume_max_ice_psd = make_list(self.data_file_number)
        plume_max_ice_psd_300 = make_list(self.data_file_number)
        plume_max_ice_psd_350 = make_list(self.data_file_number)
        plume_max_ice_psd_400 = make_list(self.data_file_number)
        plume_max_ice_psd_450 = make_list(self.data_file_number)
        plume_max_ice_psd_500 = make_list(self.data_file_number)
        plume_max_ice_psd_550 = make_list(self.data_file_number)
        plume_max_ice_count_300 = make_list(self.data_file_number)
        plume_max_ice_count_350 = make_list(self.data_file_number)
        plume_max_ice_count_400 = make_list(self.data_file_number)
        plume_max_ice_count_450 = make_list(self.data_file_number)
        plume_max_ice_count_500 = make_list(self.data_file_number)
        plume_max_ice_count_550 = make_list(self.data_file_number)
        plume_max_liq_psd = make_list(self.data_file_number)
        plume_max_accumulated_heat_release = make_list(self.data_file_number)
        temporary_plume_max_accumulated_heat_release = make_list(self.data_file_number)
        plume_1000m_xgrid = make_list(self.data_file_number)
        plume_1000m_zgrid = make_list(self.data_file_number)
        plume_2000m_xgrid = make_list(self.data_file_number)
        plume_2000m_zgrid = make_list(self.data_file_number)
        plume_3000m_xgrid = make_list(self.data_file_number)
        plume_3000m_zgrid = make_list(self.data_file_number)
        plume_4000m_xgrid = make_list(self.data_file_number)
        plume_4000m_zgrid = make_list(self.data_file_number)
        plume_2000m_time = np.zeros(self.data_file_number, dtype=int)
        plume_3000m_time = np.zeros(self.data_file_number, dtype=int)
        plume_4000m_time = np.zeros(self.data_file_number, dtype=int)
        plume_2000m_all_qice = make_list(self.data_file_number)
        plume_3000m_all_qice = make_list(self.data_file_number)
        plume_4000m_all_qice = make_list(self.data_file_number)
        plume_2000m_all_nice = make_list(self.data_file_number)
        plume_3000m_all_nice = make_list(self.data_file_number)
        plume_4000m_all_nice = make_list(self.data_file_number)

        for k in range(self.data_file_number):
            reduced_w_data, data = {}, {}
            with open(self.data_files[k], "rb") as openfile:
                while True:
                    try:
                        data = pickle.load(openfile)
                    except EOFError:
                        break
            with open(self.reduced_w_data_files[k], "rb") as openfile:
                while True:
                    try:
                        reduced_w_data = pickle.load(openfile)
                    except EOFError:
                        break

            plume_time = np.array(data["plume_time"])
            plume_detected, plume_first_detected_time = False, 0.0

            arrive_at_2000m, arrive_at_3000m, arrive_at_4000m = False, False, False
            for t in range(plume_time.shape[0]):
                qv = np.array(data["plume_qv"][t])
                qice = np.array(data["plume_qice"][t])
                nice = np.array(data["plume_nice"][t])
                nagg = np.array(data["plume_nagg"][t])
                nliq = np.array(data["plume_nliq"][t])
                qliq = np.array(data["plume_qliq"][t])
                dliq = np.array(data["plume_dliq"][t])
                dice = np.array(data["plume_dice"][t])
                dens = np.array(data["plume_dens"][t])
                temp = np.array(data["plume_temp"][t])
                pot_temp = np.array(data["plume_pot_temp"][t])
                pres = np.array(data["plume_pres"][t])
                rd_rhoh_mp = np.array(reduced_w_data["plume_reduced_rhoh_mp"][t])
                # momz_t_mp = np.array(data["plume_momz_t_mp"][t])
                qv_t_mp = np.array(data["plume_qv_t_mp"][t])

                rh = np.array(data["plume_rh"][t])
                rhi = np.array(data["plume_rhi"][t])
                w = np.array(data["plume_w"][t])
                w_bk = np.array(reduced_w_data["plume_w_bk"][t])
                reduced_w = np.array(reduced_w_data["plume_reduced_w"][t])
                tke = np.array(reduced_w_data["plume_tke"][t])
                cact = np.array(reduced_w_data["plume_cact"][t])
                reduced_cact = np.array(reduced_w_data["plume_reduced_cact"][t])
                ice_count = np.array(data["plume_ice_count"][t])
                ice_psd = np.array(data["plume_ice_psd"][t])
                liq_psd = np.array(data["plume_liq_psd"][t])
                acratio = np.array(data["plume_ice_acratio"][t])
                col_rate = np.array(-data["plume_col_rate"][t])
                liq_supersat = amps_liqsupersat(pres, temp, qv)
                ice_supersat = amps_icesupersat(pres, temp, qv)
                plume_location_x = np.array(data["plume_location_x"][t])
                plume_location_y = np.array(data["plume_location_y"][t])
                plume_location_z = np.array(data["plume_location_z"][t])

                masked_plume = np.ma.masked_where(nice < NICE_THRESHOLD, nice)
                masked_plume = np.ma.filled(masked_plume, np.nan)
                plume_threshold = np.nanpercentile(masked_plume, 1)
                mask = np.where(nice > plume_threshold, True, False)
                mask_300 = np.where((plume_location_z >= 300.0) & (plume_location_z < 350.0), True, False)
                mask_350 = np.where((plume_location_z >= 350.0) & (plume_location_z < 400.0), True, False)
                mask_400 = np.where((plume_location_z >= 400.0) & (plume_location_z < 450.0), True, False)
                mask_450 = np.where((plume_location_z >= 450.0) & (plume_location_z < 500.0), True, False)
                mask_500 = np.where((plume_location_z >= 500.0) & (plume_location_z < 550.0), True, False)
                mask_550 = np.where((plume_location_z >= 550.0) & (plume_location_z < 600.0), True, False)

                if arrive_at_3000m:
                    plume_location_y = np.where(plume_location_y < 2000.0, plume_location_y + 4000.0, plume_location_y)

                current_x = np.mean(plume_location_x[mask])
                current_y = np.mean(plume_location_y[mask])
                current_z = np.mean(plume_location_z[mask])

                if not plume_detected:
                    plume_detected = True
                    plume_first_detected_time = plume_time[t]
                if np.any(mask):
                    plume_max_time[k].append(plume_time[t] - plume_first_detected_time)
                    plume_max_loc_x[k].append(current_x)
                    plume_max_loc_y[k].append(current_y)
                    plume_max_loc_z[k].append(current_z)
                    plume_max_col_rate[k].append(np.mean(col_rate[mask]))
                    plume_max_qtotal[k].append(np.mean(qice[mask] + qliq[mask]))
                    plume_max_qv_t[k].append(np.mean(qv_t_mp[mask]))
                    plume_max_buoyancy[k].append(np.mean(pot_temp[mask] * (1.0 + (R_V / R_D - 1.0) * qv[mask] / dens[mask] / 1000.0 - (qice[mask] + qliq[mask]) / dens[mask] / 1000.0 ) ) )
                    plume_max_temperature[k].append(np.mean(temp[mask]) - 273.15)
                    plume_max_qice[k].append(np.mean(qice[mask]))
                    plume_max_qliq[k].append(np.mean(qliq[mask]))
                    plume_max_nice[k].append(np.mean(nice[mask]) * 1000.0)
                    plume_max_total_nice[k].append(np.sum(nice) * self.grid_volume * 1000000.0)
                    plume_max_nagg[k].append(np.mean(nagg[mask]) * 1000.0)
                    plume_max_nliq[k].append(np.mean(nliq[mask]))
                    plume_max_dice[k].append(np.mean(dice[mask]))
                    plume_max_dliq[k].append(np.mean(dliq[mask]))

                    plume_max_tke[k].append(np.mean(tke[mask]))
                    plume_max_cact[k].append(np.mean(cact[mask]))
                    plume_max_reduced_cact[k].append(np.mean(reduced_cact[mask]))

                    plume_max_rh[k].append(np.mean(rh[mask]))
                    plume_max_rhi[k].append(np.mean(rhi[mask]))
                    plume_max_amps_rh[k].append(np.mean(liq_supersat[mask]))
                    plume_max_amps_rhi[k].append(np.mean(ice_supersat[mask]))
                    plume_max_w[k].append(np.mean(w[mask]))
                    plume_max_w_bk[k].append(np.mean(w_bk[mask]))
                    
                    plume_max_ice_count[k].append(np.sum(ice_count[:, mask], axis=1))
                    plume_max_ice_count_300[k].append(np.sum(ice_count[:, mask & mask_300], axis=1))
                    plume_max_ice_count_350[k].append(np.sum(ice_count[:, mask & mask_350], axis=1))
                    plume_max_ice_count_400[k].append(np.sum(ice_count[:, mask & mask_400], axis=1))
                    plume_max_ice_count_450[k].append(np.sum(ice_count[:, mask & mask_450], axis=1))
                    plume_max_ice_count_500[k].append(np.sum(ice_count[:, mask & mask_500], axis=1))
                    plume_max_ice_count_550[k].append(np.sum(ice_count[:, mask & mask_550], axis=1))

                    mean_acratio = np.sum(ice_count * acratio, axis=0)
                    plume_max_acratio[k].append(np.mean(mean_acratio[mask]))
                    plume_max_qtotal_plus_qv[k].append(np.mean(qv[mask] + qice[mask] + qliq[mask]))

                    plume_max_ice_psd[k].append(np.mean(ice_psd[:, mask], axis=1))
                    plume_max_ice_psd_300[k].append(np.mean(ice_psd[:, mask & mask_300], axis=1))
                    plume_max_ice_psd_350[k].append(np.mean(ice_psd[:, mask & mask_350], axis=1))
                    plume_max_ice_psd_400[k].append(np.mean(ice_psd[:, mask & mask_400], axis=1))
                    plume_max_ice_psd_450[k].append(np.mean(ice_psd[:, mask & mask_450], axis=1))
                    plume_max_ice_psd_500[k].append(np.mean(ice_psd[:, mask & mask_500], axis=1))
                    plume_max_ice_psd_550[k].append(np.mean(ice_psd[:, mask & mask_550], axis=1))
                    plume_max_liq_psd[k].append(np.mean(liq_psd[:, mask], axis=1))

                    mask_incloud = np.where(qliq > 0.01, True, False)
                    if len(plume_max_accumulated_heat_release[k]) == 0:
                        temporary_plume_max_accumulated_heat_release[k].append(np.mean(rd_rhoh_mp[(mask & mask_incloud)]) * self.grid_volume)
                        plume_max_accumulated_heat_release[k].append(0.0)
                    else:
                        temporary_plume_max_accumulated_heat_release[k].append(np.mean(rd_rhoh_mp[(mask & mask_incloud)]) * self.grid_volume)
                        plume_max_accumulated_heat_release[k].append(plume_max_accumulated_heat_release[k][-1] + temporary_plume_max_accumulated_heat_release[k][-1] * self.dtime)
                    plume_max_incloud_w[k].append(np.mean(w[(mask & mask_incloud)]))
                    plume_max_reduced_w[k].append(np.mean(reduced_w[(mask & mask_incloud)]))


                    mask_distance = list(map(lambda y: np.where((plume_location_y > y) & (plume_location_y < y + self.grid_spacing), True, False), [1000.0, 2000.0, 3000.0, 4000.0]))
                    assert mask_distance[0].shape == mask.shape, f"mask shape mismatch! {mask_distance[0].shape}, {mask.shape}"
                    if np.any(mask_distance[0] & mask):
                        plume_1000m_xgrid[k].append(plume_location_x[(mask_distance[0] & mask)])
                        plume_1000m_zgrid[k].append(plume_location_z[(mask_distance[0] & mask)])
                    if np.any(mask_distance[1] & mask):
                        plume_2000m_xgrid[k].append(plume_location_x[(mask_distance[1] & mask)])
                        plume_2000m_zgrid[k].append(plume_location_z[(mask_distance[1] & mask)])
                    if np.any(mask_distance[2] & mask):
                        plume_3000m_xgrid[k].append(plume_location_x[(mask_distance[2] & mask)])
                        plume_3000m_zgrid[k].append(plume_location_z[(mask_distance[2] & mask)])
                    if np.any(mask_distance[3] & mask): 
                        plume_4000m_xgrid[k].append(plume_location_x[(mask_distance[3] & mask)])
                        plume_4000m_zgrid[k].append(plume_location_z[(mask_distance[3] & mask)])
                    if arrive_at_2000m and not arrive_at_4000m:
                        plume_2000m_all_qice[k].append(qice)
                        plume_2000m_all_nice[k].append(nice)
                
                if not arrive_at_3000m and current_y > 3000.0:
                    plume_3000m_time[k] = t
                    arrive_at_3000m = True
                if not arrive_at_2000m and current_y > 2000.0:
                    plume_2000m_time[k] = t
                    arrive_at_2000m = True
                if not arrive_at_4000m and current_y > 4000.0:
                    plume_4000m_time[k] = t
                    arrive_at_4000m = True

                if current_y > 4400.0:
                    break
        plume_state = PlumeState(
            plume_max_time=plume_max_time,
            plume_max_loc_x=plume_max_loc_x,
            plume_max_loc_y=plume_max_loc_y,
            plume_max_loc_z=plume_max_loc_z,
            plume_max_rh=plume_max_rh,
            plume_max_rhi=plume_max_rhi,
            plume_max_amps_rh=plume_max_amps_rh,
            plume_max_amps_rhi=plume_max_amps_rhi,
            plume_max_w=plume_max_w,
            plume_max_w_bk=plume_max_w_bk,
            plume_max_incloud_w=plume_max_incloud_w,
            plume_max_reduced_w=plume_max_reduced_w,
            plume_max_qtotal=plume_max_qtotal,
            plume_max_qtotal_plus_qv=plume_max_qtotal_plus_qv,
            plume_max_qv_t=plume_max_qv_t,
            plume_max_pot_temperature=plume_max_pot_temperature,
            plume_max_temperature=plume_max_temperature,
            plume_max_buoyancy=plume_max_buoyancy,
            plume_max_ice_count=plume_max_ice_count,
            plume_max_ice_count_300=plume_max_ice_count_300,
            plume_max_ice_count_350=plume_max_ice_count_350,
            plume_max_ice_count_400=plume_max_ice_count_400,
            plume_max_ice_count_450=plume_max_ice_count_450,
            plume_max_ice_count_500=plume_max_ice_count_500,
            plume_max_ice_count_550=plume_max_ice_count_550,
            plume_max_qice=plume_max_qice,
            plume_max_qliq=plume_max_qliq,
            plume_max_dice=plume_max_dice,
            plume_max_dliq=plume_max_dliq,
            plume_max_nice=plume_max_nice,
            plume_max_total_nice=plume_max_total_nice,
            plume_max_nagg=plume_max_nagg,
            plume_max_nliq=plume_max_nliq,
            plume_max_tke=plume_max_tke,
            plume_max_cact=plume_max_cact,
            plume_max_reduced_cact=plume_max_reduced_cact,
            plume_max_col_rate=plume_max_col_rate,
            plume_max_acratio=plume_max_acratio,
            plume_max_ice_psd=plume_max_ice_psd,
            plume_max_ice_psd_300=plume_max_ice_psd_300,
            plume_max_ice_psd_350=plume_max_ice_psd_350,
            plume_max_ice_psd_400=plume_max_ice_psd_400,
            plume_max_ice_psd_450=plume_max_ice_psd_450,
            plume_max_ice_psd_500=plume_max_ice_psd_500,
            plume_max_ice_psd_550=plume_max_ice_psd_550,
            plume_max_liq_psd=plume_max_liq_psd,
            plume_max_accumulated_heat_release=plume_max_accumulated_heat_release,
            temporary_plume_max_accumulated_heat_release=temporary_plume_max_accumulated_heat_release,
            plume_1000m_xgrid=plume_1000m_xgrid,
            plume_1000m_zgrid=plume_1000m_zgrid,
            plume_2000m_xgrid=plume_2000m_xgrid,
            plume_2000m_zgrid=plume_2000m_zgrid,
            plume_3000m_xgrid=plume_3000m_xgrid,
            plume_3000m_zgrid=plume_3000m_zgrid,
            plume_4000m_xgrid=plume_4000m_xgrid,
            plume_4000m_zgrid=plume_4000m_zgrid,
            plume_2000m_time=plume_2000m_time,
            plume_3000m_time=plume_3000m_time,
            plume_4000m_time=plume_4000m_time,
            plume_2000m_all_qice=plume_2000m_all_qice,
            plume_3000m_all_qice=plume_3000m_all_qice,
            plume_4000m_all_qice=plume_4000m_all_qice,
            plume_2000m_all_nice=plume_2000m_all_nice,
            plume_3000m_all_nice=plume_3000m_all_nice,
            plume_4000m_all_nice=plume_4000m_all_nice,
        )
        object.__setattr__(self, "plume_state", plume_state)
                