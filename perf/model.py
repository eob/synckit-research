import networkx as nx
from random import *
import datetime

# Import the Django stuff
from django.core.management import setup_environ
import sys
sys.path.append(('/'.join(__file__.split('/')[:-2])) + '/server')
import settings

class Page:
    def __init__(self, name, URL):
        self.name = name
        self.url = URL
        self.p_landing = 0.0
        self.data = []
    
    def __str__(self):
        return self.name

class User:
    def __init__(self, visit_rate, visit_time_unit, last_visit_time):
        self.visits = []
        self.visit_rate = visit_rate
        self.visit_time_unit = visit_time_unit
        self.last_visit_time = last_visit_time
        self.next_visit_time = None
    
    def perform_next_visit(self, site):
        visit = Visit(self.last_visit_time, self.next_visit_time, site.generate_click_trail())
        self.visits.append(visit)
        self.last_visit_time = self.next_visit_time
        self.plan_next_visit()
        return visit
    
    def plan_next_visit(self):
        time_delta = expovariate(self.visit_rate)
        params = {self.visit_time_unit : time_delta}
        if (self.next_visit_time == None):
            self.next_visit_time = self.last_visit_time + datetime.timedelta(**params)
        else:
            self.next_visit_time += datetime.timedelta(**params)
    
    def visits_to_json(self):
        visits = ",".join([visit.to_json() for visit in self.visits])
        return "[%s]" % (visits)
        
class Visit:
    def __init__(self, last_time, this_time, click_trail):
        self.last_time = last_time
        self.this_time = this_time
        self.click_trail = click_trail
    
    def __str__(self):
        return str(self.last_time) + ", " + str(self.this_time) + ", " + str(self.click_trail)
    
    def to_json(self):
        return '{"time":"%s", "clicktrail":%s}' % (self.this_time, self.click_trail.to_json())

class ClickTrail:
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return str([page.name for page in self.path])

    def to_json(self):
        comma_list = ",".join([('"%s"' % page.name) for page in self.path])
        return '[%s]' % (comma_list)

class Site:
    def __init__(self, base_url):
        self.landing_page = None
        self.graph = None
        self.base_url = base_url
        
    def create_graph(self, pages, articles_per_page, prob_of_next, prob_of_leaving):
        self.graph = nx.DiGraph()
    
        # The main pages
        main_pages = []
        article_pages = []
        END = Page("END", "END")
        urlroot = self.base_url

        prob_of_article = (1.0 - prob_of_next - prob_of_leaving) / articles_per_page
        
        for i in range(pages):
            page = Page("Page " + str(i), urlroot)
            if i == 0:
                page.p_landing = 1.0
            self.graph.add_node(page)
            main_pages.append(page)
            for j in range(articles_per_page):
                # 10 Articles per page
                num = i * articles_per_page + i + 1
                article = Page("Link " + str(num), urlroot)
                self.graph.add_node(article)
                self.graph.add_edge(page, article, weight=prob_of_article)
                article_pages.append(article)
    
        # Set ending probabilities
        for a in article_pages:
            self.graph.add_edge(a, END, weight=1.0)
        for p in main_pages:
            self.graph.add_edge(p, END, weight=prob_of_leaving)
        
        # Set transition prob from main page to main page
        for i in range(len(main_pages) - 1):
            p1 = main_pages[i]
            p2 = main_pages[i+1]
            self.graph.add_edge(p1, p2, weight=prob_of_next)       
             
    def sample_start_page(self):
        r = random()
        sum = 0.0
        for page in self.graph:
            sum += page.p_landing
            if sum > r:
                return page
        return None
    
    def sample_click_trail(self, landing_page):
        click_trail = []
        cur_page = landing_page
        while cur_page.name != "END":
            click_trail.append(cur_page)
            
            r = random()
            sum = 0.0
            for neighbor in self.graph[cur_page]:
                link = self.graph[cur_page][neighbor]
                sum += link['weight']
                if sum > r:
                    cur_page = neighbor
                    break
        return ClickTrail(click_trail)

    def generate_click_trail(self):
        start = self.sample_start_page()
        trail = self.sample_click_trail(start)
        return trail

class Blog(Site):
    def __init__(self, base_url):
        Site.__init__(self, base_url)
        self.create_graph(10, 10, 0.3, 0.4)


class OnePageBlog(Site):
    def __init__(self, base_url):
        Site.__init__(self, base_url)
        self.create_graph(10, 10, 0.0, 1.0)

class Wiki(Site):
    def __init__(self, base_url, p_leave):
        Site.__init__(self, base_url)
        self.build_site()
        self.p_leave = p_leave
    
    def build_site(self):
        pages = []
        self.graph = nx.DiGraph()
        page_cache = {}
        
        END = Page("END", "END")
        self.graph.add_node(END)
        
        # Add the pages
        for page in pages:
            page_node = Page(page.title, urlroot + '?pageid=' + page.id)
            page_cache[page.id] = page_node
            self.graph.add_node(page_node)
        
        # Add the nodes
        for page in pages:
            linksum = 0
            for other in page.outlinks:
                linksum += other.access_probability
            for other in page.outlinks:
                self.graph.add_edge(page, other, weight=((other.access_probability / float(linksum)) * (1.0 - self.p_leave))
            self.graph_add_edge(page, END, weight=self.p_leave)  
