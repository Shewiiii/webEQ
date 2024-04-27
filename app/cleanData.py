from autoeq.frequency_response import FrequencyResponse


def cleanData(frequencies, gains, upshift: int = 60, center=[800, 1200]):
    # change direct les variables
    data = FrequencyResponse(name='temp', frequency=frequencies, raw=gains)
    data.interpolate()
    data.center(center)
    cfrequencies = list(data.frequency)
    cgains = list(data.raw)
    for gain in range(len(cgains)):
        cgains[gain] += upshift
    return cfrequencies, cgains
