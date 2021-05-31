# -*- coding: utf-8 -*-

import serial
import subprocess
import logging
from pipython import GCSDevice, pitools
from time import sleep

# Constants
LASER_DESK_COM = 'COM6'

# Start Laser Desk
# laser_desk_path = r'C:\Program Files\SCANLAB\laserDesk\SLLaserDesk.exe'
# print(f'Starting Laser Desk application at {laser_desk_path}')
# subprocess.Popen([laser_desk_path])
# print('Succesfully started Laser Desk application')

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
            
print(f'initialize connected stages: {STAGES}')
pitools.startup(PI, stages=STAGES, refmodes=REFMODE)
print('Connected Stages:',
      f'{PI.qCST()}')

print('===============================================')

servo_dict = PI.qSVO()
reference_dict = PI.qFRF()

if all(v for v in servo_dict.values()):
    print('Servo-control is set ON for all axes')
else:
    print('WARNING: servo-control is not set ON for axes',
          f'{[k for k in servo_dict.keys() if servo_dict[k]==False]}')

if all(v for v in reference_dict.values()):
    print('All axes have been succesfully referenced.')
else:
    print('WARNING: the following axes have not been referenced properly',
          f'{[k for k in reference_dict.keys() if reference_dict[k]==False]}')
    
rangemin = list(PI.qTMN().values())
rangemax = list(PI.qTMX().values())
ranges = zip(rangemin, rangemax)

# error_dict = {i: PI.TranslateError(i) for i in range(10000) 
#              if PI.TranslateError(i) != str(i)}

pi_error = PI.qERR()
if pi_error > 0:
    print(f'WARNING: an error occurred (error code: {pi_error})',
          PI.TranslateError(pi_error))

LaserDesk = serial.Serial(LASER_DESK_COM)
if LaserDesk.is_open:
    print('Serial connection was successfully established.')
else:
    print('Serial port could not be opened.')

print('===============================================')

listen = True
while listen:
    bytes_waiting = LaserDesk.in_waiting
    if bytes_waiting==0:
        continue
    input_bytes = LaserDesk.read_until(b'\x03')
    input_string = input_bytes.decode()[1:-1]
    # print(f'input: {input_string}')
    
    if input_string=='End':
        listen = False
        continue
    
    controller_ready_flag = PI.IsControllerReady()
    while any(v for v in PI.IsMoving().values()):
        sleep(0.5)
    
    try:
        PI.send(input_string)
        print(f'string sent to pi controller: {input_string}')
        if any(v for v in PI.IsMoving().values()):
            print('axes are moving', end='')
            while any(v for v in PI.IsMoving().values()):
                print('.', end='')
                sleep(1)
        if all(v for v in PI.qONT().values()):
            print('axes stopped moving and are on target')
            print('absolute motor positions are now:')
            print(PI.qPOS())
            print('===============================================')
        else:
            print('some axes are not on target:')
            print(PI.qONT())
            print('===============================================')
        LaserDesk.write(b'\x02 1 \x03')
    except Exception as e:
        print('An exception occured while sending the command to the PI controller:')
        print(e)
        LaserDesk.write(b'\x02 0 \x03')
        
LaserDesk.close()