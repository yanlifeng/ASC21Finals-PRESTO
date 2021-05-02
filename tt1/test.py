import os
import sys
import time
from subprocess import getoutput


def dur(op=None, clock=[time.time()]):
    res = ''
    if op != None:
        duration = time.time() - clock[0]
        res = '%-30s === %.6f \n' % (op, duration)
    clock[0] = time.time()
    return res


c1 = ['prepsubband -sub -subdm 5.75 -nsub 32 -downsamp 1 -o Sband ../GBT_Lband_PSR.fil',
      'prepsubband -nsub 32 -lodm 0.000000 -dmstep 0.500000 -numdms 24 -numout 531000 -downsamp 1 -o Sband Sband_DM5.75.sub[0-9]*',
      'prepsubband -sub -subdm 17.75 -nsub 32 -downsamp 1 -o Sband ../GBT_Lband_PSR.fil',
      'prepsubband -nsub 32 -lodm 12.000000 -dmstep 0.500000 -numdms 24 -numout 531000 -downsamp 1 -o Sband Sband_DM17.75.sub[0-9]*',
      'prepsubband -sub -subdm 29.75 -nsub 32 -downsamp 1 -o Sband ../GBT_Lband_PSR.fil',
      'prepsubband -nsub 32 -lodm 24.000000 -dmstep 0.500000 -numdms 24 -numout 531000 -downsamp 1 -o Sband Sband_DM29.75.sub[0-9]*',
      'prepsubband -sub -subdm 41.75 -nsub 32 -downsamp 1 -o Sband ../GBT_Lband_PSR.fil',
      'prepsubband -nsub 32 -lodm 36.000000 -dmstep 0.500000 -numdms 24 -numout 531000 -downsamp 1 -o Sband Sband_DM41.75.sub[0-9]*',
      'prepsubband -sub -subdm 53.75 -nsub 32 -downsamp 1 -o Sband ../GBT_Lband_PSR.fil',
      'prepsubband -nsub 32 -lodm 48.000000 -dmstep 0.500000 -numdms 24 -numout 531000 -downsamp 1 -o Sband Sband_DM53.75.sub[0-9]*',
      'prepsubband -sub -subdm 65.75 -nsub 32 -downsamp 1 -o Sband ../GBT_Lband_PSR.fil',
      'prepsubband -nsub 32 -lodm 60.000000 -dmstep 0.500000 -numdms 24 -numout 531000 -downsamp 1 -o Sband Sband_DM65.75.sub[0-9]*',
      'prepsubband -sub -subdm 77.75 -nsub 32 -downsamp 1 -o Sband ../GBT_Lband_PSR.fil',
      'prepsubband -nsub 32 -lodm 72.000000 -dmstep 0.500000 -numdms 24 -numout 531000 -downsamp 1 -o Sband Sband_DM77.75.sub[0-9]*']
