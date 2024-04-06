from flask import Flask, render_template, request, send_file
from app.getFRoT import getFRoTList
from app.getEQ import getParaEQ, getIIRString
from app.computeFilters import getAllFR
from app.cleanData import normalize
from app.dynamicAutoEQ import autoEQ
app = Flask(__name__)


class Parameters():
    iem = ""
    rawiem = ""
    target = ""


@app.route('/', methods=['GET', 'POST'])
def index():
    FRList = list(getFRoTList('frequency_responses').keys())
    targetList = list(getFRoTList('targets').keys())
    return render_template('index.html', FRList=FRList, targetList=targetList, result=None)


@app.route('/results', methods=['GET', 'POST'])
def results():
    # dictionnaire avec en clé le model et en valeur le nom du fichier brut
    FRDict = getFRoTList('frequency_responses')
    targetList = list(getFRoTList('targets').keys())

    Parameters.iem = str(request.form.get('select1'))
    Parameters.rawiem = FRDict[Parameters.iem]
    Parameters.target = str(request.form.get('select2'))
    print(Parameters.iem, Parameters.target)

    frequencies, gains, newgains, Tgains, paraEQ, iir = autoEQ(
        Parameters.iem, Parameters.target)
    Tgains = normalize(frequencies, newgains, Tgains)

    return render_template('index.html',
                           FRList=list(FRDict.keys()),
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
