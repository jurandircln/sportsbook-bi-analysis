# ADR-005: Catálogo de Dados como Artefato de Governança Obrigatório

**Data:** 2026-04-26
**Status:** Aceita

## Contexto

Em projetos de dados com múltiplas fontes e transformações, é comum que pessoas
diferentes interpretem os mesmos campos de formas distintas. Exemplo: "Gross Revenue"
poderia ser interpretado como `turnover`, `winnings` ou `turnover - winnings`.
Sem uma fonte de verdade documentada, o sistema de BI perde confiabilidade.

## Decisão

O catálogo de dados é um artefato de governança obrigatório, versionado junto com
o código no repositório. Localizado em `docs/technical-context/data-catalog/`,
organizado por camada medalhão.

**Protocolo:** Qualquer alteração de schema ou nova métrica derivada exige atualização
do catálogo na mesma PR/commit. A skill `update-data-catalog` deve ser invocada
sempre que houver mudança estrutural nos dados.

O catálogo documenta por tabela: descrição, colunas com tipos e definições,
regras de negócio aplicadas, fonte de origem e exemplos quando relevante.

## Consequências

Governança explícita garante que o agente de BI, o dashboard e os desenvolvedores
trabalhem com a mesma definição de cada campo. O custo é a disciplina de manter
o catálogo atualizado a cada mudança — minimizado pela skill `update-data-catalog`.
