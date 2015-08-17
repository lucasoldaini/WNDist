# WNDist

problem: finding the distance (i.e., shortest path length) between two nodes
in the NLTK implementation of WordNet is:

##### A. slow

```python
from nltk.corpus import wordnet as wnnltk
nltk_exec_time = time.time()
dists = []
for s1, s2 in product(wn.synsets(w0), wn.synsets(w1)):
    dists.append(s1.shortest_path_distance(s2))
nltk_exec_time = time.time() - nltk_exec_time
print(nltk_exec_time)

>>> 4.06659889221
```

##### B. not flexible

There is no way to specify a subset of relationships to consider when evaluating the distance.

------

This library solves both issues: it is fast and flexible. It uses the excellent [NetworkX](https://networkx.github.io), plus a combination of pickling and shelving to achieve greater speed. Here's the same task in WNDist:

```python
from wordnet_distance.wndist import WNDist

# specify a cache folder where to store the cached results,
# as well as provide the location of the wordnet dicitonary
wn = WNDist(cachedir='cache', sourcedir='dict')
w0, w1 = 'war', 'peace'
custom_exec_time = time.time()
wncstm.lemmasdist(w0, w1)
custom_exec_time = time.time() - custom_exec_time
print(custom_exec_time)

>>> 0.0069420337677
```

The source dictionary is avaiable from the official [WordNet page on Princeton's website](http://wordnet.princeton.edu/wordnet/download/)


