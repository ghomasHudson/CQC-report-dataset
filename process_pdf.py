import re
import json
from extractPages import extract_wrapper,extract_wrapper_outline
from pathlib import Path
import os
import glob

def clean_page_heading(heading):
    heading = re.sub("\s+"," ",heading)
    heading = heading.replace("<h1>","")
    heading = heading.replace("</h1>","")
    return heading.strip()


def merge_headings(text):
    ''' Merges headings which begin with lowercase letter'''
    chunks = []
    sSplit = text.split("<h1>")
    for i,s in enumerate(sSplit[1:]):
        hSplit = s.split("</h1>")
        chunks.append(("heading",hSplit[0],re.match("^\W*[A-Z]",hSplit[0])))
        if not re.match("^\W$",hSplit[1]):
            chunks.append(("text",hSplit[1],None))

    output = sSplit[0]
    in_heading = False
    for i in range(len(chunks)):
        chunk = chunks[i]
        print(chunk)
        if chunk[0] == "heading":
            if not in_heading or chunk[2]:
                output += "\n\n<h1>"
            in_heading = True
            output += chunk[1]
            if i+1>=len(chunks) or chunks[i+1][0] == "text" or chunks[i+1][2]:
                output += "</h1>\n"
        else:
            output += chunk[1]
            in_heading = False
    return output



def extract(filename,areas):
    '''Extract text and scores from pdf'''
    # *************************************
    # Pass 1 - Get document structure
    # *************************************
    text = extract_wrapper_outline(open(filename,'rb'))
    #text = re.sub("\*\*","",text)
    text = re.sub("\# ","",text)
    text = re.sub("\n[\n\s]+","\n",text)
    text = re.split("Page \d+",text)

    #Remove first 2 pages
    text = text[2:]
    page_headings = [""]
    output = {}

    reached_detailed_findings = False

    # Get ratings
    for page in text:
        page = page.replace("<h1>","")
        page = page.replace("</h1>","")
        pSplit = page.split("\n")
        page_headings.append(clean_page_heading(page))
    '''
    # Create map of page numbers
    page_numbers_map = {}
    for i,heading in enumerate(page_headings):
        page_numbers_map[heading] = page_numbers_map.get(heading,[]) + [i]

    # Fill any gaps
    for heading in page_numbers_map.keys():
        nums = page_numbers_map[heading]
        page_numbers_map[heading] = list(range(min(nums),max(nums)+1))
    '''

    # *************************************
    # Pass 2 - Get text
    # *************************************
    for service in areas:
        page_numbers = []

        # Find matching page nums
        service_name_stripped = re.sub(r'\W+', '', service["name"])
        for i,heading in enumerate(page_headings):
            heading = re.sub(r'\W+', '', heading)
            if service_name_stripped in heading:
                page_numbers += [i]
        if page_numbers == []:
            print("Cant find section: '"+service["name"]+"' - SKIPPED")
        else:
            print("Writing",service["name"])
            # Fill any gaps
            page_numbers = list(range(min(page_numbers),max(page_numbers)+1))

            data = extract_wrapper(open(filename,'rb'),page_numbers=page_numbers)

            #Fix break lines in titles
            # If new line begins with capital letter - subtitle
            # else a long title with line break
            '''
            print(data)
            data = re.split("<h1>",data)
            for i in range(len(data)):
                dSplit = data[i].split("</h1>",1) # just get the title (strip of the continuing text)
                title = dSplit[0] # select the title bit
                title = title.replace("•","")
                title = re.sub("\n*([A-Z].*)","</h1><h1>\g<1>",title) #
                data[i] = "</h1>".join([title]+dSplit[1:]) # join the continuing text back on
                breakpoint()
            data = "<h1>".join(data)
            '''


            data = data.replace("\n"," ").strip()
            data = re.sub("\s+"," ",data)
            data = merge_headings(data)

            data = data.replace("<h1>","\n\n# ")
            data = data.replace("</h1>","\n")
            data = data.replace("•","\n- ")
            data = re.sub(re.compile(r"-\W*\n\n",re.MULTILINE),"\n",data)
            data = re.sub("\n\n\n","\n",data)
            data = data.replace("–","")
            data = re.sub("We had not previously rated \w*\.","",data)
            data = re.sub("We had not rated \w*\.","",data)
            data = re.sub("Our rating of this service*.\.","",data)
            data = re.sub(re.compile(r'Our rating of.*stayed the same',re.MULTILINE),"\n",data)
            data = re.sub(re.compile(r'We (had)? rated.*as\W*#.*[\.:]',re.MULTILINE),"\n",data)
            data = re.sub(re.compile(r'We (had)? rated.*as[a-zA-Z\s\n]*[\.:]',re.MULTILINE),"\n",data)
            data = re.sub(re.compile(r'Safe Effective Caring Responsive Well-led',re.MULTILINE),"\n",data)


            SEARCH_STRINGS = ["rated it as", "was now rated as"]
            for search_string in SEARCH_STRINGS:
                new_data = []
                skip = False
                for line in data.split("\n"):
                    if search_string in line:
                        sents = line.split(".")
                        good_sents = []
                        for sent in sents:
                            if search_string not in sent:
                                good_sents.append(sent)
                            else:
                                print("REMOVED:",sent)
                        new_data.append(".".join(good_sents))
                        skip = True
                    elif skip and line != "":
                        skip = False
                    else:
                        new_data.append(line)
                data = "\n".join(new_data)

            if "requires improvement" in data.lower():
                print("WARNING: 'requires improvements' found")

            ratings = ["Outstanding","Good","Requires improvement", "Inadequate"]
            for rating in ratings:
                data = data.replace(rating,"<RATING>")

            service_text = data

            output[service["name"]] = service_text.strip()

    return output

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process pdfs')
    parser.add_argument('input_dir', metavar='F', type=str,help='PDf file')
    args = parser.parse_args()

    for filepath in glob.iglob(os.path.join(args.input_dir,"*.pdf")):
        try:
            areas = json.load(open(filepath[:-4]+".labels"))
            filename = Path(filepath).name
            print(filename)
            text = extract(filepath,areas)
            for k in text.keys():
                open(filepath[:-4]+"."+k.replace(" ","_")+".txt",'w').write(text[k])
        except Exception as e:
            print("Some ERR",e)
