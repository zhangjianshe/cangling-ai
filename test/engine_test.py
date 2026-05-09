from cangling.engine.imagebot_engine import ImageBotEngine, RunningContext


def main():
    context: RunningContext = ImageBotEngine().get_context()
    step_count: int = 3
    context.node_begin("Hello test")

    for step in range(step_count):
        context.step_begin(format(f"STEP{step}"), step)
        context.step_message(step, format("message from step{step} message"))
        for progress in range(10):
            context.step_progress(step, progress)
        context.step_end(step, True, format(f"STEP{step} END"))
    context.write("NAME", "ZhangJianshe")
    context.write("AGE", str(18))
    context.node_end(True)


if __name__ == "__main__":
    main()
