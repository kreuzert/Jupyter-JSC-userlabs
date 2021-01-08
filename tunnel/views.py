import json

import os
import socket
from subprocess import Popen, check_output, STDOUT, CalledProcessError, PIPE

from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from rest_framework.views import APIView

from tunnel.models import Tunnels

# import the logging library
import logging

# Get an instance of a logger
log = logging.getLogger("Tunnel")


class LogLevel(APIView):
    def post(self, request, loglevel):
        try:
            log.trace(f"LogLevel POST: {loglevel}")
            if loglevel in ["NOTSET", "0"]:
                level = 0
            elif loglevel in ["TRACE", "5"]:
                level = 5
            elif loglevel in ["DEBUG", "10"]:
                level = 10
            elif loglevel in ["INFO", "20"]:
                level = 20
            elif loglevel in ["WARNING", "30"]:
                level = 30
            elif loglevel in ["ERROR", "40"]:
                level = 40
            elif loglevel in ["CRITICAL", "FATAL", "50"]:
                level = 50
            else:
                return HttpResponseBadRequest()
            log.setLevel(level)
            log.info(f"LogLevel switched to {level}")
            return HttpResponse(status=200)
        except:
            log.exception("Bugfix required")
            return HttpResponse(status=500)

class Health(APIView):
    def get(self, request):
        log.trace("Health check called")
        return HttpResponse(status=200)


class Port(APIView):
    def get(self, request):
        try:
            uuidcode = request.headers.get('uuidcode', '<no_uuidcode>')
            log.info(f"uuidcode={uuidcode} Get random port")
            """Get a single random port."""
            sock = socket.socket()
            while True:
                try:
                    sock.bind(("", 0))
                    port = sock.getsockname()[1]
                    tunnel = Tunnels.objects.filter(port1=port).first()
                    if tunnel is None:
                        break
                    else:
                        continue
                except OSError:
                    pass
                
            sock.close()
            log.trace(f"uuidcode={uuidcode} Return: {port}")
            return HttpResponse(f"{port}", status=200)
        except:
            log.exception("Bugfix required")
            return HttpResponse(status=500)

class Available(APIView):
    def get(self, request, node):
        try:
            uuidcode = request.headers.get('uuidcode', '<no_uuidcode>')
            log.info(f"uuidcode={uuidcode} Check if {node} is available")
            expected_output = os.environ.get("AVAILABLE_OUTPUT", "Jupyter-JSC: node is reachable")
            log.trace(f"uuidcode={uuidcode} expected output: {expected_output}")
            cmd = ['ssh', '-F', os.environ.get('SSHCONFIGFILE', '~/.ssh/config'), f"available_{node}"]
            try:
                log.trace("uuidcode={uuidcode} Command: {cmd}".format(uuidcode=uuidcode, cmd=' '.join(cmd)))
                output = check_output(cmd, stderr=STDOUT, timeout=int(os.environ.get('SSHTIMEOUT', 3)))  
                result = expected_output in output.decode("utf-8")          
                log.trace(f"uuidcode={uuidcode} Output: {output} -> {result}")
                if result:
                    response = HttpResponse("True", status=200)
                else:
                    response = HttpResponse("False", status=200)
            except CalledProcessError as e:
                log.exception(f"Error while checking availability for {node}")
                response = HttpResponse("False", status=200)
            return response
        except:
            log.exception("Bugfix required")
            return HttpResponse(status=500)
    
class Remote(APIView):
    def get(self, request, node):
        try:
            uuidcode = request.headers.get('uuidcode', '<no_uuidcode>')
            log.info(f"uuidcode={uuidcode} Get status of remote tunnel for {node}")
            cmd = ['timeout' , os.environ.get('SSHTIMEOUT', "3"), 'ssh', '-F', os.environ.get('SSHCONFIGFILE', '~/.ssh/config'), f'remote_{node}', 'status']
            log.trace("uuidcode={uuidcode} Check for Remote tunnel: {cmd}".format(uuidcode=uuidcode, cmd=' '.join(cmd)))
            p = Popen(cmd, stderr=PIPE, stdout=PIPE)
            p.communicate()
            return_code = p.returncode
            running_code = int(os.environ.get("REMOTE_OK_CODE", 217))
            non_running_code = int(os.environ.get("REMOTE_NOT_OK_CODE", 218))
            log.trace(f"uuidcode={uuidcode} Exit code: {return_code}")
            if return_code == running_code:
                response = HttpResponse("True", status=200)
            elif return_code == non_running_code:
                response = HttpResponse("False", status=200)
            else:
                raise Exception(f"Remote POST ssh for {node} cmd finished with exit code {return_code}")
            return response
        except:
            log.exception("Bugfix required")
            return HttpResponse(status=500)

    def post(self, request, node):
        try:
            uuidcode = request.headers.get('uuidcode', '<no_uuidcode>')
            log.info(f"uuidcode={uuidcode} Start remote tunnel for {node}")
            cmd = ['timeout' , os.environ.get('SSHTIMEOUT', "3"), 'ssh', '-F', os.environ.get('SSHCONFIGFILE', '~/.ssh/config'), f'remote_{node}', 'start']
            log.trace("uuidcode={uuidcode} Start Remote tunnel: {cmd}".format(uuidcode=uuidcode, cmd=' '.join(cmd)))
            p = Popen(cmd, stderr=PIPE, stdout=PIPE)
            p.communicate()
            return_code = p.returncode
            running_code = int(os.environ.get("REMOTE_OK_CODE", 217))
            non_running_code = int(os.environ.get("REMOTE_NOT_OK_CODE", 218))
            log.trace(f"uuidcode={uuidcode} Exit code: {return_code}")
            if return_code == running_code:
                response = HttpResponse("True", status=200)
            elif return_code == non_running_code:
                response = HttpResponse("False", status=200)
            else:
                raise Exception(f"Remote POST ssh for {node} cmd finished with exit code {return_code}")
            return response
        except:
            log.exception("Bugfix required")
            return HttpResponse(status=500)
    
    def delete(self, request, node):
        try:
            uuidcode = request.headers.get('uuidcode', '<no_uuidcode>')
            log.info(f"uuidcode={uuidcode} Stop remote tunnel for {node}")
            cmd = ['timeout' , os.environ.get('SSHTIMEOUT', "3"), 'ssh', '-F', os.environ.get('SSHCONFIGFILE', '~/.ssh/config'), f'remote_{node}', 'stop']
            log.trace("uuidcode={uuidcode} Stop Remote tunnel: {cmd}".format(uuidcode=uuidcode, cmd=' '.join(cmd)))
            p = Popen(cmd, stderr=PIPE, stdout=PIPE)
            p.communicate()
            return_code = p.returncode
            running_code = int(os.environ.get("REMOTE_OK_CODE", 217))
            non_running_code = int(os.environ.get("REMOTE_NOT_OK_CODE", 218))
            log.trace(f"uuidcode={uuidcode} Exit code: {return_code}")
            if return_code == running_code:
                response = HttpResponse("False", status=200)
            elif return_code == non_running_code:
                response = HttpResponse("True", status=200)
            else:
                raise Exception(f"Remote POST ssh for {node} cmd finished with exit code {return_code}")
            return response
        except:
            log.exception("Bugfix required")
            return HttpResponse(status=500)


