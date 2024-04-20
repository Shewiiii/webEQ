from app.getFRoT import *
from app.getFRfromFile import *
from app.cleanData import cleanData
import matplotlib.pyplot as plt
import math

headphones = ['Audeze', 'Hifiman', 'Bose', 'HyperX',
              'Sennheiser HD', 'Sennheiser HE-1', 'Sony WH', 'AKG', 'Focal', 'Logitech', 'Beyerdynamic', 'Project', 'nodip']

class Constants:
    coeffs = [1, 4, 3, 2]
    listLength = 695
    bassBounds = [20, 100]
    bounds = [100, 3000]
    upperBounds = [3000, 7000]
    trebleBounds = [9000, 20000]
    excludeHeadphones = True


def rmsValue(arr):
    m = len(arr)
    #source: https://www.geeksforgeeks.org/program-to-calculate-root-mean-square/
    square = 0
    mean = 0.0
    root = 0.0
     
    #Calculate square
    for i in range(0,m):
        square += (arr[i]**2)
     
    #Calculate Mean 
    mean = (square / (float)(m))
     
    #Calculate Root
    root = math.sqrt(mean)
     
    return root

def isHeadphone(device: str):
    for headphone in headphones:
        if headphone in device:
            return True
    return False


def getScore(device: str, target: list, to100: bool = True, coeffs: list = Constants.coeffs, listLength: int = Constants.listLength, bounds: list = Constants.bounds, upperBounds: list = Constants.upperBounds, bassBounds: list = Constants.bassBounds, trebleBounds: list = Constants.trebleBounds) -> float:
    fr = getFRfromFile(device)
    # fr: ([frequency],[gain])

    t = getFRfromFile(target.replace('.txt', ''), 'targets')
    # t (target): ([frequency],[gain])

    frequencies, gains = cleanData(fr[0], fr[1])
    Tfrequencies, Tgains = cleanData(t[0], t[1])

    scoresBass = []
    scoresMid = []
    scoresUMid = []
    scoresTreble = []

    for i in range(listLength):
        # check if in bounds
        # coeffs: [coef bass, coef mid, coef treble]

        if bassBounds[0] < frequencies[i] <= bassBounds[1]:
            scoresBass.append(abs(Tgains[i]-gains[i]))
    
        if bounds[0] <= frequencies[i] <= bounds[1]:
            scoresMid.append(abs(Tgains[i]-gains[i]))

        if upperBounds[0] <= frequencies[i] <= upperBounds[1]:
            scoresUMid.append(abs(Tgains[i]-gains[i]))

        if trebleBounds[0] < frequencies[i] <= trebleBounds[1]:
            scoresTreble.append(abs(Tgains[i]-gains[i]))

    AVGscore = (rmsValue(scoresBass)*coeffs[0]+rmsValue(scoresMid)*coeffs[1]+rmsValue(scoresUMid)*coeffs[2]+rmsValue(scoresTreble)*coeffs[3])/4
    if to100:
        AVGscore = round(100/AVGscore, 2)
        return AVGscore
    return round(AVGscore, 2)

def findClosestToTarget(target: str, to100: bool = False,coeffs: list = Constants.coeffs, bounds: list = Constants.bounds, upperBounds: list = Constants.upperBounds, bassBounds: list = Constants.bassBounds, trebleBounds: list = Constants.trebleBounds, excludeHeadphones: bool = Constants.excludeHeadphones) -> list:
    scoreDict = {}
    dico = getFRoTDict('frequency_responses')

    for iem in dico.values():

        # ===Excluse headphones if needed===
        if excludeHeadphones:
            if isHeadphone(iem):
                ignore = True
            else:
                ignore = False
        else:
            ignore = False

        # Take only AVG frequency responses
        if ignore == False:
            AVGscore = getScore(iem, target, to100=to100, bassBounds=bassBounds, bounds=bounds, upperBounds=upperBounds,
                                 trebleBounds=trebleBounds, coeffs=coeffs)
            scoreDict[iem.replace(' (AVG)', '')] = AVGscore
            if to100 == True:
                sortedList = sorted(scoreDict.items(), key=lambda x: x[1],reverse=True)
            else:
                sortedList = sorted(scoreDict.items(), key=lambda x: x[1])
    
    return sortedList


def top(size, target, coeffs: list = Constants.coeffs, bounds: list = Constants.bounds, upperBounds: list = Constants.upperBounds, bassBounds: list = Constants.bassBounds, trebleBounds: list = Constants.trebleBounds, excludeHeadphones: bool = Constants.excludeHeadphones):
    sortedList = findClosestToTarget(target, to100=True, bassBounds=bassBounds, bounds=bounds, upperBounds=upperBounds, trebleBounds=trebleBounds, coeffs=coeffs, excludeHeadphones=excludeHeadphones)
    
    print(f'Target: {target}, calculating score from {bassBounds[0]} Hz to {bounds[1]} Hz and {trebleBounds[0]} Hz to {trebleBounds[1]} Hz.')
    print(f'Coeffs: \nBass: {coeffs[0]} ({bassBounds[0]}Hz - {bassBounds[1]}Hz)\nMidrange: {coeffs[1]} ({bounds[0]}Hz - {bounds[1]}Hz)\nUpper-midrange: {coeffs[2]} ({upperBounds[0]}Hz - {upperBounds[1]}Hz)\nTreble: {coeffs[3]} ({trebleBounds[0]}Hz - {trebleBounds[1]}Hz)')
    print('')
    for i in range(size):
        # score=100/delta(pondéré)
        print(f'{i+1}. {sortedList[i][0]}, score: {sortedList[i][1]}')


def plot(size: int, target: str, height: int, coeffs: list = Constants.coeffs, bounds: list = Constants.bounds, upperBounds: list = Constants.upperBounds, bassBounds: list = Constants.bassBounds, trebleBounds: list = Constants.trebleBounds, excludeHeadphones: bool = Constants.excludeHeadphones):
    sortedList = findClosestToTarget(target, to100=True, bassBounds=bassBounds, bounds=bounds, upperBounds=upperBounds, trebleBounds=trebleBounds, coeffs=coeffs, excludeHeadphones=excludeHeadphones)
    devices = [sortedList[size-1-i][0] for i in range(size)]
    scores = [sortedList[size-1-i][1] for i in range(size)]
    fig, ax = plt.subplots()
    fig.set_figheight(height)
    ax.barh(devices, scores)
    
    ax.grid(color ='black',alpha = 0.2)
    ax.set_axisbelow(True)

    for i in ax.patches:
        plt.text(i.get_width()+0.2, i.get_y()+0.5, 
                str(round((i.get_width()), 2)),
                fontsize = 8,
                color ='black')

    print(f'Target: {target}, calculating score from {bassBounds[0]} Hz to {bounds[1]} Hz and {trebleBounds[0]} Hz to {trebleBounds[1]} Hz.')
    print(f'Coeffs: \nBass: {coeffs[0]} ({bassBounds[0]}Hz - {bassBounds[1]}Hz)\nMidrange: {coeffs[1]} ({bounds[0]}Hz - {bounds[1]}Hz)\nUpper-midrange: {coeffs[2]} ({upperBounds[0]}Hz - {upperBounds[1]}Hz)\nTreble: {coeffs[3]} ({trebleBounds[0]}Hz - {trebleBounds[1]}Hz)')
    print('')
    plt.show()