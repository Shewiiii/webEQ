from flask import Flask, render_template, request, send_file, redirect, make_response
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
import datetime


app = Flask(__name__)

FRDict = getFRoTDict('frequency_responses')
# dictionnaire avec en clé le model et en valeur le nom du fichier brut
targetList = list(getFRoTDict('targets').keys())
FRList = list(FRDict.keys())
rawFRList = list(FRDict.values())


def gekiyaba(target: str):
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

    # ======read cookies======
    seliem = request.cookies.get('iem')
    gekiyaba = request.cookies.get('gekiyaba')
    if seliem == None and gekiyaba == None:
        seliem = ''
        gekiyaba = 'False'
    print("selected iem:", seliem)
    print("gekiyaba:", gekiyaba)

    response = make_response(
        render_template(
            'index.html',
            FRList=FRList,
            targetList=targetList,
            result=None,
            seliem=seliem,
            gekiyaba=gekiyaba,
            rawFRList=rawFRList
        )
    )
    # ======return======
    return response


@app.route('/processAQ', methods=['GET', 'POST'])
def processAQ():
    id = get_free_id()

    # ======put data in the database======
    iem = str(request.form.get('iem'))
    if iem == '':
        return redirect('/')
    rawiem = FRDict[iem]
    target = str(request.form.get('target'))
    algo = 'default'
    filterCount = int(request.form.get('filterCount'))
    mode = str(request.form.get('mode'))
    eqres = str(request.form.get('EQres'))  # basically 'yes', or 'no'

    # ======gekiyaba!======
    gekiyabaa = gekiyaba(target)
    if gekiyabaa:
        target = FRDict[target]

    # ======Store in db======
    log(rawiem, iem, target, algo, filterCount, eqres, mode)

    # ======set cookies======
    response = make_response(
        redirect(f'/results/{id}')
    )
    response.set_cookie(
        'iem',
        iem,
        expires=datetime.datetime.now() + datetime.timedelta(days=30)
    )
    response.set_cookie(
        'gekiyaba',
        str(gekiyabaa),
        expires=datetime.datetime.now() + datetime.timedelta(days=30)
    )

    # ======return======
    return response


@app.route('/saveChart', methods=['POST'])
def saveChart():
    data = request.json['data']
    imgData = data[0]
    id = data[1]
    createChartImage(imgData, id)
    return redirect("/")


@app.route('/chart/<id>', methods=['GET', 'POST'])
def chart(id):
    path = f'generated_files/chart{id}.png'
    return send_file(path)


@app.route('/results/<id>')
def results(id):
    entity = getEntity(id)

    # ======get all data======
    (rawiem,
     iem,
     target,
     algo,
     processed,
     filterCount,
     eqres,
     mode,
     results
     ) = entity[1:]
    if algo == 'default':
        return resultsAQ(id, rawiem, iem, target, algo, processed, filterCount, eqres, mode)
    elif algo == 'lochbaum':
        return resultsLO(id, rawiem, iem, target, algo, processed, results)
    else:
        return redirect('/')


def resultsAQ(
    id,
    rawiem,
    iem,
    target,
    algo,
    processed,
    filterCount,
    eqres,
    mode
):
    # ======if target is None..======
    if target == 'None' or target == '':
        response = make_response(redirect('/'))
        response.set_cookie(
            'iem',
            iem,
            expires=datetime.datetime.now() + datetime.timedelta(days=30)
        )
        return response

    # ======gekiyaba !!======
    gekiyabaa = gekiyaba(target)

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
    (
        frequencies,
        gains,
        newGains,
        Tgains,
        results,
        IIR
    ) = autoEQ(
        iem,
        target,
        config,
        concha_interference,
        filterTypes,
        gekiyabaa
    )

    # ======return======
    return render_template(
        'index.html',
        FRList=FRList,
        targetList=targetList,
        result="aouiiii",
        results=results,
        iem=iem,
        target=target,
        iir=IIR,
        frequencies=frequencies,
        gains=gains,
        newGains=newGains,
        Tgains=Tgains,
        id=id,
        algo=algo,
        processed=processed
    )


