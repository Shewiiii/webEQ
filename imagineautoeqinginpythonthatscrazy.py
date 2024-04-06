from autoeq.frequency_response import FrequencyResponse
from autoeq.constants import PEQ_CONFIGS
import pathlib
from app.getFRoT import getFRoTList
from app.getFRfromFile import *
from numpy import array
#def...

FRlist = getFRoTList('frequency_responses')
target = 'Shewi Target'
iem = 'Razer Moray'

frequencies,gains = getFRfromFile(f'{FRlist[iem]}.txt',relativepath='frequency_responses')    
Tfrequencies,Tgains = getFRfromFile(f'{target}.txt',relativepath='targets')

iemAQ = FrequencyResponse(name=iem,frequency=frequencies,raw=gains)
targetAQ = FrequencyResponse(name=target,frequency=Tfrequencies,raw=Tgains)

iemAQ.interpolate()
iemAQ.center()
iemAQ.compensate(targetAQ)
iemAQ.smoothen()
iemAQ.equalize(concha_interference=True,treble_f_lower=15000,treble_f_upper=20001,max_gain=10)

peqs = iemAQ.optimize_parametric_eq({'filters': [{'type': 'PEAKING'}] * 1}, 48000)
i = 0
for filt in peqs[0].filters:
    i+=1
    print(f'Filter {i}: ON PK Fc {filt.fc:.2f} Hz Gain {filt.gain:.2f} dB Q {filt.q:.2f}')

iemAQ.plot()
