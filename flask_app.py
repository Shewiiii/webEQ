from flask import Flask, render_template, request, send_file, redirect
from app.getFRoT import getFRoTList
from app.computeFilters import getNewGain
from app.cleanData import normalize
from app.dynamicAutoEQ import autoEQ
from fractions import Fraction
from app.getFRfromFile import *
from autoeq.constants import PEQ_CONFIGS
from app.lochbaumEQ import getLochbaum
from app.createFiles import *
from app.getEQ import getParaEQ2
from autoeq.frequency_response import FrequencyResponse

app = Flask(__name__)

FRDict = getFRoTList('frequency_responses')
# dictionnaire avec en clé le model et en valeur le nom du fichier brut
targetList = list(getFRoTList('targets').keys())
FRList = list(FRDict.keys())

def gekiyaba(target):
    return not target in targetList

class EQ():
    iem = ""
    rawiem = ""
    target = ""
    frequencies = []
    gains = []
    Tgains = []
    newGains = []
    results = []
    IIR = ""
    deltaGains = []
    gekiyaba = False

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', FRList=FRList, targetList=targetList, result=None)


@app.route('/resultsAQ', methods=['GET', 'POST'])
def resultsAQ():
    

    #======store target an IEM from form======
    EQ.iem = str(request.form.get('iem'))
    EQ.target = str(request.form.get('target'))
    EQ.gekiyaba =  gekiyaba(EQ.target)
    if EQ.gekiyaba:
        #check if gekiyaba mode !!! 
        EQ.target = FRDict[EQ.target]
    print('choix:', EQ.iem, EQ.target)

    if EQ.iem == 'None' or EQ.target == 'None':
            #pour s'assurer que l'utilisateur a bien choisi quelque chose
            return redirect('/')
    EQ.rawiem = FRDict[EQ.iem]

    #======settings======
    filterCount = int(request.form.get('filterCount'))
    if str(request.form.get('EQres')) == 'yes':
        concha_interference = False
    else:
        concha_interference = True

    mode = str(request.form.get('mode'))
    if mode == 'standard':
        config = {
            'filters': 
            [{'type': 'LOW_SHELF','fc': 105.0},{'type': 'HIGH_SHELF','fc': 10000.0}]+
            [{'type': 'PEAKING'}] * (filterCount-2)}
        filterTypes = ['LSQ','HSC'] + ['PK'] * (filterCount-2)
    elif mode == 'moondrop':
        config = PEQ_CONFIGS['MOONDROP_FREE_DSP']
        filterTypes = ['PK'] * 9

    #======autoEQ======
    EQ.frequencies, \
    EQ.gains, \
    EQ.newGains, \
    EQ.Tgains, \
    EQ.results, \
    EQ.IIR = autoEQ(EQ.iem,\
                            EQ.target,\
                            config,\
                            concha_interference,\
                            filterTypes,\
                            EQ.gekiyaba)

    EQ.Tgains = normalize(EQ.frequencies, EQ.newGains, EQ.Tgains)

    #======return======
    return render_template('index.html',
                        FRList=FRList,
                        targetList=targetList,
                        result="aouiiii",
                        results=EQ.results,
                        iem=EQ.iem,
                        target=EQ.target,
                        iir=EQ.IIR, \
                        # pour graph:
                        frequencies=EQ.frequencies, \
                        gains=EQ.gains, \
                        newgains=EQ.newGains, \
                        Tgains=EQ.Tgains
                        )


@app.route('/wavelet')
def wavelet():
    path = f'generated_files/{EQ.iem} [{EQ.target}] (Wavelet,Equalizer APO).txt'
    return send_file(path, as_attachment=True)


@app.route('/poweramp')
def poweramp():
    path = f'generated_files/{EQ.iem} [{EQ.target}] (Poweramp).json'
    return send_file(path, as_attachment=True)


@app.route('/parametric')
def parametric():
    path = f'generated_files/{EQ.iem} [{EQ.target}] (Parametric EQ).txt'
    return send_file(path, as_attachment=True)


