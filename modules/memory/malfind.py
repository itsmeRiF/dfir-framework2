def parse_malfind(path):

    findings=[]


    current={}


    with open(
        path,
        "r",
        errors="ignore"
    ) as f:


        for line in f:


            line=line.strip()


            if "Process" in line:

                current["process"]=line


            if "Protection" in line:

                current["protection"]=line



            if current:

                findings.append(current)

                current={}


    return findings