c2 = ['realfft Sband_DM64.00.dat', 'realfft Sband_DM70.00.dat', 'realfft Sband_DM33.00.dat',
      'realfft Sband_DM57.50.dat', 'realfft Sband_DM45.00.dat', 'realfft Sband_DM82.50.dat',
      'realfft Sband_DM53.00.dat', 'realfft Sband_DM6.50.dat', 'realfft Sband_DM75.00.dat', 'realfft Sband_DM58.50.dat',
      'realfft Sband_DM63.50.dat', 'realfft Sband_DM66.50.dat', 'realfft Sband_DM49.50.dat',
      'realfft Sband_DM74.00.dat', 'realfft Sband_DM8.50.dat', 'realfft Sband_DM16.00.dat', 'realfft Sband_DM34.00.dat',
      'realfft Sband_DM71.00.dat', 'realfft Sband_DM54.00.dat', 'realfft Sband_DM32.00.dat',
      'realfft Sband_DM44.50.dat', 'realfft Sband_DM23.50.dat', 'realfft Sband_DM27.00.dat',
      'realfft Sband_DM57.00.dat', 'realfft Sband_DM29.50.dat', 'realfft Sband_DM30.50.dat',
      'realfft Sband_DM44.00.dat', 'realfft Sband_DM59.50.dat', 'realfft Sband_DM23.00.dat',
      'realfft Sband_DM42.50.dat', 'realfft Sband_DM76.00.dat', 'realfft Sband_DM79.50.dat',
      'realfft Sband_DM79.00.dat', 'realfft Sband_DM9.00.dat', 'realfft Sband_DM56.50.dat', 'realfft Sband_DM68.00.dat',
      'realfft Sband_DM28.50.dat', 'realfft Sband_DM83.50.dat', 'realfft Sband_DM3.50.dat', 'realfft Sband_DM3.00.dat',
      'realfft Sband_DM33.50.dat', 'realfft Sband_DM51.50.dat', 'realfft Sband_DM32.50.dat',
      'realfft Sband_DM52.50.dat', 'realfft Sband_DM27.50.dat', 'realfft Sband_DM46.00.dat',
      'realfft Sband_DM14.00.dat', 'realfft Sband_DM40.00.dat', 'realfft Sband_DM8.00.dat', 'realfft Sband_DM21.50.dat',
      'realfft Sband_DM81.00.dat', 'realfft Sband_DM15.50.dat', 'realfft Sband_DM54.50.dat',
      'realfft Sband_DM60.50.dat', 'realfft Sband_DM28.00.dat', 'realfft Sband_DM71.50.dat', 'realfft Sband_DM5.50.dat',
      'realfft Sband_DM50.50.dat', 'realfft Sband_DM67.00.dat', 'realfft Sband_DM47.50.dat',
      'realfft Sband_DM26.00.dat', 'realfft Sband_DM82.00.dat', 'realfft Sband_DM29.00.dat',
      'realfft Sband_DM56.00.dat', 'realfft Sband_DM70.50.dat', 'realfft Sband_DM72.00.dat', 'realfft Sband_DM1.00.dat',
      'realfft Sband_DM14.50.dat', 'realfft Sband_DM73.50.dat', 'realfft Sband_DM41.50.dat',
      'realfft Sband_DM73.00.dat', 'realfft Sband_DM65.50.dat', 'realfft Sband_DM25.00.dat',
      'realfft Sband_DM40.50.dat', 'realfft Sband_DM47.00.dat', 'realfft Sband_DM62.50.dat',
      'realfft Sband_DM43.50.dat', 'realfft Sband_DM4.00.dat', 'realfft Sband_DM15.00.dat', 'realfft Sband_DM65.00.dat',
      'realfft Sband_DM42.00.dat', 'realfft Sband_DM25.50.dat', 'realfft Sband_DM41.00.dat',
      'realfft Sband_DM35.50.dat', 'realfft Sband_DM1.50.dat', 'realfft Sband_DM63.00.dat', 'realfft Sband_DM83.00.dat',
      'realfft Sband_DM74.50.dat', 'realfft Sband_DM7.00.dat', 'realfft Sband_DM61.50.dat', 'realfft Sband_DM18.50.dat',
      'realfft Sband_DM39.00.dat', 'realfft Sband_DM80.00.dat', 'realfft Sband_DM53.50.dat',
      'realfft Sband_DM77.00.dat', 'realfft Sband_DM50.00.dat', 'realfft Sband_DM2.50.dat', 'realfft Sband_DM52.00.dat',
      'realfft Sband_DM35.00.dat', 'realfft Sband_DM12.50.dat', 'realfft Sband_DM18.00.dat',
      'realfft Sband_DM62.00.dat', 'realfft Sband_DM6.00.dat', 'realfft Sband_DM4.50.dat', 'realfft Sband_DM49.00.dat',
      'realfft Sband_DM45.50.dat', 'realfft Sband_DM69.00.dat', 'realfft Sband_DM26.50.dat',
      'realfft Sband_DM60.00.dat', 'realfft Sband_DM24.00.dat', 'realfft Sband_DM43.00.dat',
      'realfft Sband_DM77.50.dat', 'realfft Sband_DM78.00.dat', 'realfft Sband_DM30.00.dat',
      'realfft Sband_DM55.00.dat', 'realfft Sband_DM21.00.dat', 'realfft Sband_DM69.50.dat',
      'realfft Sband_DM10.50.dat', 'realfft Sband_DM48.50.dat', 'realfft Sband_DM34.50.dat',
      'realfft Sband_DM24.50.dat', 'realfft Sband_DM10.00.dat', 'realfft Sband_DM22.00.dat', 'realfft Sband_DM0.00.dat',
      'realfft Sband_DM5.00.dat', 'realfft Sband_DM48.00.dat', 'realfft Sband_DM64.50.dat', 'realfft Sband_DM11.00.dat',
      'realfft Sband_DM2.00.dat', 'realfft Sband_DM31.50.dat', 'realfft Sband_DM39.50.dat', 'realfft Sband_DM17.00.dat',
      'realfft Sband_DM13.00.dat', 'realfft Sband_DM61.00.dat', 'realfft Sband_DM12.00.dat',
      'realfft Sband_DM76.50.dat', 'realfft Sband_DM38.50.dat', 'realfft Sband_DM55.50.dat',
      'realfft Sband_DM17.50.dat', 'realfft Sband_DM80.50.dat', 'realfft Sband_DM59.00.dat',
      'realfft Sband_DM22.50.dat', 'realfft Sband_DM16.50.dat', 'realfft Sband_DM9.50.dat', 'realfft Sband_DM67.50.dat',
      'realfft Sband_DM19.00.dat', 'realfft Sband_DM58.00.dat', 'realfft Sband_DM20.00.dat',
      'realfft Sband_DM78.50.dat', 'realfft Sband_DM37.00.dat', 'realfft Sband_DM31.00.dat',
      'realfft Sband_DM13.50.dat', 'realfft Sband_DM75.50.dat', 'realfft Sband_DM38.00.dat',
      'realfft Sband_DM36.00.dat', 'realfft Sband_DM37.50.dat', 'realfft Sband_DM20.50.dat',
      'realfft Sband_DM81.50.dat', 'realfft Sband_DM66.00.dat', 'realfft Sband_DM51.00.dat',
      'realfft Sband_DM19.50.dat', 'realfft Sband_DM72.50.dat', 'realfft Sband_DM11.50.dat', 'realfft Sband_DM7.50.dat',
      'realfft Sband_DM36.50.dat', 'realfft Sband_DM68.50.dat', 'realfft Sband_DM0.50.dat', 'realfft Sband_DM46.50.dat']
