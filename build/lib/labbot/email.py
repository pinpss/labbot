"""
decorates function to send email on start and finish/failure
"""
from boltons.funcutils import wraps
import smtplib
import yaml
import os


def emaildec(func, config_file="~/passepartout/config/passepartout/emaildec.yaml"):
    """decorator which sends email on various func events

    Parameters
    ----------
    func : function
        function for which we'd like email logs
    config_file : str
        location of yaml config containing email login info

    Returns
    -------
    func : function
        decorated to handle emails

    Notes
    -----
    This sends an email when:

    1. func starts
    2. func fails
    3. func finishes
    """

    @wraps(func)
    def nfunc(*args, **kwds):

        cf = os.path.expanduser(config_file)

        _send_email(func, "started", cf, *args, **kwds)

        try:
            res = func(*args, **kwds)
        except Exception as e:
            _send_email(func, "failed with error %s" % str(e),
                        cf, *args, **kwds)
            raise e

        _send_email(func, "finished", cf, *args, **kwds)

        return res

    return nfunc


def _send_email(func, log, config_file, *args, **kwds):
    """internal function for sending log updates to a specified email"""

    with open(config_file, "r") as fd:
        config = yaml.load(fd)

    message = ("From: %s <%s> \n"
               "%s \n"
               "%s") % (func.__name__, config["femail"], log,
                        str((args, kwds)))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(config["femail"], config["password"])

    server.sendmail(config["femail"], config["temail"], message)
    server.quit()
