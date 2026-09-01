import sys, json, datetime as dt
import env
from itauapipix.itau_api_pix import ItauClient, EmptyPixList
fim = dt.datetime.utcnow(); ini = fim - dt.timedelta(days=int(sys.argv[1]) if len(sys.argv) > 1 else 7)
c = ItauClient.from_credentials(**env.credenciais['coralli'])
try:
    r = c.received_pixs(ini.strftime('%Y-%m-%dT%H:%M:%SZ'), fim.strftime('%Y-%m-%dT%H:%M:%SZ'))
    d = r.json(); px = d.get('pix', [])
    print(f"HTTP {r.status_code} | {len(px)} pix | total R$ {sum(float(p['valor']) for p in px):.2f}")
    for p in px[:10]: print(p['horario'], p['valor'], p['endToEndId'], p.get('infoPagador',''))
except EmptyPixList:
    print("HTTP 404 — token OK, nenhum pix no período")