c3 = ['accelsearch -zmax 0 Sband_DM0.00.fft', 'accelsearch -zmax 0 Sband_DM9.50.fft',
      'accelsearch -zmax 0 Sband_DM59.50.fft', 'accelsearch -zmax 0 Sband_DM14.00.fft',
      'accelsearch -zmax 0 Sband_DM83.00.fft', 'accelsearch -zmax 0 Sband_DM69.50.fft',
      'accelsearch -zmax 0 Sband_DM81.00.fft', 'accelsearch -zmax 0 Sband_DM31.50.fft',
      'accelsearch -zmax 0 Sband_DM22.00.fft', 'accelsearch -zmax 0 Sband_DM27.50.fft',
      'accelsearch -zmax 0 Sband_DM26.50.fft', 'accelsearch -zmax 0 Sband_DM56.50.fft',
      'accelsearch -zmax 0 Sband_DM61.50.fft', 'accelsearch -zmax 0 Sband_DM58.00.fft',
      'accelsearch -zmax 0 Sband_DM10.00.fft', 'accelsearch -zmax 0 Sband_DM21.00.fft',
      'accelsearch -zmax 0 Sband_DM38.50.fft', 'accelsearch -zmax 0 Sband_DM43.50.fft',
      'accelsearch -zmax 0 Sband_DM68.50.fft', 'accelsearch -zmax 0 Sband_DM43.00.fft',
      'accelsearch -zmax 0 Sband_DM55.50.fft', 'accelsearch -zmax 0 Sband_DM20.50.fft',
      'accelsearch -zmax 0 Sband_DM63.50.fft', 'accelsearch -zmax 0 Sband_DM77.50.fft',
      'accelsearch -zmax 0 Sband_DM12.50.fft', 'accelsearch -zmax 0 Sband_DM68.00.fft',
      'accelsearch -zmax 0 Sband_DM41.50.fft', 'accelsearch -zmax 0 Sband_DM19.00.fft',
      'accelsearch -zmax 0 Sband_DM8.00.fft', 'accelsearch -zmax 0 Sband_DM42.00.fft',
      'accelsearch -zmax 0 Sband_DM57.00.fft', 'accelsearch -zmax 0 Sband_DM30.50.fft',
      'accelsearch -zmax 0 Sband_DM27.00.fft', 'accelsearch -zmax 0 Sband_DM7.50.fft',
      'accelsearch -zmax 0 Sband_DM7.00.fft', 'accelsearch -zmax 0 Sband_DM64.00.fft',
      'accelsearch -zmax 0 Sband_DM72.50.fft', 'accelsearch -zmax 0 Sband_DM47.50.fft',
      'accelsearch -zmax 0 Sband_DM5.00.fft', 'accelsearch -zmax 0 Sband_DM0.50.fft',
      'accelsearch -zmax 0 Sband_DM75.50.fft', 'accelsearch -zmax 0 Sband_DM63.00.fft',
      'accelsearch -zmax 0 Sband_DM17.50.fft', 'accelsearch -zmax 0 Sband_DM28.00.fft',
      'accelsearch -zmax 0 Sband_DM8.50.fft', 'accelsearch -zmax 0 Sband_DM56.00.fft',
      'accelsearch -zmax 0 Sband_DM12.00.fft', 'accelsearch -zmax 0 Sband_DM82.50.fft',
      'accelsearch -zmax 0 Sband_DM80.50.fft', 'accelsearch -zmax 0 Sband_DM74.50.fft',
      'accelsearch -zmax 0 Sband_DM1.00.fft', 'accelsearch -zmax 0 Sband_DM49.00.fft',
      'accelsearch -zmax 0 Sband_DM18.00.fft', 'accelsearch -zmax 0 Sband_DM36.50.fft',
      'accelsearch -zmax 0 Sband_DM4.00.fft', 'accelsearch -zmax 0 Sband_DM33.50.fft',
      'accelsearch -zmax 0 Sband_DM78.50.fft', 'accelsearch -zmax 0 Sband_DM41.00.fft',
      'accelsearch -zmax 0 Sband_DM50.00.fft', 'accelsearch -zmax 0 Sband_DM5.50.fft',
      'accelsearch -zmax 0 Sband_DM83.50.fft', 'accelsearch -zmax 0 Sband_DM81.50.fft',
      'accelsearch -zmax 0 Sband_DM75.00.fft', 'accelsearch -zmax 0 Sband_DM23.50.fft',
      'accelsearch -zmax 0 Sband_DM4.50.fft', 'accelsearch -zmax 0 Sband_DM52.00.fft',
      'accelsearch -zmax 0 Sband_DM13.00.fft', 'accelsearch -zmax 0 Sband_DM57.50.fft',
      'accelsearch -zmax 0 Sband_DM60.50.fft', 'accelsearch -zmax 0 Sband_DM77.00.fft',
      'accelsearch -zmax 0 Sband_DM62.00.fft', 'accelsearch -zmax 0 Sband_DM61.00.fft',
      'accelsearch -zmax 0 Sband_DM16.00.fft', 'accelsearch -zmax 0 Sband_DM40.00.fft',
      'accelsearch -zmax 0 Sband_DM29.50.fft', 'accelsearch -zmax 0 Sband_DM16.50.fft',
      'accelsearch -zmax 0 Sband_DM37.00.fft', 'accelsearch -zmax 0 Sband_DM50.50.fft',
      'accelsearch -zmax 0 Sband_DM35.50.fft', 'accelsearch -zmax 0 Sband_DM11.00.fft',
      'accelsearch -zmax 0 Sband_DM22.50.fft', 'accelsearch -zmax 0 Sband_DM1.50.fft',
      'accelsearch -zmax 0 Sband_DM45.00.fft', 'accelsearch -zmax 0 Sband_DM82.00.fft',
      'accelsearch -zmax 0 Sband_DM72.00.fft', 'accelsearch -zmax 0 Sband_DM67.00.fft',
      'accelsearch -zmax 0 Sband_DM23.00.fft', 'accelsearch -zmax 0 Sband_DM70.00.fft',
      'accelsearch -zmax 0 Sband_DM40.50.fft', 'accelsearch -zmax 0 Sband_DM60.00.fft',
      'accelsearch -zmax 0 Sband_DM14.50.fft', 'accelsearch -zmax 0 Sband_DM66.00.fft',
      'accelsearch -zmax 0 Sband_DM76.50.fft', 'accelsearch -zmax 0 Sband_DM70.50.fft',
      'accelsearch -zmax 0 Sband_DM58.50.fft', 'accelsearch -zmax 0 Sband_DM49.50.fft',
      'accelsearch -zmax 0 Sband_DM2.50.fft', 'accelsearch -zmax 0 Sband_DM39.50.fft',
      'accelsearch -zmax 0 Sband_DM37.50.fft', 'accelsearch -zmax 0 Sband_DM78.00.fft',
      'accelsearch -zmax 0 Sband_DM52.50.fft', 'accelsearch -zmax 0 Sband_DM18.50.fft',
      'accelsearch -zmax 0 Sband_DM65.50.fft', 'accelsearch -zmax 0 Sband_DM25.50.fft',
      'accelsearch -zmax 0 Sband_DM46.50.fft', 'accelsearch -zmax 0 Sband_DM19.50.fft',
      'accelsearch -zmax 0 Sband_DM20.00.fft', 'accelsearch -zmax 0 Sband_DM54.00.fft',
      'accelsearch -zmax 0 Sband_DM34.50.fft', 'accelsearch -zmax 0 Sband_DM79.50.fft',
      'accelsearch -zmax 0 Sband_DM71.00.fft', 'accelsearch -zmax 0 Sband_DM76.00.fft',
      'accelsearch -zmax 0 Sband_DM34.00.fft', 'accelsearch -zmax 0 Sband_DM28.50.fft',
      'accelsearch -zmax 0 Sband_DM45.50.fft', 'accelsearch -zmax 0 Sband_DM3.00.fft',
      'accelsearch -zmax 0 Sband_DM38.00.fft', 'accelsearch -zmax 0 Sband_DM31.00.fft',
      'accelsearch -zmax 0 Sband_DM29.00.fft', 'accelsearch -zmax 0 Sband_DM35.00.fft',
      'accelsearch -zmax 0 Sband_DM48.50.fft', 'accelsearch -zmax 0 Sband_DM80.00.fft',
      'accelsearch -zmax 0 Sband_DM15.50.fft', 'accelsearch -zmax 0 Sband_DM62.50.fft',
      'accelsearch -zmax 0 Sband_DM44.00.fft', 'accelsearch -zmax 0 Sband_DM46.00.fft',
      'accelsearch -zmax 0 Sband_DM54.50.fft', 'accelsearch -zmax 0 Sband_DM64.50.fft',
      'accelsearch -zmax 0 Sband_DM15.00.fft', 'accelsearch -zmax 0 Sband_DM73.50.fft',
      'accelsearch -zmax 0 Sband_DM24.00.fft', 'accelsearch -zmax 0 Sband_DM67.50.fft',
      'accelsearch -zmax 0 Sband_DM51.50.fft', 'accelsearch -zmax 0 Sband_DM69.00.fft',
      'accelsearch -zmax 0 Sband_DM24.50.fft', 'accelsearch -zmax 0 Sband_DM11.50.fft',
      'accelsearch -zmax 0 Sband_DM26.00.fft', 'accelsearch -zmax 0 Sband_DM33.00.fft',
      'accelsearch -zmax 0 Sband_DM3.50.fft', 'accelsearch -zmax 0 Sband_DM55.00.fft',
      'accelsearch -zmax 0 Sband_DM53.00.fft', 'accelsearch -zmax 0 Sband_DM65.00.fft',
      'accelsearch -zmax 0 Sband_DM53.50.fft', 'accelsearch -zmax 0 Sband_DM21.50.fft',
      'accelsearch -zmax 0 Sband_DM47.00.fft', 'accelsearch -zmax 0 Sband_DM36.00.fft',
      'accelsearch -zmax 0 Sband_DM79.00.fft', 'accelsearch -zmax 0 Sband_DM51.00.fft',
      'accelsearch -zmax 0 Sband_DM59.00.fft', 'accelsearch -zmax 0 Sband_DM73.00.fft',
      'accelsearch -zmax 0 Sband_DM71.50.fft', 'accelsearch -zmax 0 Sband_DM66.50.fft',
      'accelsearch -zmax 0 Sband_DM13.50.fft', 'accelsearch -zmax 0 Sband_DM32.00.fft',
      'accelsearch -zmax 0 Sband_DM30.00.fft', 'accelsearch -zmax 0 Sband_DM6.50.fft',
      'accelsearch -zmax 0 Sband_DM32.50.fft', 'accelsearch -zmax 0 Sband_DM39.00.fft',
      'accelsearch -zmax 0 Sband_DM42.50.fft', 'accelsearch -zmax 0 Sband_DM48.00.fft',
      'accelsearch -zmax 0 Sband_DM74.00.fft', 'accelsearch -zmax 0 Sband_DM2.00.fft',
      'accelsearch -zmax 0 Sband_DM6.00.fft', 'accelsearch -zmax 0 Sband_DM44.50.fft',
      'accelsearch -zmax 0 Sband_DM9.00.fft', 'accelsearch -zmax 0 Sband_DM17.00.fft',
      'accelsearch -zmax 0 Sband_DM10.50.fft', 'accelsearch -zmax 0 Sband_DM25.00.fft']
