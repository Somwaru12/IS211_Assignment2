import argparse
import urllib.request
import logging
import datetime

def downloadData(url):
    """
    downloads the csv text from any given url decodes it and returns
    it as a string 
    """
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode('utf-8')


def _configure_logging():
    """
    makes the assignment2 logger write in error.log file
    """
    logger = logging.getLogger('assignment2')
    logger.setLevel(logging.ERROR)

    if not logger.handlers:
        fh = logging.FileHandler('error.log', mode='w', encoding='utf-8')
        fh.setLevel(logging.ERROR)
        fh.setFormatter(logging.Formatter('%(message)s')) 
        logger.addHandler(fh)


def _parse_header(header_line):
    """
    return the id, name, and birthday based on the text in the header row
    if the header is missing or unexpected, it goes back to the usual order
    """
    if not header_line:
        return {'id': 0, 'name': 1, 'birthday': 2}

    cols = [c.strip().lower() for c in header_line.split(',')]
    idx = {'id': None, 'name': None, 'birthday': None}
    for i, h in enumerate(cols):
        if h == 'id':
            idx['id'] = i
        elif h == 'name':
            idx['name'] = i
        elif h in ('birthday', 'birthdate'):
            idx['birthday'] = i

    if None in idx.values():
        return {'id': 0, 'name': 1, 'birthday': 2}
    return idx


def processData(file_content):
    """
    Process CSV text and return a dictionary that maps id to (name, birthday).

    - Reads the file one line at a time.
    - Birthdays should be in dd/mm/YYYY format; change them to 
    datetime.date.
    - On a bad birthday, there was an error processing #<linenum> 
    for #<id> and that row should be skipped.
    """
    logger = logging.getLogger('assignment2')
    people = {}

    # make newlines normal and break up into lines
    lines = file_content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    if not lines:
        return people

    # header
    header = lines[0]
    indices = _parse_header(header)

    # data lines start at line number 2 the header is 1
    for lineno, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue

        # Simple CSV split (your data has no commas in names)
        parts = [p.strip() for p in line.split(',')]

        # Guard against short rows
        try:
            raw_id = parts[indices['id']]
            name = parts[indices['name']]
            bday_raw = parts[indices['birthday']]
        except Exception:
            # unknown ID if it can’t even read it
            logger.error(f"Error processing line #{lineno} for ID #<unknown>")
            continue

        # parse ID 
        try:
            person_id = int(raw_id)
        except Exception:
            person_id = raw_id  

        # parse birthday (dd/mm/YYYY)
        try:
            bday = datetime.datetime.strptime(bday_raw, "%d/%m/%Y").date()
        except Exception:
            logger.error(f"Error processing line #{lineno} for ID #{person_id}")
            continue

        people[person_id] = (name, bday)

    return people


def displayPerson(id, personData):
    """
    print the person info or the 'not found' message if the 
    birthday is invalid.
    """
    if id in personData:
        name, bday = personData[id]
        print(f"Person #{id} is {name} with a birthday of {bday.isoformat()}")
    else:
        print("No user found with that id")


def main(url):
    _configure_logging()

    try:
        csv_text = downloadData(url)
    except Exception as e:
        print(f"Failed to download data: {e}")
        return

    # to dict id name, date
    personData = processData(csv_text)

    # until user enters a num less then or equal to 0
    while True:
        raw = input("Enter an ID to lookup (<=0 to quit): ").strip()
        if raw == '':
            continue
        try:
            lookup_id = int(raw)
        except ValueError:
            print("Please enter an integer ID.")
            continue

        if lookup_id <= 0:
            break

        displayPerson(lookup_id, personData)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL to the datafile", type=str, required=True)
    args = parser.parse_args()
    main(args.url) 