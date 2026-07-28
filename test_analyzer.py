from modules.memory.analyzer import analyze_memory
import json


result = analyze_memory(
    "sample_memory/output"
)


print(
    json.dumps(
        result,
        indent=4
    )
)