c4 = ['prepfold -n 64 -nsub 32 -dm 49.500000 -p 1.853673 GBT_Lband_PSR.fil -o Sband_DM49.50 -noxwin -nodmsearch',
      'prepfold -n 64 -nsub 32 -dm 11.000000 -p 0.034772 GBT_Lband_PSR.fil -o Sband_DM11.00 -noxwin -nodmsearch',
      'prepfold -n 64 -nsub 32 -dm 10.500000 -p 0.034725 GBT_Lband_PSR.fil -o Sband_DM10.50 -noxwin -nodmsearch',
      'prepfold -n 64 -nsub 32 -dm 62.500000 -p 0.004622 GBT_Lband_PSR.fil -o Sband_DM62.50 -noxwin -nodmsearch',
      'prepfold -n 64 -nsub 32 -dm 3.000000 -p 0.005603 GBT_Lband_PSR.fil -o Sband_DM3.00 -noxwin -nodmsearch',
      'prepfold -n 64 -nsub 32 -dm 29.000000 -p 0.010950 GBT_Lband_PSR.fil -o Sband_DM29.00 -noxwin -nodmsearch',
      'prepfold -n 64 -nsub 32 -dm 12.000000 -p 0.002469 GBT_Lband_PSR.fil -o Sband_DM12.00 -noxwin -nodmsearch',
      'prepfold -n 64 -nsub 32 -dm 40.000000 -p 0.003707 GBT_Lband_PSR.fil -o Sband_DM40.00 -noxwin -nodmsearch',
      'prepfold -n 64 -nsub 32 -dm 83.000000 -p 0.002693 GBT_Lband_PSR.fil -o Sband_DM83.00 -noxwin -nodmsearch',
      'prepfold -n 64 -nsub 32 -dm 23.000000 -p 0.009633 GBT_Lband_PSR.fil -o Sband_DM23.00 -noxwin -nodmsearch',
      'prepfold -n 64 -nsub 32 -dm 22.000000 -p 0.007858 GBT_Lband_PSR.fil -o Sband_DM22.00 -noxwin -nodmsearch']
