# Matriz de rastreabilidade

Esta lista impede que um pedido do briefing desapareça entre as microfases. Os
IDs referem-se a `docs/PLANO-MICROFASES.md`.

- **Baseline versionado e prompt privado:** C00.

## Entregáveis científicos solicitados

- **Viabilidade científica:** C01–C06, L01–L07 e gate G0/G1.
- **Datasets concretos e campos reais:** D01–D10.
- **Download, licença, formatos e representação:** D02–D10, R01–R04 e H01–H09.
- **Melhor par de treino/teste e alternativas:** D08–D10.
- **Definição de neurônio equivalente:** C02, C03, D08 e R07.
- **Arquiteturas candidatas:** L06, B06–B08, M01–M06 e S02.
- **Baselines obrigatórios:** B01–B09.
- **Tarefas self-supervised:** L06, M01 e S01.
- **Riscos de leakage:** C05, R05–R08, H03–H07 e M06–M08.
- **Métricas, calibração e open-set:** C04, R06, B01–B03 e S08.
- **VRAM, RAM, armazenamento e tempo:** D09, R02, H08, M04 e S05.
- **MVP executável em 8 GB:** B01–B09 e M01–M10.
- **Experimento sério/paper:** S01–S12 e P01–P09.
- **Novidade versus literatura:** L01–L07, S11 e P05.
- **Roadmap técnico:** o plano completo, com gates G0–G8.

## Requisitos metodológicos adicionais

- **Topologia somente:** H05, B03–B08, M01–M10.
- **Topologia e atributos:** S03.
- **Morfologia:** S04.
- **Connectivity vs morphology vs combinação:** S04.
- **Escala de parâmetros:** S05.
- **Cross-direction:** S09.
- **Treino multi-source/leave-one-out:** S10.
- **Clustering emergente:** S07.
- **Link prediction zero-shot no alvo:** S01.
- **Falsificação e controles negativos:** C04, B09, M09 e S08.
- **Reprodução independente:** P02 e P03.

## Saídas possíveis e honestas

- Se o gate de dados falhar, produzir um relatório de inviabilidade e uma
  reformulação; não treinar.
- Se o MVP empatar com degree-only, a conclusão é que o modelo complexo não
  demonstrou sinal adicional no protocolo observado.
- Se houver sinal em somente um par, chamar o resultado de estudo entre os dois
  datasets, não de universalidade entre indivíduos.
- Se o protocolo confirmatório falhar mas uma análise pós-unseal funcionar,
  rotulá-la exploratória e exigir novo alvo para confirmação.

## Programa posterior

O possível uso dos embeddings para intervenção, comportamento e organismos
incorporados não integra os claims deste estudo. Ele possui escopo, hipóteses e
gates próprios em `docs/PLANO-MICROFASES-NEXT.md` e só começa após G8.
