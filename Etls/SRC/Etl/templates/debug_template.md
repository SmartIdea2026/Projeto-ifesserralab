# Debug Template

Use para investigar bugs de forma estruturada e reduzir o risco de mudanca de comportamento nao intencional.

## Identificacao

- **ID:** _(ex: B-001)_
- **Titulo breve:** _(uma linha)_
- **Spec ou contexto:** _(link para Spec, US ou descricao curta)_

## Sintoma

- **O que acontece:** _(comportamento observado)_
- **O que era esperado:** _(comportamento esperado)_
- **Quando ocorre:** _(passos para reproduzir, ambiente, frequencia)_
- **Onde:** _(tela, endpoint, servico, arquivo)_

## Ja verificado

- [ ] _(hipotese descartada 1)_
- [ ] _(hipotese descartada 2)_

## Hipoteses

1. _(hipotese 1)_
2. _(hipotese 2)_
3. _(hipotese 3)_

## Instrucao para o agente

```text
Estou debugando: [sintoma em uma linha].
Reproducao: [passos].
Comportamento esperado: [uma linha].
Hipoteses iniciais: [lista].

Nao alterar comportamento sem avisar.
Objetivo: identificar causa raiz e propor a menor correcao segura possivel.
```

## Resultado

- **Causa raiz:** _(breve)_
- **Correcao aplicada:** _(arquivos e resumo)_
- **Como validar:** _(teste ou passo manual)_
- **Spec ou task atualizada:** _(ID ou arquivo)_
