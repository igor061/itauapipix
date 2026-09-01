#!/usr/bin/env bash
# Uso: gera_cert.sh <CLIENT_ID> <TOKEN_TEMPORARIO>   (token vale 5 min)
set -euo pipefail
CID=${1:?client_id}; TOK=${2:?token temporario}
D=$(dirname "$(readlink -f "$0")")/certs; mkdir -p "$D"; cd "$D"; umask 077
openssl req -new -subj "/CN=$CID/OU=Coralli/L=BRASILIA/ST=DF/C=BR" -nodes -sha512 -newkey rsa:2048 \
  -keyout itau.key -out itau.csr 2>/dev/null
curl -sS -X POST https://sts.itau.com.br/seguranca/v1/certificado/solicitacao \
  -H "Content-Type: text/plain" -H "Authorization: Bearer $TOK" --data-binary @itau.csr -o resposta.txt -w 'HTTP %{http_code}\n'
grep -q 'BEGIN CERTIFICATE' resposta.txt || { echo "Falhou:"; cat resposta.txt; exit 1; }
sed -n '/BEGIN CERTIFICATE/,/END CERTIFICATE/p' resposta.txt > itau.crt
cat itau.crt itau.key > itau.pem
echo "OK: certs/itau.pem gerado. Validade:"; openssl x509 -in itau.crt -noout -enddate
echo "Secret novo (guarde em ~/.config/itau.env):"; grep -i '^secret' resposta.txt || echo "(não veio Secret na resposta — use o client_secret do portal)"
