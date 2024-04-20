from os import listdir, path
import pathlib


def getFRoTDict(relativePath: str) -> dict:
    path = pathlib.Path(__file__).parents[1] / relativePath
    templist = listdir(path)
    templist.sort()
    dico = {}
    finalist = []
    for iem in templist:
        key = iem.replace('.txt', '').replace('(AVG)', '').replace('(L)', '').replace('(R)', '')
        if key[-1] == ' ':
            key = key[:-1]
        dico[key] = iem.replace('.txt', '')
    return dico
