from pdfminer.high_level import extract_pages
from pdfminer.pdfpage import *
from pdfminer.pdfinterp import *
import io
from io import StringIO
from pdfminer.converter import *
from pdfminer.layout import *



class TextConverter(PDFConverter):
    def __init__(self, rsrcmgr, outfp, codec='utf-8', pageno=1, laparams=None,
                 showpageno=False, imagewriter=None,is_valid_fn=None):
        PDFConverter.__init__(self, rsrcmgr, outfp, codec=codec, pageno=pageno,
                              laparams=laparams)
        self.showpageno = showpageno
        self.imagewriter = imagewriter
        self.is_bold = False
        self.is_valid_fn = is_valid_fn
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
                            self.write_text("<h1>")
                        #print(item.get_text(),end="")
                        self.is_bold = True
                    else:
                        if self.is_bold:
                            self.write_text("</h1>")
                        self.is_bold = False

                bad_item = False
                if hasattr(item, 'size'):
                    if self.is_valid_fn != None and not self.is_valid_fn(item):
                        bad_item = True

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
                 caching=True, codec='utf-8', laparams=None,is_valid_fn=None,showpageno=False):
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
                               laparams=laparams,is_valid_fn=is_valid_fn,showpageno=showpageno)
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

def extract_wrapper_outline(fp):
    def is_valid_item(item):
        to_remove = [
            ('SourceSansPro-Light', 44.0), # Docmenent title
            ('SourceSansPro-Bold', 18.0), # Document subheading
            ('SourceSansPro-Regular', 12.0), # Address
            ('SourceSansPro-Light', 11.25), # Main text
            ('SourceSansPro-Light', 11.249999999999972), # Extra bits of main text
            ('SourceSansPro-Light', 11.249999999999993), # Extra main text
            ('SourceSansPro-Bold', 11.249999999999943), # Extra main text
            ('SourceSansPro-Light', 11.249999999999943), # Extra main text
            ('SourceSansPro-Bold', 11.250000000000007), # Extra main text
            ('SourceSansPro-Regular', 22.0), # "Overall rating for this location"
            ('SourceSansPro-Regular', 16.0), # Purple thin heading in box (Mental Health Act responsibilities ....)
            ('SourceSansPro-Regular', 18.0), # Single dash -
            ('SourceSansPro-Bold', 16.0),# white grey box headings
            ('SourceSansPro-Light', 12.0),# contents page
            ('SourceSansPro-Regular', 15.000000000000057),
            ('SourceSansPro-Regular', 15.0), # Are sevices caring/ responsibvle/safe/well lead... ********
            ('SourceSansPro-Bold', 13.0), # Rating (big table at top of detailed section) ****
            ('SourceSansPro-Bold', 14.0), # Specific boxes (e.g. Are surgery services safe?
            ('SourceSansPro-Light', 11.250000000000014),
            ('SourceSansPro-Bold', 10.0), # page nums
            ('SourceSansPro-Regular', 10.0), # footer
            #('SourceSansPro-Regular', 26.0), # Page Headings ****
            ('SourceSansPro-Bold', 11.25), # In text headings (e.g. Services we rate)
            ('SourceSansPro-Bold', 15.0), # some titles, some qurestions - purple headings
            ('SourceSansPro-Regular', 11.0), # Summary table text
            ('SourceSansPro-Light', 10.999999999999943), # Extra summary table text
            ('SourceSansPro-Light', 11.0), # Extra summary table text
            ('SourceSansPro-Light', 0.0), # Wierdly spaced page headings
            ('SourceSansPro-Bold', 12.0), # BOLD: Action the provider SHOULD take to improve
            ('SourceSansPro-Light', 10.999999999999986),
            ('SourceSansPro-Semibold', 10.0), # Page 16, detailed findings summary table headings
            ('SourceSansPro-Light', 10.0), # Page 16, detailed findings summary table data
        ]
        if item.size < 20:
            return False
        for x in to_remove:
            if item.fontname == x[0] and item.size == x[1]:
                return False
        return True

    return extract_text(fp,laparams=LAParams(line_margin=2,char_margin=3,boxes_flow=-1),is_valid_fn=is_valid_item,showpageno=True)

def extract_wrapper(fp,page_numbers=None):
    def is_valid_item(item):
        '''
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
        ]
        '''

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
            ('SourceSansPro-Bold', 18.0),
        ]
        for x in to_remove:
            if item.fontname == x[0] and item.size == x[1]:
                return False
        return True

    return extract_text(fp,laparams=LAParams(line_margin=2,char_margin=3,boxes_flow=-1),is_valid_fn=is_valid_item,page_numbers=page_numbers)

if __name__ == "__main__":
    text = extract_wrapper(open("AAAH0830.pdf",'rb'))
    print(re.sub(r"\W+"," ",text))#.replace("\n"," ")))
    breakpoint()
