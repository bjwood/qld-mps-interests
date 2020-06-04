import re
import sys
from tika import parser

mp_pattern = r'^([A-Z]*), ([A-Z][a-z]*) ([A-Z][a-z]* )?(\(.*\)?)'
sc_pattern = r'Subclause 7\(5\)\(.\)(\(.?.?.?\))?( and \(.?.?.?\).*)?( to \(.?.?.?\))?(-\(.?.?.?\))?'
members = []
subclauses = {}

class Member:
    def __init__(self, first_name, surname, electorate):
        self.first_name = first_name
        self.surname = surname
        self.electorate = electorate

def load_pdf(path):
    raw = parser.from_file(path)
    content = raw['content']
    # TODO: use this metadata
    print(raw["metadata"])
    return content

def parse_mp(mp_search):
    surname = mp_search.group(1)
    first_name = mp_search.group(2)
    electorate = mp_search.group(4)
    # If there's more than one set of brackets, this MP has a nickname
    # eg. SMITH, Robert James (Bob) (Clayfield)
    # We only want the electorate, so we split on the ") (" sequence and take only the second half
    if electorate.count("(") > 1:
        electorate = electorate.split(") (")[1]
    electorate = electorate.replace("(", "").replace(")", "")
    return Member(first_name, surname, electorate)

def parse_content(content):
    current_question = ""
    last_line_empty = False

    for line in content.splitlines():
        mp_search = re.search(mp_pattern, line)
        if mp_search is not None:
            member = parse_mp(mp_search)
            members.append(member)
            print(member.first_name, member.surname + ", Member for", member.electorate)
            last_line_empty = False
        sc_search = re.search(sc_pattern, line)
        if sc_search is not None:
            sc_name = sc_search.group()
            if sc_name not in subclauses:
                subclauses[sc_name] = "a"
            current_question = sc_name
            last_line_empty = False
        elif line.strip():
            # Line has content
            # Only parse after we have encountered an empty line
            # Otherwise we'll cop the explainer text for the subclause as well
            if last_line_empty:
                print("Answer for cq", current_question, ":", line)
        else:
            # Blank line
            last_line_empty = True


def main():
    if len(sys.argv) != 2:
        print("Usage: parse.py input_file.pdf")
        exit()
    pdf_path = sys.argv[1]
    content = load_pdf(pdf_path)
    parse_content(content)

if __name__ == "__main__":
    main()