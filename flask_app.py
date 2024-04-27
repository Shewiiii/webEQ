from flask import Flask, render_template, request, send_file, redirect
from app.getFRoT import getFRoTDict
from app.computeFilters import getNewGain
from app.dynamicAutoEQ import autoEQ
from fractions import Fraction
from app.getFRfromFile import *
from autoeq.constants import PEQ_CONFIGS
from app.lochbaumEQ import getLochbaum
from app.createFiles import *
from app.getEQ import getParaEQ2
from autoeq.frequency_response import FrequencyResponse
from app.database import *
import json
# TODO:
# remember the choices
# not let continue if a target/iem has not been chosen
# support simult. requests

app = Flask(__name__)

FRDict = getFRoTDict('frequency_responses')
# dictionnaire avec en clé le model et en valeur le nom du fichier brut
targetList = list(getFRoTDict('targets').keys())
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
    id = get_free_id()
    return render_template('index.html', FRList=FRList, targetList=targetList, result=None, id=id)


@app.route('/processAQ/<id>', methods=['GET', 'POST'])
def processAQ(id):
    # ======put data in the database======
    iem = str(request.form.get('iem'))
    rawiem = FRDict[iem]
    target = str(request.form.get('target'))
    algo = 'default'
    filterCount = int(request.form.get('filterCount'))
    mode = str(request.form.get('mode'))
    eqres = str(request.form.get('EQres'))  # basically 'yes', or 'no'
    log(rawiem, iem, target, algo, filterCount, eqres, mode)

    # ======return======
    return redirect(f'/resultsAQ/{id}')


@app.route('/resultsAQ/<id>')
def resultsAQ(id):
    entity = getEntity(id)
    iem, target = entity[2:4]
    filterCount, eqres, mode = entity[6:9]

    gekiyabaa = gekiyaba(target)
    if gekiyabaa:
        # check if gekiyaba mode !!!
        target = FRDict[target]
    print('choix:', iem, target)

    # ======settings======
    if eqres == 'yes':
        concha_interference = False
    else:
        concha_interference = True

    if mode == 'standard':
        config = {
            'filters':
            [{'type': 'LOW_SHELF', 'fc': 105.0}, {'type': 'HIGH_SHELF', 'fc': 10000.0}] +
            [{'type': 'PEAKING'}] * (filterCount-2)}
        filterTypes = ['LSQ', 'HSC'] + ['PK'] * (filterCount-2)
    elif mode == 'moondrop':
        config = PEQ_CONFIGS['MOONDROP_FREE_DSP']
        filterTypes = ['PK'] * 9

    # ======autoEQ======
    frequencies, \
        gains, \
        newGains, \
        Tgains, \
        results, \
        IIR = autoEQ(iem,
                     target,
                     config,
                     concha_interference,
                     filterTypes,
                     gekiyabaa)

    # ======return======
    return render_template('index.html',
                           FRList=FRList,
                           targetList=targetList,
                           result="aouiiii",
                           results=results,
                           iem=iem,
                           target=target,
                           iir=IIR,
                           # pour graph:
                           frequencies=frequencies,
                           gains=gains,
                           newgains=newGains,
                           Tgains=Tgains,
                           id=id
                           )


@app.route('/wavelet/<id>')
def wavelet(id):
    entity = getEntity(id)
    # entity: 0:id, 1:raw, 2:iem, 3:target, 4:datetime
    path = f'generated_files/{entity[2]} [{entity[3]}] (Wavelet,Equalizer APO).txt'
    return send_file(path, as_attachment=True)


@app.route('/poweramp/<id>')
def poweramp(id):
    entity = getEntity(id)
    path = f'generated_files/{entity[2]} [{entity[3]}] (Poweramp).json'
    return send_file(path, as_attachment=True)


@app.route('/parametric/<id>')
def parametric(id):
    entity = getEntity(id)
    path = f'generated_files/{entity[2]} [{entity[3]}] (Parametric EQ).txt'
    return send_file(path, as_attachment=True)


