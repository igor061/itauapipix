"""Lista Pix recebidos no Banco do Brasil.  Uso: teste_bb.py <empresa> [dias]
Lê .env<empresa> neste diretório e o cert em ~/projects/bbapipix/client_certs/<empresa>.pem.
Ver docs/consulta-pix-bb.md."""
import sys, re, base64, datetime as dt, os, requests

empresa = sys.argv[1]; dias = int(sys.argv[2]) if len(sys.argv) > 2 else 0
if dias > 4: sys.exit("BB limita a janela a menos de 5 dias")
kv = dict(re.findall(r'^(\w+)\s*=\s*"?([^"\n]+)"?', open(f'.env{empresa}').read(), re.M))
cid, csec = base64.b64decode(kv['basic_auth']).decode().split(':', 1)
dk = kv['developer_application_key']
cert = os.path.expanduser(f'~/projects/bbapipix/client_certs/{empresa}.pem')

tok = requests.post('https://oauth.bb.com.br/oauth/token', auth=(cid, csec), timeout=30,
                    data={'grant_type': 'client_credentials', 'scope': 'pix.read'})
tok.raise_for_status(); tok = tok.json()
hoje = dt.date.today(); ini = hoje - dt.timedelta(days=dias)
r = requests.get('https://api-pix.bb.com.br/pix/v2/pix', cert=cert, timeout=30,
                 headers={'Authorization': f"{tok['token_type']} {tok['access_token']}", 'x-developer-application-key': dk},
                 params={'inicio': f'{ini}T00:00:01UTC-3', 'fim': f'{hoje}T23:59:59UTC-3', 'gw-dev-app-key': dk})
if r.status_code == 404:
    sys.exit(f"HTTP 404 — token e cert OK, nenhum pix entre {ini} e {hoje}")
r.raise_for_status()
px = r.json().get('pix', [])
print(f"{empresa}: {len(px)} pix de {ini} a {hoje} | total R$ {sum(float(p['valor']) for p in px):.2f}")
for p in px:
    print(p['horario'][:16].replace('T', ' '), p['valor'], p['endToEndId'], p['pagador'].get('nome', ''), p.get('infoPagador', ''))
