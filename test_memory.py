from modules.memory.analyzer import analyze_memory


data = analyze_memory(
    "sample_memory/output"
)


print(data["summary"])


print("\nMalfind:")
for item in data["malfind"][:5]:
    print(item)