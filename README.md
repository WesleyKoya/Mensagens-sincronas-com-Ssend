# Prática 4 — Mensagens síncronas com `Ssend` (MPI)

Programa em **Python + mpi4py** que demonstra, com **exatamente dois processos**, o comportamento do envio
**síncrono** `Ssend()`: a chamada só termina depois que o `Recv` correspondente foi iniciado pelo destinatário.

> Disciplina: Programação de Aplicações de Alto Desempenho — Engenharia da Computação — Universidade Veiga de Almeida (UVA)
> Aluno: Wesley Coutinho da Silva

## Como funciona

- **Rank 1** espera `--atraso` segundos (`time.sleep`) **antes** de chamar `Recv`.
- **Rank 0** chama `Ssend` imediatamente e mede, com `MPI.Wtime()`, quanto tempo a chamada demora para retornar.
  Como o `Ssend` só conclui quando o `Recv` começa, esse tempo é aproximadamente igual ao atraso configurado.
- O rank 1 calcula `2 · valor + 1` e devolve o resultado ao rank 0 com outro `Ssend`, usando outra **tag**.
- O rank 0 recebe a resposta e confere o valor.

| Constante   | Valor | Uso |
|-------------|-------|-----|
| `TAG_IDA`   | 101   | Mensagem rank 0 → rank 1 |
| `TAG_VOLTA` | 202   | Mensagem rank 1 → rank 0 |

Os buffers são arrays NumPy `int64`, enviados com o tipo MPI `MPI.INT64_T` (métodos com inicial maiúscula do mpi4py).

### Por que não há deadlock?

A ordem das chamadas é **complementar**: rank 0 faz `Ssend` → `Recv`; rank 1 faz `Recv` → `Ssend`.
Se os dois chamassem `Ssend` primeiro, ambos ficariam bloqueados esperando um `Recv` que nunca seria executado.

## Requisitos

- Python 3.8+
- Uma implementação MPI instalada:
  - **Windows:** [Microsoft MPI (MS-MPI)](https://learn.microsoft.com/message-passing-interface/microsoft-mpi) — *Runtime* e *SDK*
  - **Linux (Debian/Ubuntu):** `sudo apt install openmpi-bin libopenmpi-dev`
  - **macOS:** `brew install open-mpi`
- Bibliotecas Python:

```bash
pip install -r requirements.txt
```

## Execução

```bash
mpiexec -n 2 python pratica4_mensagens_sincronas.py --valor 35 --atraso 1.5
```

| Argumento  | Descrição | Padrão |
|------------|-----------|--------|
| `--valor`  | Valor inteiro enviado pelo rank 0. | 21 |
| `--atraso` | Segundos que o rank 1 espera antes de chamar `Recv` (≥ 0). | 1.0 |
| `-n` (mpiexec) | **Deve ser 2.** Com outro valor o programa exibe um erro e encerra. | — |

## Exemplo de saída

`mpiexec -n 2 python pratica4_mensagens_sincronas.py --valor 35 --atraso 1.5`

```text
[rank 1] Esperando 1.50 s ANTES de chamar Recv...
[rank 0] Tentando enviar 35 com Ssend...
[rank 1] Mensagem recebida: 35.
[rank 1] Enviando de volta 71 com Ssend...
[rank 0] Ssend retornou após 1.500 s.
[rank 0] Resposta recebida: 71.
[rank 0] Conferência: True
[rank 0] Bloqueio >= atraso configurado? True
[rank 1] Resposta entregue.
```

A resposta `71` vem de `2·35 + 1`. O tempo de bloqueio do `Ssend` acompanha o atraso do receptor.
A ordem das linhas entre rank 0 e rank 1 pode variar, pois os processos imprimem de forma independente.

### Validação do número de processos

`mpiexec -n 3 python pratica4_mensagens_sincronas.py --valor 7 --atraso 0.5`

```text
[ERRO] Este programa exige exatamente 2 processos (recebeu 3).
       Use: mpiexec -n 2 python pratica4_mensagens_sincronas.py
```

## Observações

- A espera do remetente no `Ssend` é tempo ocioso. Em aplicações reais, o envio síncrono é indicado quando se quer
  garantia de que o destinatário iniciou a recepção; para sobrepor comunicação e computação, use `Isend`/`Irecv`.
- Com o envio padrão (`Send`) e mensagem pequena, é comum a chamada retornar quase instantaneamente graças ao
  buffer interno do MPI; com `Ssend`, isso não ocorre.

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `pratica4_mensagens_sincronas.py` | Código-fonte da prática |
| `requirements.txt` | Dependências Python |
| `README.md` | Este arquivo |
