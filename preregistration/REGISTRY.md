# Registro do pré-registro — hashes e assinaturas

Pré-registro **assinado** em 2026-09-14 por Alexandre Zanata, revisor humano
único que acumula os papéis de responsável científico, revisor de estatística e
custodiante (limitação declarada). Os hashes abaixo congelam os 12 artefatos
científicos; a versão assinada `1.0` tem os mesmos bytes da minuta `1.0-draft` —
nenhum artefato congelado foi alterado após a assinatura (o `CHANGELOG.md` não é
congelado, pois registra as próprias mudanças). Qualquer edição posterior
invalida os hashes e exige entrada no `CHANGELOG.md` e nova assinatura quando
afetar o confirmatório.

## 1. Artefatos congelados

- SHA-256 `fb54cafb92be40085b296417393e72276b99640c785acc99e9dc18253725ee6a` — `preregistration/PROTOCOL.md`
- SHA-256 `a83354403df32094342c3284f2dd4b2eb22c32f9a8e45fa9d00a73bc567c7501` — `preregistration/cards/E1-selecao-fonte.md`
- SHA-256 `62eac8ab8917c9fd3ac648576044e87ec7798c7bfcab972ec6eb48d9e3c05b9f` — `preregistration/cards/E2-mvp-zero-shot.md`
- SHA-256 `b89d37b4d5f9c8d4dfd7320030deb733f3fd6956c0a1c584dcf664bbb3aafa29` — `preregistration/cards/E3-nivel2-condicional.md`
- SHA-256 `2ae11d2bbe7589280b4dbf82433dd64b8839819fef49b2e65dc5a2a6bbd15160` — `docs/research/STATISTICAL-ANALYSIS-PLAN.md`
- SHA-256 `06baec9cb5c99774f3f0fc202c18000448d5a8872810a5435b826e2ae4b9266e` — `docs/research/RUN-CONTRACT.md`
- SHA-256 `8357d449c718a2ee2fb50b8fdda9eefcf664d4416dba19d31bec862e7c265cfb` — `docs/research/FIREWALL.md`
- SHA-256 `1be6628faed19a09037100ab8407fce8a55333008d4059c50daa9c46f4208bee` — `docs/research/DESFECHOS-E-FALSIFICACAO.md`
- SHA-256 `da9ed19a8e05f3cac7f9c70f05deceb1a11fc4b121b5918f58351026fff176f5` — `docs/research/EQUIVALENCIA.md`
- SHA-256 `a1c0016c92b2fd3078d10cc1d14f7bd2562e394f949a71f3122f5e369c0c764e` — `research/datasets/CROSSWALK-AUDIT.md`
- SHA-256 `9ecdbcc25c4c834601eae903013f65320aeab00d5e654ff75afb0b1bcd72026e` — `research/datasets/SELECAO.md`
- SHA-256 `eab6b4f08515355ec19c6546e93b0a1e3977fd994e73f31320aa18b8f654fb97` — `docs/gates/G2-DADOS.md`

## 2. Assinaturas

- Responsável científico: Alexandre Zanata — 2026-09-14
- Revisor de estatística: Alexandre Zanata — 2026-09-14 (mesmo revisor acumulando papéis; limitação declarada)
- Custodiante designado: Alexandre Zanata — 2026-09-14 (mesmo revisor acumulando papéis; limitação declarada)
- Data da assinatura: 2026-09-14
- Hash do pacote assinado: 9411af0ca15501b253934f5e2134d978a95526dcf2c4cb7923a677a685f658b1 (SHA-256 da concatenação das 12 linhas de artefatos congelados, na ordem, separadas por quebra de linha)

## 3. Regras

- O pré-registro vale com as três assinaturas, o registro da data e o hash do
  pacote conferindo com os 12 artefatos congelados.
- O executor não altera este arquivo após a assinatura; mudanças seguem o
  `CHANGELOG.md`.
- Validação: `python3 tools/validate_research.py`.
