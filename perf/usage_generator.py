# Site Model

import networkx as nx

urlroot = "http://locahost:8080/"

class Page:
    def __init__(self, name, URL):
        self.name = name
        self.url = URL
        self.data = []
    
    def __str__(self):
        return self.name

def generate_blog(pages, articles_per_page, prob_of_next, prob_of_leaving):
    G = nx.Graph()

    # The main pages
    main_pages = []
    article_pages = []
    END = Page("END", "END")
    prob_of_article = (1.0 - prob_of_next - prob_of_leaving) / articles_per_page
    
    for i in range(pages):
        page = Page("Page " + str(i), urlroot + "?page=" + str(i))
        G.add_node(page)
        main_pages.append(page)
        for j in range(articles_per_page):
            # 10 Articles per page
            num = i * articles_per_page + i + 1
            article = Page("Article " + str(num), urlroot + "?article=" + str(num))
            G.add_node(article)
            G.add_edge(page, article, weight=prob_of_article)
            article_pages.append(article)

    # Set ending probabilities
    for a in article_pages:
        G.add_edge(a, END, weight=1.0)
    for p in main_pages:
        G.add_edge(p, END, weight=prob_of_leaving)
    
    # Set transition prob from main page to main page
    for i in range(len(main_pages) - 1):
        p1 = main_pages[i]
        p2 = main_pages[i+1]
        G.add_edge(p1, p2, weight=prob_of_next)

    return G


blog = generate_blog(10, 10, 0.3, 0.4)

print blog