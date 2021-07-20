import datetime
import logging
import os

from volterra_helpers import createVoltSession, getQuota
from quota_helpers import getQuotaViolations
from teams_helpers import postQuotaViolations

import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

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
