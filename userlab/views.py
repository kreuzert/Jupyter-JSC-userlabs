import json
import logging
import os

from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from rest_framework.views import APIView

from userlab.models import UserLab

# import the logging library

# Get an instance of a logger
log = logging.getLogger("UserLab")


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


class UserLab(APIView):
    def get(self, request, id):
        try:
            uuidcode = request.headers.get("uuidcode", "<no_uuidcode>")
            log.info(f"uuidcode={uuidcode} Get status of UserLab")

            userlab = UserLab.objects.filter(backend_id=id).first()
            running = userlab.status(uuidcode)
            if running:
                response = HttpResponse("True", 200)
            else:
                response = HttpResponse("False", 200)
            return response
        except:
            log.exception("Bugfix required")
            return HttpResponse(status=500)

    def post(self, request, id, username, image, port):
        try:
            uuidcode = request.headers.get("uuidcode", "<no_uuidcode>")
            log.info(f"uuidcode={uuidcode} Start UserLab")

            popen_kwargs = json.loads(request.body.decode("utf8"))
            env = popen_kwargs.get("env")
            log.trace(
                "uuidcode={uuidcode} Start UserLab with:\nID: {id}\nUsername: {username}\nImage: {image}\nPort: {port}\nEnv: {env}".format(
                    uuidcode=uuidcode,
                    id=id,
                    username=username,
                    image=image,
                    port=port,
                    env=env,
                )
            )
            userlab = UserLab.objects.filter(backend_id=id).first()

            if userlab is not None:
                log.warning(
                    f"uuidcode={uuidcode} UserLab with backend_id {id} already exists"
                )
                trust_hub = os.environ.get("TRUST_HUB", "false").lower() in (
                    "true",
                    "1",
                )
                if trust_hub:
                    userlab.stop(uuidcode)
                    userlab.delete()
                else:
                    return HttpResponse("False", status=200)

            userlab = UserLab(
                startuuidcode=uuidcode,
                backend_id=id,
                username=username,
                image=image,
                port=port,
            )
            userlab.start(uuidcode, env)
            userlab.save()
            return HttpResponse("True", status=200)
        except:
            log.exception("Bugfix required")
            return HttpResponse(status=500)

    def delete(self, request, id):
        try:
            uuidcode = request.headers.get("uuidcode", "<no_uuidcode>")
            log.info(f"uuidcode={uuidcode} Stop UserLab for {id}")

            userlab = UserLab.objects.filter(backend_id=id).first()
            if userlab is None:
                log.error(f"uuidcode={uuidcode} Could not find any userlab for id {id}")
            else:
                userlab.stop(uuidcode)
                userlab.delete()

            response = HttpResponse(status=200)
            return response
        except:
            log.exception("Bugfix required")
            return HttpResponse(status=500)