def resultsLO(
    id,
    rawiem,
    iem,
    target,
    algo,
    processed,
    results
):

    # ======get all data======
    results = json.loads(results.replace("'", '"'))
    gekiyabaa = gekiyaba(target)
    IIR = paraToIIR(results)
    (frequencies,
     gains,
     Tgains,
     _,
     _
     ) = getLochbaum(
        rawiem,
        target,
        gekiyabaa
    )

    newGains, deltaGains = getNewGain(frequencies, gains, results)
    # ======return======
    return render_template(
        'index.html',
        FRList=FRList,
        targetList=targetList,
        result="aouiiii",
        results=results,
        iem=iem,
        target=target,
        iir=IIR,
        frequencies=frequencies,
        gains=gains,
        newGains=newGains,
        Tgains=Tgains,
        id=id,
        algo=algo,
        processed=processed
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


@app.route('/processLO', methods=['GET', 'POST'])
def processLO():

    id = get_free_id()

    # ======store target an IEM from form======
    EQ.iem = str(request.form.get('iem'))
    if EQ.iem == '':
        return redirect('/')
    EQ.rawiem = FRDict[EQ.iem]
    EQ.target = str(request.form.get('target'))

    # ======if target is None..======
    if EQ.iem == 'None':
        response = make_response(redirect('/'))
        response.set_cookie(
            'iem',
            EQ.iem,
            expires=datetime.datetime.now() + datetime.timedelta(days=30)
        )
        return response

    # ======check if gekiyaba mode !!======
    EQ.gekiyaba = gekiyaba(EQ.target)

    if EQ.gekiyaba:
        EQ.target = FRDict[EQ.target]
    print('choix:', EQ.iem, EQ.target)

    # ======settings=====
    EQ.filterCount = int(request.form.get('filterCount'))

    EQ.frequencies, EQ.gains, Tgains, iemLoch, targetLoch = getLochbaum(
        EQ.rawiem, EQ.target, EQ.gekiyaba)

    # =====setting cookies========
    response = make_response(
        render_template(
            'lochbaum.html',
            iemLoch=iemLoch,
            targetLoch=targetLoch,
            filterCount=EQ.filterCount,
            id=id
        )
    )
    response.set_cookie(
        'iem',
        EQ.iem,
        expires=datetime.datetime.now() + datetime.timedelta(days=30)
    )
    response.set_cookie(
        'gekiyaba',
        str(EQ.gekiyaba),
        expires=datetime.datetime.now() + datetime.timedelta(days=30)
    )

    # ======return======
    return response


@app.route('/process-data', methods=['POST'])
# FOR LOCHBAUM OBV
def process_data():
    EQ.results = request.json['data']
    EQ.newGains, EQ.deltaGains = getNewGain(
        EQ.frequencies, EQ.gains, EQ.results)

    # ======Create files======
    createParaEQFile(EQ.iem, EQ.target, EQ.results)
    createPAFile(EQ.iem, EQ.target, EQ.results)
    iemAQ = FrequencyResponse(
        name="temp",
        frequency=EQ.frequencies,
        raw=EQ.gains,
        equalization=EQ.deltaGains
    )
    # to create wavelet file
    createWaveletFile(EQ.iem, EQ.target, iemAQ)

    # ======Save in Database======
    log(FRDict[EQ.iem], EQ.iem, EQ.target, 'lochbaum',
        EQ.filterCount, 'no', '', results=EQ.results)
    # ======return======

    return redirect("/")


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
            string += (f'Filter {i}: ON PK Fc {int(filt.fc)} Hz Gain '
                       f'{round(filt.gain,1)} dB Q {round(filt.q,1)}\n')
        path = pathlib.Path(
            __file__
        ).parents[0] / f'generated_files/ {f.filename}'
        open(path, 'w').write(string)
        return send_file(path, as_attachment=True)

    return render_template('moondrop.html')


@app.route('/iir', methods=['GET', 'POST'])
def iir():
    result = None
    string = ''
    if request.method == 'POST':
        f = request.files['file']
        path = pathlib.Path(
            __file__
        ).parents[0] / f'generated_files/ {f.filename}'
        f.save(path)
        results = getParaEQ2(path)
        string = paraToIIR(results)
        result = 'aouiiiiii'
    return render_template('iir.html', result=result, string=string)


if __name__ == "__main__":
    app.run(debug=True)
