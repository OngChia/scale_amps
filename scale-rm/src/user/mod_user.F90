!-------------------------------------------------------------------------------
!> module USER
!!
!! @par Description
!!          User defined module
!!
!! @author Team SCALE
!!
!<
!-------------------------------------------------------------------------------
#include "scalelib.h"
module mod_user
  !-----------------------------------------------------------------------------
  !
  !++ used modules
  !
  use scale_precision
  use scale_io
  use scale_prof
  use scale_atmos_grid_cartesC_index
  use scale_tracer
  !-----------------------------------------------------------------------------
  implicit none
  private
  !-----------------------------------------------------------------------------
  !
  !++ Public procedure
  !
  public :: USER_tracer_setup
  public :: USER_setup
  public :: USER_finalize
  public :: USER_mkinit
  public :: USER_calc_tendency
  public :: USER_update

  !-----------------------------------------------------------------------------
  !
  !++ Public parameters & variables
  !
  !-----------------------------------------------------------------------------
  !
  !++ Private procedure
  !
  !-----------------------------------------------------------------------------
  !
  !++ Private parameters & variables
  !
  logical, private :: USER_do = .false. !< do user step?

  ! *********************************************************************
  ! -- these are defined for AMPS idealized runs
  ! *********************************************************************
  logical :: SWITCH_VERTICAL_ACCE_TYPE = .false.
  logical :: SWITCH_MOMZ = .false.
  logical :: SWITCH_RHOU = .false.
  logical :: SWITCH_RHOV = .false.
  logical :: SWITCH_DENS = .false.
  logical :: SWITCH_QVAP_ONLY = .false.
  logical :: SWITCH_RHOT = .false.
  logical :: SWITCH_TEMP = .false.
  logical :: SWITCH_RHOQ = .false.
  
  logical :: DO_CLOUD_SEEDING = .false.
  real(RP) :: RELEASE_INP_CONC_TIME_RATE = 0.0_RP
  real(RP) :: RELEASE_INP_Z_LOWER_LIMIT = 0.0_RP
  real(RP) :: RELEASE_INP_X_LOWER_LIMIT = 0.0_RP
  real(RP) :: RELEASE_INP_X_UPPER_LIMIT = 0.0_RP
  integer :: RELEASE_INP_TIME_HOUR_LOWER_LIMIT = 0
  integer :: RELEASE_INP_TIME_HOUR_UPPER_LIMIT = 0
  integer :: RELEASE_INP_TIME_MIN_LOWER_LIMIT = 0
  integer :: RELEASE_INP_TIME_MIN_UPPER_LIMIT = 0
  integer :: RELEASE_INP_TIME_SEC_LOWER_LIMIT = 0
  integer :: RELEASE_INP_TIME_SEC_UPPER_LIMIT = 0

  real(RP), allocatable :: largeScaleTTendency(:) ! large-scale temperature forcing
  real(RP), allocatable :: largeScaleQTendency(:) ! large-scale vapor forcing
  real(RP), allocatable :: WLS(:) ! large-scale sinking
  real(RP) :: sfc_largeScaleTTendency, sfc_largeScaleQTendency, sfc_wls

  !-----------------------------------------------------------------------------
contains
  !-----------------------------------------------------------------------------
  !> Config before setup of tracers
  subroutine USER_tracer_setup
    use scale_tracer, only: &
       TRACER_regist
    implicit none

    ! if you want to add tracers, call the TRACER_regist subroutine.
    ! e.g.,
!    integer, parameter     :: NQ = 1
!    integer                :: QS
!    character(len=H_SHORT) :: NAME(NQ)
!    character(len=H_MID)   :: DESC(NQ)
!    character(len=H_SHORT) :: UNIT(NQ)
!
!    data NAME (/ 'name' /)
!    data DESC (/ 'tracer name' /)
!    data UNIT (/ 'kg/kg' /)
    !---------------------------------------------------------------------------

