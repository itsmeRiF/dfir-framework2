from modules.memory.volatility_runner import run_volatility


result = run_volatility(

    memory_file="sample_memory/abc.raw",

    output_dir="sample_memory/output",

    volatility_path="K:\\CyberX-DFIR-framework2\\dfir-framework2\\tools\\volatility3"

)


print("\nRESULT:")
print(result)