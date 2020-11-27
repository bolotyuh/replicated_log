from asyncio import events, ensure_future


async def wait_n(fs, *, loop=None, n=1):
    if loop is None:
        loop = events.get_event_loop()

    fs = {ensure_future(f, loop=loop) for f in set(fs)}

    waiter = loop.create_future()

    if n > len(fs):
        raise ValueError('arg `n` can`t be bigger than count of tasks')

    counter = len(fs)
    completed_count = 0

    def _on_completion(f):
        nonlocal counter
        nonlocal completed_count
        counter -= 1
        completed_count += 1

        if counter <= 0 or completed_count >= n:
            if not waiter.done():
                waiter.set_result(None)

    for f in fs:
        f.add_done_callback(_on_completion)

    try:
        await waiter
    finally:
        for f in fs:
            f.remove_done_callback(_on_completion)

    done, pending = set(), set()
    for f in fs:
        if f.done():
            done.add(f)
        else:
            pending.add(f)
    return done, pending
