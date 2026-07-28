import os



def find_output_file(output_dir, keywords):

    if not output_dir or not os.path.exists(output_dir):
        return None


    for file in os.listdir(output_dir):

        filename = file.lower()


        for keyword in keywords:

            if keyword.lower() in filename:

                return os.path.join(
                    output_dir,
                    file
                )


    return None




def read_file(path):

    if not path:
        return []


    if not os.path.exists(path):
        return []


    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        return f.readlines()




def analyze_processes(path):

    processes=[]


    for line in read_file(path):

        line=line.strip()


        if not line:
            continue


        if line.startswith("Volatility"):
            continue


        if line.startswith("PID"):
            continue


        parts=line.split()


        if len(parts)<3:
            continue


        try:

            pid=int(parts[0])
            ppid=int(parts[1])


            processes.append({

                "pid": pid,

                "ppid": ppid,

                "name": parts[2]

            })


        except:

            continue


    return processes




def analyze_network(path):

    network=[]


    for line in read_file(path):

        line=line.strip()


        if not line:
            continue


        if line.startswith("Volatility"):
            continue


        if line.startswith("Offset"):
            continue


        parts=line.split()


        if len(parts)<7:
            continue


        try:

            network.append({

                "protocol": parts[1],

                "local":
                    f"{parts[2]}:{parts[3]}",

                "remote":
                    f"{parts[4]}:{parts[5]}",

                "state":
                    parts[6]

            })


        except:

            continue



    return network



def analyze_malfind(path):

    findings=[]


    for line in read_file(path):

        line=line.strip()


        if not line:
            continue


        if line.startswith("Volatility"):
            continue


        if line.startswith("PID"):
            continue


        parts=line.split()


        if len(parts)<6:
            continue


        try:

            pid=int(parts[0])


            findings.append({

                "pid": pid,

                "process": parts[1],

                "protection":
                    " ".join(parts[5:7])

            })


        except:

            continue



    return findings



def count_entries(path, headers):

    count=0


    for line in read_file(path):

        line=line.strip()


        if not line:
            continue


        if line.startswith("Volatility"):
            continue


        skip=False


        for h in headers:

            if line.startswith(h):
                skip=True


        if skip:
            continue


        count+=1


    return count





def analyze_memory(output_dir):




    process_file = find_output_file(
        output_dir,
        [
            "pslist",
            "process"
        ]
    )


    network_file = find_output_file(
        output_dir,
        [
            "netstat",
            "netscan",
            "network"
        ]
    )


    dll_file = find_output_file(
        output_dir,
        [
            "dlllist",
            "dll"
        ]
    )


    malfind_file = find_output_file(
        output_dir,
        [
            "malfind"
        ]
    )


    driver_file = find_output_file(
        output_dir,
        [
            "driverscan",
            "driver"
        ]
    )


    service_file = find_output_file(
        output_dir,
        [
            "svcscan",
            "service"
        ]
    )




    processes = analyze_processes(
        process_file
    )


    network = analyze_network(
        network_file
    )


    malfind = analyze_malfind(
        malfind_file
    )



    summary={

        "process_count":
            len(processes),


        "network_count":
            len(network),


        "malfind_count":
            len(malfind),


        "dll_count":
            count_entries(
                dll_file,
                [
                    "PID"
                ]
            ),


        "driver_count":
            count_entries(
                driver_file,
                [
                    "Offset"
                ]
            ),


        "service_count":
            count_entries(
                service_file,
                [
                    "Offset"
                ]
            )

    }




    risk_score=0


    suspicious_processes=[]


    risk_score += (
        len(malfind) * 5
    )



    suspicious_names=[

        "powershell.exe",

        "cmd.exe",

        "rundll32.exe",

        "regsvr32.exe",

        "mshta.exe",

        "wscript.exe",

        "cscript.exe"

    ]



    for process in processes:


        name=process["name"].lower()


        if name in suspicious_names:


            suspicious_processes.append(
                process
            )


            risk_score += 10




    return {


        "summary": summary,


        "risk_score": risk_score,


        "processes": processes,


        "network": network,


        "malfind": malfind,


        "suspicious_processes":
            suspicious_processes

    }