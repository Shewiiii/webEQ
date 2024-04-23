from autoeq.frequency_response import FrequencyResponse
from autoeq.constants import PEQ_CONFIGS
from pathlib import Path
from app.getFRoT import getFRoTDict
from app.getFRfromFile import *
from random import randint
from app.computeFilters import *
from app.createFiles import *


    
def autoEQ(iem:str,target:str,config,concha_interference,filterTypes,gekiyaba,upshift:int=60):
    FRList = getFRoTDict('frequency_responses')
    frequencies,gains = getFRfromFile(f'{FRList[iem]}.txt',relativepath='frequency_responses') 
    if gekiyaba:   
        Tfrequencies,Tgains = getFRfromFile(f'{target}.txt',relativepath='frequency_responses')
    else:
        Tfrequencies,Tgains = getFRfromFile(f'{target}.txt',relativepath='targets')

    iemAQ = FrequencyResponse(name=iem,frequency=frequencies,raw=gains)
    targetAQ = FrequencyResponse(name=target,frequency=Tfrequencies,raw=Tgains)

    iemAQ.interpolate()
    iemAQ.center()
    iemAQ.compensate(targetAQ)
    iemAQ.smoothen()
    iemAQ.equalize(concha_interference=concha_interference)

    targetAQ.interpolate()
    targetAQ.center()
    targetAQ.smoothen()

    peqs = iemAQ.optimize_parametric_eq(config, 44100)
    #generate results (parametric) filters
    i = 0
    restults = []
    for filt in peqs[0].filters:
        restults.append({'type':filterTypes[i],'freq':round(filt.fc),'q':round(filt.q,1),'gain':round(filt.gain,1)})
        i+=1
        #[{'type':'PK','freq':20.0,'q':1.0,'gain':3.0}]

    frequencies = list(iemAQ.frequency)
    gains = list(iemAQ.raw)
    newGains = list(iemAQ.raw+iemAQ.parametric_eq)
    idealGains = list(iemAQ.equalized_raw)
    Tgains = list(targetAQ.raw)

    for i in range(len(frequencies)):
        gains[i] += upshift
        newGains[i] += upshift
        Tgains[i] += upshift
        idealGains[i] += upshift

    #generate IIR string
    IIRstring = paraToIIR(restults)
    #Create files
    createParaEQFile(iem,target,restults)
    createPAFile(iem,target,restults)
    createWaveletFile(iem,target,iemAQ)
    
    return frequencies, gains, newGains, Tgains, restults, IIRstring
