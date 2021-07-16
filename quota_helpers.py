import json
import logging


def getQuotaViolations(quotas=None):
    # process the quota_usage value
    quotaViolations = []
    for key in quotas['quota_usage']:
        logging.debug("Processing {0} quota:".format(key))
        if not quota_within_threshold(quotas['quota_usage'][key]):
            quotaViolations.append(key)

    return quotaViolations


def quota_within_threshold(q=None, t=.9):
    # determine if the quota object is within the desired threshold

    limit = q['limit']['maximum']
    usage = q['usage']['current']

    logging.debug("limit: {0}, usage: {1}".format(limit, usage))

    # check if there are set limits on the quota
    # we don't worry about limits less than 0 or equal to 1
    if limit < 2:
        return True
    elif usage > (limit * t):
        return False
    else:
        return True
