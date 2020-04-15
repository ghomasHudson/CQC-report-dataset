from pdfminer.high_level import extract_pages
from pdfminer.pdfpage import *
from pdfminer.pdfinterp import *
import io
from io import StringIO
from pdfminer.converter import *
from pdfminer.layout import *



class TextConverter(PDFConverter):
    def __init__(self, rsrcmgr, outfp, codec='utf-8', pageno=1, laparams=None,
                 showpageno=False, imagewriter=None):
        PDFConverter.__init__(self, rsrcmgr, outfp, codec=codec, pageno=pageno,
                              laparams=laparams)
        self.showpageno = showpageno
        self.imagewriter = imagewriter
        self.is_bold = False
        return

    def write_text(self, text):
        text = utils.compatible_encode_method(text, self.codec, 'ignore')
        if self.outfp_binary:
            text = text.encode()
        self.outfp.write(text)
        return

    def receive_layout(self, ltpage):
        def render(item):
            if isinstance(item, LTContainer):
                for child in item:
                    render(child)
            elif isinstance(item, LTText):
                if hasattr(item,"fontname"):
                    if "Bold" in item.fontname and item.size == 11.25:
                        if not self.is_bold:
                            #print("\n\n",item.size)
                            self.write_text("**")
                        #print(item.get_text(),end="")
                        self.is_bold = True
                    else:
                        if self.is_bold:
                            self.write_text("**")
                        self.is_bold = False

                bad_item = False
                if hasattr(item, 'size'):
                    to_remove = [

                        ("SourceSansPro-Regular",10.0),
                        ("SourceSansPro-Bold",10.0),
                        ("SourceSansPro-Bold",13.0),
                        ("SourceSansPro-Bold",14.0),
                        ("SourceSansPro-Bold",14.0),
                        ("SourceSansPro-Bold",15.0),
                        ("SourceSansPro-Regular",12.0),
                        ("SourceSansPro-Semibold",10.0),
                        ("SourceSansPro-Regular",26.0),
                        ("SourceSansPro-Light",44.0),
                        ("SourceSansPro-Bold",15.0),
                        ("SourceSansPro-Light",12.0),
                        ('SourceSansPro-Light', 0.0),
                        '''
                        #('SourceSansPro-Light', 44.0),
                        #('SourceSansPro-Regular', 12.0),
                        #('SourceSansPro-Light', 11.25),
                        ('SourceSansPro-Regular', 22.0),
                        ('SourceSansPro-Regular', 16.0),
                        ('SourceSansPro-Regular', 18.0),
                        #('SourceSansPro-Bold', 18.0),
                        ('SourceSansPro-Bold', 16.0),
                        ('SourceSansPro-Regular', 15.000000000000057),
                        ('SourceSansPro-Regular', 15.0),
                        #('SourceSansPro-Bold', 13.0),
                        #('SourceSansPro-Bold', 14.0),
                        ('SourceSansPro-Light', 11.250000000000014),
                        #('SourceSansPro-Bold', 10.0),
                        #('SourceSansPro-Regular', 10.0),
                        #('SourceSansPro-Regular', 26.0),
                        ('SourceSansPro-Bold', 11.25),
                        ('SourceSansPro-Light', 11.249999999999972),
                        #('SourceSansPro-Bold', 15.0),
                        ('SourceSansPro-Regular', 11.0),
                        ('SourceSansPro-Light', 12.0),
                        #('SourceSansPro-Light', 0.0),
                        ('SourceSansPro-Bold', 12.0),
                        ('SourceSansPro-Light', 11.249999999999993),
                        ('SourceSansPro-Bold', 11.249999999999943),
                        ('SourceSansPro-Light', 11.0),
                        ('SourceSansPro-Light', 10.999999999999943),
                        ('SourceSansPro-Light', 10.999999999999986),
                        ('SourceSansPro-Semibold', 10.0),
                        ('SourceSansPro-Light', 10.0),
                        ('SourceSansPro-Light', 11.249999999999943),
                        ('SourceSansPro-Bold', 11.250000000000007),
                        '''
                    ]
                    for x in to_remove:
                        if __name__ == "__main__":
                            pass
                            #print("\t",item._text,x,(item.fontname,item.size))
                        if item.fontname == x[0] and item.size == x[1]:
                            bad_item = True
                            if __name__ == "__main__":
                                pass
                                #print("\tBAD")
                            break

                    if __name__ == "__main__":
                        #print("END\n\n")
                        pass
                if not bad_item:

                    if __name__ == "__main__" and hasattr(item, 'size'):
                        print(item.fontname,item.size)
                        print("\t",item._text)
                    self.write_text(item.get_text())
            if isinstance(item, LTTextBox):
                self.write_text('\n')
            elif isinstance(item, LTImage):
                if self.imagewriter is not None:
                    self.imagewriter.export_image(item)
        if self.showpageno:
            self.write_text('Page %s\n' % ltpage.pageid)
        render(ltpage)
        self.write_text('\f')
        return

    # Some dummy functions to save memory/CPU when all that is wanted
    # is text.  This stops all the image and drawing output from being
    # recorded and taking up RAM.
    def render_image(self, name, stream):
        if self.imagewriter is None:
            return
        PDFConverter.render_image(self, name, stream)
        return

    def paint_path(self, gstate, stroke, fill, evenodd, path):
        return

def extract_text(pdf_file, password='', page_numbers=None, maxpages=0,
                 caching=True, codec='utf-8', laparams=None):
    """Parse and return the text contained in a PDF file.
    :param pdf_file: Either a file path or a file-like object for the PDF file
        to be worked on.
    :param password: For encrypted PDFs, the password to decrypt.
    :param page_numbers: List of zero-indexed page numbers to extract.
    :param maxpages: The maximum number of pages to parse
    :param caching: If resources should be cached
    :param codec: Text decoding codec
    :param laparams: An LAParams object from pdfminer.layout. If None, uses
        some default settings that often work well.
    :return: a string containing all of the text extracted.
    """
    if laparams is None:
        laparams = LAParams()

    with pdf_file as fp, StringIO() as output_string:
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, codec=codec,
                               laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.get_pages(
                fp,
                page_numbers,
                maxpages=maxpages,
                password=password,
                caching=caching,
                check_extractable=True,
        ):
            interpreter.process_page(page)

        return output_string.getvalue()

def extract_wrapper(fp):
    return extract_text(fp,laparams=LAParams(line_margin=2,char_margin=3,boxes_flow=-1))

if __name__ == "__main__":
    text = extract_wrapper(open("AAAH0830.pdf",'rb'))
    print(re.sub(r"\W+"," ",text.replace("\n"," ")))
    breakpoint()
    open("test2.txt",'w').write(text)
