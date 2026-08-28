#!/usr/bin/python3
import getpass
import argparse
import shutil
import atexit
import os
import re

import requests

try:
    import readline
except ImportError:
    readline=None

"""
Interactive SQL console. Statements entered here are executed via HTTP
against api/data/entitylistfilter.py (POST <url>/api/v1.0/data?query_lang=sql),
exactly like any other REST client of this API.
"""

CONTINUATION_PROMPT="      -> "

YELLOW="\033[33m"
RESET="\033[0m"

VIEW_MODES=("auto", "normal", "vertical", "compact")
QL_MODES=("sql", "xml")

XML_ROOT_CLOSE_TAG="</restapi>"

HISTORY_FILE=os.path.expanduser("~/.restapi_cli_history")
HISTORY_LENGTH=1000


def setup_history():
    if readline is None:
        return

    try:
        readline.read_history_file(HISTORY_FILE)
    except FileNotFoundError:
        pass

    readline.set_history_length(HISTORY_LENGTH)
    atexit.register(readline.write_history_file, HISTORY_FILE)


def make_prompt(username, base_url):
    return f"{YELLOW}restapi {username}@[{base_url}] > {RESET}"


def read_statement(prompt, querylang="sql"):
    lines=[]
    continuation_prompt=f"{YELLOW}{CONTINUATION_PROMPT}{RESET}"
    xml_mode=False
    while True:
        try:
            line=input(prompt)
        except EOFError:
            return None

        stripped=line.strip()
        if not lines and stripped=="":
            continue

        if not lines and stripped.startswith("!"):
            return stripped

        if not lines and querylang=="xml" and stripped.startswith("<"):
            xml_mode=True

        lines.append(line)

        if xml_mode:
            if "\n".join(lines).strip().endswith(XML_ROOT_CLOSE_TAG):
                break
        elif stripped.endswith(";"):
            break

        prompt=continuation_prompt

    statement="\n".join(lines).strip()
    if not xml_mode and statement.endswith(";"):
        statement=statement[:-1]

    return statement


def print_result(result, viewmode="auto"):
    if result is None:
        print("(no rows)")
        return

    if isinstance(result, dict):
        result=[result]

    if not isinstance(result, list) or len(result)==0:
        print("(no rows)")
        return

    columns=list(result[0].keys())
    widths={col: len(col) for col in columns}
    for row in result:
        for col in columns:
            widths[col]=max(widths[col], len(str(row.get(col, ""))))

    if viewmode=="vertical":
        print_result_vertical(result, columns)
    elif viewmode=="normal":
        print_result_table(result, columns, widths)
    elif viewmode=="compact":
        print_result_table_compact(result, columns, widths)
    else:
        table_width=sum(widths.values())+3*(len(columns)-1)
        terminal_width=shutil.get_terminal_size(fallback=(120, 24)).columns
        if table_width>terminal_width:
            print_result_vertical(result, columns)
        else:
            print_result_table(result, columns, widths)


def print_result_table(result, columns, widths):
    def format_row(values):
        return " | ".join(str(value).ljust(widths[col]) for col, value in zip(columns, values))

    print(format_row(columns))
    print("-+-".join("-"*widths[col] for col in columns))
    for row in result:
        print(format_row([row.get(col, "") for col in columns]))

    print(f"({len(result)} row(s))")


