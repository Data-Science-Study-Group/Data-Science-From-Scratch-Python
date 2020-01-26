"""
Created on Sun Jan 26 16:51:40 2020

@author: Neeraj

Description: An impelementation of mapper and reducer functions with a few
examples in Python.
Reference: Chapter 25 MapReduce
"""

from typing import Iterable, Iterator, Tuple, List

def tokenize(document: str) -> List[str]:
    """Just split on whitespace"""
    return document.split()

def wc_mapper(document: str) -> Iterator[Tuple[str, int]]:
    """For each word in a document, emit (word, 1)"""
    for word in tokenize(document):
        yield (word, 1)

def wc_reducer(word: str,
              counts: Iterable[int]) -> Iterator[Tuple[str, int]]:
    """Sum up the counts for a word"""
    yield (word, sum(counts))

from collections import defaultdict

def word_count(documents: List[str]) -> List[Tuple[str, int]]:
    """Count the words in the input documents using MapReduce"""
    collector = defaultdict(list) # to store grouped values
    
    for document in documents:
        for word, count in wc_mapper(document):
            collector[word].append(count)
            
    return [output
           for word, counts in collector.items()
           for output in wc_reducer(word, counts)]

# Writing a general map_reduce function

from typing import Callable, Iterable, Any, Tuple

# A key/value pair is just a 2-tuple
KV = Tuple[Any, Any]

# A Mapper is a function that returns an Iterable of key/value pairs
Mapper = Callable[..., Iterable[KV]]

# A Reducer is a function that takes a key and an iterable of values
# and returns a key/value pair

Reducer = Callable[[Any, Iterable], KV]

def map_reduce(inputs: Iterable,
              mapper: Mapper,
              reducer: Reducer) -> List[KV]:
    """Run MapReduce on the inputs using mapper and reducer"""
    collector = defaultdict(list)
    
    for input in inputs:
        for key, value in mapper(input):
            collector[key].append(value)
    
    return [output
           for key, values in collector.items()
           for output in reducer(key, values)]

def values_reducer(values_fn: Callable) -> Reducer:
    """Return a reducer that just applies values_fn to its values"""
    def reduce(key, values: Iterable) -> KV:
        return (key, values_fn(values))         
    return reduce

sum_reducer = values_reducer(sum)
max_reducer = values_reducer(max)
min_reducer = values_reducer(min)
count_distinct_reducer = values_reducer(lambda values: len(set(values)))


status_updates = [
        {"id": 2,
         "username" : "neerajkumar",
         "text" : "Should I use the second edition of Joel's data science book?",
         "created_at" : datetime.datetime(2018, 2, 21, 11, 47, 0),
         "liked_by" : ["data_guy", "data_gal", "mike"] },
         # ...
    ]

def data_science_day_mapper(status_update: dict) -> Iterable:
    """Yields (day_of_week, 1) of status_update contains 'data science'"""
    if "data science" in status_update["text"].lower():
        day_of_week = status_update["created_at"].weekday()
        yield (day_of_week, 1)
        
data_science_days = map_reduce(status_updates, data_science_day_mapper,
                              sum_reducer)

from collections import Counter
def words_per_user_mapper(status_update: dict):
    user = status_update["username"]
    for word in tokenize(status_update["text"]):
        yield (user, (word, 1))
        
def most_popular_word_reducer(user: str,
                             words_and_counts: Iterable[KV]):
    
    """Given a sequence of (word, count) pairs,
    return the word with the highest total count"""
    word_counts = Counter()
    for word, count in words_and_counts:
        word_counts[word] += count
        word, count = word_counts.most_common(1)[0]
        
        yield (user, (word, count))
        
user_words = map_reduce(status_updates, 
                        words_per_user_mapper,
                       most_popular_word_reducer)


def liker_mapper(status_update: dict):
    user = status_update["username"]
    for liker in status_update["liked_by"]:
        yield (user, liker)
        
distinct_likers_per_user = map_reduce(status_updates, 
                                      liker_mapper,
                                     count_distinct_reducer)


from typing import NamedTuple

class Entry(NamedTuple):
    name: str
    i: int
    j: int
    value: float

def matrix_multiply_mapper(num_rows_a: int, num_cols_b: int) -> Mapper:
    # C[x][y] = A[x][0] * B[0][y] + ... + A[x][m] * B[m][y]
    #
    # so an element A[i][j] goes into every C[i][y] with coef B[j][y]
    # and an element B[i][j] goes into every C[x][j] with coef A[x][i]
    def mapper(entry: Entry):
        if entry.name == "A":
            for y in range(num_cols_b):
                key = (entry.i, y)              # which element of C
                value = (entry.j, entry.value)  # which entry in the sum
                yield (key, value)
        else:
            for x in range(num_rows_a):
                key = (x, entry.j)              # which element of C
                value = (entry.i, entry.value)  # which entry in the sum
                yield (key, value)

    return mapper

def matrix_multiply_reducer(key: Tuple[int, int],
                            indexed_values: Iterable[Tuple[int, int]]):
    results_by_index = defaultdict(list)

    for index, value in indexed_values:
        results_by_index[index].append(value)

    # Multiply the values for positions with two values
    # (one from A, and one from B) and sum them up.
    sumproduct = sum(values[0] * values[1]
                     for values in results_by_index.values()
                     if len(values) == 2)

    if sumproduct != 0.0:
        yield (key, sumproduct)

A = [[3, 2, 0],
     [0, 0, 0]]

B = [[4, -1, 0],
     [10, 0, 0],
     [0, 0, 0]]
