# Rastreabilidade NEXT — NeuroVerse

Os IDs apontam para `docs/PLANO-MICROFASES-NEXT.md`.

## Entregáveis pedidos

- **Avaliação científica e crítica:** NX00–NX02, NV01–NV03 e NG1.
- **Novidade e trabalhos próximos:** NV02, NV03, NT05 e NG11.
- **Datasets Connectome → Behavior:** NV04–NV06.
- **Primeiro comportamento:** NV06 e NV07.
- **Mapping neurônio → intervenção → comportamento:** NV05, NB01–NB04.
- **Arquitetura mínima:** NC01–NC08.
- **Aprendido versus determinístico:** NX02, NC01, ND03 e NO02–NO03.
- **Runtime inicial e progressão 0–3:** NC03–NC05, NE03, ND04 e NI03.
- **Representação e memória:** NC02–NC03, NO06.
- **Roadmap Stage 0–10:** plano completo, gates NG0–NG11.
- **Go/no-go entre stages:** NG0–NG11.
- **Único próximo experimento:** NV07 e NB01–NB11.
- **Primeiro resultado publicável:** NG2, NI06 ou NT05 conforme força da evidência.
- **Risco simulação versus biologia:** NX02, NC01, NO05, NG6 e NG11.
- **Reprodutibilidade:** NX01, NB02, NC06–NC08 e todos os gates.

## Funcionalidades da engine

- **API universal do organismo:** NC01 e NC05.
- **Runtime plugável:** NC01, NC04 e ND04.
- **Arrays sparse/vectorized:** NC02–NC03.
- **Grafo completo, top-k, threshold, subgraph e event-driven:** NO06 e NS02–NS03.
- **Sensory adapters com provenance:** NC01, NC05, NO02.
- **Motor high-level e low-level:** ND03, NO01, NO07 e gate NG6.
- **Internal state grounded/synthetic:** NO03.
- **Config e CLI de experimentos:** NC06.
- **Logging em níveis:** NC06.
- **Behavior/Neural/Trajectory metrics:** NC07 e NO05.
- **Activate/inhibit/lesion:** NI01–NI06.
- **Missing structure com flags:** ND02 e NS01.
- **Cross-animal behavior:** NT01–NT05.
- **Minecraft:** NM01–NM04.
- **Organismos sintéticos e null graphs:** NS01–NS04.
- **Artificial evolution:** NA01–NA04.

## Saídas honestas

- Se `NG1` falhar, produzir dataset feasibility report e não treinar predictor.
- Se `NG2` falhar, não usar o embedding como base biológica da engine e não abrir
  o Core neste programa. Um sandbox técnico exigiria autorização e plano novos.
- Se C. elegans falhar, não mascarar a falha pulando direto para uma mosca maior.
- Se o Stage 4/5 depender de regras de adapter, relatar controlador projetado,
  não comportamento emergente.
- Minecraft, mutações e evolução permanecem artificiais mesmo quando funcionam.
