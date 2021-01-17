import networkx as nx
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import plotly.offline as py

import time
import sys
import random
from queue import Queue
from dataclasses import dataclass

# ----------------------------------------------------------------------------------------------------------------------
# ------ CONSTANTS -----------------------------------------------------------------------------------------------------
MAX_DEPTH = 3
MAX_LINKS_PER_PAGE = 10
DEBUG = True
NOT_LIST = ['Wikipedia:', 'Category:', 'http', '//', 'Help:', 'Portal:', 'Template:']
# ----------------------------------------------------------------------------------------------------------------------


@dataclass
class Node:
    url: str
    depth: int = 0


def make_edge(x, y, width):
    """Creates a scatter trace for the edge between x's and y's with given width.
    Returns:
        edge trace that goes between the points with given width.

    Source: https://github.com/rweng18/midsummer_network
    """
    return go.Scatter(
        x=x, y=y,
        line=dict(width=width,
                  color='cornflowerblue'),
        mode='lines')


def plotly_graph(g):
    """Create plotly graph based on the given networkx graph g."""
    # Draw the nodes
    pos = nx.spring_layout(g)   # get positions for the nodes

    node_trace = go.Scatter(
        x=[], y=[],
        text=[],
        textposition='top center',
        textfont_size=10,
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            color=['cornflowerblue'],
            size=[25],
            line=None)
    )
    for node in g.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple(['<b>' + node + '</b>'])

    # Draw the edges
    edge_trace = []
    for edge in g.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        trace = make_edge([x0, x1, None], [y0, y1, None], 1)
        edge_trace.append(trace)

    # Create Figure:
    fig = go.Figure(layout=go.Layout(
        title='<br>Network graph',
        titlefont_size=16,
        showlegend=False,
        hovermode='closest'
    ))
    fig.add_trace(node_trace)
    for trace in edge_trace:
        fig.add_trace(trace)

    fig.show()
    py.plot(fig, filename='wikipedia.html')
    print("DONE!")


def link_filter(x):
    return "/wiki/" in x['href'] and not any(i in x['href'] for i in NOT_LIST)


# TODO: Fix, HTML selector not working properly, sometimes e.g. links to picture are found! making a KeyError
def find_links_from_html(html, max_links=MAX_LINKS_PER_PAGE):
    """Return all links and titles in lists from given html (string). Returned links are only the latter part of the
    wikipedia URL, i.e. if link is 'https://en.wikipedia.org/wiki/Henry_N._Jeter' returns /wiki/Henry_N._Jeter """
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.body.find_all('a', attrs={
                                        'href': True,          # Needs to contain a href attribute
                                        'title': True,         # Also a link
                                        'dir': False,          # We do not want ones with dir nor
                                        'accesskey': False},   # accesskey attributes.
                                    class_=None,                       # Should not have a class
                                    limit=max_links)
    # TODO: Make this part more efficient! Very inefficient!!!!
    # remove all that do not match "/wiki/" and does not contain "Wikipedia:" or "Category:" in it
    links = list(filter(link_filter, links))
    titles = list(map(lambda x: x['title'], links))      # extract the 'title' attribute
    links = list(map(lambda x: x['href'], links))       # extract the 'href' attribute
    return title_filter(soup.title.text), links, titles


def title_filter(title):
    """Filters title names. Some titles may contain '- Wikipedia' at the end of it."""
    if 'Wikipedia' in title:
        result = title.split(" - W", 2)[0]
        return result
    else:
        return title


def main(url, max_depth=MAX_DEPTH, max_links=5, sleep=0.1):
    """ Main driver function, given input url,
    1. find all links on the page
    2. move on to the linked pages
        2.a) Add page and its links as nodes to graph
        2.b) Create edges between the page and its links.
    3. iterate until predetermined depth has been reached

    Returns:
        g - Graph
    """
    g = nx.Graph()
    q = Queue()     # Queue has O(1) complexity for most operations
    q.put(Node(url, 0))
    prefix_url = "https://en.wikipedia.org"

    while not q.empty():
        current = q.get()
        depth = current.depth

        try:
            time.sleep(sleep)
            current_html = requests.get(current.url).text
        except requests.exceptions.ConnectionError:
            print("Connection error! [Too many HTTP requests? -> Add sleep]")

        if DEBUG:
            print("[Depth: {}/{}] Current page - {}".format(depth, max_depth, current.url))

        cur_title, links, titles = find_links_from_html(current_html, max_links=max_links)

        # If longest path from G's root to cur_title more or equal to LINK_DEPTH
        # -> dont put current nodes children links to q
        # -> iteration goes back to one of roots children links.
        if depth < max_depth:
            g.add_node(cur_title)
            g.add_nodes_from(titles)
            # Adds edges between cur_title and all names defined in titles.
            g.add_edges_from(map(lambda x: (cur_title, x), titles))

            for link in links:
                q.put(Node(prefix_url + link, depth+1))
    return g


def graph_stats(graph, print_stats=True):
    degrees = [val for (node, val) in graph.degree()]
    stats = {
        "nodes": len(graph.nodes()),
        "edges": len(graph.edges()),
        "max_degree": max(degrees),
        "max_path": 1,
    }
    if print_stats:
        print("{:10s} {:5d}".format('Nodes', stats['nodes']))
        print("{:10s} {:5d}".format('Edges', stats['edges']))
        print("{:10s} {:5d}".format('Max degree', stats['max_degree']))
        print("{:10s} {:5d}".format('Max path', stats['max_path']))
    return stats


# ----------------------------------------------------------------------------------------------------------------------
# -------------- TESTS -------------------------------------------------------------------------------------------------


def plotly_graph_test():
    graph = nx.Graph()
    graph.add_nodes_from([str(i) for i in range(10)])  # 0...9

    # graph with 0 as the root, connected to all other nodes 1...9
    graph.add_edges_from(map(lambda x: ("0", str(x)), [x for x in range(1, 10)]))

    plotly_graph(graph)


# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    #url = "https://en.wikipedia.org/wiki/Special:Random"
    # url = 'https://en.wikipedia.org/wiki/Adolf_Hitler'
    url = 'https://en.wikipedia.org/wiki/Finland'
    t1 = time.time()
    g = main(url, max_links=5, max_depth=4, sleep=0)
    t2 = time.time()
    print("Time taken: {} seconds".format(t2-t1))
    graph_stats(g)
    plotly_graph(g)

