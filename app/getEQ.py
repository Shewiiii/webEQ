from os import listdir, path
import pathlib
import re


def getPath(iem: str, target: str, type: str, extention):
    return pathlib.Path(__file__).parents[1] / 'presets' / target / type / f'{iem} [{target}].{extention}'


def getIIRPath(iem: str, target: str):
    return pathlib.Path(__file__).parents[1] / 'presets' / target / 'IIR' / f'{iem} [{target}]_IIR.txt'


def getOnlinePath(iem: str, target: str, type: str, extention):
    return f'https://raw.githubusercontent.com/Shewiiii/EQutilities/0ff9f3db450e19077b56f902e3635ea263647b9f/presets/betterAutoEQ/{target}/{type}/{iem} [{target}].{extention}'


def getIIRString(iem: str, target: str):
    path = getIIRPath(iem, target)
    return open(path, 'r').readline()


def getParaEQ(iem: str, target: str) -> dict:
    EQPath = getPath(iem, target, 'Parametric', 'txt')
    paras = open(EQPath, 'r').readlines()[1:]
    final = {}
    for para in paras:
        # trouve float dans un str #donc [num du filtre, fréquence, gain, q value]
        values = re.findall(r"[-+]?(?:\d*\.*\d+)", para)
        if values[1] != '0':
            # dans valeur une liste: fréquence, gain, q value
            final[f'{values[0]}'] = values[1:]
    return final
