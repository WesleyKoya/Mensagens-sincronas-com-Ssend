"""
Prática 4 - Mensagens síncronas com Ssend (MPI / mpi4py).

Objetivo
--------
Demonstrar, com exatamente dois processos, que Ssend() é um envio
SÍNCRONO: a chamada só retorna depois que o Recv correspondente foi
iniciado pelo destinatário.

Como o experimento funciona
---------------------------
* O rank 1 espera 'atraso' segundos ANTES de chamar Recv.
* O rank 0 chama Ssend imediatamente e mede quanto tempo a chamada demora
  para retornar. Esse tempo deve ser aproximadamente igual ao atraso.
* Em seguida o rank 1 responde (2·valor + 1) com outro Ssend, usando outra
  tag, e o rank 0 confere a resposta.

Execução
--------
    mpiexec -n 2 python pratica4_mensagens_sincronas.py --valor 35 --atraso 1.5
"""

import argparse
import time

import numpy as np

try:
    from mpi4py import MPI
except ImportError as erro:
    raise SystemExit(
        "A biblioteca mpi4py não foi encontrada.\n"
        "Instale com:  pip install mpi4py\n"
        "e verifique se há uma implementação MPI (MS-MPI, OpenMPI ou MPICH)."
    ) from erro


TAG_IDA = 101      # mensagem de ida:   rank 0 -> rank 1
TAG_VOLTA = 202    # mensagem de volta: rank 1 -> rank 0


def registrar(mensagem):
    """Imprime a linha inteira de uma só vez (evita mistura entre ranks)."""
    print(mensagem + "\n", end="", flush=True)


def calcular_resposta(valor):
    """Cálculo feito apenas pelo rank 1: 2·valor + 1."""
    return 2 * valor + 1


def ler_argumentos():
    parser = argparse.ArgumentParser(
        description="Demonstração de envio síncrono (Ssend) com MPI."
    )
    parser.add_argument("--valor", type=int, default=21,
                        help="Valor enviado pelo rank 0 (padrão: 21).")
    parser.add_argument("--atraso", type=float, default=1.0,
                        help="Segundos que o rank 1 espera antes de chamar "
                             "Recv (padrão: 1.0).")
    args = parser.parse_args()
    if args.atraso < 0:
        parser.error("--atraso deve ser maior ou igual a zero")
    return args


def main():
    args = ler_argumentos()

    comunicador = MPI.COMM_WORLD
    rank = comunicador.Get_rank()
    total_processos = comunicador.Get_size()

    # O experimento só faz sentido com exatamente 2 processos.
    if total_processos != 2:
        if rank == 0:
            registrar(f"[ERRO] Este programa exige exatamente 2 processos "
                      f"(recebeu {total_processos}).\n"
                      "       Use: mpiexec -n 2 python "
                      "pratica4_mensagens_sincronas.py")
        return

    # Alinha os dois processos antes de começar.
    comunicador.Barrier()

    if rank == 0:
        buffer_envio = np.array([args.valor], dtype=np.int64)
        registrar(f"[rank 0] Tentando enviar {args.valor} com Ssend...")

        t_inicio = MPI.Wtime()
        comunicador.Ssend([buffer_envio, MPI.INT64_T], dest=1, tag=TAG_IDA)
        t_bloqueio = MPI.Wtime() - t_inicio
        registrar(f"[rank 0] Ssend retornou após {t_bloqueio:.3f} s.")

        buffer_resposta = np.empty(1, dtype=np.int64)
        comunicador.Recv([buffer_resposta, MPI.INT64_T], source=1, tag=TAG_VOLTA)
        resposta = int(buffer_resposta[0])
        esperado = calcular_resposta(args.valor)

        registrar(f"[rank 0] Resposta recebida: {resposta}.")
        registrar(f"[rank 0] Conferência: {resposta == esperado}")
        registrar(f"[rank 0] Bloqueio >= atraso configurado? "
                  f"{t_bloqueio >= args.atraso * 0.95}")

    else:  # rank 1
        registrar(f"[rank 1] Esperando {args.atraso:.2f} s ANTES de chamar Recv...")
        time.sleep(args.atraso)

        buffer_recebido = np.empty(1, dtype=np.int64)
        comunicador.Recv([buffer_recebido, MPI.INT64_T], source=0, tag=TAG_IDA)
        valor_recebido = int(buffer_recebido[0])
        registrar(f"[rank 1] Mensagem recebida: {valor_recebido}.")

        resultado = calcular_resposta(valor_recebido)
        registrar(f"[rank 1] Enviando de volta {resultado} com Ssend...")
        buffer_volta = np.array([resultado], dtype=np.int64)
        comunicador.Ssend([buffer_volta, MPI.INT64_T], dest=0, tag=TAG_VOLTA)
        registrar("[rank 1] Resposta entregue.")


if __name__ == "__main__":
    main()
