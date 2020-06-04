qld-members-interests
======
This script parses the Queensland Parliament's [Register of Members' Interests](https://www.parliament.qld.gov.au/members/current/register-members-interests) PDF. It extracts each listed MP and their interests, then inserts them to a PostgreSQL database for ease of access.

Dependencies
------
- Apache Tika via [tika-python](https://github.com/chrismattmann/tika-python) 
- PostgreSQL
- SQLAlchemy
  
Syntax
------
`python parse.py MembersRegister.pdf`