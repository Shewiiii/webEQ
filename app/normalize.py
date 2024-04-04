from app.getFRfromFile import getFRfromFile
def normalize(frequencies:list,newgains:list,Tfrequencies:list,Tgains,at:float=1000.0):
    Tvalcount = len(Tfrequencies)
    i = 0
    j = 0
    while frequencies[i] <= at:
        i+=1
    while Tfrequencies[j] <= at:
        j+=1
    deltagain = newgains[i]-Tgains[j]
    for l in range(Tvalcount):
        Tgains[l] += deltagain-0.2
    return Tgains