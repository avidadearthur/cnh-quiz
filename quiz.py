#!/usr/bin/env python3
"""CLI quiz for the CNH (Banco Nacional de Questões) question bank.

Picks questions using weighted selection — wrong/unseen questions surface
more often. Progress is persisted in data/stats.json across sessions.
Each question shows its módulo and dificuldade, then the shuffled
alternatives (a/b/c/d...). After answering, prints whether the user was
right or wrong and shows the comentário.
"""
import json
import random
import string
import sys
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "questoes.json"
STATS_PATH = Path(__file__).parent / "data" / "stats.json"


def load_questions():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_stats():
    if STATS_PATH.exists():
        with open(STATS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_stats(stats):
    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def question_weight(qid, stats):
    s = stats.get(qid)
    if not s or s["seen"] == 0:
        return 2.0  # unseen: medium-high priority
    error_rate = 1 - s["correct"] / s["seen"]
    return 1 + 2 * error_rate  # range [1.0, 3.0]


def ask_question(q):
    print("\n" + "=" * 70)
    print(f"[{q['modulo']}] - Dificuldade: {q['dificuldade']}")
    if q.get("codigo_placa"):
        print(f"Código da placa: {q['codigo_placa']}")
    print(f"\n{q['pergunta']}\n")

    alternativas = [q["alternativa_correta"]] + list(q["alternativas_incorretas"])
    random.shuffle(alternativas)
    correta_idx = alternativas.index(q["alternativa_correta"])
    letras = string.ascii_lowercase[: len(alternativas)]

    for letra, alt in zip(letras, alternativas):
        print(f"  {letra}) {alt}")

    while True:
        resp = input(f"\nResposta ({'/'.join(letras)}, ou 'q' para sair): ").strip().lower()
        if resp == "q":
            return None
        if resp in letras:
            break
        print("Entrada inválida, tente novamente.")

    acertou = resp == letras[correta_idx]
    if acertou:
        print("\n✔ Correto!")
    else:
        print(f"\n✘ Errado! A resposta correta era: {letras[correta_idx]}) {q['alternativa_correta']}")

    if q.get("comentario"):
        print(f"\nComentário: {q['comentario']}")

    return acertou


def main():
    questions = load_questions()
    stats = load_stats()
    by_id = {str(q["id"]): q for q in questions}
    all_ids = list(by_id.keys())

    acertos = 0
    total = 0
    pool = list(all_ids)

    print("Quiz CNH - Banco Nacional de Questões")
    print("Digite 'q' a qualquer momento para sair.\n")

    while True:
        if not pool:
            pool = list(all_ids)
            print("\n[Todas as questões respondidas nesta sessão — reiniciando!]\n")

        weights = [question_weight(qid, stats) for qid in pool]
        (qid,) = random.choices(pool, weights=weights, k=1)
        pool.remove(qid)
        q = by_id[qid]

        result = ask_question(q)
        if result is None:
            break
        total += 1
        if result:
            acertos += 1

        s = stats.setdefault(qid, {"seen": 0, "correct": 0})
        s["seen"] += 1
        if result:
            s["correct"] += 1

        print(f"\nSessão: {acertos}/{total} ({acertos / total:.0%})")

    save_stats(stats)

    print("\n" + "=" * 70)
    if total:
        print(f"Você acertou {acertos}/{total} ({acertos / total:.0%})")
    print("Até a próxima!")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nSaindo...")
        sys.exit(0)
