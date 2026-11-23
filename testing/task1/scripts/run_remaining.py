from pathlib import Path
import subprocess,os,json,sys
root=Path(__file__).resolve().parents[1]
env=dict(os.environ,PYTHONPATH='.',QT_QPA_PLATFORM_PLUGIN_PATH='/opt/miniconda3/envs/osdagbridge-env/lib/python3.12/site-packages/PySide6/Qt/plugins/platforms')
for n in range(4,18):
 attempt=1
 while (root/f'runs/TC{n:02}/attempt{attempt}').exists():attempt+=1
 dest=root/f'runs/TC{n:02}/attempt{attempt}';dest.mkdir(parents=True,exist_ok=True)
 with (root/f'logs/TC{n:02}_attempt{attempt}.log').open('w') as log:
  print('START',n,flush=True)
  p=subprocess.Popen(['/opt/miniconda3/envs/osdagbridge-env/bin/python','-u',str(root/'scripts/task1_case.py'),str(n),str(dest)],cwd='/Users/ananditasinha/OsdagBridge/src',env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  try:code=p.wait(timeout=360)
  except subprocess.TimeoutExpired:
   import signal
   os.killpg(p.pid,signal.SIGTERM);code=124
   (dest/'supervisor_timeout.json').write_text(json.dumps({'timeout_seconds':360,'pid':p.pid}))
  print('FINISH',n,code,flush=True)
