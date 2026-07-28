def parse_pslist(path):

    processes=[]


    with open(
        path,
        "r",
        errors="ignore"
    ) as f:


        for line in f:


            if line.startswith("PID"):

                continue


            parts=line.split()


            if len(parts)>=4:


                processes.append({

                    "pid":parts[0],

                    "name":parts[1],

                    "ppid":parts[2],

                    "threads":parts[3]

                })


    return processes