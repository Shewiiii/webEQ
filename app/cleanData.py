from autoeq.frequency_response import FrequencyResponse

def normalize(frequencies: list, newgains: list, Tgains, at: int = 35):
    #THIS IS SO CURSED LMAO
    Tvalcount = len(frequencies)
    deltagain = newgains[at]-Tgains[at]
    for l in range(Tvalcount):
        Tgains[l] += deltagain
    return Tgains

def cleanData(frequencies,gains,upshift:int=60):
    #change direct les variables
    data = FrequencyResponse(name='temp',frequency=frequencies,raw=gains)
    data.interpolate()
    data.center()
    cfrequencies = list(data.frequency)
    cgains = list(data.raw)
    for gain in range(len(cgains)):
        cgains[gain] += upshift
    return cfrequencies,cgains

