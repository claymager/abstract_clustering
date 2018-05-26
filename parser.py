from bs4 import BeautifulSoup
from datetime import datetime
import requests

def read_block( soup ):
    """
    Soup → Dict
    reads specific td format
    """
    block = [a for a in list( soup.children ) if a.name != "br" ]
    out = dict()
    if "/" in block[0]:
        date_str = block.pop(0)
        out["date"] = datetime.strptime(date_str, "%m/%d/%Y")
    if block[0] == str(block[0]):
        pubmed_id = block.pop(0)
        out["pubmed_id"] = pubmed_id
    out["doi"] = block[0].text
    if len(block) != 1:
        print(out)
        raise UnexpectedFormatError
    return out

def read_row( soup ):
    """
    Soup → Dict
    """
    paper = dict()
    paper["rwdb_id"] = soup.find(id=lambda x: \
            x and x.startswith("grdRetraction_Title")).attrs["title"]

    paper["title"] = soup.find (class_="rTitleNotIE").text

    subjects = soup.find(class_="rSubject").text.split(";")
    paper["subjects"] = [ a.strip() for a in subjects if a.strip() != ""]

    journal = soup.find(class_="rJournal").text
    paper["journal"] = " ".join( journal.split()[:-2] )

    # A few papers are missing publisher
    try:
        paper["publisher"] = soup.find(class_="rPublisher").text
    except AttributeError:
        pass

    # [(Department, University, Location, etc)]
    institutions = soup.find_all(class_="rInstitution")
    paper["institutions"] = [ a.text.strip() for a in institutions ]

    reasons = soup.find_all(class_="rReason")
    paper["reasons"] = [ a.text[1:] for a in reasons ]

    authors = soup.find_all(class_="authorLink")
    paper["authors"] = [ a.text for a in authors]

    authors_block = soup.find(class_="authorLink").parent
    publication_block = authors_block.find_next_sibling()
    retraction_block = publication_block.find_next_sibling()
    type_block = retraction_block.find_next_sibling()
    final_block = type_block.find_next_sibling()
    try:
        paper["publication"] = read_block(publication_block)
        paper["retraction"] = read_block(retraction_block)
    except:
        print(paper["title"])
    children = list(type_block.children)
    paper["doc_types"] = [ v for k, v in enumerate(children) if k%2 == 0 ]
    paper["notice_type"] = paper["doc_types"].pop().text

    t = list(final_block.children)[1]
    children = list(t.children)
    paper["countries"] = [ v for k, v in enumerate(children) if k%2 == 0 ][:-1]
    paper["notes"] = soup.find(alt="NotesAdmin").attrs["title"]

    return paper

def read_table( soup ):
    """
    Soup → [Dict]
    Primary parser for retractiondatabase.org query results
    """
    rows = soup.find_all( class_="mainrow" )
    papers = []
    for row in rows:
        papers.append (read_row (row))
    return papers

def read_to_mongo( soup, collection ):
    """
    Soup, MongoClient collection → IO ()
    Impure parser of retractiondatabase.org query that inserts results into mongodb
    """
    rows = soup.find_all( class_="mainrow" )
    for row in rows:
        info = read_row(row)
        if not collection.find_one(info):
            collection.insert_one(info)

def fulltext_links( pubmed_id ):
    """
    Str → IO (Soup)
    Gets fulltext links from a pubmed id
    no crawl delay included here. robots.text requests 5s.
    """
    url = "https://www.ncbi.nlm.nih.gov/pubmed/{}".format(pubmed_id)
    html = requests.get(url).text
    soup =  BeautifulSoup( html, "lxml" )
    div = soup.find( "div", class_="icons portlet" )
    if not div: return []
    anchors = div.find_all("a")
    return [ a.attrs["href"] for a in anchors ]

def get_fulltext( pubmed_id ):
    """
    Str → IO Dict(a)
    Gets processed fulltext of article from pubmed id
    Uses any known parser
    """
    links = fulltext_links( pubmed_id )
    # probably over-engineering. currently one known parser.
    for url_stem in known_parsers:
        for url in links:
            if url_stem in url:
                html = requests.get( url ).text
                soup = BeautifulSoup( html, "lxml" )
                return known_parsers[url_stem](soup)
    return {"links": links}

def parse_ncbi_fulltext( soup ):
    """
    Soup → Dict
    """
    article_soup = soup.find(class_="jig-ncbiinpagenav")
    sections = article_soup.find_all(class_="tsec")
    abstract = parse_ncbi_abstract( sections.pop(0) )
    text = [p.text for sec in sections for p in sec.find_all("p")]
    out = {"text": " ".join(text), **abstract }
    return out

def parse_ncbi_abstract( soup ):
    """
    Soup → Dict
    """
    texts = [p.text for p in soup.find_all("p")]
    out = {"abstract": " ".join(texts)}
    keywords = soup.find("span", class_="kwd-text")
    if keywords:
        keywords = keywords.text
        keywords = keywords.split(", ")
        for i, kw in enumerate(keywords):
            if "(" in kw:
                compound_kw = kw.split(" (")
                keywords[i] = compound_kw[0]
                abbrev = compound_kw[1].replace(")","")
                keywords.append(abbrev)
        out["keywords"] = keywords
    return out

known_parsers = {"ncbi.nlm.nih.gov": parse_ncbi_fulltext}

