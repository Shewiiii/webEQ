from autoeq.frequency_response import FrequencyResponse
from autoeq.constants import PEQ_CONFIGS
from pathlib import Path
from app.getFRoT import getFRoTList
from app.getFRfromFile import *
from random import randint
from app.computeFilters import *
from app.cleanData import normalize
from app.createFiles import *


    
def autoEQ(iem:str,target:str,config,concha_interference,filterTypes,upshift:int=60):
    FRList = getFRoTList('frequency_responses')
    frequencies,gains = getFRfromFile(f'{FRList[iem]}.txt',relativepath='frequency_responses')    
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
    #generate paraEQ filters
    i = 0
    paraEQ = {}
    for filt in peqs[0].filters:
        paraEQ[i] = [filterTypes[i],round(filt.fc),round(filt.gain,1),round(filt.q,1)]
        i+=1
        #{1: [frequency,gain,q]}

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

    Tgains = normalize(frequencies,idealGains,Tgains)
    #generate IIR string
    IIRstring = paraToIIR(paraEQ)
    #Create files
    createParaEQFile(iem,target,paraEQ)
    createPAFile(iem,target,paraEQ)
    createWaveletFile(iem,target,iemAQ)
    
    return frequencies, gains, newGains, Tgains, paraEQ, IIRstring
