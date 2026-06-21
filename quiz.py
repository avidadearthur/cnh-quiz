#!/usr/bin/env python3
"""CLI quiz for the CNH (Banco Nacional de Questões) question bank.

Picks random questions until the user quits ('q'). Each question shows
its módulo and dificuldade, then the shuffled alternatives (a/b/c/d...).
After answering, prints whether the user was right or wrong and shows
the comentário.
"""
import json
import random
import string
import sys
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "questoes.json"


def load_questions():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


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
    acertos = 0
    total = 0

    print("Quiz CNH - Banco Nacional de Questões")
    print("Digite 'q' a qualquer momento para sair.\n")

    while True:
        q = random.choice(questions)
        result = ask_question(q)
        if result is None:
            break
        total += 1
        if result:
            acertos += 1

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
