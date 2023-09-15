from flask import Flask, jsonify, request
import datetime
import httplib2
import json

app = Flask(__name__)

def make_data(json_data):
    data = {"fields": {}, "parents": [], "childs": []}
    label 
    filter_data = {}; parents = {}; childs = {}
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
    for parent, parent_filter in parents.items():
        parent_data = {"trackor_type": parent, "filter": parent_filter}
        data["parents"].append(parent_data)
    for child, child_filter in childs.items():
        child_data = {"trackor_type": child, "filter": child_filter}
        data["childs"].append(child_data)
    return data, filter_data

def create(token: str, data: json, domain: str, ttype: str) -> json:
    headers = {
        'accept': 'application/json',
        'Content-Type': 'text/plain',
        'Authorization': f'Basic {token}'
    }
    http = httplib2.Http()
    url = f'https://{domain}/api/v3/trackor_types/{ttype}/trackors'
    response, content = http.request(url, method='POST', headers=headers, body=json.dumps(data))
    return json.loads(content.decode('utf-8'))

@app.route("/create", methods=["POST"])
def create_post():
    json_data = request.get_json()
    message = "DONE: "
    if ("TYPE" and "TOKEN" and "DOMAIN") in json_data:
        data, filter = make_data(json_data)
        result = create(json_data["TOKEN"], data, json_data["DOMAIN"], json_data["TYPE"])
        message += result["TRACKOR_KEY"]
    else: message = "Insufficient data for queries"
    now = datetime.datetime.now()
    print(f"{now} - Response: {message}")
    return jsonify({"message": message})

# if __name__ == "__main__":
    # app.run(host="0.0.0.0", debug=False)

json_data = {
    "TOKEN": "aXNmYW5fd2g6MTIzNDU2",
    "DOMAIN": "cloud-erp.onevizion.com",
    "TYPE": "WEBHOOK",
    "SET:T.W_NAME": "Test create",
    "CHECK:T.TRACKOR_KEY": "10033",
}
data, filter = make_data(json_data)
print(data)
print(filter)