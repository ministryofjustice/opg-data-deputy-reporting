from chalice import Chalice

app = Chalice(app_name="sirius_documents")


@app.route("/reports/{id}", methods=["GET"])
def get_reports(id):
    return {"get_reports": id}


@app.route("/reports/{id}/supportingdocuments", methods=["POST"])
def post_supportingdocs(id):
    return {"hello": id}


@app.route("/clients/{caseref}/reports", methods=["POST"])
def post_reports(caseref):
    return {"hello": caseref}
