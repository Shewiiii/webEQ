from autoeq.frequency_response import FrequencyResponse
from autoeq.constants import PEQ_CONFIGS
import pathlib
from app.getFRoT import getFRoTDict
from app.getFRfromFile import *
from numpy import array
#def...

FRlist = getFRoTDict('frequency_responses')
target = 'Shewi Target'
iem = '64 audio Völour (m15)'

frequencies,gains = getFRfromFile(f'{FRlist[iem]}.txt',relativepath='frequency_responses')    
Tfrequencies,Tgains = getFRfromFile(f'{target}.txt',relativepath='targets')

iemAQ = FrequencyResponse(name=iem,frequency=frequencies,raw=gains)
targetAQ = FrequencyResponse(name=target,frequency=Tfrequencies,raw=Tgains)

iemAQ.interpolate()
iemAQ.center()
iemAQ.compensate(targetAQ)
iemAQ.smoothen()
iemAQ.equalize(concha_interference=True,max_gain=10)

peqs = iemAQ.optimize_parametric_eq({'filters': [{'type': 'HIGH_SHELF','fc': 10000.0,'q': 0.7}]+[{'type': 'PEAKING'}] * 10}, 48000)
i = 0
for filt in peqs[0].filters:
    i+=1
    print(f'{filt.gain:.2f} db, {filt.fc:.2f} Hz, {filt.q:.2f} Q')

iemAQ.plot()
