import json
import pandas as pd
import numpy as np
from weasyprint import HTML, CSS 
import os
from flask import Flask, request, make_response
from dominate.tags import *
from dominate.util import raw
import base64

app = Flask(__name__)
port = int(os.environ.get('PORT', 3000))

@app.route('/')
def hello():
   return "Hello!"

@app.route('/pdf/', methods=('GET', 'POST'))
def pdf_gen():
    text = request.args.get('text')
    ar = request.args.get('area')    
    res_json = request.json
    skill_data = []
    data = json.loads(res_json)
    table_values = []

    point1_data = data['Point1']
    if point1_data['strErr'] == "":
        items_num = text + " " + ar + " " + str(point1_data['arrData'][0]['sSummary'][0]['intCount']) + " skills are found"
        point1_skills = point1_data['arrData'][0]['sSummary'][1]['arrTerm']
        for skill in point1_skills:
            value = round(skill['dblQuota'], 3)
            skill_data.append(dict(Skill=skill['strTerm'], Percent=value ))             
    else:
        items_num = text + " " + ar + " " + point1_data['strErr']

    # extract headers from input data
    table_headers = [headers.title() for headers in skill_data[0]]

    # extract table data from input data
    if skill_data:  
        table_values = [str(v) for d in skill_data for k, v in d.items()]

    # convert input data to HTML
    a = np.array(table_values)
    df = pd.DataFrame(a.reshape(-1, len(table_headers)), columns=table_headers)
       
    html_string = df.to_html(index=False)
    html_string = str(html(head(h2("Skills analyzer"), h3(items_num)), body(raw(html_string))))
    
    html_doc = HTML(string=html_string)
    pdf_data = html_doc.write_pdf(stylesheets=[CSS('./css/report.css')])
    pdf_encoded = base64.b64encode(pdf_data)
    response = make_response(pdf_encoded)
    #return pdf_encoded, 200
    return response
   
if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=port)
    app.run(host='localhost', port=port)
