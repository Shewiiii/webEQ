from autoeq.frequency_response import FrequencyResponse
from autoeq.constants import PEQ_CONFIGS
from pathlib import Path
from app.getFRoT import getFRoTList
from app.getFRfromFile import *
from random import randint
from app.computeFilters import *
from app.cleanData import normalize


def paraToIIR(paraEQ):
    paraEQList = list(paraEQ.values())
    string = f"iir:type=lshelf;f={paraEQList[0][0]};g={paraEQList[0][1]};q={paraEQList[0][2]},"
    string = f"iir:type=hshelf;f={paraEQList[0][0]};g={paraEQList[0][1]};q={paraEQList[0][2]},"
    for paras in paraEQList[2:]:
        string = string + f"iir:type=peak;f={paras[0]};g={paras[1]};q={paras[2]},"
    return string

def createParaEQFile(iem:str,target:str,paraEQ:dict):
    filePath = pathlib.Path(__file__).parents[1] / f'generated_files/{iem} [{target}] (Parametric EQ).txt'

    paraEQList = list(paraEQ.values())
    string = f'Filter 1: ON LSC Fc {paraEQList[0][0]} Hz Gain {paraEQList[0][1]} dB Q {paraEQList[0][2]}\n'
    string = f'Filter 2: ON HSC Fc {paraEQList[0][0]} Hz Gain {paraEQList[0][1]} dB Q {paraEQList[0][2]}\n'
    i = 2
    for paras in paraEQList[2:]:
        i += 1
        string += f'Filter {i}: ON PK Fc {paras[0]} Hz Gain {paras[1]} dB Q {paras[2]}\n'
    open(filePath,'w').write(string)

def createPAFile(iem:str,target:str,paraEQ:dict):
    filePath = pathlib.Path(__file__).parents[1] / f'generated_files/{iem} [{target}] (Poweramp).json'
    bands = [{"type":0,"channels":0,"frequency":90,"q":0,"gain":0.0,"color":0},{"type":1,"channels":0,"frequency":10000,"q":0,"gain":0.0,"color":0}]
    paraEQList = list(paraEQ.values())
    for paras in paraEQList[1:]:
        bands.append({"type":3,"channels":0,"frequency":paras[0],"q":paras[2],"gain":paras[1],"color": randint(-16711680,0)})
    for i in range(4,6):
        bands.append({"type":i,"channels":0,"frequency":paraEQList[0][0],"q":paraEQList[0][2],"gain":paraEQList[0][1],"color": randint(-16711680,0)})
    string = str([{"name":f"{iem} [{target}]","preamp":0.0,"parametric": True,"bands": bands}]).replace("'",'"').replace("True","true")
    open(filePath,'w').write(string)

def createWaveletFile(iem:str,target:str,iemAQ):
    string = iemAQ.eqapo_graphic_eq()
    filePath = pathlib.Path(__file__).parents[1] / f'generated_files/{iem} [{target}] (Wavelet,Equalizer APO).txt'
    open(filePath,'w').write(string)
    
def autoEQ(iem:str,target:str,config,concha_interference,treble_f_lower,upshift:int=60):
    FRlist = getFRoTList('frequency_responses')
    frequencies,gains = getFRfromFile(f'{FRlist[iem]}.txt',relativepath='frequency_responses')    
    Tfrequencies,Tgains = getFRfromFile(f'{target}.txt',relativepath='targets')

    iemAQ = FrequencyResponse(name=iem,frequency=frequencies,raw=gains)
    targetAQ = FrequencyResponse(name=target,frequency=Tfrequencies,raw=Tgains)

    iemAQ.interpolate()
    iemAQ.center()
    iemAQ.compensate(targetAQ)
    iemAQ.smoothen()
    iemAQ.equalize(concha_interference=concha_interference,treble_f_lower=treble_f_lower,treble_f_upper=20000,treble_window_size=1/12,treble_gain_k=1)

    targetAQ.interpolate()
    targetAQ.center()
    targetAQ.smoothen()

    peqs = iemAQ.optimize_parametric_eq(config, 44100)
    #generate paraEQ filters
    i = 0
    paraEQ = {}
    for filt in peqs[0].filters:
        i+=1
        paraEQ[i] = [round(filt.fc),round(filt.gain,1),round(filt.q,1)]
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
