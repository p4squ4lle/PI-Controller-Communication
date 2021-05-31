# -*- coding: utf-8 -*-

import serial
import subprocess
import logging
from pipython import GCSDevice, pitools


# Initialize PI Motor Controller
SN = '120060504'
STAGES = ['M-521.DG1', 'M-405.DG(FW000.000)', 'M-405.DG(FW000.000)',]
REFMODE = 'FRF'

PI = GCSDevice('C-844')
PI.ConnectUSB(serialnum=SN)
print('connected: {}'.format(PI.qIDN().strip()))
    
print('===============================================')
    
if PI.HasqVER():
    print('version info: {}'.format(PI.qVER().strip()))
    
print('===============================================')
            
print('initialize connected stages...')
pitools.startup(PI, stages=STAGES, refmodes=REFMODE)
print('===============================================')

    