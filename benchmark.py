from app.getFRoT import *
from app.getFRfromFile import *
from app.cleanData import *
import matplotlib.pyplot as plt
from math import *

headphones = ['Audeze', 'Hifiman', 'Bose', 'HyperX',
              'Sennheiser HD', 'Sennheiser HE-1', 'Sony WH', 'AKG', 'Focal', 'Logitech', 'Beyerdynamic', 'Project', 'nodip','Yamaha','Auribus']


class Constants:
    coeffs = [1, 3, 4, 2]
    listLength = 695
    bassBounds = [20, 150]
    bounds = [150, 3000]
    upperBounds = [3000, 8000]
    trebleBounds = [11000, 18500]
    excludeHeadphones = True


def isHeadphone(device: str):
    for headphone in headphones:
        if headphone in device:
            return True
    return False


def getScore(device: str, target: list, showDelta: bool = False, to100: bool = True, coeffs: list = Constants.coeffs, listLength: int = Constants.listLength, bounds: list = Constants.bounds, upperBounds: list = Constants.upperBounds, bassBounds: list = Constants.bassBounds, trebleBounds: list = Constants.trebleBounds) -> float:
    fr = getFRfromFile(device)
    # fr: ([frequency],[gain])

    t = getFRfromFile(target.replace('.txt', ''), 'targets')
    # t (target): ([frequency],[gain])

    frequencies, gains = cleanData(fr[0], fr[1], upshift=0)
    Tfrequencies, Tgains = cleanData(t[0], t[1], upshift=0)

    score = 0
    n = 0
    bscore = 0
    b = 0
    mscore = 0
    m = 0
    umscore = 0
    um = 0
    tscore = 0
    t = 0

    for i in range(listLength):
        # check if in bounds
        # coeffs: [coef bass, coef mid, coef treble]
        delta = abs(Tgains[i]-gains[i])

        if bassBounds[0] <= frequencies[i] <= bassBounds[1]:
            score += delta*coeffs[0]
            bscore += delta
            b += 1
            n += 1

        if bounds[0] <= frequencies[i] <= bounds[1]:
            score += delta*coeffs[1]
            mscore += delta
            m += 1
            n += 1

        if upperBounds[0] <= frequencies[i] <= upperBounds[1]:
            score += delta*coeffs[2]
            umscore += delta
            um += 1
            n += 1

        if trebleBounds[0] <= frequencies[i] <= trebleBounds[1]:
            score += delta*coeffs[3]
            tscore += delta
            t += 1
            n += 1

    AVGscore = score/n
    if to100:
        AVGscore = 100/AVGscore

    if showDelta == True:
        all = [bscore/b, mscore/m, umscore/um, tscore/t]
        final = [round(AVGscore, 2)]
        for i in all:
            final.append(round(i, 1))
        return final
    return round(AVGscore, 2)


def showScore(device: str, target: list, showDelta: bool = False, showTop: bool = True):
    scores = getScore(device, target, showDelta=True)
    iem = device.replace(' (AVG)', '')

    topText =  ''
    if showTop == True:
        sortedList = findClosestToTarget(target,excludeHeadphones=False)
        test = ''
        i = 0
        while iem != test:
            test = sortedList[i][0]
            lengthList = len(sortedList)
            i += 1
        topText = f'Top {round((lengthList-(lengthList-i))/lengthList*100,2)} % ({i}/{lengthList})\n'
    print(f'Score: {scores[0]}\n{topText}Average delta between the target and the FR:\nBass ({Constants.bassBounds[0]}Hz - {Constants.bassBounds[1]}Hz): {scores[1]} dB\nMidrange ({Constants.bounds[0]}Hz - {Constants.bounds[1]}Hz): {scores[2]} dB\nUppder-midrange ({Constants.upperBounds[0]}Hz - {Constants.upperBounds[1]}Hz): {scores[3]} dB\nTreble ({Constants.trebleBounds[0]}Hz - {Constants.trebleBounds[1]}Hz): {scores[3]} dB')

