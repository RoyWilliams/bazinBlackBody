""""
Running the BazinBlackBody fit on an ZTF alert read from a file
"""
import json

# Read the file
objectId = 'ZTF24absojni'
file = 'sample_alert/%s.json' % objectId
alert = json.loads(open(file).read())

# Run the fitting engine
import BBBEngine
BE = BBBEngine.BBB('ZTF', verbose=True)
(dicte, dictb) =  BE.make_fit(alert)
if dicte: 
    BE.plot(alert, dicte, 'image/%s_e.png'%objectId)
if dictb: 
    BE.plot(alert, dictb, 'image/%s_b.png'%objectId)