@app.route('/lochbaum/<id>', methods=['GET', 'POST'])
def lochbaum(id):

    # ======store target an IEM from form======
    EQ.iem = str(request.form.get('iem'))
    EQ.rawiem = FRDict[EQ.iem]
    EQ.target = str(request.form.get('target'))
    EQ.gekiyaba = gekiyaba(EQ.target)
    if EQ.gekiyaba:
        # check if gekiyaba mode !!!
        EQ.target = FRDict[EQ.target]
    print('choix:', EQ.iem, EQ.target)

    # ======settings=====
    EQ.filterCount = int(request.form.get('filterCount'))

    EQ.frequencies, EQ.gains, Tgains, iemLoch, targetLoch = getLochbaum(
        EQ.rawiem, EQ.target, EQ.gekiyaba)

    # ======return======
    return render_template('lochbaum.html', iemLoch=iemLoch, targetLoch=targetLoch, filterCount=EQ.filterCount, id=id)


@app.route('/process-data', methods=['POST'])
def process_data():
    EQ.results = request.json['data']
    EQ.newGains, EQ.deltaGains = getNewGain(
        EQ.frequencies, EQ.gains, EQ.results)


    # ======Create files======
    createParaEQFile(EQ.iem, EQ.target, EQ.results)
    createPAFile(EQ.iem, EQ.target, EQ.results)
    iemAQ = FrequencyResponse(
        name="temp", frequency=EQ.frequencies, raw=EQ.gains, equalization=EQ.deltaGains)
    # to create wavelet file
    createWaveletFile(EQ.iem, EQ.target, iemAQ)

    # ======Save in Database======
    log(FRDict[EQ.iem], EQ.iem, EQ.target, 'locbaum',
        EQ.filterCount, 'no', '', results=EQ.results)
    # ======return======
    return redirect("/")


@app.route('/resultsLO/<id>')
def results2(id):
    entity = getEntity(id)

    # ======get all data======
    iem, target = entity[2:4]
    rawiem = FRDict[iem]
    results = json.loads(entity[9].replace("'",'"'))
    gekiyabaa = gekiyaba(target)
    IIR = paraToIIR(results)
    frequencies, gains, Tgains, iemLoch, targetLoch = getLochbaum(
        rawiem, target, gekiyabaa)

    newGains, deltaGains = getNewGain(frequencies, gains, results)
    # ======return======
    return render_template('index.html',
                           FRList=FRList,
                           targetList=targetList,
                           result="aouiiii",
                           results=results,
                           iem=iem,
                           target=target,
                           iir=IIR, \
                           # pour graph:
                           frequencies=frequencies, \
                           gains=gains, \
                           newgains=newGains, \
                           Tgains=Tgains,
                           id=id
                           )


@app.route('/moondrop', methods=['GET', 'POST'])
def moondrop():
    if request.method == 'POST':
        f = request.files['file']
        path = f'uploads/{f.filename}'
        f.save(path)
        results = getParaEQ2(path)

        frequencies = list(FrequencyResponse(name='temp').frequency)
        # len: 695
        gains = [60.0]*695
        newGains, deltaGains = getNewGain(frequencies, gains, results)
        base = FrequencyResponse(name='idk', frequency=frequencies, raw=gains)
        base.interpolate()
        base.center()
        target = FrequencyResponse(
            name='uwu', frequency=frequencies, raw=newGains)
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
        peqs = base.optimize_parametric_eq(config, 44100)[0].filters

        string = ''
        i = 0
        for filt in peqs:
            i += 1
            string += f'Filter {i}: ON PK Fc {int(filt.fc)} Hz Gain {round(filt.gain,1)} dB Q {round(filt.q,1)}\n'
        path = f'generated_files/{f.filename}'
        open(path, 'w').write(string)
        return send_file(path, as_attachment=True)

    return render_template('moondrop.html')


@app.route('/iir', methods=['GET', 'POST'])
def iir():
    result = None
    string = ''
    if request.method == 'POST':
        f = request.files['file']
        path = f'uploads/{f.filename}'
        f.save(path)
        results = getParaEQ2(path)
        string = paraToIIR(results)
        result = 'aouiiiiii'
    return render_template('iir.html', result=result, string=string)


if __name__ == "__main__":
    app.run(debug=True)
