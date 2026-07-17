# AMPS Update 20260603 — Summary of Changes

Comparison between `contrib/AMPS` (previous) and `contrib/AMPS_update_20260603/AMPS_update_20260603` (new).
Most changes are tagged `2026/06 T.Hashino updated` or attributed to `Y.SATO (2025-04-22)`.

---

## Files changed

### `Makefile`
- Added `makedir` as a prerequisite target.
- Split `allclean` into `distclean` (removes build artifacts) + `allclean` (calls `distclean`).

---

### `com_amps.F90`
- **`CCNMAX`** default changed: 230.0 → 215.0 cm⁻³.
- **`INMAX`** new parameter added: 1.7e-3 cm⁻³ (limiting IN concentration for `flagp_a=3`).
- **`nucleation_halflife`** variable **removed**.

---

### `class_Cloud_Micro.F90`
- `nucleation_halflife` removed from type declaration, constructor, and all call signatures.
- Ice nucleation call (`micexfg(10)==1`) now also requires `act_type >= 2`.
- `dbintendl` dimension reduced from `(7,2,mxnbin,L)` → `(3,2,mxnbin,L)` — aggregation and freezing bin tendency diagnostics removed.

---

### `class_Group.F90`
- **Aerosol floor** `n_lmt_ap` restored to `1.0e-5` (was set to `0.0d0`); corresponding error-abort checks for negative aerosol mass/concentration re-enabled (they had been commented out).
- **Aspect ratio tolerance** `allow=1.0e-4` introduced; `phi_ic == 1.0` comparisons replaced by `1.0 ± allow`.
- **`get_effect_area` / `get_circum_area`** function signatures extended with new `is_mod2` argument (instead of using `IS%is_mod(2)` internally); area calculation bug with `i_sh_le1` vs `i_sh_le2` corrected.
- **Terminal velocity error handling** (Y.SATO, 2025-04-22): when `vtm > 50 m/s`, abort only if mass or concentration exceeds 1e-10; otherwise issue a `LOG_WARN` instead of `PRC_abort`.
- **New subroutine `diag_habit_v4t`** added — a revised habit diagnosis function for polycrystals including an Oliktok aspect-ratio parameterization.

---

### `class_Ice_Shape.F90`
- Two new fields added to the ice shape struct: `q_e_ic` (porosity/area ratio of initial crystal) and `q_e_im` (of matured particle).
- `diag_habit_v4` renamed/replaced by `diag_habit_v4t` in the public interface.
- `get_effect_area` / `get_circum_area` updated to accept the new `is_mod2` argument.

---

### `class_Mass_Bin.F90`
- Collision mass fraction parameter: `frac = 0.1` → `frac = 0.01`.
- Bug fix in mass transfer: `dum2 = mass1/mass_q_grp` → `dum2 = mass2/mass_q_grp`.

---

### `mod_amps_lib.F90`
- Removed two stale comment markers: `! changed for sheba` / `! end changed for sheba`.

---

### `mod_amps_utility.F90`
- `nbin_h` and `INMAX` added to argument/variable lists; `nucleation_halflife` removed.
- Aerosol concentration floor code (setting `acon_q`, `amt_q`, `ams_q` minimums) **restored** (was commented out with a TODO note).
- Several `actINF_p`-related code blocks added as **commented-out** stubs for IN activation tracking (not yet active).

---

### `mod_amps_core.F90` (most extensive changes)

#### Nucleation interface changes
- `nucleation_halflife` / `frac_dust` removed from `deposition_mode_vec` call signature.
- `deposition_mode_vec` now takes `mes_rc` and `flagp_a` instead.
- `contact_mode` call **vectorized** — moved outside the grid loop (now passes full `ga` array rather than per-column `ag%TV(n)`).
- Immersion/homogeneous freezing calls updated to pass full `ga` array.

#### CCN / IN activation fixes
- **CCN activation**: `sw_allow` replaced by `sw_act_allow = 0.02` (critical supersaturation floor).
- **`flagp_a` limiter** for blocking `INMAX` usage when `flagp_a ∈ {-3,-2,-6,-5}` re-enabled (was commented out in both CCN and DHF paths).
- **Ice nucleation function**: switched from `get_inact_tropic` to `get_inact` with background (`ni_0`) subtraction for both deposition and contact modes.
- **Deposition nucleation**: now accounts for already-nucleated background with `max(get_inact(si) - ni_0(n), 0)`.
- DHF limiter (`akk_lmt_DHF`) with `INMAX` re-enabled (was commented out).

#### Collision / sedimentation
- New parameters `aNp_min = 1e-20` and `aMp_min = 1e-20` replace hardcoded `1e-30` in particle collision filter.
- Bug fix: `g%MS(i,n)%mass(1)` → `mass(rmt)` / `mass(imt)` in several collision/sedimentation checks.
- `cal_xxx_p_v5_vec` now takes `ag` (air group) as its first argument at all call sites.

#### Code cleanup
- Large block of legacy commented-out code removed (old matrix-solver stubs `!!$`, habit diagnostics `!!c`, etc.).
- New commented-out `actINF_p` infrastructure stubs added (parallel to `mod_amps_utility` changes).
