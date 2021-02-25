! Tests the module saturn_ls (saturn_ls.f95)
! Written 2020 by LE Hanson

program test_saturn_ls
  use saturn_Ls
  implicit none
  double precision :: uxt, jdx, xx, Ls2, Ls
  
  ! First (earth) day of Saturn Year 1
  write(*,'("Sept 22, 1950")')
  uxt = -608342400 ! Sept 22, 1950
  jdx = 2433546.5d0 ! Sept 22, 1950
  call test_Ls_unix_jd(uxt, jdx) ! -> -2.950558573

  ! Voyager Titan flyby
  write(*,'("Nov 12, 1980")')
  uxt = 342835200 ! Nov 12, 1980
  jdx = 2444555.5d0 ! Nov 12, 1980
  call test_Ls_unix_jd(uxt, jdx) ! -> 368.60583260337

  ! First Cassini Titan encounter
  write(*,'("July 2, 2004")')
  uxt = 1088726400 ! July 2, 2004
  jdx = 2453188.5d0 ! July 2, 2004
  call test_Ls_unix_jd(uxt, jdx) ! -> 652.9366412074

  ! Huygens Titan descent
  write(*,'("Jan 14, 2005")')
  uxt = 1105660800 ! Jan 14, 2005
  jdx = 2453384.5d0 ! Jan 14, 2005
  call test_Ls_unix_jd(uxt, jdx) ! -> 660.21532977540
  
  write(*,'("Jan 1, 2008")')
  uxt = 1199145600d0 ! Jan 1, 2008
  jdx = 2454466.5d0 ! Jan 1, 2008
  call test_Ls_unix_jd(uxt, jdx) ! -> 699.5430943745

  ! Last Cassini Titan encounter
  write(*,'("April 21, 2017")')
  uxt = 1492732800 ! April 21, 2017
  jdx = 2457864.5d0 ! April 21, 2017
  call test_Ls_unix_jd(uxt, jdx) ! -> 808.970963677941

  ! Dragonfly estimated landing date
  write(*,'("Jan 1, 2036")')
  uxt = 2082758400 ! Jan 1, 2005
  jdx = 2464693.5d0 ! Jan 1, 2005
  call test_Ls_unix_jd(uxt, jdx) ! -> 1040.43780183648
  

end program test_saturn_ls
