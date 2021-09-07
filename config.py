import os,yaml

__all__ = [
  'config',
  '_current_path'
]
_current_path = os.path.dirname(os.path.realpath(__file__))
with open(f'{_current_path}/config.yml') as _f:
  config = yaml.load(_f.read(),Loader = yaml.SafeLoader)