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
        self.interests = {}

    def add_interest(self, subsection, text):
        if subsection in self.interests:
            self.interests[subsection] += text
        else:
            self.interests[subsection] = text

def load_pdf(path):
    raw = parser.from_file(path)
    content = raw['content']
    # TODO: use this metadata for published date
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
    current_section = ""
    member_index = -1
    empty_line_count = 0

    for line in content.splitlines():
        mp_search = re.search(mp_pattern, line)
        # Does this line define a member?
        if mp_search is not None:
            member = parse_mp(mp_search)
            members.append(member)
            member_index += 1
            empty_line_count = 0
        # Does this line define a subclause?
        sc_search = re.search(sc_pattern, line)
        if sc_search is not None:
            sc_name = sc_search.group().strip()
            if sc_name not in subclauses:
                subclauses[sc_name] = "a"
            current_section = sc_name
            empty_line_count = 0
        # If this line isn't blank, then it must contain a member's interests
        elif line.strip():
            # Only parse after we have encountered an empty line
            # Otherwise we'll cop the explainer text for the subclause as well
            if empty_line_count > 0 and member_index > -1:
                # The only thing we're getting after 3 blank lines is a page number,
                # which we don't want
                if empty_line_count < 3:
                    members[member_index].add_interest(current_section, line)
        else:
            # Blank line
            empty_line_count += 1


def main():
    if len(sys.argv) != 2:
        print("Usage: parse.py input_file.pdf")
        exit()
    pdf_path = sys.argv[1]
    content = load_pdf(pdf_path)
    parse_content(content)
    for member in members:
        print(member.first_name, member.surname + ", Member for", member.electorate)
        for interest, details in member.interests.items():
            for item in details.split("; "):
                print(interest + ": " + item.strip())

if __name__ == "__main__":
    main()