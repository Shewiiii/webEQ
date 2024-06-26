import pathlib
from random import randint
import base64

parent = pathlib.Path(__file__).parents[1] / f'generated_files/'

def paraToIIR(restults: list):

    filtersDict = {"PK": "peak", "LSQ": "lshelf", "HSC": "hshelf"}

    string = ''
    for para in restults:
        string = string + \
            f"iir:type={filtersDict[para['type']]};f={para['freq']};g={para['gain']};q={para['q']},"
    return string


def createParaEQFile(iem: str, target: str, restults: list):

    filePath = parent / f'{iem} [{target}] (Parametric EQ).txt'

    string = ''
    i = 0
    preamp = 0
    for para in restults:
        i += 1
        string += f"Filter {i}: ON {para['type']} Fc {para['freq']} Hz Gain {para['gain']} dB Q {para['q']}\n"
        #get the highest amplitude to set the preamp value:
        if preamp < para['gain']:
            preamp = para['gain']
    string = f'Preamp: {preamp} dB\n' + string
    open(filePath, 'w').write(string)


def createPAFile(iem: str, target: str, restults: list):

    filePath = parent / f'{iem} [{target}] (Poweramp).json'
    filtersDict = {"PK": 3, "LSQ": 4, "HSC": 5}

    bands = [{"type": 0, "channels": 0, "frequency": 90, "q": 0, "gain": 0.0, "color": 0}, {
        "type": 1, "channels": 0, "frequency": 10000, "q": 0, "gain": 0.0, "color": 0}]

    for para in restults:
        bands.append({"type": filtersDict[para['type']], "channels": 0, "frequency": para['freq'],
                     "q": para['q'], "gain": para['gain'], "color": randint(-16711680, 0)})
    string = str([{"name": f"{iem} [{target}]", "preamp": 0.0, "parametric": True,
                 "bands": bands}]).replace("'", '"').replace("True", "true")
    open(filePath, 'w').write(string)


def createWaveletFile(iem: str, target: str, iemAQ):

    string = iemAQ.eqapo_graphic_eq()
    filePath = parent / f'{iem} [{target}] (Wavelet,Equalizer APO).txt'
    open(filePath, 'w').write(string)


def createChartImage(data: str,id: int):

    filePath = parent / f'chart{id}.png'
    data = data.replace('data:image/png;base64,','')
    imgdata = base64.b64decode(data)
    open(filePath, 'wb').write(imgdata)
