import logging
import os
from pathlib import Path
from subprocess import PIPE
from subprocess import Popen

from django.db import models

log = logging.getLogger("UserLab")


class UserLab(models.Model):
    startuuidcode = models.TextField(null=False, max_length=40)
    backend_id = models.IntegerField(null=False)
    username = models.TextField(null=False, max_length=250)
    image = models.TextField(null=False)
    port = models.IntegerField(null=False)

    def start(self, uuidcode, env):
        # Create directory and files to start UserLabs
        jobs_base_path = os.environ.get("JOBS_BASE_PATH")
        job_path = os.path.join(jobs_base_path, str(self.backend_id))
        Path(job_path).mkdir(parents=True, exist_ok=True)

        # Create Environment file with JupyterHub-User information
        start_env_keys_list = os.environ.get("START_ENV_KEYS", "").split()
        env_list = [f"{x}={y}" for x, y in env.items() if x in start_env_keys_list]

        env_file = os.path.join(job_path, "start.env")
        with open(env_file, "w") as f:
            f.write("\n".join(env_list))

        # Create file with mounts from projects
        ## TODO

        # Run start.sh Script
        start_script_path = os.environ.get("START_SCRIPT_PATH")
        cmd = [
            "/bin/bash",
            start_script_path,
            self.username,
            self.id,
            self.image,
            self.port,
            env.get("JUPYTERHUB_API_TOKEN"),
        ]
        log.debug(
            "uuidcode={uuidcode} Start UserLab: {cmd}".format(
                uuidcode=uuidcode, cmd=" ".join(cmd)
            )
        )
        p = Popen(cmd, stderr=PIPE, stdout=PIPE)
        out, err = p.communicate(timeout=int(os.environ.get("SCRIPT_TIMEOUT", "3")))
        log.debug(f"uuidcode={uuidcode} - Out:\n{out}\nErr:\n{err}")

    def stop(self, uuidcode):
        stop_script_path = os.environ.get("STOP_SCRIPT_PATH")
        cmd = ["/bin/bash", stop_script_path, self.backend_id]
        log.debug(
            "uuidcode={uuidcode} Stop UserLabl: {cmd}".format(
                uuidcode=uuidcode, cmd=" ".join(cmd)
            )
        )
        p = Popen(cmd, stderr=PIPE, stdout=PIPE)
        out, err = p.communicate(timeout=int(os.environ.get("SCRIPT_TIMEOUT", "3")))
        log.debug(f"uuidcode={uuidcode} - Out:\n{out}\nErr:\n{err}")

    def status(self, uuidcode):
        status_script_path = os.environ.get("STATUS_SCRIPT_PATH")
        cmd = ["/bin/bash", status_script_path, self.backend_id]
        log.debug(
            "uuidcode={uuidcode} Status UserLab: {cmd}".format(
                uuidcode=uuidcode, cmd=" ".join(cmd)
            )
        )
        p = Popen(cmd, stderr=PIPE, stdout=PIPE)
        out, err = p.communicate(timeout=int(os.environ.get("SCRIPT_TIMEOUT", "3")))
        return_code = p.returncode
        log.debug(f"uuidcode={uuidcode} - Out:\n{out}\nErr:{err}")
        return return_code == 0
