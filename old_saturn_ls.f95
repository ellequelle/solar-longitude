! Functions to calculate solar longitude at Saturn from UNIX timestamp or Julian Date.
! Written 2020 by LE Hanson

module saturn_Ls
  implicit none
  
  !double precision UNIX_to_Ls, JD_to_Ls

  !double precision unix_to_xx, JD_to_xx, xx_to_Ls

  !double precision :: unix_to_Ls
  public unix_to_Ls
  public JD_to_Ls
  public unix_to_xx
  public JD_to_xx
  public xx_to_Ls


contains

  !pure elemental
 function unix_to_Ls(unx)
    double precision :: unix_to_Ls
    double precision, intent(in) :: unx
    double precision :: xx
    xx = unix_to_xx(unx) 
    unix_to_Ls = xx_to_Ls(xx) 
    return
  end function unix_to_Ls
    
  !pure elemental
 function JD_to_Ls(JD)
    double precision :: JD_to_Ls
    double precision, intent(in) :: JD
    double precision :: xx
    xx = JD_to_xx(JD) 
    JD_to_Ls = xx_to_Ls(xx) 
    return
  end function JD_to_Ls


  !pure elemental
 function unix_to_xx(unx)
    double precision :: unix_to_xx
    double precision, intent(in) :: unx
    !unix_to_xx = unx*5d-10 - 1262304000*5d-10
    unix_to_xx = unx*5d-10 - 0.633152
    return
  end function unix_to_xx
  
  !pure elemental
 function JD_to_xx(JD)
    double precision :: JD_to_xx
    double precision, intent(in) :: JD
    !JD_to_xx = 4.32e-5*JD - 105.43338 - 0.631152
    JD_to_xx = 4.32d-5*JD - 105.43338d0 - 0.631152d0
    return
  end function JD_to_xx

  !pure elemental
 function xx_to_Ls(xx)
    double precision :: xx_to_Ls
    double precision, intent(in) :: xx
    ! fit parameters
    double precision :: coef0(10)
    double precision :: cosps(3)
    double precision :: sinps(3)
    double precision :: xout
    integer :: ii

    coef0 = (/ 718.6900125511373d0, 774.1305095617424d0, -0.8446076817777325d0, &
         5.625920617250136d0, 2.3096357989383614d0, -12.987278185298077d0, &
         -1.3977724796575686d0, 12.802556973961142d0, -0.19768056277896529d0, &
         -4.694767647649146d0 /)
    cosps = (/ 0.07393232d0, -0.17575192d0,  6.2167401d0 /)
    sinps = (/ 0.03684395d0, -0.36251834d0, -0.19146985d0 /)

!    xout = 0
!    xout = coef0(1) + xx*(coef0(2) + xx*(coef0(3) + xx*(coef0(4) &
!         + xx*(coef0(5) + xx*(coef0(6) + xx*(coef0(7) + xx*(coef0(8) &
!         + xx*(coef0(9) + xx*coef0(10)))))))))

    xout = coef0(size(coef0))
    do ii = size(coef0)-1, 1, -1
       xout = xout*xx + coef0(ii)
    enddo
!    xout = 0
!!GCC$ unroll 0
!    do ii = 1, 10
!       xout = xout + coef0(ii)*xx**(ii-1)
!    end do
    xout = xout + cosps(3)*cos( xx/cosps(1) + cosps(2) )
    xout = xout + sinps(3)*sin( xx/sinps(1) + sinps(2) )
    xx_to_Ls = xout
    return
  end function xx_to_Ls

 
  subroutine test_Ls_unix_jd(uxt, jdx)
    double precision, intent(in) :: uxt, jdx
    double precision :: xxa, Ls2a, Lsa, xxb, Ls2b, Lsb
    xxa = JD_to_xx(jdx)
    Ls2a = JD_to_Ls(jdx)
    Lsa = mod(Ls2a, 360.0)
    write(*,"(a, f13.1, a, f12.9, a, f20.14, a, f20.14, a, i1)") &
         " JD  ", jdx, " (", xxa, ") -> ", Ls2a, " or", Lsa, ", SY ", floor(Ls2a/360)

    xxb = unix_to_xx(uxt)
    Ls2b = unix_to_Ls(uxt)
    Lsb = mod(Ls2b, 360.0)
    write(*,"(a, f13.1, a, f12.9, a, f20.14, a, f20.14, a, i1)") &
         " UNIX", uxt, " (", xxb, ") -> ", Ls2b, " or", Lsb, ", SY ",  floor(Ls2b/360)
    
    write(*,"(2x, a, e12.4, a, e12.4)") " delta x:", xxb-xxa, " delta Ls:", Ls2b-Ls2a
    return
  end subroutine test_Ls_unix_jd

end module saturn_Ls






