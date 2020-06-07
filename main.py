import re
import sys
import time
import argparse
from tika import parser

from base import engine, Session, Base
from member import Member
from section import Section
from interest import Interest
from version import Version

mp_pattern = r'^([A-Z]*), ([A-Z][a-z]*) ([A-Z][a-z]* )?(\(.*\)?)'
sc_pattern = r'Subclause 7\(5\)\(.\)(\(.?.?.?\))?( and \(.?.?.?\).*)?( to \(.?.?.?\))?(-\(.?.?.?\))?'

members = []
sections = []


def load_pdf(path):
    raw = parser.from_file(path)
    content = raw['content']
    date_str = raw['metadata']['date']
    date = time.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return content, date


def parse_mp(mp_search, version):
    last_name = mp_search.group(1)
    first_name = mp_search.group(2)
    electorate = mp_search.group(4)
    # If there's more than one set of brackets, this MP has a nickname
    # eg. SMITH, Robert James (Bob) (Clayfield)
    # We only want the electorate, so we split on the ") (" sequence and take only the second half
    if electorate.count("(") > 1:
        electorate = electorate.split(") (")[1]
    electorate = electorate.replace("(", "").replace(")", "")
    return Member(first_name, last_name, electorate, version)


def parse_content(content, version):
    current_section = ""
    member_index = -1
    empty_line_count = 0
    pending_text = ""

    for line in content.splitlines():
        mp_search = re.search(mp_pattern, line)
        # Does this line define a member?
        if mp_search is not None:
            member = parse_mp(mp_search, version)
            existing_member_found = False
            for existing_member in members:
                if (member.first_name == existing_member.first_name and 
                    member.last_name == existing_member.last_name and 
                    member.electorate == existing_member.electorate):
                    existing_member_found = True
                    break
            if not existing_member_found:
                members.append(member)
                member_index += 1
            empty_line_count = 0
        # Does this line define a subclause?
        sc_search = re.search(sc_pattern, line)
        if sc_search is not None:
            sc_name = sc_search.group().strip()
            sc_count = 0
            existing_section_found = False
            for existing_section in sections:
                if sc_name == existing_section.name:
                    existing_section_found = True
                    break
                sc_count += 1
            if not existing_section_found:
                sections.append(Section(sc_name, version))
            current_section = sc_count
            empty_line_count = 0
        # If this line isn't blank, then it must contain a member's interests
        elif line.strip():
            # Only parse after we have encountered an empty line
            # Otherwise we'll cop the explainer text for the subclause as well
            if empty_line_count > 0 and member_index > -1:
                # The only thing we're getting after 3 blank lines is a page number,
                # which we don't want
                if empty_line_count < 3:
                    pending_text += line
        else:
            # Blank line
            if pending_text != "":
                members[member_index].add_interest(sections[current_section], pending_text)
                pending_text = ""
            empty_line_count += 1


def prepare_db(drop_all):
    if drop_all:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return Session()


def handle_args():
    parser = argparse.ArgumentParser(description="Parse a QLD Members' Interests PDF to a database.")
    parser.add_argument('input', help='the PDF file to parse')
    parser.add_argument('--dropall', action='store_true', help='drop all tables before processing begins')
    return parser.parse_args()

def main():
    args = handle_args()
    content, date = load_pdf(args.input)
    session = prepare_db(args.dropall)
    # Before we go too far, we should make sure this pdf doesn't already exist
    date_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", date)
    matching_versions = session.query(Version).filter(Version.date == date_str).count()
    if matching_versions > 0:
        print("An entry already exists for this PDF. To drop all tables, run this script with --dropall")
        return
    else:
        version = Version(date_str)
        session.add(version)
    parse_content(content, version)
    for section in sections:
        session.add(section)
    for member in members:
        print(member.first_name, member.last_name + ", Member for", member.electorate)
        session.add(member)
    print("Committing to database...")
    session.commit()
    session.close()
    print("Done.")


if __name__ == "__main__":
    main()
