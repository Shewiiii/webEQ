import numpy as np
import matplotlib.pyplot as plt
from getFRfromFile import *
from getEQ import getParaEQ
from math import *

def peak(frequency,q,gain,samplerate=48000): #source: source code of listener/crinacle/...'s graph tool
    frequency = frequency / samplerate
    w0 = 2* pi * frequency
    sinw0 = sin(w0)
    cosw0 = cos(w0)
    a = pow(10,(gain/40))
    alpha = sinw0 / (2 * q)

    a0 = 1 + alpha / a
    a1 = -2 * cosw0
    a2 = 1 - alpha / a
    b0 = 1 + alpha * a
    b1 = -2 * cosw0
    b2 = 1 - alpha * a

    return [1.0,a1/a0,a2/a0,b0/a0,b1/a0,b2/a0]

def calcGains(frequencies:list,coeffs:list,samplerate=48000):

    valcount = len(frequencies)
    gains = [0]*valcount
    for i in range(len(coeffs)):
        a0, a1, a2, b0, b1, b2 = coeffs[i]
        for j in range(valcount):
            w = 2 * pi * frequencies[j] / samplerate
            phi = 4 * pow(sin(w / 2), 2)
            c = ( \
                10 * log10(pow(b0 + b1 + b2, 2) + \
                    (b0 * b2 * phi - (b1 * (b0 + b2) + 4 * b0 * b2)) * phi) - \
                10 * log10(pow(a0 + a1 + a2, 2) + \
                    (a0 * a2 * phi - (a1 * (a0 + a2) + 4 * a0 * a2)) * phi))
            gains[j] += c
    return gains

def getCoeffs(rawFilename:str,target:str) -> list:
    coeffs = []
    paraDico = getParaEQ(rawFilename.replace('.txt',''),target)
    for settings in paraDico.values(): #donc [fréquence,gain,Q] mais en string pas float
        coeffs.append(peak(float(settings[0]),float(settings[2]),float(settings[1])))
    return coeffs

def plotEQ(rawiem,target):
    frequencies,gains = getFRfromFile(rawiem.replace('.txt','')+'.txt') #get FR of the iem from a/the txt file
    AVGgain = 0

    valcount = len(frequencies)
    for a in gains:
        AVGgain += a
    AVGgain = AVGgain/valcount

    coeffs = getCoeffs(rawiem,target) #compute the coeffs of the peak EQs
    deltaGains = calcGains(frequencies,coeffs) #cumpute the gains of the final EQ
    newgains = []
    for i in range(valcount):
        newgains.append(gains[i]+deltaGains[i]) #reshape de final EQ basically

    Tfrequencies,Tgains = getFRfromFile(target+'.txt','targets') #FR of the target

    plt.plot(frequencies,gains,'b')
    plt.plot(frequencies,newgains,'r')
    plt.plot(Tfrequencies,Tgains,'gray',linestyle='dashed')
    plt.grid(True, which="both")
    plt.xscale("log")
    plt.axis([20,20000,AVGgain-15,AVGgain+15])
    plt.show()

#plotEQ('[APROX]Moondrop Blessing2 (AVG)','Shewi Target')