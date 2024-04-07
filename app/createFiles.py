import pathlib
from random import randint

def paraToIIR(paraEQ:dict):

    filtersDict = {"Peak":"peak","LShelf":"lshelf","HShelf":"hshelf"}
    paraEQList = list(paraEQ.values())

    string = ''
    for paras in paraEQList:
        string = string + f"iir:type={filtersDict[paras[0]]};f={paras[1]};g={paras[2]};q={paras[3]},"
    return string

def createParaEQFile(iem:str,target:str,paraEQ:dict):

    filePath = pathlib.Path(__file__).parents[1] / f'generated_files/{iem} [{target}] (Parametric EQ).txt'
    filtersDict = {"Peak":"PK","LShelf":"LSC","HShelf":"HSC"}

    paraEQList = list(paraEQ.values())
    string = ''
    i = 0
    for paras in paraEQList:
        i += 1
        string += f'Filter {i}: ON {filtersDict[paras[0]]} Fc {paras[1]} Hz Gain {paras[2]} dB Q {paras[3]}\n'
    open(filePath,'w').write(string)

def createPAFile(iem:str,target:str,paraEQ:dict):

    filePath = pathlib.Path(__file__).parents[1] / f'generated_files/{iem} [{target}] (Poweramp).json'
    filtersDict = {"Peak":3,"LShelf":4,"HShelf":5}

    bands = [{"type":0,"channels":0,"frequency":90,"q":0,"gain":0.0,"color":0},{"type":1,"channels":0,"frequency":10000,"q":0,"gain":0.0,"color":0}]

    paraEQList = list(paraEQ.values())
    for paras in paraEQList:
        bands.append({"type":filtersDict[paras[0]],"channels":0,"frequency":paras[1],"q":paras[3],"gain":paras[2],"color": randint(-16711680,0)})
    string = str([{"name":f"{iem} [{target}]","preamp":0.0,"parametric": True,"bands": bands}]).replace("'",'"').replace("True","true")
    open(filePath,'w').write(string)

def createWaveletFile(iem:str,target:str,iemAQ):
    string = iemAQ.eqapo_graphic_eq()
    filePath = pathlib.Path(__file__).parents[1] / f'generated_files/{iem} [{target}] (Wavelet,Equalizer APO).txt'
    open(filePath,'w').write(string)