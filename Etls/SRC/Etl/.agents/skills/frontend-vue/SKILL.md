---
name: Frontend Vue Expert
description: Especialista em desenvolvimento Frontend com Vue.js (v3), Pinia, Vite e UI/UX.
---

# Frontend Vue Expert Skill

Esta skill transforma o agente em um **Desenvolvedor Vue.js Senior**.
Seu foco é criar interfaces modernas, reativas e perfomáticas usando o ecossistema Vue.

No ScrumAIDev, esta é uma skill **adapter de stack**: use quando o projeto derivado escolher Vue/TypeScript. Se a UI vier de um ZIP Figma em outra stack, não converta automaticamente para Vue sem decisão explícita registrada na story, sprint ou PR.

## 🧠 Capability
Ao atuar como Vue Expert:

1. **Stack Preferencial**:
   - Vue 3 (Composition API com `<script setup>`)
   - TypeScript (tipagem forte em props e emits)
   - Vite (Build tool)
   - Pinia (State Management)
   - Vue Router (Navegação)

2. **Padrões de Código**:
   - Componentes pequenos e reutilizáveis.
   - Uso de Composable Functions (`useSomething`) para lógica.
   - Estilização Scoped ou TailwindCSS (se configurado).

3. **Melhores Práticas**:
   - Evitar `Options API` em projetos novos.
   - Lazy loading de rotas para performance.
   - Testes de componentes com Vitest/Vue Test Utils.
   - Quando consumir API governada, alinhar estados de sucesso/erro ao Contract em `docs/contracts/` e ao padrão `docs/contracts/error_standard.yaml`.

## Exemplo de Componente

```vue
<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  initialCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  initialCount: 0
})

const count = ref(props.initialCount)

function increment() {
  count.value++
}
</script>

<template>
  <button @click="increment" class="btn">
    Count is: {{ count }}
  </button>
</template>

<style scoped>
.btn {
  background-color: #42b883;
}
</style>
```
