import numpy as np
import matplotlib.pyplot as plt
from app.getFRfromFile import *
from app.getEQ import getParaEQ
from math import *
# source: source code of listener/crinacle/...'s graph tool
def peak(frequency, q, gain, samplerate=48000):
    frequency = frequency / samplerate
    w0 = 2 * pi * frequency
    sinw0 = sin(w0)
    cosw0 = cos(w0)
    a = pow(10, (gain/40))
    alpha = sinw0 / (2 * q)

    a0 = 1 + alpha / a
    a1 = -2 * cosw0
    a2 = 1 - alpha / a
    b0 = 1 + alpha * a
    b1 = -2 * cosw0
    b2 = 1 - alpha * a

    return [1.0, a1/a0, a2/a0, b0/a0, b1/a0, b2/a0]


def calcGains(frequencies: list, coeffs: list, samplerate=48000) -> list:

    valcount = len(frequencies)
    gains = [0]*valcount
    for i in range(len(coeffs)):
        a0, a1, a2, b0, b1, b2 = coeffs[i]
        for j in range(valcount):
            w = 2 * pi * frequencies[j] / samplerate
            phi = 4 * pow(sin(w / 2), 2)
            c = (
                10 * log10(pow(b0 + b1 + b2, 2) +
                           (b0 * b2 * phi - (b1 * (b0 + b2) + 4 * b0 * b2)) * phi) -
                10 * log10(pow(a0 + a1 + a2, 2) +
                           (a0 * a2 * phi - (a1 * (a0 + a2) + 4 * a0 * a2)) * phi))
            gains[j] += c
    return gains


def getCoeffsAndPara(results) -> list:
    #results example: [{'type': 'PK', 'freq': 20, 'q': 0.7, 'gain': -4.6},...]
    coeffs = []
    paraEQ = {}
    i = 0
    filtersDict = {"PK":"Peak","LSC":"LShelf","HSC":"HShelf"}
    for filter in results:
        i+= 1
        coeffs.append(peak(filter['freq'], filter['q'], filter['gain']))
        paraEQ[i] = [filtersDict[filter['type']],filter['freq'],filter['gain'],filter['q']]
    return coeffs,paraEQ


def getNewGain(frequencies:list,gains: list, Tgains: list,results:list) -> list:
    # get FR of the iem from a/the txt file
    valcount = len(gains)

    coeffs,paraEQ = getCoeffsAndPara(results)
    # compute the coeffs of the peak EQs

    deltaGains = calcGains(frequencies, coeffs)
    # cumpute the gains of the final EQ
    newGains = []
    for i in range(valcount):
        # reshape de final EQ basically
        newGains.append(gains[i]+deltaGains[i])
    return newGains,paraEQ,deltaGains
