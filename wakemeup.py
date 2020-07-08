#!/usr/bin/env python

import random
import os
from yaml import load, dump
from yaml import CLoader as Loader, CDumper as Dumper
from curses import *
from time import sleep
import difflib
import qrcode
import hashlib
import importlib
from pathlib import Path
import itertools
import inspect

KEYWORD_ONE = 'Ego'

REPLACE_CHARS = {
    "forall": "∀",
    "all": "∀",
    "exists": "∃",
    "in": "∈",
    "alpha": "α",
    "beta": "β"
}

REPLACE_CHARS_NO_ESCAPE = {
    "<-": REPLACE_CHARS["in"]
}

class CONFIG:
    INNER_WIN_SIZE = 0.5
    TIMEOUT = 10
    WINS = 6
    EDITOR = os.environ.__contains__("EDITOR") and os.environ["EDITOR"] or "nano"
    WORKING_DIR=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    QUESTION_DIR="./tasks/"
    CACHE_DIR = os.path.expanduser("~") + "/.cache/wakemeup"
    WORKING_FILE = f"{CACHE_DIR}/wf"
    IGNORE = ["tasks/db/axiomy_vp.yaml", "tasks/db/example.yaml"]

def qr_code_generation_stage_one():
    code = KEYWORD_ONE
    for x in range(10):
        code = str(hashlib.md5(code.encode()).hexdigest())
    return code


def prepare_window(stdscr):
    max_y, max_x = stdscr.getmaxyx()
    win_size_y, win_size_x = max_y * CONFIG.INNER_WIN_SIZE, max_x * CONFIG.INNER_WIN_SIZE
    begin_y = (max_y - win_size_y) / 2
    begin_x = (max_x - win_size_x) / 2

    win_size_y, win_size_x, begin_y, begin_x = int(win_size_y), int(win_size_x), int(begin_y), int(begin_x)

    win = newwin(win_size_y, win_size_x, begin_y, begin_x)
    box_win = newwin(win_size_y + 2, win_size_x + 2, begin_y - 1, begin_x - 1)

    box_win.box()
    box_win.refresh()

    return win


def load_random_question():
    def yaml_driver(question_p):
        with open(question_p) as file:
            data = load(file, Loader=Loader)
            return data["question"], data["answer"]

    def py_driver(question_p):
        return importlib.import_module(question_p.replace("./", "").replace("/", ".").replace(".py", "")).generate()

    question_path = random.choice([
        x.as_posix() for x
        in itertools.chain(Path(CONFIG.QUESTION_DIR).rglob('*.py'), Path(CONFIG.QUESTION_DIR).rglob('*.yaml'))
        if x.as_posix() not in CONFIG.IGNORE
    ])

    path, extension = os.path.splitext(question_path)

    extensions = {
        ".yaml": yaml_driver,
        ".py": py_driver
    }

    question, answer = extensions[extension](question_path)
    return {"question": question, "answer": answer}


def editor(stdscr, win, task):
    if not os.path.isdir(CONFIG.CACHE_DIR):
        os.makedirs(CONFIG.CACHE_DIR)

    with open(CONFIG.WORKING_FILE, 'w+') as file:
        file.write("Your question for today: \n")
        file.write(task["question"])
        file.write("\n\n")

    os.system("nvim +4 " + CONFIG.WORKING_FILE)

    with open(CONFIG.WORKING_FILE, 'r') as file:
        answer = file.readlines()

    answer = answer[3:]

    return str.join('', answer)


def replace_specials(answer):
    for special in REPLACE_CHARS:
        answer = answer.replace("\\" + special, REPLACE_CHARS[special])
    for special in REPLACE_CHARS_NO_ESCAPE:
        answer = answer.replace(special, REPLACE_CHARS_NO_ESCAPE[special])
    return answer


KEYWORD_TWO = 'Surgere'


def confirm(win, answer):
    win.clear()
    win.addstr("This is your answer, do you wish to submit? y/n")

    win.addstr(3, 0, answer)

    while True:
        ch = win.getkey()
        if ch == 'n':
            return False
        if ch == 'y':
            return True
        if ch is not None:
            win.addstr(str(ch))

        sleep(0.05)


def qr_code_generation_stage_two():
    code = KEYWORD_TWO
    for x in range(10):
        code = str(hashlib.md5(code.encode()).hexdigest())
    return code


def check(win, task, answer):
    win.clear()

    win.move(0, 0)
    win.addstr("Answer:\n", A_BOLD)
    win.addstr(task["answer"] + "\n\n")
    win.addstr("Your submission:\n", A_BOLD)
    win.addstr(answer + "\n")
    win.addstr("Diff:\n", A_BOLD)

    ratio = difflib.SequenceMatcher(None, task["answer"], answer).ratio()
    diff = difflib.unified_diff(task["answer"], answer, n=0)
    diff_str = ''.join(diff)
    win.addstr(diff_str + "\n\n")

    diff_n = len(diff_str)
    good_enough = ratio > 0.4

    win.addstr(f'The string is good enough: {good_enough}, ({ratio})')

    while True:
        ch = win.getkey()
        if ch == 'c': return good_enough, ratio
        sleep(0.05)


def show_qr_code():
    img = qrcode.make(
        f"AUTO v2: {qr_code_generation_stage_one()} {qr_code_generation_stage_two()} {qr_code_generation_stage_three()}"
    )
    img.save(f"{CONFIG.CACHE_DIR}/qr_code")
    os.system(f"./helper.sh {CONFIG.CACHE_DIR}/qr_code")


def log(answer, sameness):
    if not os.path.isdir(f"{CONFIG.CACHE_DIR}/log"):
        os.makedirs(f"{CONFIG.CACHE_DIR}/log")

    name = hashlib.md5(answer.encode()).hexdigest()

    with open(f"{CONFIG.CACHE_DIR}/log/{name}", "w") as f:
        f.write(answer)
        f.write(f"\nSameness: {sameness}\n")


def timeout(win, wins):
    for x in range(CONFIG.TIMEOUT, 0, -1):
        win.clear()
        win.move(0, 0)
        win.addstr("[ TIMEOUT ] Please wait for: ")
        win.addstr(str(x), A_BOLD)
        win.move(1, 0)
        win.addstr("Currently finish round ")
        win.addstr(f"{wins}", A_BOLD)
        win.addstr(f" ( < {CONFIG.WINS} )")
        win.refresh()
        sleep(1)


def qr_code_generation_stage_three():
    code = KEYWORD_THREE
    for x in range(10):
        code = str(hashlib.md5(code.encode()).hexdigest())
    return code


def round(stdscr, win, wins):
    task = load_random_question()
    answer = editor(stdscr, win, task)
    answer = replace_specials(answer)
    confirm(win, answer)
    success, closeness = check(win, task, answer)
    log(answer, closeness)
    timeout(win, wins)
    return success


KEYWORD_THREE = 'Nunc'


def main(stdscr):
    stdscr.clear()
    win = prepare_window(stdscr)

    wins = 0

    while wins < CONFIG.WINS:
        if round(stdscr, win, wins):
            wins += 1

    show_qr_code()
    sleep(5)
    stdscr.clear()


os.chdir(CONFIG.WORKING_DIR)
wrapper(main)
