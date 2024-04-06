from flask import Flask, render_template, request, send_file, redirect
from app.getFRoT import getFRoTList
from app.getEQ import getParaEQ, getIIRString
from app.computeFilters import getAllFR
from app.cleanData import normalize
from app.dynamicAutoEQ import autoEQ
from fractions import Fraction
from autoeq.constants import PEQ_CONFIGS

app = Flask(__name__)
FRDict = getFRoTList('frequency_responses')
# dictionnaire avec en clé le model et en valeur le nom du fichier brut
FRList = list(FRDict.keys())
class Parameters():
    iem = ""
    rawiem = ""
    target = ""


@app.route('/', methods=['GET', 'POST'])
def index():
    targetList = list(getFRoTList('targets').keys())
    return render_template('index.html', FRList=FRList, targetList=targetList, result=None)


@app.route('/results', methods=['GET', 'POST'])
def results():
    targetList = list(getFRoTList('targets').keys())

    Parameters.iem = str(request.form.get('iem'))
    Parameters.target = str(request.form.get('target'))
    print('choix:', Parameters.iem, Parameters.target)

    if Parameters.iem == 'None' or Parameters.target == 'None':
            #pour s'assurer que l'utilisateur a bien choisi quelque chose
            return redirect('/')
    Parameters.rawiem = FRDict[Parameters.iem]

    filterCount = int(request.form.get('filterCount'))
    if str(request.form.get('EQres')) == 'Yes':
        concha_interference = True
    else:
        concha_interference = False

    if str(request.form.get('EQabobe10k')) == 'Yes':
        treble_f_lower = float(19000)
    else:
        treble_f_lower = float(10000)

    mode = str(request.form.get('mode'))
    if mode == 'Standard':
        config = {
            'filters': [{'type': 'PEAKING'}] * filterCount}
    elif mode == 'Moondrop Free DSP':
        config = PEQ_CONFIGS['MOONDROP_FREE_DSP']
    frequencies, gains, newgains, Tgains, paraEQ, iir = autoEQ(Parameters.iem,\
                                                               Parameters.target,\
                                                                config,\
                                                                concha_interference,\
                                                                treble_f_lower)
    Tgains = normalize(frequencies, newgains, Tgains)

    return render_template('index.html',
                           FRList=FRList,
                           targetList=targetList,
                           result="aouiiii",
                           paraEQ=paraEQ,
                           iem=Parameters.iem,
                           target=Parameters.target,
                           iir=iir, \
                           # pour graph:
                           frequencies=frequencies, \
                           gains=gains, \
                           newgains=newgains, \
                           Tgains=Tgains
                           )


@app.route('/wavelet')
def wavelet():
    path = f'generated_files\\{Parameters.iem} [{Parameters.target}] (Wavelet,Equalizer APO).txt'
    return send_file(path, as_attachment=True)


@app.route('/poweramp')
def poweramp():
    path = f'generated_files\\{Parameters.iem} [{Parameters.target}] (Poweramp).json'
    return send_file(path, as_attachment=True)


@app.route('/parametric')
def parametric():
    path = f'generated_files\\{Parameters.iem} [{Parameters.target}] (Parametric EQ).txt'
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
