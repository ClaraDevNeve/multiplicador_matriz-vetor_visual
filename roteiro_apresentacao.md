# Roteiro de Apresentação

**Projeto:** Multiplicador Matriz-Vetor Visual  
**Tempo estimado:** 10-15 minutos

---

## Dymitre Tyziano Matos de Arruda (2 min)

### 1. Contextualização
- **Saudação e apresentação do grupo**
- **Contextualização:**
  - O que é multiplicação matriz-vetor?
  - Onde é usada (álgebra linear, computação gráfica, machine learning, redes neurais)
  - Importância no currículo de computação/matemática
  - Por que uma visualização passo a passo é útil para o aprendizado

---

## Luiz Fernando (3 min)

### 2. Objetivo e Fundamentação Matemática
- **Objetivo do projeto:**
  - Demonstrar visualmente cada etapa do cálculo matriz-vetor
  - Facilitar a compreensão do processo matemático
- **Explicação matemática:**
  - Fórmula: `b[i] = Σ(a[i][j] × x[j])`
  - Cada elemento do resultado é o produto interno de uma linha da matriz pelo vetor
  - Demonstrar com exemplo numérico simples (ex: 2×2 na lousa ou papel)
  - Mostrar passo a passo manualmente antes do programa
- **Por que visualizar:**
  - Abstracão matemática vs. visualização concreta
  - Identificar padrões e compreender o fluxo de dados

---

## Maria Clara Neves Gomes (4-5 min) — Parte mais cobrada

### 3. Explicação do Código
- **Visão geral da arquitetura:**
  - Linguagem: Python 3
  - Biblioteca: Tkinter (GUI nativa)
  - Estrutura orientada a objetos

- **Classes principais (explicar com código na tela):**
  - **`Celula`:** Widget customizado para input numérico
    - Herda de `tk.Frame`
    - Gerencia `StringVar` e validação
    - Métodos: `get()`, `set()`, `highlight()`, `readonly()`
  - **`Grade`:** Container de células organizadas em matriz
    - Renderiza colchetes visuais `[ ]`
    - Métodos: `get_dados()`, `set_dados()`, `limpar_highlights()`
  - **`App`:** Janela principal e fluxo da aplicação
    - Construção da UI (`_build_ui`)
    - Lógica de cálculo (`multiplicar_matriz_vetor`)
    - Controle de estado (`passo_atual`, `passos`)

- **Destaques técnicos do código:**
  - Separação lógica/UI (função `multiplicar_matriz_vetor` pura)
  - Sistema de "passos" para navegação
  - Dicionário de configuração de cores (paleta temática)
  - Tratamento de entrada (vírgula vs. ponto)

---

## Vinicius Antony Silva Pereira (2-3 min)

### 4. Demonstração Visual e Execução
- **Execução ao vivo:**
  - Rodar o programa: `python matriz_vetor.py`
  - Interface em tela cheia/projeção

- **Demonstração interativa:**
  - Mostrar valores padrão (3×3)
  - Explicar destaques de cores:
    - 🔵 Azul: linha da matriz sendo calculada
    - 🟠 Âmbar: elementos do vetor correspondentes
    - 🟢 Verde: resultado do elemento atual
  - Clicar em "Calcular" e navegar pelos passos
  - Mostrar a fórmula atualizada em cada passo

- **Recursos adicionais:**
  - Mudar tamanho da matriz (2×2, 3×3, 4×4)
  - Inserir valores manualmente
  - Botão "Aleatório" e "Limpar"

- **Conclusão:**
  - Recapitular valor educacional
  - Abrir para perguntas

---

## Dicas para a Apresentação

1. **Teste antes:** Execute o programa (`python matriz_vetor.py`) para garantir que tudo funciona
2. **Valores preparados:** Tenha alguns exemplos numéricos simples caso precise demonstrar rapidamente
3. **Interaja:** Peça para alguém da audiência sugerir valores para testar ao vivo
4. **Destaque visual:** Explique as cores logo no início — elas são o diferencial do projeto

---

## Checklist Pré-Apresentação

- [ ] Projeto clonado/aberto no computador de apresentação
- [ ] Python instalado e funcionando
- [ ] Tela/configuração de projeção testada
- [ ] Resolução da janela ajustada para ser visível à distância