@app.route('/lochbaum', methods=['GET', 'POST'])
def lochbaum():
    #======store target an IEM from form======
    EQ.iem = str(request.form.get('iem'))
    EQ.target = str(request.form.get('target'))
    EQ.gekiyaba =  gekiyaba(EQ.target)
    if EQ.gekiyaba:
        #check if gekiyaba mode !!! 
        EQ.target = FRDict[EQ.target]

    print('choix:', EQ.iem, EQ.target)

    if EQ.iem == 'None' or EQ.target == 'None':
            #pour s'assurer que l'utilisateur a bien choisi quelque chose
            return redirect('/')
    EQ.rawiem = FRDict[EQ.iem]

    #======settings=====
    filterCount = int(request.form.get('filterCount'))

    #======get all data======
    EQ.frequencies,EQ.gains,EQ.Tgains,iemLoch,targetLoch = getLochbaum(EQ.rawiem,EQ.target,EQ.gekiyaba)

    #======return======
    return render_template('lochbaum.html',iemLoch=iemLoch,targetLoch=targetLoch,filterCount=filterCount)

@app.route('/process-data', methods = ['POST'])
def process_data(): 
    EQ.results = request.json['data'] 
    
    EQ.newGains,EQ.deltaGains = getNewGain(EQ.frequencies,EQ.gains,EQ.results)
    EQ.Tgains = normalize(EQ.frequencies, EQ.newGains, EQ.Tgains,at=240)

    #======return======
    return redirect("/resultsLO")


@app.route('/resultsLO')
def results2():
    print(EQ.results)

    #======get all data======
    EQ.IIR = paraToIIR(EQ.results)
    createParaEQFile(EQ.iem,EQ.target,EQ.results)
    createPAFile(EQ.iem,EQ.target,EQ.results)
    iemAQ = FrequencyResponse(name="temp",frequency=EQ.frequencies,raw=EQ.gains,equalization=EQ.deltaGains)
    #to create wavelet file
    createWaveletFile(EQ.iem,EQ.target,iemAQ)

    #======return======
    return render_template('index.html',
                        FRList=FRList,
                        targetList=targetList,
                        result="aouiiii",
                        results=EQ.results,
                        iem=EQ.iem,
                        target=EQ.target,
                        iir=EQ.IIR, \
                        # pour graph:
                        frequencies=EQ.frequencies, \
                        gains=EQ.gains, \
                        newgains=EQ.newGains, \
                        Tgains=EQ.Tgains
                        )

@app.route('/moondrop', methods=['GET','POST'])
def moondrop():
    if request.method == 'POST':   
        f = request.files['file'] 
        path = f'uploads/{f.filename}'
        f.save(path)
        results = getParaEQ2(path)

        frequencies = list(FrequencyResponse(name='temp').frequency)
        #len: 695
        gains = [60.0]*695
        newGains,deltaGains = getNewGain(frequencies,gains,results)
        base = FrequencyResponse(name='idk',frequency=frequencies,raw=gains)
        base.interpolate()
        base.center()
        target = FrequencyResponse(name='uwu',frequency=frequencies,raw=newGains)
        base.compensate(target)
        base.equalize()

        config = {
        'optimizer': {
            'min_std': 0.008
        },
        'filters': [{
            'type': 'PEAKING',
            'min_q': 0.5,
            'max_q': 6.0,
            'min_fc': 40.0,
            'max_fc': 20000.0,
            'min_gain': -12.0,
            'max_gain': 3.0,
        }] * 9
        }   
        peqs = base.optimize_parametric_eq(config,44100)[0].filters
        
        string = ''
        i = 0
        for filt in peqs:
            i += 1
            string += f'Filter {i}: ON PK Fc {int(filt.fc)} Hz Gain {round(filt.gain,1)} dB Q {round(filt.q,1)}\n'
        path = f'generated_files/{f.filename}'
        open(path,'w').write(string)
        return send_file(path, as_attachment=True)

    return render_template('moondrop.html')


if __name__ == "__main__":
    app.run(debug=True)
