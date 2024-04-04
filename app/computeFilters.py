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


def calcGains(frequencies: list, coeffs: list, samplerate=48000):

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


def getCoeffs(rawFilename: str, target: str) -> list:
    coeffs = []
    paraDico = getParaEQ(rawFilename.replace('.txt', ''), target)
    # donc [fréquence,gain,Q] mais en string pas float
    for settings in paraDico.values():
        coeffs.append(peak(float(settings[0]), float(
            settings[2]), float(settings[1])))
    return coeffs


def getAllFR(rawiem: str, target: str) -> list:
    # get FR of the iem from a/the txt file
    frequencies, gains = getFRfromFile(rawiem.replace('.txt', '')+'.txt')
    AVGgain = 0

    valcount = len(frequencies)
    for a in gains:
        AVGgain += a
    AVGgain = AVGgain/valcount

    coeffs = getCoeffs(rawiem, target)  # compute the coeffs of the peak EQs
    # cumpute the gains of the final EQ
    deltaGains = calcGains(frequencies, coeffs)
    newgains = []
    for i in range(valcount):
        # reshape de final EQ basically
        newgains.append(gains[i]+deltaGains[i])

    Tfrequencies, Tgains = getFRfromFile(
        target+'.txt', 'targets')  # FR of the target

    return frequencies, gains, newgains, Tfrequencies, Tgains, AVGgain
