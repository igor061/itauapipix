# Consulta de Pix recebidos — Banco do Brasil

Cobre as lojas com aplicação na API Pix V2 do BB: Viedra (CNB), SR Nacional,
SR Gold (BSB), Thema (TER), SR Manhattan (MHT) e Drocer (DCR).

## Consulta rápida

```bash
cd ~/projects/itauapipix
.venv/bin/python teste_bb.py viedra      # hoje
.venv/bin/python teste_bb.py viedra 4    # últimos 4 dias
```

O script lê `.env<empresa>` e usa o cert `~/projects/bbapipix/client_certs/<empresa>.pem`.
Já prontos: `viedra`, `srnacional`, `srgold`.

## Onde estão as credenciais

| O quê | Onde |
|---|---|
| client_id, client_secret, developer_key de cada loja | Planilha Google `1bBR-p7Toeg4_K9Zswh8kmgbjBvoDzD54FmYQ7qD3nXc`, bloco `APIBB` |
| Certificado e-CNPJ (PFX base64 + senha) | Infisical `https://infisical.porv.net`, projeto `certificados`, env `prod`, chaves `<EMPRESA>_PFX_B64` e `<EMPRESA>_PFX_SENHA` |
| Acesso ao Infisical nesta máquina | Machine identity `hermes-desktop-agent` (Viewer), credenciais em `~/.hermes/.infisical_creds` |
| Cliente Python original | `~/projects/bbapipix` (repo `igor061/bbapipix`) |

## Preparar uma loja nova

1. Criar `.env<empresa>` na raiz deste repo (o `.gitignore` cobre `.env*`):

   ```
   basic_auth="<base64 de client_id:client_secret>"
   developer_application_key="<developer_key>"
   ```

   ```bash
   printf '%s:%s' "$CLIENT_ID" "$CLIENT_SECRET" | base64 -w0
   ```

2. Baixar o PFX do Infisical e converter para PEM:

   ```bash
   cd ~/projects/infisical-manager
   export INFISICAL_CLIENT_ID=$(python3 -c "import json;print(json.load(open('/home/igor/.hermes/.infisical_creds'))['client_id'])")
   export INFISICAL_CLIENT_SECRET=$(python3 -c "import json;print(json.load(open('/home/igor/.hermes/.infisical_creds'))['client_secret'])")
   P=0fa8de10-ee9f-433b-b30f-88f965e5acee; D=~/projects/bbapipix/client_certs; E=VIEDRA; e=viedra
   python3 infisical_manager.py --project $P -e prod get ${E}_PFX_B64 | tr -d ' \n"' | base64 -d > $D/$e.pfx
   python3 infisical_manager.py --project $P -e prod get ${E}_PFX_SENHA | tr -d '\n"' > $D/.senha
   openssl pkcs12 -in $D/$e.pfx -passin file:$D/.senha -nodes -legacy -out $D/$e.pem
   rm $D/.senha; chmod 600 $D/*
   openssl x509 -in $D/$e.pem -noout -subject -enddate   # confere CNPJ e validade
   ```

## Regras da API do BB

- `GET https://api-pix.bb.com.br/pix/v2/pix` exige mTLS com o e-CNPJ da loja. Sem cert, ou com cert vencido, dá `SSL alert bad/unknown certificate`.
- OAuth em `https://oauth.bb.com.br/oauth/token` com `grant_type=client_credentials` e **`scope=pix.read`** obrigatório (sem ele: `invalid_scope`).
- Header `x-developer-application-key` e query `gw-dev-app-key`, ambos com a developer key.
- Janela `inicio`/`fim` **menor que 5 dias**. Formato `YYYY-MM-DDTHH:MM:SSUTC-3`.
- Lista vazia vem como **HTTP 404 `NaoEncontrado`**, não como `200 []`.
- Campos úteis: `horario`, `valor`, `endToEndId`, `pagador.nome`, `pagador.cpf|cnpj`, `infoPagador`, `txid`.

## Estado das contas em 2026-09-11

| Loja | Cert válido até | Último Pix listado |
|---|---|---|
| Viedra | 06/2027 | recebe normalmente |
| SR Nacional | 05/2027 | 06/2025 — nada desde então |
| SR Gold | 03/2027 | 12/2025 — nada em 2026 |
| SR Trend | vencido 04/2025 | client_id/secret também inválidos |
