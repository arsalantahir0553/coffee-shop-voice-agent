from . import audio_io, config, llm_client, menu, order_session, stt, tts


def build_system_prompt(session):
    return llm_client.SYSTEM_TEMPLATE.format(
        shop_name=menu.MENU["shop_name"],
        menu_text=menu.menu_as_text(),
        standard_questions="; ".join(menu.MENU["standard_questions"]),
        current_order=session.receipt_text(),
    )


def apply_agent_actions(session, action):
    for item in action.get("add_items", []):
        _, error = session.add_item(
            item.get("drink", ""),
            size=item.get("size"),
            hot_or_iced=item.get("hot_or_iced"),
            milk=item.get("milk"),
            add_on_names=item.get("add_ons", []),
        )
        if error:
            print(f"[warning] {error}")
    if action.get("remove_last_item"):
        session.remove_last()


def run_order_loop():
    print(f"Welcome to {menu.MENU['shop_name']}! Press Ctrl+C to quit.")
    session = order_session.OrderSession()
    history = []

    while True:
        try:
            input("\nPress ENTER, then speak your order...")
        except (EOFError, KeyboardInterrupt):
            break

        audio = audio_io.record_until_silence()
        if audio.size == 0:
            print("Didn't catch anything, try again.")
            continue

        user_text = stt.transcribe(audio)
        if not user_text:
            print("Didn't catch anything, try again.")
            continue
        print(f"You said: {user_text}")

        system_prompt = build_system_prompt(session)
        action, raw = llm_client.get_agent_turn(system_prompt, history, user_text)
        apply_agent_actions(session, action)

        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": raw})

        reply = action.get("reply", "")
        print(f"Agent: {reply}")
        tts.speak(reply)

        if action.get("order_complete"):
            session.log()
            print("\nOrder confirmed and logged:")
            print(session.receipt_text())
            tts.speak(f"Your order has been placed. Thank you for visiting {menu.MENU['shop_name']}!")

            again = input("\nStart a new order? (y/n): ").strip().lower()
            if again != "y":
                break
            session = order_session.OrderSession()
            history = []


if __name__ == "__main__":
    run_order_loop()
