import time
import requests
import config
import os
import shutil
import json
import traceback
import base64

from git import Repo
from pathlib import Path

def get_inspec_analysis(thread_id, request_data):
  try:
    profile = request_data['profile']
    os_host = request_data['os']
    optionals = ""
    if request_data['optionals'] != None and request_data['optionals'] != "" and request_data['optionals'] != "None":
      optionals = "--input {}".format(request_data['optionals'])

    if os_host != "kubernetes":
      username = request_data['username']
      password = request_data['password']
      host = request_data['host']
    else:
      namespace = request_data['namespace']
      pod = request_data['pod']
      container = request_data['container']
      kubeconfig_name = request_data['kubeconfig_name']
      kubeconfig_file_b64 = request_data['kubeconfig_file']
      base64_bytes = kubeconfig_file_b64.encode('ascii')
      message_bytes = base64.b64decode(base64_bytes)
      kubeconfig_file = message_bytes.decode('ascii')
      kc_name = "{}/{}".format(config.KUBE_CONFIG_PATH, kubeconfig_name)
      f = open(kc_name, "w")
      f.write(kubeconfig_file)
      f.close()

    if profile == "" or os_host == "" or (os_host != "kubernetes" and (username == "" or password == "" or host == "")) or (os_host == "kubernetes" and (namespace == "" or pod == "" or container == "" or kubeconfig_file == "" or kubeconfig_name == "")):
      print("Thread {} - Parameters missed".format(thread_id))
      return { "status": False, "message" : "Parameters missed" }
    
    profile_name = profile.split("/")[1]
    profile_dir = "/opt/profiles-inspec/{}".format(profile_name)

    if Path(profile_dir) and Path(profile_dir).is_dir():
      shutil.rmtree(Path(profile_dir))

    print("Thread {} - Clone of {}".format(thread_id, profile))
    Repo.clone_from("https://github.com/{}".format(profile), profile_dir)
 
    if os_host == "windows": 
      profile_cmd = "cd /opt/profiles-inspec/{} && inspec exec . --backend winrm --user {} --password {} --host {} --chef-license=accept-silent {} --reporter json:-".format(profile_name, username, password, host, optionals)
    if os_host == "linux": 
      profile_cmd = "cd /opt/profiles-inspec/{} && inspec exec . -t ssh://{}@{} --user {} --password {} {} --chef-license=accept-silent --reporter json:-".format(profile_name, username, host, username, password, optionals)
    if os_host == "kubernetes":
      profile_cmd = "export KUBECONFIG={} && export namespace={} && export pod={} && export container={} && cd /opt/profiles-inspec/{} && inspec exec . -t kubernetes:// {} --chef-license=accept-silent --reporter json:-".format(kc_name, namespace, pod, container, profile_name, optionals)

    if profile_cmd == "":
      return { "status": False, "message": "Unknown OS" }
      
    print("Thread {} - Execute {}".format(thread_id, profile_cmd))
    profile_output = os.popen(profile_cmd)
    print("Thread {} - OUTPUT COMMAND: {}".format(thread_id, profile_output))
    return prepare_json(json.load(profile_output))
  except Exception as e:
    print("Thread {} - Main error: {}: {}".format(thread_id, str(e), str(traceback.format_exc())))
    return { "status": False, "message": str(e) }
    
def pulisci(stringa):
  return stringa.replace("'"," ").replace('"'," ")

def prepare_json(input_json):
  r = [] 
  i = 0
  try:
    for control in input_json['profiles'][0]['controls']:
      control_id = pulisci(control["id"])
      control_title = pulisci(control["title"])
      control_desc = pulisci(control["desc"])
      control_impact = control["impact"]

      for result in control["results"]:
        result_status = pulisci(result["status"])
        result_desc = pulisci(result["code_desc"])
        if result_status == 'failed':
          color = 3
        else:
          color = 1
        r.append({
          "id": i,
          "color": color,
          "control_id": control_id,
          "control_title": control_title,
          "rule_sev": control_impact,
          "control_impact": control_impact,
          "control_desc": control_desc,
          "result_status": pulisci(result_status),
          "result_desc": pulisci(result_desc)
        })
        i = i + 1

  except Exception as e:
    return { "status": False, "message" : str(e) }
  return { "status": True, "rows" : r }
