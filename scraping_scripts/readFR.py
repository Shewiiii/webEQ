#skipped/not in the fr folder yet: NF Audio NF2u,NF Audio NM2+,Tin P2 Plus Commemorative Edition, Tin T1 Plus,from Tin T3 Plus to Tipsy Dunmer Pro
#Put the array here, should be [phone,brand+name+(AVG)]
all = []


phone = all[0]

iem = all[1]
iem += ' (AVG)'


string = ''
for fr, gain in phone:
    string += f'{fr}    {gain}\n'

for c in ['"', '?', ':', '/', '\\', '*', '<', '>', '|']:
    iem = iem.replace(c, ' ')
open(f'{iem}.txt','w').write(string)