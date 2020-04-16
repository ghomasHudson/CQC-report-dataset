import re
import json
from extractPages import extract_wrapper,extract_wrapper_outline
from pathlib import Path


def extract(filename):
    '''Extract text and scores from pdf'''
    output = {}
    # *************************************
    # Pass 1 - Get document structure
    # *************************************
    text = extract_wrapper_outline(open(filename,'rb'))
    text = re.sub("\*\*","",text)
    text = re.sub("\n[\n\s]+","\n",text)
    text = re.split("Page \d+",text)

    #Remove first 2 pages
    text = text[2:]
    page_headings = []
    output = {}

    # Get ratings
    for page in text:
        if page.count("\n") > 5:
            # Is a ratings table
            pSplit = page[1:].split("\n")
            table_index = pSplit.index("Safe")
            page_heading = " ".join(pSplit[:table_index])
            pSplit = pSplit[table_index:]
            pSplit = [p for p in pSplit if p!= ""]
            questions = pSplit[:int(len(pSplit)/2)]
            answers = pSplit[int(len(pSplit)/2):]

            questions = [q.strip() for q in questions]
            answers = [a.strip() for a in answers]

            output[page_heading] = dict(zip(questions,answers))
            page_headings.append("SECTION")
        else:
            # Is a page heading
            page_headings.append(page.replace("\n"," ").strip())

    # Create map of page numbers
    page_numbers_map = {}
    for k in output:
        page_numbers_map[k] = [i for i,x in enumerate(page_headings) if x == k]


    # *************************************
    # Pass 2 - Get text
    # *************************************
    for service in page_numbers_map.keys():
        print(service,page_numbers_map[service])
        data = extract_wrapper(open(filename,'rb'),page_numbers=page_numbers_map[service])

        data = data.replace("\n\n**","**")
        data = [data]
        service_text = ""
        for chunk in data:
            points = chunk.split("•")
            for p in points:
                pSplit = p.split("**",1)
                if len(pSplit) > 1:
                    p,title = pSplit
                p = p.replace("\n"," ").strip()
                p = re.sub("\s+"," ",p)
                if p != '':
                    service_text += "- "+p+"\n"
                if len(pSplit) > 1:
                    title = title[:-2].replace("\n"," ").replace("*","").replace("–","").strip()
                    service_text += "\n# "+title+"\n"

        output[service] = {"ratings":output[service],"text":service_text.strip()}
    return output

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process pdfs')
    parser.add_argument('filename', metavar='F', type=str,
                        help='PDf file')

    args = parser.parse_args()
    filename = args.filename
    output_dir = "output"
    stem = Path(filename).stem
    data = extract(filename)
    for k in data:
        open(output_dir+"/"+stem+"."+k.replace(" ","_")+".txt",'w').write(data[k]["text"])
        open(output_dir+"/"+stem+"."+k.replace(" ","_")+".labels",'w').write(json.dumps(data[k]["ratings"]))