!    call TRACER_regist( QS,   & ! [OUT]
!                        NQ,   & ! [IN]
!                        NAME, & ! [IN]
!                        DESC, & ! [IN]
!                        UNIT  ) ! [IN]

    return
  end subroutine USER_tracer_setup

  !-----------------------------------------------------------------------------
  !> Setup before setup of other components
  subroutine USER_setup
    use scale_prc, only: &
       PRC_abort
    use scale_const, only: &
       PI => CONST_PI
    use scale_prc_cartesC, only: &
       PRC_2Drank
    use scale_prc, only: &
       PRC_myrank
    use scale_atmos_grid_cartesC, only: &
       GLOBAL_DOMAIN_CX => ATMOS_GRID_CARTESC_CXG, &
       GLOBAL_DOMAIN_CY => ATMOS_GRID_CARTESC_CYG, &
       DOMAIN_CX => ATMOS_GRID_CARTESC_CX, &
       DOMAIN_CY => ATMOS_GRID_CARTESC_CY, &
       CZ  => ATMOS_GRID_CARTESC_CZ, &
       FZ  => ATMOS_GRID_CARTESC_FZ
    implicit none

    integer, parameter :: EXP_klim = 501 ! there was a bug: EXP_klim = 100 (3/4/2020), after
                                         ! SHEBA has been run
    integer            :: EXP_kmax

    logical  :: USER_const = .true.

    real(RP) :: EXP_z   (EXP_klim+1) ! height      [m]

    real(RP) :: SFC_TTND             ! surface large-scale temperature tendency [K/s]
    real(RP) :: EXP_ttnd(EXP_klim+1) ! large-scale temperature tendency [K/s]
    real(RP) :: SFC_QTND             ! surface large-scale vapor tendency [kg/kg/s]
    real(RP) :: EXP_qtnd(EXP_klim+1) ! large-scale vapor tendency [kg/kg/s]
    real(RP) :: SFC_WSIK             ! surface large-scale sinking [m/s]
    real(RP) :: EXP_Wsik(EXP_klim+1) ! large-scale sinking [m/s]

    character(len=H_LONG) :: USER_file = ''

    real(RP) :: T_tend = 0.0_RP
    real(RP) :: Q_tend = 0.0_RP
    real(RP) :: W_sink = 0.0_RP

    real(RP) :: fact1, fact2, ttnd(KA), qtnd(KA), wlse(KA)

    integer :: k, kref
    integer :: fid
    integer :: ierr

    namelist / PARAM_USER / &
       USER_do, &
       USER_file, &
       USER_const, &
       SWITCH_VERTICAL_ACCE_TYPE, &
       SWITCH_MOMZ, &
       SWITCH_RHOU, &
       SWITCH_RHOV, &
       SWITCH_DENS, &
       SWITCH_QVAP_ONLY, &
       SWITCH_RHOT, &
       SWITCH_TEMP, &
       SWITCH_RHOQ, &
       DO_CLOUD_SEEDING, &
       RELEASE_INP_CONC_TIME_RATE, &
       RELEASE_INP_Z_LOWER_LIMIT, &
       RELEASE_INP_X_LOWER_LIMIT, &
       RELEASE_INP_X_UPPER_LIMIT, &
       RELEASE_INP_TIME_HOUR_LOWER_LIMIT, &
       RELEASE_INP_TIME_HOUR_UPPER_LIMIT, &
       RELEASE_INP_TIME_MIN_LOWER_LIMIT, &
       RELEASE_INP_TIME_MIN_UPPER_LIMIT, &
       RELEASE_INP_TIME_SEC_LOWER_LIMIT, &
       RELEASE_INP_TIME_SEC_UPPER_LIMIT

    !---------------------------------------------------------------------------

    LOG_NEWLINE
    LOG_INFO("USER_setup",*) 'Setup'

    !--- read namelist
    rewind(IO_FID_CONF)
    read(IO_FID_CONF,nml=PARAM_USER,iostat=ierr)
    if( ierr < 0 ) then !--- missing
       LOG_INFO("USER_setup",*) 'Not found namelist. Default used.'
    elseif( ierr > 0 ) then !--- fatal error
       LOG_ERROR("USER_setup",*) 'Not appropriate names in namelist PARAM_USER. Check!'
       call PRC_abort
    endif
    LOG_NML(PARAM_USER)

    LOG_NEWLINE
    LOG_INFO("USER_setup",*) 'This module is dummy.'

    ! initialization of local arrays
    allocate(largeScaleTTendency(KA),largeScaleQTendency(KA),WLS(KA))
    largeScaleTTendency(:) = 0.0_RP
    largeScaleQTendency(:) = 0.0_RP
    WLS(:) = 0.0_RP

    ! temporarily set to zero
    if ( USER_const .eqv. .true. ) then

       largeScaleTTendency(KS:KE) = T_tend
       largeScaleQTendency(KS:KE) = Q_tend
       WLS(KS:KE) = W_sink

       sfc_largeScaleTTendency = largeScaleTTendency(KS)
       sfc_largeScaleQTendency = largeScaleQTendency(KS)
       sfc_wls = WLS(KS)

       WLS(KE+1) = WLS(KE)
       WLS(KS-1) = WLS(KS)

    else

       fid = IO_get_available_fid()
       open( fid,                                 &
             file   = trim(USER_file), &
             form   = 'formatted',                &
             status = 'old',                      &
             iostat = ierr                        )

       if ( ierr /= 0 ) then
          LOG_ERROR("read_largescale_amps",*) '[user_setup/read_largescale] Input file not found!'
          call PRC_abort
       endif

       !--- read sounding file till end
       read(fid,*) SFC_TTND, SFC_QTND, SFC_WSIK

       LOG_INFO("USER_setup",*) '+ Surface large-scale temperature tendency [K/s]', SFC_TTND

       sfc_largeScaleTTendency = SFC_TTND
       sfc_largeScaleQTendency = SFC_QTND
       sfc_wls = SFC_WSIK

       do k = 2, EXP_klim
          read(fid,*,iostat=ierr) EXP_z(k), EXP_ttnd(k), EXP_qtnd(k), EXP_wsik(k)
          if ( ierr /= 0 ) exit
       enddo

       EXP_kmax = k - 1
       close(fid)

       ! Boundary
       EXP_z   (1)          = 0.0_RP
       EXP_ttnd(1)          = SFC_TTND
       EXP_qtnd(1)          = SFC_QTND
       EXP_wsik(1)          = SFC_WSIK
       EXP_z   (EXP_kmax+1) = 100.E3_RP
       EXP_ttnd(EXP_kmax+1) = EXP_ttnd(EXP_kmax)
       EXP_qtnd(EXP_kmax+1) = EXP_qtnd(EXP_kmax)
       EXP_wsik(EXP_kmax+1) = EXP_wsik(EXP_kmax)

       !--- linear interpolate to model grid
       do k = KS, KE
          do kref = 2, EXP_kmax+1
             if (       CZ(k) >  EXP_z(kref-1) &
                  .AND. CZ(k) <= EXP_z(kref  ) ) then

                fact1 = ( EXP_z(kref) - CZ(k)   ) / ( EXP_z(kref)-EXP_z(kref-1) )
                fact2 = ( CZ(k) - EXP_z(kref-1) ) / ( EXP_z(kref)-EXP_z(kref-1) )

                ttnd(k) = EXP_ttnd(kref-1) * fact1 &
                        + EXP_ttnd(kref  ) * fact2
                qtnd(k) = EXP_qtnd(kref-1) * fact1 &
                        + EXP_qtnd(kref  ) * fact2
                wlse(k) = EXP_wsik(kref-1) * fact1 &
                        + EXP_wsik(kref  ) * fact2

             endif
          enddo
       enddo

       do k = KS, KE
          largeScaleTTendency(k) = ttnd(k)
          largeScaleQTendency(k) = qtnd(k)
          WLS(k) = wlse(k)
       enddo

       WLS(KE+1) = WLS(KE)
       WLS(KS-1) = sfc_wls
    endif

    LOG_NEWLINE
    LOG_INFO("USER_setup",'(1x,A)') 'Large-scale advective tendency of temperature, water vapor, and subsidence'
    LOG_INFO_CONT('(1x,A)') '====================================================='
    LOG_INFO_CONT('(1x,A)') '      GRID CENTER         Tadv            Qadv             W'
    do k = KS-1, KE
       LOG_INFO_CONT('(1x,A,ES15.5,A,ES15.5,A,ES15.5,A,ES15.5)') '    ', CZ(k), '   ', largeScaleTTendency(k), '   ', largeScaleQTendency(k), '   ', WLS(k)
    enddo
    LOG_INFO_CONT('(1x,A)') '====================================================='

    LOG_NEWLINE
    LOG_INFO("USER_setup",'(1x,A)') 'SEEDING CY'
    LOG_INFO_CONT('(1x,A)') '====================================================='
    do k = JS, JE
       LOG_INFO_CONT('(1x,A,I5,2ES15.5)') '    ', k, GLOBAL_DOMAIN_CY(PRC_2Drank(PRC_myrank, 2)*(JE - JS + 1) + k), DOMAIN_CY(k)
       WRITE(*,'(1x,A,2I5,2ES15.5)') '  CY  ', PRC_myrank, k, GLOBAL_DOMAIN_CY(PRC_2Drank(PRC_myrank, 2)*(JE - JS + 1) + k), DOMAIN_CY(k)
    enddo
    LOG_INFO_CONT('(1x,A)') '====================================================='

    LOG_NEWLINE
    LOG_INFO("USER_setup",'(1x,A)') 'SEEDING CX'
    LOG_INFO_CONT('(1x,A)') '====================================================='
    do k = IS, IE
       LOG_INFO_CONT('(1x,A,I5,2ES15.5)') '    ', k, GLOBAL_DOMAIN_CX(PRC_2Drank(PRC_myrank, 1)*(IE - IS + 1) + k), DOMAIN_CX(k)
       WRITE(*,'(1x,A,2I5,2ES15.5)') '  CX  ', PRC_myrank, k, GLOBAL_DOMAIN_CX(PRC_2Drank(PRC_myrank, 1)*(IE - IS + 1) + k), DOMAIN_CX(k)
    enddo
    LOG_INFO_CONT('(1x,A)') '====================================================='

    return
  end subroutine USER_setup

  !-----------------------------------------------------------------------------
  !> Finalization
  subroutine USER_finalize
    implicit none
    !---------------------------------------------------------------------------

    LOG_NEWLINE
    LOG_INFO("USER_finalize",*) 'Finalize'

    if (allocated(largeScaleTTendency)) deallocate(largeScaleTTendency)
    if (allocated(largeScaleQTendency)) deallocate(largeScaleQTendency)
    if (allocated(WLS)) deallocate(WLS)
    if (allocated(largeScaleTTendency)) deallocate(largeScaleTTendency)

    return
  end subroutine USER_finalize

  !-----------------------------------------------------------------------------
  !> Make initial state
  subroutine USER_mkinit
    use scale_prc, only: &
       PRC_abort
    use scale_atmos_hydrometeor, only: &
       ATMOS_HYDROMETEOR_dry, &
       N_HYD, &
       I_HC
    use mod_atmos_vars, only: &
       DENS, &
       MOMZ, &
       MOMX, &
       MOMY, &
       RHOT, &
       QTRC
    use mod_atmos_phy_mp_vars, only: &
       QA_MP, &
       QS_MP, &
       QE_MP
    use mod_atmos_phy_mp_driver, only: &
       ATMOS_PHY_MP_driver_qhyd2qtrc
    implicit none
    !---------------------------------------------------------------------------

    real(RP) :: RHO(KA)
    real(RP) :: VELX(KA)
    real(RP) :: VELY(KA)
    real(RP) :: POTT(KA)
    real(RP) :: QV1D(KA)
    real(RP) :: QCI1D(KA)
    real(RP) :: QNUM1D(KA)

    real(RP) :: qv(KA,IA,JA)
    real(RP) :: QHYD(KA,IA,JA,N_HYD)
    real(RP) :: QNUM(KA,IA,JA,N_HYD)

    integer :: ierr
    integer :: k, i, j
    !---------------------------------------------------------------------------

    LOG_NEWLINE
    LOG_INFO("MKINIT_CLOUDLAB",*) 'Nothing to be done. Continue...'

    
    return
  end subroutine USER_mkinit

  !-----------------------------------------------------------------------------
  !> Calculation tendency
  subroutine USER_calc_tendency
    use scale_const, only: &
       CONST_GRAV, &
       CONST_EPS
    use scale_atmos_grid_cartesC_real, only: &
       REAL_CZ => ATMOS_GRID_CARTESC_REAL_CZ, &
       REAL_FZ => ATMOS_GRID_CARTESC_REAL_FZ
    use scale_file_history, only: &
       FILE_HISTORY_in
    use mod_atmos_vars, only: &
       DENS,  &
       MOMZ   => MOMZ_av, &
       U, &
       V, &
       W, &
       QTRC,  &
       PRES,  &
       TEMP,  &
       POTT,  &
       RHOT,  &
       DENS_t => DENS_tp, & ! cell center
       RHOU_t => RHOU_tp, & ! cell center
       RHOV_t => RHOV_tp, & ! cell center
       MOMZ_t => MOMZ_tp, & ! cell face
       RHOT_t => RHOT_tp, & ! cell center
       RHOQ_t => RHOQ_tp    ! cell center
    use mod_atmos_phy_mp_vars, only: &
       QS_MP, &
       QE_MP
    use scale_time, only: &
       TIME_NOWDATE, &
       dt => TIME_DTSEC
    use scale_prc_cartesC, only: &
       PRC_2Drank
    use scale_prc, only: &
       PRC_myrank
    use scale_atmos_grid_cartesC, only: &
       GLOBAL_DOMAIN_CX => ATMOS_GRID_CARTESC_CXG, &
       GLOBAL_DOMAIN_CY => ATMOS_GRID_CARTESC_CYG, &
       DOMAIN_CZ => ATMOS_GRID_CARTESC_CZ
    use scale_atmos_phy_mp_amps, only: &
       nca, &
       nba, &
       I_QPPVA
    use com_amps, only: &
       coef_ap, &
       eps_ap
    implicit none
    !---------------------------------------------------------------------------

    real(RP) :: MOMZ_t_USER(KA,IA,JA)
    real(RP) :: RHOU_t_USER(KA,IA,JA)
    real(RP) :: RHOV_t_USER(KA,IA,JA)
    real(RP) :: DENS_t_USER(KA,IA,JA)
    real(RP) :: RHOT_t_USER(KA,IA,JA)
    real(RP) :: RHOH_t_USER(KA,IA,JA)
    real(RP) :: TEMP_t_USER(KA,IA,JA)
    real(RP) :: RHOQ_t_USER(KA,IA,JA,QS_MP:QE_MP)
    real(RP) :: RHOQ_t_SEED(KA,IA,JA,QS_MP:QE_MP)

    real(RP) :: subsidence_sink(KA,IA,JA)

    real(RP) :: DENS_column(KA), RHOT_column(KA), U_column(KA), V_column(KA), W_column(KA), POTT_column(KA)
    real(RP) :: QTRC_column(KA,QA), MOMZ_column(KA), TEMP_column(KA)
    real(RP) :: FZ(KA), FDZ(KA), RFDZ(KA), RCDZ(KA)

    real(RP) :: SINK_DUP, SINK_UP, SINK_CEN


    integer  :: k, i, j, iq, ipa_qpa, ica, iba

    if ( .not. USER_do ) then
       return
    endif

    LOG_PROGRESS(*) 'atmosphere / user'

    MOMZ_t_USER(:,:,:) = 0.0_RP
    RHOU_t_USER(:,:,:) = 0.0_RP
    RHOV_t_USER(:,:,:) = 0.0_RP
    DENS_t_USER(:,:,:) = 0.0_RP
    RHOT_t_USER(:,:,:) = 0.0_RP
    RHOH_t_USER(:,:,:) = 0.0_RP
    TEMP_t_USER(:,:,:) = 0.0_RP

    RHOQ_t_USER(:,:,:,:) = 0.0_RP
    RHOQ_t_SEED(:,:,:,:) = 0.0_RP

    subsidence_sink = 0.0_RP

    ! Perform drone cloud seeding. We only spread INP on the first row in J direction between x=[800, 1200] (m) assuming that size of the domain in I direction is 2 km.
    ! The height of cloud seeding is at 500 m according to the BAMS paper.
    ! Cloud seeding only happens after 1 hour into the simulation at 1800 for 2 min assuming the model correctly spins up after 1 hour.
    if ( DO_CLOUD_SEEDING .and. &
         TIME_NOWDATE(4) >= RELEASE_INP_TIME_HOUR_LOWER_LIMIT .and. &
         TIME_NOWDATE(5) >= RELEASE_INP_TIME_MIN_LOWER_LIMIT .and. &
         TIME_NOWDATE(6) >= RELEASE_INP_TIME_SEC_LOWER_LIMIT .and. &
         TIME_NOWDATE(4) < RELEASE_INP_TIME_HOUR_UPPER_LIMIT .and. &
         TIME_NOWDATE(5) < RELEASE_INP_TIME_MIN_UPPER_LIMIT .and. &
         TIME_NOWDATE(6) < RELEASE_INP_TIME_SEC_UPPER_LIMIT &
         ) then
       do k = KS, KE
         !if ( DOMAIN_CZ(k) >= 500.0D0 - CONST_EPS .and. GLOBAL_DOMAIN_CY(PRC_2Drank(PRC_myrank, 2)*(JE - JS + 1) + JS) < 50.0D0 ) then
         if ( DOMAIN_CZ(k) >= RELEASE_INP_Z_LOWER_LIMIT + CONST_EPS .and. GLOBAL_DOMAIN_CY(PRC_2Drank(PRC_myrank, 2)*(JE - JS + 1) + JS) < 50.0D0 ) then
           LOG_PROGRESS(*) 'atmosphere / user / cloud_seeding', k
           !$omp parallel do OMP_SCHEDULE_ default(none) &
           !$omp private(i, ipa_qpa, ica, iba) &
           !$omp shared(IS, IE, JS, JE, RHOQ_t_SEED, DENS, coef_ap, eps_ap, dt, k, nca, nba, I_QPPVA, QS_MP, PRC_2Drank, PRC_myrank, &
           !$omp        GLOBAL_DOMAIN_CX, RELEASE_INP_X_LOWER_LIMIT, RELEASE_INP_X_UPPER_LIMIT, &
           !$omp        RELEASE_INP_CONC_TIME_RATE)
            do i = IS, IE
                if ( GLOBAL_DOMAIN_CX(PRC_2Drank(PRC_myrank, 1)*(IE - IS + 1) + i) >= RELEASE_INP_X_LOWER_LIMIT .and. &
                     GLOBAL_DOMAIN_CX(PRC_2Drank(PRC_myrank, 1)*(IE - IS + 1) + i) <= RELEASE_INP_X_UPPER_LIMIT ) then
                   ipa_qpa = 0
                   do ica = 1, nca
                      do iba = 1, nba
                         if ( ica /= 2 ) then
                            ipa_qpa = ipa_qpa + 3
                            cycle
                         endif
                         RHOQ_t_SEED(k,i,JS,QS_MP+I_QPPVA+ipa_qpa-1) = RHOQ_t_SEED(k,i,JS,QS_MP+I_QPPVA+ipa_qpa-1) + &
                            RELEASE_INP_CONC_TIME_RATE * coef_ap(ica) / dt * 1000.0_RP
                         RHOQ_t_SEED(k,i,JS,QS_MP+I_QPPVA+ipa_qpa) = RHOQ_t_SEED(k,i,JS,QS_MP+I_QPPVA+ipa_qpa) + &
                            RELEASE_INP_CONC_TIME_RATE * DENS(k,i,JS) / dt
                         RHOQ_t_SEED(k,i,JS,QS_MP+I_QPPVA+ipa_qpa+1) = RHOQ_t_SEED(k,i,JS,QS_MP+I_QPPVA+ipa_qpa+1) + &
                            RELEASE_INP_CONC_TIME_RATE * coef_ap(ica) * eps_ap(ica) / dt * 1000.0_RP
                           
                         ipa_qpa = ipa_qpa + 3
                      enddo
                   enddo
                endif
            enddo
            exit
         endif
       enddo

       !$omp parallel do default(none) private(i,j,k,iq) OMP_SCHEDULE_ collapse(2) &
       !$omp shared(JS,JE,IS,IE,KS,KE,QS_MP,QE_MP,RHOQ_t,RHOQ_t_SEED)
       do i = IS, IE
       do j = JS, JE
       do k = KS, KE
          do iq = QS_MP, QE_MP
             RHOQ_t(k,i,j,iq) = RHOQ_t(k,i,j,iq) + RHOQ_t_SEED(k,i,j,iq)
          enddo
       enddo
       enddo
       enddo

    endif

    ipa_qpa = 0
    do ica = 1, nca
       do iba = 1, nba
          if ( ica /= 3 ) then
             ipa_qpa = ipa_qpa + 3
             cycle
          endif
          call FILE_HISTORY_in( RHOQ_t_SEED(:,:,:,QS_MP+I_QPPVA+ipa_qpa-1), 'RHOQ_t_SEED_mass', 'cloud-seeding mass',          'kg/m3/s',   fill_halo=.true. )
          call FILE_HISTORY_in( RHOQ_t_SEED(:,:,:,QS_MP+I_QPPVA+ipa_qpa), 'RHOQ_t_SEED_conc', 'cloud-seeding concentration',          'kg/m3/s /cm3',   fill_halo=.true. )
          call FILE_HISTORY_in( RHOQ_t_SEED(:,:,:,QS_MP+I_QPPVA+ipa_qpa+1), 'RHOQ_t_SEED_sol_mass', 'cloud-seeding soluböe mass',          'kg/m3/s',   fill_halo=.true. )
          ipa_qpa = ipa_qpa + 3
          LOG_PROGRESS(*) 'atmosphere / user / cloud_seeding / indices', QS_MP+I_QPPVA+ipa_qpa-1, QS_MP+I_QPPVA+ipa_qpa, QS_MP+I_QPPVA+ipa_qpa+1
       enddo
    enddo


    !$omp parallel do &
    !$omp private(FZ,FDZ,RFDZ,RCDZ,DENS_column,TEMP_column,POTT_column,U_column,V_column,W_column,RHOT_column,MOMZ_column,QTRC_column, &
    !$omp         SINK_CEN,SINK_UP,SINK_DUP)
    do j = JS, JE
    do i = IS, IE

       ! define grid interval
       FZ(1:KA) = REAL_FZ(1:KA,i,j)
       FDZ(KS-1) = REAL_CZ(KS,i,j) - REAL_FZ(KS-1,i,j)
       RFDZ(KS-1) = 1.0_RP / FDZ(KS-1)
       do k = KS, KE
          FDZ(k) = REAL_CZ(k+1,i,j) - REAL_CZ(k  ,i,j)
          RFDZ(k) = 1.0_RP / FDZ(k)
          RCDZ(k) = 1.0_RP / ( REAL_FZ(k  ,i,j) - REAL_FZ(k-1,i,j) )
       enddo

       ! define columnar prognotic variables with boundary condition (upper and lower)
       do k = KS, KE
          DENS_column(k) = DENS(k,i,j)
          TEMP_column(k) = TEMP(k,i,j)
          POTT_column(k) = POTT(k,i,j)
          U_column(k) = U(k,i,j)
          V_column(k) = V(k,i,j)
          W_column(k) = W(k,i,j)
          RHOT_column(k) = RHOT(k,i,j)
          MOMZ_column(k) = MOMZ(k,i,j)
          do iq = 1, QA
             QTRC_column(k,iq) = QTRC(k,i,j,iq)
          enddo
       enddo
       ! the upper boundary condition by linear extrapolation
       DENS_column(KE+1) = 2.0_RP*DENS_column(KE) - DENS_column(KE-1)
       TEMP_column(KE+1) = 2.0_RP*TEMP_column(KE) - TEMP_column(KE-1)
       POTT_column(KE+1) = 2.0_RP*POTT_column(KE) - POTT_column(KE-1)
       RHOT_column(KE+1) = 2.0_RP*RHOT_column(KE) - RHOT_column(KE-1)
       U_column(KE+1)    = 2.0_RP*U_column(KE)    - U_column(KE-1)
       V_column(KE+1)    = 2.0_RP*V_column(KE)    - V_column(KE-1)
       W_column(KE+1)    = -W_column(KE)
       MOMZ_column(KE:KE+1) = 0.0_RP
       do iq = 1, QA
          QTRC_column(KE+1,iq) = 2.0_RP*QTRC_column(KE,iq) - QTRC_column(KE-1,iq)
       enddo
       ! the lower boundary condition assumes constant extrapolation
       DENS_column(KS-1) = DENS_column(KS)
       TEMP_column(KS-1) = TEMP_column(KS)
       POTT_column(KS-1) = POTT_column(KS)
       U_column(KS-1)    = U_column(KS)
       V_column(KS-1)    = V_column(KS)
       W_column(KS-1)    = W_column(KS)
       RHOT_column(KS-1) = RHOT_column(KS)
       MOMZ_column(KS-1) = MOMZ_column(KS)
       MOMZ_column(KS-2) = MOMZ_column(KS) ! z momentum needs two halo values
       do iq = 1, QA
          QTRC_column(KS-1,iq) = QTRC_column(KS,iq)
       enddo

       ! compute large-scale forcing
       do k = KS, KE
 
          ! large-scale cooling forcing
          TEMP_t_USER(k,i,j) = TEMP_t_USER(k,i,j) + largeScaleTTendency(k) &
                                                 * DENS(k,i,j) * POTT(k,i,j) / TEMP(k,i,j)
 
          ! large-scale vapor forcing
          RHOQ_t_USER(k,i,j,QS_MP) = RHOQ_t_USER(k,i,j,QS_MP) + largeScaleQTendency(k) * DENS(k,i,j)
 
          ! large-scale vapor forcing
          DENS_t_USER(k,i,j) = DENS_t_USER(k,i,j) + largeScaleQTendency(k) * DENS(k,i,j)
 
          SINK_CEN = WLS(k)
          SINK_UP = WLS(k+1)
          SINK_DUP = WLS(k-1)
 
          subsidence_sink(k,i,j) = SINK_CEN
 
          ! -- x momentum --
          RHOU_t_USER(k,i,j) = RHOU_t_USER(k,i,j) &
                            - 0.5_RP*(SINK_UP + SINK_CEN) &
                            * (U_column(k+1) - U_column(k))*RFDZ(k)
 
          ! -- y momentum --
          RHOV_t_USER(k,i,j) = RHOV_t_USER(k,i,j) &
                            - 0.5_RP*(SINK_UP + SINK_CEN) &
                            * (V_column(k+1) - V_column(k))*RFDZ(k)
 
          ! -- mixing ratio --
          if ( SWITCH_QVAP_ONLY ) then
             iq = QS_MP
             RHOQ_t_USER(k,i,j,iq) = RHOQ_t_USER(k,i,j,iq) &
                                  - 0.5_RP*(SINK_UP + SINK_CEN) &
                                  * (QTRC_column(k+1,iq) - QTRC_column(k,iq))*RFDZ(k)
          else
             do iq = QS_MP, QE_MP
                RHOQ_t_USER(k,i,j,iq) = RHOQ_t_USER(k,i,j,iq) &
                                     - 0.5_RP*(SINK_UP + SINK_CEN) &
                                     * (QTRC_column(k+1,iq) - QTRC_column(k,iq))*RFDZ(k)
             enddo
          endif
 
          ! -- energy --
          RHOT_t_USER(k,i,j) = RHOT_t_USER(k,i,j) &
                            - 0.5_RP*(SINK_UP + SINK_CEN) &
                            * (POTT_column(k+1) - POTT_column(k))*RFDZ(k)
 
       enddo
 
       ! large-scale sinking forcing, the simple first-order upwind advection scheme is used
       do k = KS, KE-1
          SINK_CEN = WLS(k)
          SINK_UP = WLS(k+1)
          SINK_DUP = WLS(k+2)
 
          ! -- z momentum --
          if (SWITCH_VERTICAL_ACCE_TYPE) then
             MOMZ_t_USER(k,i,j) = MOMZ_t_USER(k,i,j) &
                               + 0.5_RP*(SINK_CEN + SINK_UP) &
                               * 0.5_RP*(DENS_column(k) + DENS_column(k+1))
          else
             MOMZ_t_USER(k,i,j) = MOMZ_t_USER(k,i,j) &
                               - SINK_UP &
                               * ( MOMZ_column(k+1)*2.0_RP/( DENS_column(k+2) &
                                                          + DENS_column(k+1)) &
                                  -  MOMZ_column(k  )*2.0_RP/( DENS_column(k+1) &
                                                             + DENS_column(k  )))*RCDZ(k+1)
          endif
       enddo


    enddo
    enddo

    call FILE_HISTORY_in( MOMZ_t_USER(:,:,:), 'MOMZ_t_USER', 'large-scale momz sinking',            'kg/m2/s2',  fill_halo=.true. )

    call FILE_HISTORY_in( RHOU_t_USER(:,:,:), 'RHOU_t_USER', 'large-scale rhou sinking',            'kg/m2/s2',  fill_halo=.true. )

    call FILE_HISTORY_in( RHOV_t_USER(:,:,:), 'RHOV_t_USER', 'large-scale rhov sinking',            'kg/m2/s2',  fill_halo=.true. )

    call FILE_HISTORY_in( DENS_t_USER(:,:,:), 'DENS_t_USER', 'large-scale rho sinking',               'kg/m3/s',   fill_halo=.true. )

    call FILE_HISTORY_in( RHOT_t_USER(:,:,:), 'RHOT_t_USER', 'large-scale pt sinking', 'K*kg/m3/s', fill_halo=.true. )

    call FILE_HISTORY_in( TEMP_t_USER(:,:,:), 'TEMP_t_USER', 'large-scale pt cooling', 'K*kg/m3/s', fill_halo=.true. )

    iq = QS_MP
    call FILE_HISTORY_in( RHOQ_t_USER(:,:,:,iq), 'RHOQ_t_USER', 'large-scale qv sinking',          'kg/m3/s',   fill_halo=.true. )

    call FILE_HISTORY_in( subsidence_sink(:,:,:), 'subsidence_sink', 'large-scale sinking', 'm/s', fill_halo=.true. )

    if ( SWITCH_MOMZ ) then
       !$omp parallel do default(none) private(i,j,k) OMP_SCHEDULE_ collapse(2) &
       !$omp shared(JS,JE,IS,IE,KS,KE,MOMZ_t,MOMZ_t_USER)
       do i = IS, IE
       do j = JS, JE
       do k = KS, KE
          MOMZ_t(k,i,j) = MOMZ_t(k,i,j) + MOMZ_t_USER(k,i,j)
       enddo
       enddo
       enddo
    endif

    if ( SWITCH_RHOU ) then
       !$omp parallel do default(none) private(i,j,k) OMP_SCHEDULE_ collapse(2) &
       !$omp shared(JS,JE,IS,IE,KS,KE,RHOU_t,RHOU_t_USER)
       do i = IS, IE
       do j = JS, JE
       do k = KS, KE
          RHOU_t(k,i,j) = RHOU_t(k,i,j) + RHOU_t_USER(k,i,j)
       enddo
       enddo
       enddo
    endif

    if ( SWITCH_RHOV ) then
       !$omp parallel do default(none) private(i,j,k) OMP_SCHEDULE_ collapse(2) &
       !$omp shared(JS,JE,IS,IE,KS,KE,RHOV_t,RHOV_t_USER)
       do i = IS, IE
       do j = JS, JE
       do k = KS, KE
          RHOV_t(k,i,j) = RHOV_t(k,i,j) + RHOV_t_USER(k,i,j)
       enddo
       enddo
       enddo
    endif

    if ( SWITCH_DENS ) then
       !$omp parallel do default(none) private(i,j,k) OMP_SCHEDULE_ collapse(2) &
       !$omp shared(JS,JE,IS,IE,KS,KE,DENS_t,DENS_t_USER)
       do i = IS, IE
       do j = JS, JE
       do k = KS, KE
          DENS_t(k,i,j) = DENS_t(k,i,j) + DENS_t_USER(k,i,j)
       enddo
       enddo
       enddo
    endif

    if ( SWITCH_RHOT ) then
    !$omp parallel do default(none) private(i,j,k) OMP_SCHEDULE_ collapse(2) &
       !$omp shared(JS,JE,IS,IE,KS,KE,RHOT_t,RHOT_t_USER)
       do i = IS, IE
       do j = JS, JE
       do k = KS, KE
          RHOT_t(k,i,j) = RHOT_t(k,i,j) + RHOT_t_USER(k,i,j)
       enddo
       enddo
       enddo
    endif

    if ( SWITCH_TEMP ) then
       !$omp parallel do default(none) private(i,j,k) OMP_SCHEDULE_ collapse(2) &
       !$omp shared(JS,JE,IS,IE,KS,KE,RHOT_t,TEMP_t_USER)
       do i = IS, IE
       do j = JS, JE
       do k = KS, KE
          RHOT_t(k,i,j) = RHOT_t(k,i,j) + TEMP_t_USER(k,i,j)
       enddo
       enddo
       enddo
    endif

    if ( SWITCH_RHOQ ) then
       !$omp parallel do default(none) private(i,j,k,iq) OMP_SCHEDULE_ collapse(2) &
       !$omp shared(JS,JE,IS,IE,KS,KE,QS_MP,QE_MP,SWITCH_QVAP_ONLY,RHOQ_t,RHOQ_t_USER)
       do i = IS, IE
       do j = JS, JE
       do k = KS, KE
          if ( SWITCH_QVAP_ONLY ) then
             RHOQ_t(k,i,j,QS_MP) = RHOQ_t(k,i,j,QS_MP) + RHOQ_t_USER(k,i,j,QS_MP)
          else
             do iq = QS_MP, QE_MP
                RHOQ_t(k,i,j,iq) = RHOQ_t(k,i,j,iq) + RHOQ_t_USER(k,i,j,iq)
             enddo
          endif
       enddo
       enddo
       enddo
    endif

    return
  end subroutine USER_calc_tendency

  !-----------------------------------------------------------------------------
  !> User step
  subroutine USER_update
    use scale_prc, only: &
       PRC_abort
    implicit none
    !---------------------------------------------------------------------------

    if ( USER_do ) then
       !call PRC_abort
    endif

    return
  end subroutine USER_update


end module mod_user
