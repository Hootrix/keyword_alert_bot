import os,yaml,sys

__all__ = [
  'config',
  '_current_path'
]
_current_path = os.path.dirname(os.path.realpath(__file__))
config_file = f'{_current_path}/config.yml'

if not os.path.exists(config_file):
    print(f"Config file '{config_file}' not found. Please configure using 'config.yml.default'.")
    sys.exit(1)

with open(config_file) as _f:
  config = yaml.load(_f.read(),Loader = yaml.SafeLoader)