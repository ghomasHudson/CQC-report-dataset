#import html
import re
from extractPages import extract_wrapper


data = extract_wrapper(open("AAAH0830.pdf",'rb'))

# Get footer
'''
footer = data.split("\x0c",1)[0].strip() # get first page
footer = footer.split("\n")[-1] # last line
footer = footer[2:] # remove page number]
#   Make footer regex
footer_regex = re.compile('\d+\s+'+footer)
#   Remove instances
data = footer_regex.sub("",data)
'''
data = data.replace("\n\n**","**")

#data = html.unescape(data)
data = data[data.index("Our ratings for this location are"):]
data = data[data.index("\x0c"):]
#data = [d for d in data.split("–––") if "•" in d]
data = [data]
for chunk in data[:1]:
    points = chunk.split("•")
    for p in points:
        #print("-----------------------")
        pSplit = p.split("**",1)
        if len(pSplit) > 1:
            p,title = pSplit
        # titles = re.findall(r'\.\n\n\w+',p)
        # for t in titles:
        #     breakpoint()
        p = p.replace("\n"," ").strip()
        p = re.sub("\s+"," ",p)
        print("-",p)
        if len(pSplit) > 1:
            title = title[:-2].replace("\n"," ").replace("*","").replace("–","").strip()
            print("\n\n#",title)


# TODO: Idea
# Make 2 passes
# Pass 1: Get sections and scores
# Pass 2: Get text
