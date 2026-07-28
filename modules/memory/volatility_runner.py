import os
import subprocess
import sys


def run_volatility(
    memory_file,
    output_dir,
    volatility_path
):

    os.makedirs(output_dir, exist_ok=True)


    # ==========================================
    # Resolve volatility executable path
    # ==========================================

    if volatility_path.lower().endswith("vol.py"):

        vol_script = volatility_path

    else:

        vol_script = os.path.join(
            volatility_path,
            "vol.py"
        )


    if not os.path.exists(vol_script):

        raise FileNotFoundError(
            f"Volatility not found: {vol_script}"
        )


    plugins = {

        "processes.txt":
            "windows.pslist.PsList",

        "network.txt":
            "windows.netstat.NetStat",

        "dlls.txt":
            "windows.dlllist.DllList",

        "malfind.txt":
            "windows.malware.malfind.Malfind",

        "drivers.txt":
            "windows.driverscan.DriverScan",

        "services.txt":
            "windows.svcscan.SvcScan"

    }


    results = {}


    for filename, plugin in plugins.items():


        output_file = os.path.join(
            output_dir,
            filename
        )


        cmd = [

            sys.executable,

            vol_script,

            "-f",

            memory_file,

            plugin

        ]


        print("\n==============================")
        print("Running:")
        print(" ".join(cmd))
        print("==============================")


        process = subprocess.run(

            cmd,

            capture_output=True,

            text=True,

            encoding="utf-8",

            errors="ignore"

        )


        # Save complete output

        with open(

            output_file,

            "w",

            encoding="utf-8",

            errors="ignore"

        ) as f:


            f.write(process.stdout)


            if process.stderr:

                f.write(
                    "\n\n===== STDERR =====\n"
                )

                f.write(process.stderr)



        results[
            filename.replace(".txt","")
        ] = output_file


        print(
            plugin,
            "completed",
            "return:",
            process.returncode
        )


        if process.stderr:

            print(
                "Warning/Error:",
                process.stderr[:300]
            )


    return results