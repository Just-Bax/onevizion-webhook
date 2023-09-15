from flask import Flask, jsonify, request
import datetime
import httplib2
import json

app = Flask(__name__)

def make_data(json_data):
    data = {"fields": {}, "parents": [], "childs": []}
    filter_data = {}; parents = {}; childs = {}
    relations =  {"parents": parents, "childs": childs}
    for item in json_data:
        if ":" in item:
            action, type_field = map(str, item.split(":"))
            type, field = map(str, type_field.split("."))
            if action == "SET" and type == "T":
                data["fields"][field] = json_data[item]
            elif action == "CHECK":
                if type == "T":
                    filter_data[field] = json_data[item]
                elif type.startswith("P-"):
                    parent = type.split("-")[1]
                    if parent not in parents: parents[parent] = {}
                    parents[parent][field] = json_data[item]
                elif type.startswith("C-"):
                    child = type.split("-")[1]
                    if child not in childs: childs[child] = {}
                    childs[child][field] = json_data[item]
    for relation_name, relation_dict in relations.items():
        for relation_ttype, relation_filter in relation_dict.items():
            relation_data = {"trackor_type": relation_ttype, "filter": relation_filter}
            data[relation_name].append(relation_data)
    return data, filter_data

def create(token: str, data: dict, domain: str, ttype: str) -> tuple:
    headers = {
        'accept': 'application/json',
        'Content-Type': 'text/plain',
        'Authorization': f'Basic {token}'
    }
    http = httplib2.Http()
    url = f'https://{domain}/api/v3/trackor_types/{ttype}/trackors'
    response, content = http.request(url, method='POST', headers=headers, body=json.dumps(data))
    if response.status in [200, 201]: return True, json.loads(content.decode('utf-8'))
    return False, content.decode('utf-8')

def update(token: str, data: dict, domain: str, ttype: str, filter: dict) -> tuple:
    headers = {
        'accept': 'application/json',
        'Content-Type': 'text/plain',
        'Authorization': f'Basic {token}'
    }
    http = httplib2.Http()
    params = '?' + '&'.join(f'{key}={value}' for key, value in filter.items())
    url = f'https://{domain}/api/v3/trackor_types/{ttype}/trackors'
    if filter: url += params
    response, content = http.request(url, method='PUT', headers=headers, body=json.dumps(data))
    if response.status in [200, 201]: return True, json.loads(content.decode('utf-8'))
    return False, content.decode('utf-8')

@app.route("/create", methods=["POST"])
def create_post():
    try:
        json_data = request.get_json()
        message = ""; success = False
        if ("TYPE" and "TOKEN" and "DOMAIN") in json_data:
            data, filter = make_data(json_data)
            success, result = create(json_data["TOKEN"], data, json_data["DOMAIN"], json_data["TYPE"])
            message = result
        else: message = "Insufficient data for queries"
    except Exception as exp: message = str(exp)
    now = datetime.datetime.now()
    print(f"{now} - Success: {success}, Message: {message}")
    return jsonify({"status": success, "message": message})

@app.route("/update", methods=["POST"])
def update_post():
    try:
        json_data = request.get_json()
        message = ""; success = False
        if ("TYPE" and "TOKEN" and "DOMAIN") in json_data:
            data, filter = make_data(json_data)
            success, result = update(json_data["TOKEN"], data, json_data["DOMAIN"], json_data["TYPE"], filter)
            message = result
        else: message = "Insufficient data for queries"
    except Exception as exp: message = str(exp)
    now = datetime.datetime.now()
    print(f"{now} - Success: {success}, Message: {message}")
    return jsonify({"status": success, "message": message})

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)