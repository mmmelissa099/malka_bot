import uuid

from agent import agent


def main():
    # Un thread_id nuevo por cada vez que arrancas la demo, asi cada
    # corrida empieza sin el historial de la vez anterior.
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("=" * 50)
    print("Bot de Instagram - Cabana Apicola Malka (demo local)")
    print("=" * 50)
    print("Escribi tu mensaje como si fueras un cliente.")
    print("Para salir: 'salir', 'exit', o Ctrl+C\n")

    while True:
        try:
            mensaje = input("Cliente: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nDemo finalizada.")
            break

        if mensaje.lower() in ("salir", "exit", "quit"):
            print("\nDemo finalizada.")
            break

        if not mensaje:
            continue

        try:
            resultado = agent.invoke(
                {"messages": [{"role": "user", "content": mensaje}]},
                config=config,
            )
            respuesta = resultado["messages"][-1].content
            print(f"Bot:     {respuesta}\n")
        except Exception:
            print(
                "Bot:     Disculpá, tuve un problema procesando eso. "
                "¿Podés reformular la pregunta?\n"
            )


if __name__ == "__main__":
    main()