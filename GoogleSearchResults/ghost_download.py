#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, codecs, logging, random
logging.basicConfig()
from ghost import Ghost
from ghost.ghost import TimeoutError as ghostTimeoutError
from time import sleep
from user_agents import agents

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

url = sys.argv[1]

ghost = Ghost(user_agent=agents[random.randint(0, len(agents) - 1)], wait_timeout=20, log_level=logging.ERROR, download_images=False)
try:
    page, _ = ghost.open(url)
except ghostTimeoutError:
    page = {}
ct = 0
while getattr(page, 'http_status', 0) != 200 and ct < 10:
    sleep(1)
    try:
        #print "TEST", ct, getattr(page, 'http_status', 0)
        setattr(ghost, 'user_agent', agents[random.randint(0, len(agents) - 1)])
        setattr(ghost, 'wait_timeout', getattr(ghost, 'wait_timeout', 20) + 4)
        page, _ = ghost.open(url)
    except ghostTimeoutError:
        pass
    ct += 1
html_text = ghost.content
del ghost

if len(sys.argv) > 2:
    output_file = sys.argv[2]
    with codecs.open(output_file, "w", "utf-8") as html_file:
        html_file.write(html_text)
else:
    print html_text

