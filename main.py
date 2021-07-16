import os
import logging

from volterra_helpers import createVoltSession, getQuota
from quota_helpers import getQuotaViolations

logging.basicConfig(level=logging.INFO)


def main():
    # Ensure the required environment variables are set
    required_vars = {'VOLT_TENANT_NAME': False,
                     'VOLT_TENANT_API_TOKEN': False}

    for v in required_vars:
        required_vars[v] = os.environ.get(v, False)

        if required_vars[v] == False:
            raise ValueError("A value must be provided for {0}".format(v))

    # create session for volterra API call
    session = createVoltSession(
        required_vars['VOLT_TENANT_API_TOKEN'], required_vars['VOLT_TENANT_NAME'])

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
    else:
        logging.info("No quota issues found")


if __name__ == "__main__":
    main()
