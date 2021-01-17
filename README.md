# Notes: Link network project 👁👄👁 
If doing this project with friends -> GitLive plugin for PyCharm

Links: 👁👄👁 
- [Networkx Doc](https://networkx.org/documentation/stable/index.html)
- [Plotly doc](https://plotly.com/python/)
- [Graph visualization example 1](https://plotly.com/python/network-graphs/)
- [Graph visualization example 2](https://towardsdatascience.com/tutorial-network-visualization-basics-with-networkx-and-plotly-and-a-little-nlp-57c9bbb55bb9)

## Dependencies:
- Networkx
- requests
- Plotly?

## Wikipedia:
Wikipedia random page url is https://en.wikipedia.org/wiki/Special:Random. Note, links on 
wikipedia pages can be found inside paragraph ```<p>...</p>```, inside tags ```<a>...</a>```
tags as an attribute ```href```, i.e. ```<a href="LINK"> ...</a>```.

## Issues:
- Latest numpy 1.19.4 didnt work on newest python (3.9)?
    * Fix: Install previous numpy 1.19.3

## Requirements:
```
Given a start page
    1. Find all links on it
    2. Create a node of current page and its links
        - Create edges between
    3. Move on to the linked pages
    
    Iterate until a predetermined depth level has been reached.
```
## Todo
- [ ] Figure out link traversal
- [ ] How to find links on page
- [ ] How to plot the graph (plotly)?
- [ ] 👁👄👁