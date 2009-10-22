# Site Model

import networkx as nx
from model import *

blog = Blog()

for i in range(30):
    start = blog.sample_start_page()
    trail = blog.sample_click_trail(start)
    print [x.name for x in trail]
