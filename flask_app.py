from flask import Flask, render_template, request,send_file
from app.getFRoT import getFRoTList
from app.getEQ import getParaEQ,getIIRString
app = Flask(__name__)

class Parameters():
    iem = ""
    rawiem = ""
    target = ""

@app.route('/', methods=['GET', 'POST'])

def index():
    FRList = list(getFRoTList('frequency_responses').keys())
    targetList = list(getFRoTList('presets').keys())
    return render_template('index.html',FRList=FRList, targetList=targetList,result=None)

@app.route('/results', methods=['GET', 'POST'])

def results():
    FRDict = getFRoTList('frequency_responses') #dictionnaire avec en clé le model et en valeur le nom du fichier brut
    targetList = list(getFRoTList('presets').keys())
    
    Parameters.iem = str(request.form.get('select1'))
    Parameters.rawiem = FRDict[Parameters.iem]
    Parameters.target = str(request.form.get('select2'))
    print(Parameters.iem,Parameters.target)
    
    paraEQ = getParaEQ(Parameters.rawiem,Parameters.target)
    iir = getIIRString(Parameters.rawiem,Parameters.target)
    return render_template('index.html',FRList=list(FRDict.keys()), targetList=targetList,result="aouiiii", paraEQ=paraEQ, iem=Parameters.iem, target=Parameters.target, iir=iir)

@app.route('/wavelet')
def wavelet():
    path = f'presets\\{Parameters.target}\\Wavelet\\{Parameters.rawiem} [{Parameters.target}].txt'
    print(path)
    return send_file(path, as_attachment=True)

@app.route('/poweramp')
def poweramp():
    path = f'presets\\{Parameters.target}\\Poweramp\\{Parameters.rawiem} [{Parameters.target}].json'
    print(path)
    return send_file(path, as_attachment=True)

@app.route('/parametric')
def parametric():
    path = f'presets\\{Parameters.target}\\Parametric\\{Parameters.rawiem} [{Parameters.target}].txt'
    print(path)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)