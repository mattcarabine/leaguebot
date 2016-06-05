import datetime


def epoch_to_datetime(epoch):
    return datetime.datetime.fromtimestamp(epoch).strftime('%c')