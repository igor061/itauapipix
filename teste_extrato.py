"""Testa a API de extrato do Itaú (account-statement v1) com a app própria do extrato.

Uso: PYTHONPATH=. .venv/bin/python teste_extrato.py [dias]   (default 1)
Credenciais no .env do repo (CREDENCIAL, SECRET, STATEMENT_ID) e cert em certs/itau_extrato.pem.
STATEMENT_ID = agência(4) + 00 + conta(5) + DAC(1).
Imprime um resumo; sai com código 0 só se as chamadas responderem 200.
"""
import base64, datetime as dt, json, os, sys
import requests

D = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://account-statement.api.itau.com/account-statement/v1'

e = dict(l.split('=', 1) for l in open(f'{D}/.env').read().splitlines() if '=' in l)
cid, sec, cert = e['CREDENCIAL'].strip(), e['SECRET'].strip(), f'{D}/certs/itau_extrato.pem'
STATEMENT_ID = e['STATEMENT_ID'].strip()

r = requests.post('https://sts.itau.com.br/api/oauth/token', cert=cert, timeout=30,
                  data={'grant_type': 'client_credentials', 'client_id': cid, 'client_secret': sec})
if not r.ok:
    print(f'Token falhou: HTTP {r.status_code} {r.text[:200]}'); sys.exit(1)
tok = r.json()['access_token']
h = {'Authorization': f'Bearer {tok}', 'x-itau-apikey': cid, 'x-itau-correlationID': 'teste-extrato'}

hoje = dt.date.today(); ini = hoje - dt.timedelta(days=int(sys.argv[1]) if len(sys.argv) > 1 else 1)
ok = True
for nome, path, q in [
    ('Saldo', '/balances', {}),
    ('Extrato', f'/statements/{STATEMENT_ID}', {'type': 'current_account', 'start_date': ini.isoformat(),
                                                'end_date': hoje.isoformat(), 'page_size': 50}),
]:
    r = requests.get(BASE + path, params=q, headers=h, cert=cert, timeout=30)
    ok &= r.status_code == 200
    print(f'{nome}: HTTP {r.status_code}')
    if r.status_code != 200:
        print('  ' + r.text[:300]); continue
    d = r.json()
    if nome == 'Extrato':
        ev = [x for b in d.get('data', []) for x in b.get('events', [])]
        print(f'  {len(ev)} lançamentos de {ini:%d/%m} a {hoje:%d/%m}')
        for x in ev[:5]: print('  ' + json.dumps(x, ensure_ascii=False)[:200])
    else:
        print('  ' + json.dumps(d, ensure_ascii=False)[:400])
sys.exit(0 if ok else 2)
