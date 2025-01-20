import yaml
from pathlib import Path
import os
import shutil
import subprocess

with open("config.yaml") as stream:
  global_config = yaml.safe_load(stream)
  
vm_dir = global_config.get('vm_dir')

# remove lck files
matching_files = []
matching_dirs = []
for root, dirs, files in os.walk(vm_dir):
  for dir_name in dirs:
    if 'lck' in dir_name:
        shutil.rmtree(os.path.join(root, dir_name))
  for file in files:
    if file.endswith('lck'):
      os.remove(os.path.join(root, file))

# start vms
for filepath in Path(vm_dir).glob('*vmwarevm'):
  fn = filepath.absolute()
  subprocess.run(['vmrun', 'start', fn, 'nogui'])