filename = sys.argv[1]
print(filename)
timeLog = ''
dur()
cwd = os.getcwd()
if not os.access('subbands', os.F_OK):
    os.mkdir('subbands')
os.chdir('subbands')
logfile = open('dedisperse.log', 'wt')
for cmd in c1:
    print(cmd)
    output = getoutput(cmd)
    logfile.write(output)
os.system('rm *.sub*')
logfile.close()
os.chdir(cwd)
timeLog += dur("p1")

dur()
os.chdir('subbands')
logfile = open('fft.log', 'wt')
for cmd in c2:
    print(cmd)
    output = getoutput(cmd)
    logfile.write(output)
logfile.close()
timeLog += dur("p2")

dur()
logfile = open('accelsearch.log', 'wt')
for cmd in c3:
    print(cmd)
    output = getoutput(cmd)
    logfile.write(output)
logfile.close()
os.chdir(cwd)
timeLog += dur("p3")

dur()
cwd = os.getcwd()
os.chdir('subbands')
os.system('ln -s ../%s %s' % (filename, filename))
logfile = open('folding.log', 'wt')
for cmd in c4:
    print(cmd)
    output = getoutput(cmd)
    logfile.write(output)
logfile.close()
os.chdir(cwd)
timeLog += dur("p4")

print(timeLog)

# for it in c1:
#     print(it)
# print("!@#$%^")
# for it in c2:
#     print(it)
# print("!@#$%^")
# for it in c3:
#     print(it)
# print("!@#$%^")
# for it in c4:
#     print(it)
