import requests
import datetime
import logging

from requests import exceptions


def createVoltSession(token=None, tenantName=None):
    now = datetime.datetime.now()
    apiToken = "APIToken {0}".format(token)
    s = requests.Session()
    s.headers.update({'Authorization': apiToken})
    urlBase = "https://{0}.console.ves.volterra.io".format(tenantName)
    create = {
        'operation': 'createVoltSession',
        'status': 'success',
        'message': 'voltSession created',
        'time': now.strftime("%m/%d/%Y, %H:%M:%S")
    }
    session = {'session': s, 'urlBase': urlBase, 'lastOp': create}
    return session


def getQuota(namespace="system", s=None):
    url = s['urlBase'] + \
        "/api/web/namespaces/{0}/quota/usage".format(namespace)
    # try:
    resp = s['session'].get(url)
    resp.raise_for_status()
    return resp.json()
    # except requests.exceptions.RequestException as e:
    #     raise exceptions
