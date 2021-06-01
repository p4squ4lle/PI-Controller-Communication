# -*- coding: utf-8 -*-

import serial
import subprocess
import logging
from datetime import datetime
from pipython import GCSDevice, pitools
from time import sleep

# Set-Up logging
dt = datetime.now()
dt_string = dt.strftime("%H-%M_%d%m%Y")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.FileHandler(f"log/{dt_string}.log"),
                              logging.StreamHandler()
                             ]
                   )
position_file = open(f'log/motor_positions_{dt_string}.csv', 'a')
position_file.write("#pos_m1, pos_m2, pos_m3 [mm]\n")

# Laser Desk COM port
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
logging.info('connected: {}'.format(PI.qIDN().strip()))
    
print('-----------------------------------------------')
    
if PI.HasqVER():
    logging.info('version info: {}'.format(PI.qVER().strip()))
    
print('-----------------------------------------------')
            
logging.info(f'initialize connected stages: {STAGES}')
pitools.startup(PI, stages=STAGES, refmodes=REFMODE)
logging.info(f'Connected Stages: {PI.qCST()}')

print('-----------------------------------------------')

servo_dict = PI.qSVO()
reference_dict = PI.qFRF()

if all(v for v in servo_dict.values()):
    logging.info('Servo-control is set ON for all axes')
else:
    logging.warning('Servo-control is not set ON for axes',
          f'{[k for k in servo_dict.keys() if servo_dict[k]==False]}')

if all(v for v in reference_dict.values()):
    logging.info('All axes have been succesfully referenced.')
    position_file.write(f"{PI.qPOS()['1']}, {PI.qPOS()['2']}, {PI.qPOS()['3']}\n")
else:
    logging.warning('The following axes have not been referenced properly',
          f'{[k for k in reference_dict.keys() if reference_dict[k]==False]}')
    
rangemin = list(PI.qTMN().values())
rangemax = list(PI.qTMX().values())
ranges = zip(rangemin, rangemax)

# error_dict = {i: PI.TranslateError(i) for i in range(10000) 
#              if PI.TranslateError(i) != str(i)}

pi_error = PI.qERR()
if pi_error > 0:
    logging.warning(f'WARNING: an error occurred (error code: {pi_error})',
          PI.TranslateError(pi_error))

LaserDesk = serial.Serial(LASER_DESK_COM)
if LaserDesk.is_open:
    logging.info('Serial connection was successfully established.')
else:
    logging.warning('Serial port could not be opened.')

print('===============================================')

listen = True
while listen:
    bytes_waiting = LaserDesk.in_waiting
    if bytes_waiting==0:
        continue
    input_bytes = LaserDesk.read_until(b'\x03')
    input_string = input_bytes.decode()[1:-1]
    
    if input_string=='End':
        logging.info("Recieved 'End' command. Stop listening")
        listen = False
        continue
    
    controller_ready_flag = PI.IsControllerReady()
    #while any(v for v in PI.IsMoving().values()):
    #   sleep(0.5)
    
    try:
        PI.send(input_string)
        logging.info(f'string sent to pi controller: {input_string}')
        if any(v for v in PI.IsMoving().values()):
            print('axes are moving', end='')
            while any(v for v in PI.IsMoving().values()):
                print('.', end='')
                sleep(1)
        if all(v for v in PI.qONT().values()):
            logging.info('axes stopped moving and are on target')
            logging.info('absolute motor positions now are:')
            logging.info(f'{PI.qPOS()}')
            position_file.write(f"{PI.qPOS()['1']}, {PI.qPOS()['2']}, {PI.qPOS()['3']}\n")
            print('===============================================')
        else:
            logging.warning(f'some axes are not on target: {PI.qONT()}')
            print('===============================================')
        LaserDesk.write(b'\x02 1 \x03')
    except Exception as e:
        logging.error('An exception occured while sending the command to the PI controller:')
        logging.error(e)
        LaserDesk.write(b'\x02 0 \x03')

position_file.close()
LaserDesk.close()
logging.info("Serial connection was closed. End of script.")