def findClosestToTarget(target: str, to100: bool = False, coeffs: list = Constants.coeffs, bounds: list = Constants.bounds, upperBounds: list = Constants.upperBounds, bassBounds: list = Constants.bassBounds, trebleBounds: list = Constants.trebleBounds, excludeHeadphones: bool = Constants.excludeHeadphones) -> list:
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
            AVGscore = getScore(iem, target, showDelta=True, to100=to100, bassBounds=bassBounds, bounds=bounds, upperBounds=upperBounds,
                                trebleBounds=trebleBounds, coeffs=coeffs)
            scoreDict[iem.replace(' (AVG)', '')] = AVGscore
            if to100 == True:
                sortedList = sorted(scoreDict.items(), key=lambda x: x[1][0], reverse=True)
            else:
                sortedList = sorted(scoreDict.items(), key=lambda x: x[1][0])

    return sortedList


# def top(size, target, coeffs: list = Constants.coeffs, bounds: list = Constants.bounds, upperBounds: list = Constants.upperBounds, bassBounds: list = Constants.bassBounds, trebleBounds: list = Constants.trebleBounds, excludeHeadphones: bool = Constants.excludeHeadphones):
#     sortedList = findClosestToTarget(target, to100=True, bassBounds=bassBounds, bounds=bounds,
#                                      upperBounds=upperBounds, trebleBounds=trebleBounds, coeffs=coeffs, excludeHeadphones=excludeHeadphones)
#     if size == 'all':
#         size = len(sortedList)

#     print(f'Target: {target}, calculating score from {bassBounds[0]} Hz to {bounds[1]} Hz and {trebleBounds[0]} Hz to {trebleBounds[1]} Hz.')
#     print(f'Coeffs: \nBass: {coeffs[0]} ({bassBounds[0]}Hz - {bassBounds[1]}Hz)\nMidrange: {coeffs[1]} ({bounds[0]}Hz - {bounds[1]}Hz)\nUpper-midrange: {coeffs[2]} ({upperBounds[0]}Hz - {upperBounds[1]}Hz)\nTreble: {coeffs[3]} ({trebleBounds[0]}Hz - {trebleBounds[1]}Hz)')
#     print('')
#     for i in range(size):
#         # score=100/delta(pondéré)
#         print(f'{i+1}. {sortedList[i][0]}, score: {sortedList[i][1]}')


def plot(size: int, target: str, height: int, coeffs: list = Constants.coeffs, bounds: list = Constants.bounds, upperBounds: list = Constants.upperBounds, bassBounds: list = Constants.bassBounds, trebleBounds: list = Constants.trebleBounds, excludeHeadphones: bool = Constants.excludeHeadphones):
    sortedList = findClosestToTarget(target, to100=True, bassBounds=bassBounds, bounds=bounds,
                                     upperBounds=upperBounds, trebleBounds=trebleBounds, coeffs=coeffs, excludeHeadphones=excludeHeadphones)
    if size == 'all':
        size = len(sortedList)

    devices = [sortedList[size-1-i][0] for i in range(size)]
    scores = [sortedList[size-1-i][1][0] for i in range(size)]
    fig, ax = plt.subplots()
    fig.set_figheight(height)
    fig.set_figwidth(8)
    ax.barh(devices, scores)

    ax.grid(color='black', alpha=0.2)
    ax.set_axisbelow(True)

    n = 0
    for bar in ax.patches:
        plt.text(bar.get_width()+0.2, bar.get_y()+0.2,
                 f'{round((bar.get_width()), 2)} #{size-n}',
                 fontsize=9,
                 color='black')
        ax.text(0.1, bar.get_y()+bar.get_height()/2,
                f'{sortedList[size-1-n][1][1:]}', color='white', ha='left', va='center', fontsize=8)
        n += 1

    print(f'Target: {target}, calculating score from {bassBounds[0]} Hz to {upperBounds[1]} Hz and {trebleBounds[0]} Hz to {trebleBounds[1]} Hz.')
    print(f'Coeffs: \nBass: {coeffs[0]} ({bassBounds[0]}Hz - {bassBounds[1]}Hz)\nMidrange: {coeffs[1]} ({bounds[0]}Hz - {bounds[1]}Hz)\nUpper-midrange: {coeffs[2]} ({upperBounds[0]}Hz - {upperBounds[1]}Hz)\nTreble: {coeffs[3]} ({trebleBounds[0]}Hz - {trebleBounds[1]}Hz)')
    print('')
    print('Score = 100/[(bassDelta*bassCoeff + midsDelta*midsCoeff + upper-midsDelta*UMidsCoeff + trebleDelta*trebleCoeff)/number of values]')
    plt.show()
