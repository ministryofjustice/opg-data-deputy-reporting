import connexion


def createDocument():
    return 'createDocument'



sirius_server = connexion.App(__name__)
sirius_server.add_api('sirius_public_api.yml')
sirius_server.run(port=4343)


