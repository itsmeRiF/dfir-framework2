from modules.parser.engines.hayabusa import HayabusaEngine


evtx_file = r"sample_memory\Security.evtx"


events = HayabusaEngine.parse(
    evtx_file
)

print(
    events[:2]
)
print(
    "Events:",
    len(events)
)


if events:
    print(
        events[0]
    )