def parse_netscan(path):

    connections=[]


    with open(
        path,
        "r",
        errors="ignore"
    ) as f:


        for line in f:


            if "TCP" not in line:

                continue


            parts=line.split()


            connections.append({

                "protocol":parts[0],

                "local":parts[1],

                "remote":parts[2],

                "state":parts[3]

            })


    return connections