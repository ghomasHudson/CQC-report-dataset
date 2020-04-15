from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

i = 0
done = {}
prev = None
for page_layout in extract_pages("AAAH0830.pdf"):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                try:
                    for character in text_line:
                        i += 1
                        if hasattr(character, 'fontname'):
                            key = (character.fontname,character.size)
                            if prev != key:
                                done[key] = done.get(key,[""]) + [""]

                            l =  done.get(key,[""])
                            l[-1] = l[-1] + character._text
                            done[key] = l
                            prev = key
                            if i>99999999999:
                                import sys;sys.exit()
                except TypeError:
                    pass

for k in done:
    print(k,done[k])
for k in done:
    print(k)
breakpoint()