def print_result_table_compact(result, columns, widths):
    terminal_width=shutil.get_terminal_size(fallback=(120, 24)).columns
    separators=3*(len(columns)-1)
    available=max(terminal_width-separators, len(columns))

    if sum(widths.values())<=available:
        fit_widths=dict(widths)
    else:
        min_width=3
        fit_widths={col: min_width for col in columns}
        remaining=available-min_width*len(columns)

        if remaining<=0:
            fit_widths={col: max(1, available//len(columns)) for col in columns}
        else:
            extra_total=sum(max(0, widths[col]-min_width) for col in columns)
            if extra_total>0:
                for col in columns:
                    extra=max(0, widths[col]-min_width)
                    fit_widths[col]+=int(remaining*extra/extra_total)

    def truncate(value, width):
        value=str(value)
        if len(value)<=width:
            return value.ljust(width)
        if width<=1:
            return value[:width]
        return value[:width-1]+"…"

    def format_row(values):
        return " | ".join(truncate(value, fit_widths[col]) for col, value in zip(columns, values))

    print(format_row(columns))
    print("-+-".join("-"*fit_widths[col] for col in columns))
    for row in result:
        print(format_row([row.get(col, "") for col in columns]))

    print(f"({len(result)} row(s))")


def print_result_vertical(result, columns):
    label_width=max(len(col) for col in columns)

    for index, row in enumerate(result):
        header=f"-[ record {index+1} ]"
        print(header+"-"*max(0, 40-len(header)))
        for col in columns:
            print(f"{col.ljust(label_width)} | {row.get(col, '')}")

    print(f"({len(result)} row(s))")


def print_help():
    print("Available commands:")
    print("  <sql statement>;        execute an SQL statement (SELECT/INSERT/UPDATE/DELETE/...)")
    print("  <fetchxml>              execute a FetchXML statement (only in ql=xml mode)")
    print("                            input starts with '<' and ends automatically at </restapi>")
    print(f"  set vm;                 show the current view mode")
    print(f"  set vm <mode>;          set the view mode, one of: {', '.join(VIEW_MODES)}")
    print("                            auto     - table if it fits the terminal width, vertical otherwise")
    print("                            normal   - always a full table")
    print("                            vertical - always one record per block (like psql \\x)")
    print("                            compact  - always a table, columns truncated to fit the terminal width")
    print("  set ql;                 show the current query language")
    print(f"  set ql=<lang>;          set the query language, one of: {', '.join(QL_MODES)}")
    print("                            sql - statements are plain SQL, terminated with ';'")
    print("                            xml - statements are FetchXML, terminated by </restapi>")
    print("  help;                   show this help")
    print("  ! import <format> <file>  import a file via POST /v1.0/import/<format>")
    print("                            (format e.g. xml, json, csv - depends on installed import plugins)")
    print("  exit; / quit;           leave the console")


def handle_set_command(statement, viewmode, querylang):
    parts=statement.split()

    if len(parts)<2 or parts[0].lower()!="set":
        print(f"unknown command: {statement}")
        return viewmode, querylang

    key=parts[1]
    value=None
    if "=" in key:
        key, value=key.split("=", 1)
        value=value if value!="" else None
    elif len(parts)>=3:
        value=parts[2]

    key=key.lower()

    if key=="vm":
        if value is None:
            print(f"viewmode is '{viewmode}'")
            return viewmode, querylang

        mode=value.lower()
        if mode not in VIEW_MODES:
            print(f"unknown viewmode '{mode}', allowed: {', '.join(VIEW_MODES)}")
            return viewmode, querylang

        print(f"viewmode set to '{mode}'")
        return mode, querylang

    if key=="ql":
        if value is None:
            print(f"query language is '{querylang}'")
            return viewmode, querylang

        lang=value.lower()
        if lang not in QL_MODES:
            print(f"unknown query language '{lang}', allowed: {', '.join(QL_MODES)}")
            return viewmode, querylang

        print(f"query language set to '{lang}'")
        return viewmode, lang

    print(f"unknown command: {statement}")
    return viewmode, querylang


def do_login(session, base_url, username, password):
    login_url=f"{base_url}/api/v1.0/core/login"

    response=session.post(login_url,
        headers={"username": username, "password": password})

    if response.status_code!=200:
        try:
            message=response.json().get('message', response.text)
        except ValueError:
            message=response.text
        return False, message

    return True, None


def do_import(session, base_url, format, filename):
    if not os.path.isfile(filename):
        print(f"file not found: {filename}")
        return

    import_url=f"{base_url}/api/v1.0/import/{format}"

    with open(filename, "rb") as file_handle:
        files={"file": (os.path.basename(filename), file_handle)}
        response=session.post(import_url, files=files)

    if response.status_code!=200:
        try:
            message=response.json().get('message', response.text)
        except ValueError:
            message=response.text
        print(f"error ({response.status_code}): {message}")
        return

    try:
        data=response.json()
        print(f"OK (import) - status={data.get('status')} results={data.get('results')}")
    except ValueError:
        print("OK (import)")


def handle_bang_command(session, base_url, statement):
    parts=statement[1:].strip().split()

    if len(parts)==3 and parts[0].lower()=="import":
        do_import(session, base_url, parts[1], parts[2])
        return

    print(f"unknown command: {statement}")


def detect_statement_type(statement, querylang):
    if querylang=="xml":
        match=re.search(r'<restapi\b[^>]*\btype\s*=\s*"([^"]+)"', statement, re.IGNORECASE)
        return match.group(1).upper() if match else ""

    return statement.strip().split(None, 1)[0].upper() if statement.strip() else ""


def execute_statement(session, url, statement, viewmode, querylang):
    sql_type=detect_statement_type(statement, querylang)
    content_type="text/xml; charset=utf-8" if querylang=="xml" else "text/plain; charset=utf-8"

    response=session.post(url,
        params={"query_lang": querylang, "page": 0, "page_size": 5000},
        headers={"Content-Type": content_type},
        data=statement.encode("utf-8"))

    if response.status_code!=200:
        try:
            message=response.json().get('message', response.text)
        except ValueError:
            message=response.text
        print(f"error ({response.status_code}): {message}")
        return

    if sql_type=="SELECT":
        print_result(response.json(), viewmode)
    else:
        print(f"OK ({sql_type.lower()})" if sql_type else "OK")


def run(base_url, username, password):
    setup_history()

    session=requests.Session()

    try:
        ok, message=do_login(session, base_url, username, password)
    except requests.exceptions.RequestException as err:
        print(f"connection error: {err}")
        return

    if not ok:
        print(f"login failed: {message}")
        return

    viewmode="auto"
    querylang="sql"
    prompt=make_prompt(username, base_url)
    url=f"{base_url}/api/v1.0/data"

    print("restapi SQL console")
    print(f"Connected to {base_url} as {username}")
    print("Enter an SQL statement terminated with ';'. Type 'exit;' to quit.")
    print("Type 'help;' for a list of available commands.\n")

    while True:
        statement=read_statement(prompt, querylang)
        if statement is None:
            print()
            break

        if statement=="":
            continue

        if statement.lower() in ("exit", "quit"):
            break

        if statement.lower()=="help":
            print_help()
            continue

        if statement.strip().lower().startswith("set "):
            viewmode, querylang=handle_set_command(statement.strip(), viewmode, querylang)
            continue

        if statement.strip().startswith("!"):
            handle_bang_command(session, base_url, statement.strip())
            continue

        try:
            execute_statement(session, url, statement, viewmode, querylang)
        except requests.exceptions.RequestException as err:
            print(f"connection error: {err}")


def main():
    argparser=argparse.ArgumentParser(description="Interactive SQL console executing statements via HTTP against api/data/entitylistfilter.py")
    argparser.add_argument("--url", required=True, help="restapi base url, e.g. http://localhost:5000")
    argparser.add_argument("--username", help="restapi username, will be prompted for if omitted")
    argparser.add_argument("--password", help="restapi password, will be prompted for if omitted")
    args=argparser.parse_args()

    username=args.username or input("Username: ")
    password=args.password or getpass.getpass("Password: ")

    base_url=args.url.rstrip('/')
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', base_url):
        base_url=f"https://{base_url}"

    run(base_url, username, password)


if __name__=="__main__":
    main()
