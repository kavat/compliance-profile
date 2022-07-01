import time
import requests
import config
import os
import shutil
import json

from git import Repo
from pathlib import Path

def get_inspec_analysis(thread_id, username, password, host, profile, os):
  try:
    if username == "" or password == "" or host == "" or profile == "" or os == "":
      print("Thread {} - Parameters missed".format(thread_id))
      return { "status": False, "message" : "Parameters missed" }
    
    profile_name = profile.split("/")[1]
    profile_dir = "/opt/profiles-inspec/{}".format(profile_name)

    if Path(profile_dir) and Path(profile_dir).is_dir():
      shutil.rmtree(Path(profile_dir))

    print("Thread {} - Clone of {}".format(thread_id, profile))
    Repo.clone_from("https://github.com/{}".format(profile), profile_dir)
 
    if os == "windows": 
      profile_cmd = "cd /opt/profiles-inspec/{} && inspec exec . --backend winrm --user {} --password {} --host {} --chef-license=accept-silent --reporter json:-".format(profile_name, username, password, host)
    if os == "linux": 
      profile_cmd = "cd /opt/profiles-inspec/{} && inspec exec . -t ssh://{}@{} --user {} --password {} --chef-license=accept-silent --reporter json:-".format(profile_name, username, host, username, password)

    if profile_cmd == "":
      return { "status": False, "message": "Unknown OS" }
      
    print("Thread {} - Execute {}".format(thread_id, profile_cmd))
    profile_output = os.popen(profile_cmd)
    print("Thread {} - OUTPUT COMMAND: {}".format(thread_id, profile_output))
    return prepare_json(json.load(profile_output))
  except Exception as e:
    print("Thread {} - Main error: {}".format(thread_id, str(e)))
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
