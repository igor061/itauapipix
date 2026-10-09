#!/usr/bin/env bash
# Uso: gera_cert.sh <CLIENT_ID> <TOKEN_TEMPORARIO> [NOME]   (gera certs/NOME.pem; default itau)
set -euo pipefail
CID=${1:?client_id}; TOK=${2:?token temporario}; N=${3:-itau}
D=$(dirname "$(readlink -f "$0")")/certs; mkdir -p "$D"; cd "$D"; umask 077
openssl req -new -subj "/CN=$CID/OU=Coralli/L=BRASILIA/ST=DF/C=BR" -nodes -sha512 -newkey rsa:2048 \
  -keyout $N.key -out $N.csr 2>/dev/null
curl -sS -X POST https://sts.itau.com.br/seguranca/v1/certificado/solicitacao \
  -H "Content-Type: text/plain" -H "Authorization: Bearer $TOK" --data-binary @$N.csr -o $N.resposta.txt -w 'HTTP %{http_code}\n'
grep -q 'BEGIN CERTIFICATE' $N.resposta.txt || { echo "Falhou:"; cat $N.resposta.txt; exit 1; }
sed -n '/BEGIN CERTIFICATE/,/END CERTIFICATE/p' $N.resposta.txt > $N.crt
cat $N.crt $N.key > $N.pem
echo "OK: certs/$N.pem gerado. Validade:"; openssl x509 -in $N.crt -noout -enddate
echo "Secret novo (guarde em ~/.config/itau.env):"; grep -qi '^secret' $N.resposta.txt && echo "(em certs/$N.resposta.txt)" || echo "(não veio Secret na resposta — use o client_secret do portal)"
