
import logging
import json
import requests


def postQuotaViolations(url, quotaViolations, tenant):
    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": "Quota Threshold Warning",
        "sections": [{
            "activityTitle": "Quota Threshold Warning",
            "activitySubtitle": "on {0} tenant".format(tenant),
            "activityImage": "https://teamsnodesample.azurewebsites.net/static/img/image9.png",
            "facts": [{
                "name": "Object above threshold",
                "value": "{0}".format(', '.join(quotaViolations))
            }],
            "markdown": "true"
        }]
    }

    logging.debug(payload)
    logging.debug(url)

    resp = requests.post(url, json.dumps(payload))

    logging.debug(resp.status_code)
    logging.debug(resp.text)
