import os
import logging

from requests.api import post

from volterra_helpers import createVoltSession, getQuota
from quota_helpers import getQuotaViolations
from teams_helpers import postQuotaViolations

logging.basicConfig(level=logging.DEBUG)


def main():
    # Ensure the required environment variables are set
    required_vars = {'VoltTenantName': False,
                     'VoltTenantApiToken': False}

    for v in required_vars:
        required_vars[v] = os.environ.get(v, False)

        if required_vars[v] == False:
            raise ValueError("A value must be provided for {0}".format(v))

    # create session for volterra API call
    session = createVoltSession(
        required_vars['VoltTenantApiToken'], required_vars['VoltTenantName'])

    # get quota
    quotas = getQuota("system", session)
    # logging.debug(quotas)

    quotaViolations = getQuotaViolations(quotas)

    logging.debug(quotaViolations)

    # display the results
    if len(quotaViolations) > 0:
        logging.info(
            "The following quota objects are above the desired threshold:")
        for q in quotaViolations:
            logging.info(q)

        # post to teams channel
        webhookUrl = os.environ.get('TeamsWebhookUrl', False)
        if(webhookUrl):
            postQuotaViolations(webhookUrl, quotaViolations,
                                required_vars['VoltTenantName'])

    else:
        logging.info("No quota issues found")


if __name__ == "__main__":
    main()
