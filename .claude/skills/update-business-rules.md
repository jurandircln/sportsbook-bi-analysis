# Skill: update-business-rules

Use esta skill ao alterar qualquer transformação da camada Silver ou ao identificar
nova regra de negócio nos dados.

## Princípio

As regras de negócio vivem na Silver. Mudá-las sem documentar gera inconsistências
entre o que o código faz e o que a equipe acredita que ele faz.

## Checklist

- [ ] Identificar qual regra está sendo criada ou alterada
- [ ] Verificar se a regra já existe em `docs/product-context/business-rules.md`
- [ ] Atualizar ou criar a regra no documento, com:
      - ID da regra (RN-NNN)
      - Descrição clara
      - Fórmula ou lógica (quando aplicável)
      - Tabelas afetadas
      - Exceções conhecidas
- [ ] Atualizar o código de transformação correspondente em `src/transformation/`
- [ ] Verificar se o catálogo de dados precisa ser atualizado (coluna computada nova?)
      → Se sim, invocar skill `update-data-catalog`
- [ ] Se a mudança for significativa, criar ADR → invocar skill `create-adr`
- [ ] Commitar `business-rules.md` junto com o código de transformação na mesma PR/commit

## Regras já documentadas (referência rápida)

| ID | Regra | Fórmula |
|---|---|---|
| RN-001 | Gross Revenue | `turnover - winnings` |
| RN-002 | Live vs. Pre-event | `placed_at >= event_start_time` |
| RN-003 | CRM Level forward-fill | Último nível registrado |
| RN-004 | Segmentação de clientes | novo / existente / saindo |
| RN-005 | Período da temporada | Set/2018 – Ago/2019 |
