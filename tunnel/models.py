from django.db import models

import logging
import os

from subprocess import Popen, check_output, STDOUT, CalledProcessError, PIPE

log = logging.getLogger("Tunnel")

def setup_connection(uuidcode, connection):
    # first check if ssh connection to the node is up
    cmd_check = ['timeout', os.environ.get('SSHTIMEOUT', "3"), 'ssh', '-F',  os.environ.get('SSHCONFIGFILE', '~/.ssh/config'), '-O', 'check', connection]
    log.trace("uuidcode={uuidcode} - Run Cmd: {cmd}".format(uuidcode=uuidcode, cmd=' '.join(cmd_check)))
    p_check = Popen(cmd_check, stderr=PIPE, stdout=PIPE)
    p_check.communicate()
    exit_code = p_check.returncode 
    log.trace(f"uuidcode={uuidcode} - Exit_code: {exit_code}")
    if exit_code == 255:
        cmd_connect = ['timeout', os.environ.get('SSHTIMEOUT', "3"), 'ssh', '-F',  os.environ.get('SSHCONFIGFILE', '~/.ssh/config'), connection]
        log.debug("uuidcode={uuidcode} - Run Cmd: {cmd}".format(uuidcode=uuidcode, cmd=' '.join(cmd_connect)))
        p_connect = Popen(cmd_connect, stderr=PIPE, stdout=PIPE)
        p_connect.communicate()
        exit_code = p_connect.returncode 
        log.debug(f"uuidcode={uuidcode} - Exit_code: {exit_code}")
    if exit_code != 0:
        raise Exception(f"uuidcode={uuidcode} - Could not connect to {connection}")


class Tunnels(models.Model):
    servername = models.TextField(null=False, max_length=300)
    system = models.TextField(null=False, max_length=20)
    node = models.TextField(null=False, max_length=23)
    hostname = models.TextField(null=False, max_length=32)
    port1 = models.IntegerField(null=False)
    port2 = models.IntegerField(null=False)
    date = models.DateTimeField(auto_now=True)

    def is_running(self, uuidcode):
        log.trace("uuidcode={uuidcode} Tunnel: {servername};{node};{hostname};{port1};{port2};{date}".format
            (
                uuidcode=uuidcode,
                servername=self.servername,
                node=self.node,
                hostname=self.hostname,
                port1=self.port1,
                port2=self.port2,
                date=self.date
            )    
        )
        cmd = ['sh', os.environ.get('CHECKPORTSCRIPT', '~/check_port.sh'), str(self.port1)]
        log.trace("uuidcode={uuidcode} Check if something is listening: {cmd}".format(uuidcode=uuidcode, cmd=' '.join(cmd)))
        p = Popen(cmd, stderr=PIPE, stdout=PIPE)
        p.communicate()
        return_code = p.returncode
        log.trace(f"uuidcode={uuidcode} Return Code: {return_code}")
        if return_code == 0:
            return True
        elif return_code == 1:
            return False
        raise Exception(f"check_port finished with non expected exit code: {return_code}")
    
    def stop(self, uuidcode):
        setup_connection(uuidcode, 'tunnel_{}'.format(self.node))
        cmd = ['timeout' , os.environ.get('SSHTIMEOUT', "3"), 'ssh', '-F', os.environ.get('SSHCONFIGFILE', '~/.ssh/config'), '-O', 'cancel', 'tunnel_{}'.format(self.node), '-L', '0.0.0.0:{}:{}:{}'.format(self.port1, self.hostname, self.port2)]
        log.trace("uuidcode={uuidcode} Delete tunnel with: {cmd}".format(uuidcode=uuidcode, cmd=' '.join(cmd)))
        p = Popen(cmd, stderr=PIPE, stdout=PIPE)
        p.communicate()
        return_code = p.returncode
        log.trace(f"uuidcode={uuidcode} Return Code: {return_code}")
        if return_code != 0:
            log.error(f"ssh finished with non expected exit code: {return_code}")
            return False
        return True


    def setup_tunnel(uuidcode, node, hostname, port1, port2):
        setup_connection(uuidcode, f'tunnel_{node}')
        cmd = ['timeout', os.environ.get('SSHTIMEOUT', "3"), 'ssh', '-F', os.environ.get('SSHCONFIGFILE', '~/.ssh/config'), '-O', 'forward', f'tunnel_{node}', '-L', f'0.0.0.0:{port1}:{hostname}:{port2}']
        log.trace("uuidcode={uuidcode} Create tunnel with: {cmd}".format(uuidcode=uuidcode, cmd=' '.join(cmd)))
        p = Popen(cmd, stderr=PIPE, stdout=PIPE)
        p.communicate()
        return_code = p.returncode
        return return_code
