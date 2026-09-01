# Sandbox Itaú (sem mTLS): ITAU_SB_CLIENT_ID / ITAU_SB_SECRET em ~/.config/itau.env
import os, sys, datetime as dt, requests
cid, sec = os.environ['ITAU_SB_CLIENT_ID'], os.environ['ITAU_SB_SECRET']
r = requests.post('https://devportal.itau.com.br/api/jwt', data={'client_id': cid, 'client_secret': sec}, timeout=20)
print('jwt:', r.status_code, r.text[:200] if r.status_code != 200 else 'ok')
r.raise_for_status(); tok = r.json()['access_token']
base = 'https://devportal.itau.com.br/sandboxapi/pix_recebimentos_ext_v2/v2'
h = {'x-sandbox-token': tok, 'Authorization': f'Bearer {tok}', 'x-itau-apikey': cid}
fim = dt.datetime.utcnow(); ini = fim - dt.timedelta(days=int(sys.argv[1]) if len(sys.argv) > 1 else 30)
r = requests.get(f'{base}/pix', headers=h, params={'inicio': ini.strftime('%Y-%m-%dT%H:%M:%SZ'), 'fim': fim.strftime('%Y-%m-%dT%H:%M:%SZ')}, timeout=20)
print('GET /pix:', r.status_code); print(r.text[:1500])
