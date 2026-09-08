import sys, datetime as dt
import env
from itauapipix.itau_api_pix import ItauClient, EmptyPixList
# A API trata inicio/fim e 'horario' em GMT-3 apesar do sufixo 'Z' — usar hora local, sem converter para UTC.
# A listagem atrasa ~5 min; GET /pix/{endToEndId} responde na hora.
BRT = dt.timezone(dt.timedelta(hours=-3))
fim = dt.datetime.now(BRT); ini = fim - dt.timedelta(days=int(sys.argv[1]) if len(sys.argv) > 1 else 7)
c = ItauClient.from_credentials(**env.credenciais['coralli'])
try:
    r = c.received_pixs(ini.strftime('%Y-%m-%dT%H:%M:%SZ'), fim.strftime('%Y-%m-%dT%H:%M:%SZ'))
    d = r.json(); px = d.get('pix', [])
    print(f"HTTP {r.status_code} | {len(px)} pix | total R$ {sum(float(p['valor']) for p in px):.2f}")
    for p in px[:10]: print(p['horario'].replace('T', ' ').rstrip('Z') + ' (GMT-3)', p['valor'], p['endToEndId'], p.get('infoPagador',''))
except EmptyPixList:
    print("HTTP 404 — token OK, nenhum pix no período")