class Tunnel(APIView):
    def get(self, request, servername):
        try:
            uuidcode = request.headers.get('uuidcode', '<no_uuidcode>')
            log.info(f"uuidcode={uuidcode} Get Tunnel Status for {servername}")
            tunnel = Tunnels.objects.filter(servername=servername).first()
            if tunnel is None:
                log.debug(f"uuidcode={uuidcode} No tunnel named {servername} in database.")
                response = HttpResponse("False", status=200)
            else:
                if tunnel.is_running(uuidcode):
                    response = HttpResponse("True", status=200)
                    response["Location"] = f"{tunnel.servername};{tunnel.node};{tunnel.hostname};{tunnel.port1};{tunnel.port2};{tunnel.date}"
                else:
                    response = HttpResponse("False", status=200)
            return response
        except:
            log.exception("Bugfix required")
            return HttpResponse(status=500)
    
    def post(self, request, servername, node, hostname, port1, port2):
        try:
            uuidcode = request.headers.get('uuidcode', '<no_uuidcode>')
            log.info(f"uuidcode={uuidcode} Start Tunnel for {servername} {node} {hostname} {port1} {port2}")
            port_tunnel = Tunnels.objects.filter(port1=port1).first()
            if port_tunnel is not None:
                log.warning(f"uuidcode={uuidcode} Tunnel with port {port1} already exists")
                trust_hub = os.environ.get("TRUST_HUB", "false").lower() in ('true', '1')
                if trust_hub:
                    port_tunnel.stop(uuidcode)
                    port_tunnel.delete()
                else:
                    return HttpResponse("False:port", status=200)
            servername_tunnel = Tunnels.objects.filter(servername=servername).first()
            if servername_tunnel is not None:
                log.warning(f"uuidcode={uuidcode} Tunnel with servername {servername} already exists")
                trust_hub = os.environ.get("TRUST_HUB", "false").lower() in ('true', '1')
                if trust_hub:
                    servername_tunnel.stop(uuidcode)
                    servername_tunnel.delete()
                else:
                    return HttpResponse("False:servername", status=200)
            
            return_code = Tunnels.setup_tunnel(uuidcode, node, hostname, port1, port2)
            log.trace(f"uuidcode={uuidcode} Return Code: {return_code}")
            if return_code == 0:
                log.debug(f"uuidcode={uuidcode} Store in database")
                tunnel = Tunnels(servername=servername, node=node, hostname=hostname, port1=port1, port2=port2)
                tunnel.save()
                response = HttpResponse("True", 200)
            else:
                raise Exception(f"ssh finished with non expected exit code: {return_code}")
            return response
        except:
            log.exception("Bugfix required")
            return HttpResponse(status=500)

    def delete(self, request, servername):
        try:
            uuidcode = request.headers.get('uuidcode', '<no_uuidcode>')
            log.info(f"uuidcode={uuidcode} Stop Tunnel for {servername}")

            tunnel = Tunnels.objects.filter(servername=servername).first()
            if tunnel is None:
                log.error(f"uuidcode={uuidcode} Could not find any tunnel for servername {servername}")
                return HttpResponse("False:servername", status=200)

            if tunnel.stop(uuidcode):
                log.debug(f"uuidcode={uuidcode} Delete from database")
                tunnel.delete()
                response = HttpResponse("True", status=200)
            else:
                response = HttpResponse("False", status=200)
            return response
        except:
            log.exception("Bugfix required")
            return HttpResponse(status=500)
