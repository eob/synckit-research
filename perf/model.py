import networkx as nx
from random import *

class Page:
    def __init__(self, name, URL):
        self.name = name
        self.url = URL
        self.p_landing = 0.0
        self.data = []
    
    def __str__(self):
        return self.name
    
class Site:
    def __init__(self):
        self.landing_page = None
        self.graph = None
        
    def create_graph(self, pages, articles_per_page, prob_of_next, prob_of_leaving):
        self.graph = nx.DiGraph()
    
        # The main pages
        main_pages = []
        article_pages = []
        END = Page("END", "END")
        urlroot = "http://locahost:8080/"

        prob_of_article = (1.0 - prob_of_next - prob_of_leaving) / articles_per_page
        
        for i in range(pages):
            page = Page("Page " + str(i), urlroot + "?page=" + str(i))
            if i == 0:
                page.p_landing = 1.0
            self.graph.add_node(page)
            main_pages.append(page)
            for j in range(articles_per_page):
                # 10 Articles per page
                num = i * articles_per_page + i + 1
                article = Page("Article " + str(num), urlroot + "?article=" + str(num))
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
        return click_trail

class Blog(Site):
    def __init__(self):
        Site.__init__(self)
        self.create_graph(10, 10, 0.3, 0.4)

