import re
from tika import parser

mp_pattern = '^([A-Z]*), ([A-Z][a-z]*) ([A-Z][a-z]* )?(\(.*\)?)'
sc_pattern = 'Subclause 7\(5\)\(.\)(\(.?.?.?\))?( and \(.?.?.?\).*)?( to \(.?.?.?\))?(-\(.?.?.?\))?'
members = []
subclauses = {}

raw = parser.from_file('MembersRegister.pdf')
print(raw["metadata"])
content = raw['content']
print("Loaded", len(content))

current_question = ""
last_line_empty = False

for line in content.splitlines():
    mp_search = re.search(mp_pattern, line)
    if mp_search is not None:
        mp_name = mp_search.group()
        mp_surname = mp_search.group(1)
        mp_firstname = mp_search.group(2)
        mp_electorate = mp_search.group(4)
        if mp_electorate.count("(") > 1:
            mp_electorate = mp_electorate.split(") (")[1]
        mp_electorate = mp_electorate.replace("(", "").replace(")", "")
        members.append(mp_name)
        print(mp_firstname, mp_surname + ", Member for", mp_electorate)
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

print('--------------')
#for sc_key in subclauses:
#    print('SC:', sc_key)
#for member in members:
    #print('MP:', member)