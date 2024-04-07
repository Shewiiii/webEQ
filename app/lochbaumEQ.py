from app.getFRfromFile import *
from app.getFRoT import getFRoTList
from autoeq.frequency_response import FrequencyResponse
from app.cleanData import normalize

# iem = 'Apple AirPods Pro 2'
# target = 'Shewi Target'

def getLochbaum(rawiem,target):
    frequencies,gains = getFRfromFile(f'{rawiem}.txt',relativepath='frequency_responses')    
    Tfrequencies,Tgains = getFRfromFile(f'{target}.txt',relativepath='targets') 

    iemAQ = FrequencyResponse(name=rawiem,frequency=frequencies,raw=gains)
    targetAQ = FrequencyResponse(name=target,frequency=Tfrequencies,raw=Tgains)

    f_step = 1.0145
    iemAQ.interpolate(f_step=f_step)
    targetAQ.interpolate(f_step=f_step)

    # targetAQ.raw = normalize(iemAQ.raw,gains,targetAQ.raw,at=240)
    print(targetAQ.raw[240],iemAQ.raw[240])
    iemLoch = []
    for i in range(len(iemAQ.frequency)):
        iemLoch.append([iemAQ.frequency[i],iemAQ.raw[i]])

    targetLoch = []
    for i in range(len(targetAQ.frequency)):
        targetLoch.append([targetAQ.frequency[i],targetAQ.raw[i]])
    return list(iemAQ.frequency),list(iemAQ.raw),list(targetAQ.raw),iemLoch,targetLoch