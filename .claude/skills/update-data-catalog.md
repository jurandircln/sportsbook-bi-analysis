# Skill: update-data-catalog

Use esta skill ao adicionar ou alterar tabelas, colunas ou métricas derivadas
em qualquer camada da arquitetura medalhão.

## Princípio

O catálogo de dados é a fonte de verdade sobre o que cada campo significa.
Sem ele, pessoas diferentes interpretam os mesmos dados de formas diferentes.

## Checklist

- [ ] Identificar qual tabela/coluna/métrica foi adicionada ou alterada
- [ ] Localizar o arquivo correto em `docs/technical-context/data-catalog/<camada>/`
- [ ] Atualizar ou criar o arquivo com:
      - Nome e propósito da tabela
      - Lista de colunas com: nome, tipo, descrição, valores possíveis (quando relevante)
      - Regras de negócio aplicadas (referenciar RN-NNN de business-rules.md)
      - Fonte de origem (para Silver/Gold: qual tabela upstream alimenta)
      - Exemplo de valores quando útil para clareza
- [ ] Verificar se `docs/technical-context/data-catalog/overview.md` precisa de atualização
- [ ] Commitar o catálogo junto com o DDL ou código na mesma PR/commit

## Estrutura dos arquivos do catálogo

```markdown
# Catálogo: <schema>.<tabela>

**Descrição:** [o que esta tabela representa]
**Camada:** [Bronze | Silver | Gold]
**Fonte:** [origem dos dados]
**Atualização:** [quando é populada/atualizada]

## Colunas

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| nome_coluna | TIPO | descrição | — |

## Regras de Negócio Aplicadas

- [RN-NNN]: [descrição resumida]

## Notas

[Observações importantes, armadilhas conhecidas, exemplos]
```
