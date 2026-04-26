# Skill: create-adr

Use esta skill ao tomar qualquer decisão técnica relevante que tenha alternativas consideradas.

## Quando criar um ADR

- Ao adotar nova tecnologia, biblioteca ou framework
- Ao definir padrão arquitetural
- Ao rejeitar abordagem que parecia óbvia
- Ao fazer mudança que quebra padrão anterior
- Ao definir convenção que afeta todo o projeto

## Checklist

- [ ] Verificar a numeração do próximo ADR em `docs/technical-context/adr/`
      (listar arquivos e usar próximo número disponível)
- [ ] Identificar o contexto: qual problema motivou a decisão?
- [ ] Descrever as alternativas consideradas (pelo menos 2)
- [ ] Documentar a decisão tomada e o motivo
- [ ] Listar as consequências (benefícios e trade-offs aceitos)
- [ ] Criar o arquivo `ADR-NNN-titulo-curto.md` em `docs/technical-context/adr/`
- [ ] Atualizar a tabela de ADRs no `CLAUDE.md`
- [ ] Se um ADR anterior for substituído, marcar como `Status: Substituída por ADR-NNN`

## Template

```markdown
# ADR-NNN: [Título curto e descritivo]

**Data:** YYYY-MM-DD
**Status:** [Proposta | Aceita | Substituída por ADR-XXX]

## Contexto

[Descreva o problema. O que estava acontecendo? Quais eram as restrições?]

## Decisão

[O que foi decidido, de forma direta.]

## Consequências

[O que muda? Quais benefícios? Quais trade-offs foram aceitos?]
```
