"""tunneling URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

import json
import logging.config
from logging.handlers import SMTPHandler
import os
from subprocess import Popen, PIPE

from tunneling import views
from tunneling.models import Tunnels

urlpatterns = [
    path("api/health", views.Health.as_view(), name="health"),
    path("api/port", views.Port.as_view(), name="port"),
    path("api/loglevel/<str:loglevel>", views.LogLevel.as_view()),
    path("api/available/<str:node>", views.Available.as_view()),
    path("api/remote/<str:node>/", views.Remote.as_view(), name="remote"),
    path("api/tunnel/<str:servername>/", views.Tunnel.as_view(), name="tunnel"),
    path("api/tunnel/<str:servername>/<str:node>/<str:hostname>/<int:port1>/<int:port2>/", views.Tunnel.as_view(), name="tunnel"),
]


def setUpLogger():
    # Who should receive the emails if an error or an exception occures?
    mail_env = os.environ.get('MAILRECEIVER', '')
    if mail_env:
        mail = mail_env.split()
    else:
        mail = []

    logger = logging.getLogger('Tunneling')
    # In trace will be sensitive information like tokens
    logging.addLevelName(5, "TRACE")
    def trace_func(self, message, *args, **kws):
        if self.isEnabledFor(5):
            # Yes, logger takes its '*args' as 'args'.
            self._log(5, message, args, **kws)
    logging.Logger.trace = trace_func
    mail_handler = SMTPHandler(
        mailhost=os.environ.get('MAILHOST'),
        fromaddr=os.environ.get('MAILFROM'),
        toaddrs=mail,
        subject=os.environ.get('MAILSUBJECT')
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(filename)s ( Line=%(lineno)d ): %(message)s'
    ))
    logging.config.fileConfig(os.environ.get('LOGGINGCONF'))
    logger.addHandler(mail_handler)

def setUpTunnels():
    log = logging.getLogger('Tunneling')
    uuidcode = 'StartUp'
    log.info(f"uuidcode={uuidcode} - Start tunnels that are still in the database")
    tunnels = Tunnels.objects.all()
    for tunnel in tunnels:
        try:
            log.info(f"uuidcode={uuidcode} Start Tunnel for {tunnel.servername} {tunnel.node} {tunnel.hostname} {tunnel.port1} {tunnel.port2}")
            cmd = ['lsof', '-t' , f'-i:{tunnel.port1}']
            log.trace("uuidcode={uuidcode} Check if something is listening: {cmd}".format(uuidcode=uuidcode, cmd=' '.join(cmd)))
            p = Popen(cmd, stderr=PIPE, stdout=PIPE)
            p.communicate()
            return_code = p.returncode
            log.trace(f"uuidcode={uuidcode} Return Code: {return_code}")
            if return_code == 0:
                log.error(f"uuidcode={uuidcode} Something is already listening on port {tunnel.port1}")
                continue
            elif return_code == 1:
                pass
            else:
                log.error(f"uuidcode={uuidcode} lsof finished with non expected exit code: {return_code}")
                continue
            return_code = views.setup_tunnel(uuidcode, tunnel.node, tunnel.hostname, tunnel.port1, tunnel.port2)
            log.trace("uuidcode={uuidcode} Return Code: {return_code}")
            if return_code == 0:
                log.info(f"uuidcode={uuidcode} Rebuilded tunnel")                
            else:
                log.error(f"uuidcode={uuidcode} Tunnel rebuild failed for {tunnel.servername} {tunnel.node} {tunnel.hostname} {tunnel.port1} {tunnel.port2}")
        except:
            log.exception(f"uuidcode={uuidcode} Tunnel rebuild failed for {tunnel.servername} {tunnel.node} {tunnel.hostname} {tunnel.port1} {tunnel.port2}")
    log.info(f"uuidcode={uuidcode} Tunnel rebuild finished")

def setUp():
    setUpLogger()
    setUpTunnels()

setUp()

