import pathlib
import re

def getFRfromFile(file:str,relativepath:str='frequency_responses') -> tuple[list,list]: #file with extention (.txt)
    path = pathlib.Path(__file__).parents[1] / relativepath / file
    lines = open(path,'r').readlines()

    frequencyList = []
    amplitudeList = []
    dico = {}
    for line in lines:
        values = re.findall(r"[-+]?(?:\d*\.*\d+)",line) #trouve float dans un str
        if len(values) == 2:
            dico[float(values[0])] = float(values[1])
    sortedDico = dict(sorted(dico.items())) 
    for fr,amplitude in sortedDico.items():
        frequencyList.append(fr)
        amplitudeList.append(amplitude)
    return frequencyList,amplitudeList

frequency,amplitude = getFRfromFile('!.txt')
