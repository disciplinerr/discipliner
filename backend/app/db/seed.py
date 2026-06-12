"""Idempotent seeding of trail phases and the fallback challenge pool.

Run: python -m app.db.seed
"""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Difficulty, FallbackChallenge, TrailPhase

PHASES = [
    {
        "number": 1,
        "name": "Foundations",
        "weeks": "Weeks 1-3",
        "topics": "HTTP\nTCP/IP\nDNS\nHow servers work\nProcesses\nFile descriptors",
        "exercises": "Build a raw TCP echo server in C\nImplement an HTTP/1.1 GET parser in Python",
    },
    {
        "number": 2,
        "name": "Backend Fundamentals",
        "weeks": "Weeks 4-7",
        "topics": "REST design\nSQL\nIndexes\nTransactions\nAuth (JWT, sessions)\nHashing",
        "exercises": "Build a REST API from scratch in FastAPI\nWrite raw SQL migrations",
    },
    {
        "number": 3,
        "name": "Systems & Concurrency",
        "weeks": "Weeks 8-11",
        "topics": "Threads\nAsync I/O\nConnection pooling\nCaching (Redis)\nMessage queues",
        "exercises": "Implement a job queue\nBenchmark a slow query and fix it",
    },
    {
        "number": 4,
        "name": "DevOps Foundations",
        "weeks": "Weeks 12-16",
        "topics": "Docker\nDocker Compose\nLinux basics\nEnvironment variables\nCI/CD concepts",
        "exercises": "Containerize an app\nWrite a Dockerfile from scratch\nSet up a GitHub Actions pipeline",
    },
    {
        "number": 5,
        "name": "Infrastructure",
        "weeks": "Weeks 17-22",
        "topics": "VPS\nSSH\nNginx\nReverse proxy\nSSL/TLS\nMonitoring (Prometheus basics)",
        "exercises": "Deploy an app to a VPS manually\nConfigure Nginx\nSet up basic monitoring",
    },
    {
        "number": 6,
        "name": "Advanced Backend",
        "weeks": "Weeks 23-28",
        "topics": "Microservices tradeoffs\nEvent-driven architecture\nSystem design basics",
        "exercises": "Design and document a system\nImplement one service with a message queue",
    },
]

# ── Fallback challenge pool ────────────────────────────────────────────────────
# Seeding is idempotent: titles are used as unique keys.
# Add new questions here; re-run `python -m app.db.seed` to insert missing ones.

B = Difficulty.beginner
I = Difficulty.intermediate
A = Difficulty.advanced

FALLBACK_CHALLENGES = [

    # ══════════════════════════════════════════════════════════════════════
    # ALGORITHMS — BEGINNER
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Binary Search",
        "math_problem": (
            "For a sorted array of n elements, binary search halves the search space "
            "each step. Show that the worst-case number of comparisons is ⌈log₂(n+1)⌉, "
            "giving O(log n) time complexity."
        ),
        "programming_task": (
            "Implement `binary_search(arr: list[int], target: int) -> int` that returns "
            "the index of target or -1 if not found. Use iterative approach."
        ),
        "difficulty": B, "category": "algorithms",
        "expected_output_example": "binary_search([1,3,5,7,9], 5) → 2\nbinary_search([1,3,5], 4) → -1",
        "constraints": "O(log n) time, O(1) space. No built-in search functions.",
    },
    {
        "title": "Bubble Sort",
        "math_problem": (
            "Bubble sort makes at most n-1 passes. Show that after k passes, "
            "the k largest elements are in their correct positions. "
            "Worst case is O(n²) comparisons; best case O(n) with early termination."
        ),
        "programming_task": (
            "Implement `bubble_sort(arr: list[int]) -> list[int]` with early-exit "
            "optimization. Return sorted array (do not modify original)."
        ),
        "difficulty": B, "category": "algorithms",
        "expected_output_example": "bubble_sort([64,34,25,12,22,11,90]) → [11,12,22,25,34,64,90]",
        "constraints": "In-place sorting on a copy. O(n²) worst, O(n) best.",
    },
    {
        "title": "Selection Sort",
        "math_problem": (
            "Selection sort always performs exactly n(n-1)/2 comparisons regardless "
            "of input order. Derive this count from the sum 1+2+…+(n-1)."
        ),
        "programming_task": (
            "Implement `selection_sort(arr: list[int]) -> list[int]`. "
            "Also return the total number of swaps performed."
        ),
        "difficulty": B, "category": "algorithms",
        "expected_output_example": "selection_sort([29,10,14,37,13]) → ([10,13,14,29,37], 4)",
        "constraints": "Exactly n-1 swaps maximum. No built-in sort.",
    },
    {
        "title": "Insertion Sort",
        "math_problem": (
            "Insertion sort is efficient on nearly-sorted data. Show that on an array "
            "with at most k inversions, it runs in O(n + k) time. "
            "An inversion is a pair (i, j) where i < j but arr[i] > arr[j]."
        ),
        "programming_task": (
            "Implement `insertion_sort(arr: list[int]) -> tuple[list[int], int]` "
            "returning (sorted_array, inversion_count)."
        ),
        "difficulty": B, "category": "algorithms",
        "expected_output_example": "insertion_sort([3,1,2]) → ([1,2,3], 2)",
        "constraints": "Count inversions during sorting. No extra arrays.",
    },
    {
        "title": "Palindrome Checker",
        "math_problem": (
            "A palindrome reads the same forwards and backwards. "
            "For a string of length n, you need at most ⌊n/2⌋ comparisons. "
            "Extend: a number is palindromic if its digit string is palindromic."
        ),
        "programming_task": (
            "Implement `is_palindrome(s: str) -> bool` for strings and "
            "`is_numeric_palindrome(n: int) -> bool` without converting to string "
            "(reverse the number mathematically)."
        ),
        "difficulty": B, "category": "algorithms",
        "expected_output_example": "is_palindrome('racecar') → True\nis_numeric_palindrome(121) → True\nis_numeric_palindrome(123) → False",
        "constraints": "is_numeric_palindrome: no str() conversion.",
    },
    {
        "title": "Sieve of Eratosthenes",
        "math_problem": (
            "The sieve marks composites by iterating multiples of each prime p "
            "starting at p². The number of operations is O(n log log n). "
            "Explain why we start at p² (all smaller multiples already marked)."
        ),
        "programming_task": (
            "Implement `sieve(n: int) -> list[int]` returning all primes ≤ n. "
            "Also implement `prime_count(n: int) -> int` using the sieve."
        ),
        "difficulty": B, "category": "algorithms",
        "expected_output_example": "sieve(30) → [2,3,5,7,11,13,17,19,23,29]\nprime_count(100) → 25",
        "constraints": "O(n log log n) time, O(n) space. Boolean array approach.",
    },
    {
        "title": "GCD and LCM",
        "math_problem": (
            "Euclid's algorithm: gcd(a, b) = gcd(b, a mod b). "
            "Show that the algorithm terminates in O(log(min(a,b))) steps "
            "using the Fibonacci property of worst cases. "
            "lcm(a, b) = a × b / gcd(a, b)."
        ),
        "programming_task": (
            "Implement `gcd(a: int, b: int) -> int` (iterative, no recursion) "
            "and `lcm(a: int, b: int) -> int`. "
            "Then `gcd_list(nums: list[int]) -> int` for a list using reduce."
        ),
        "difficulty": B, "category": "math",
        "expected_output_example": "gcd(48, 18) → 6\nlcm(4, 6) → 12\ngcd_list([12,18,24]) → 6",
        "constraints": "No math.gcd. Iterative gcd only.",
    },
    {
        "title": "Fast Modular Exponentiation",
        "math_problem": (
            "Compute aⁿ mod m in O(log n) using the property: "
            "a²ᵏ = (aᵏ)². "
            "If n is odd: aⁿ = a · aⁿ⁻¹. "
            "This reduces n multiplications to O(log n)."
        ),
        "programming_task": (
            "Implement `pow_mod(base: int, exp: int, mod: int) -> int` using "
            "binary exponentiation. Do NOT use Python's built-in pow(b, e, m)."
        ),
        "difficulty": B, "category": "math",
        "expected_output_example": "pow_mod(2, 10, 1000) → 24\npow_mod(3, 200, 13) → 9",
        "constraints": "O(log exp) multiplications. No pow() built-in.",
    },
    {
        "title": "Array Rotation",
        "math_problem": (
            "Rotating an array left by k is equivalent to reversing [0..k-1], "
            "reversing [k..n-1], then reversing the whole array. "
            "Show this three-reversal approach achieves O(n) time and O(1) space."
        ),
        "programming_task": (
            "Implement `rotate_left(arr: list[int], k: int) -> list[int]` "
            "using the three-reversal trick. "
            "Also implement `rotate_right(arr: list[int], k: int) -> list[int]`."
        ),
        "difficulty": B, "category": "algorithms",
        "expected_output_example": "rotate_left([1,2,3,4,5], 2) → [3,4,5,1,2]\nrotate_right([1,2,3,4,5], 2) → [4,5,1,2,3]",
        "constraints": "O(n) time, O(1) extra space (in-place on copy).",
    },
    {
        "title": "Stack Implementation",
        "math_problem": (
            "A stack is a LIFO structure. Amortized analysis shows that a dynamic "
            "array doubling strategy achieves O(1) amortized push/pop. "
            "Show the amortized cost: each element is moved at most once per doubling."
        ),
        "programming_task": (
            "Implement a `Stack` class with `push(val)`, `pop() -> int`, `peek() -> int`, "
            "`is_empty() -> bool`, `size() -> int`. "
            "Raise `IndexError` on pop/peek of empty stack."
        ),
        "difficulty": B, "category": "data-structures",
        "expected_output_example": "s=Stack(); s.push(1); s.push(2); s.pop() → 2; s.peek() → 1",
        "constraints": "Use a list internally. No collections.deque.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # ALGORITHMS — INTERMEDIATE
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Merge Sort with Inversion Count",
        "math_problem": (
            "Merge sort divides the array into halves, sorts each, then merges. "
            "Recurrence: T(n) = 2T(n/2) + O(n) → O(n log n). "
            "During merge, when we pick from the right half, all remaining left "
            "elements form inversions with it."
        ),
        "programming_task": (
            "Implement `merge_sort_count(arr: list[int]) -> tuple[list[int], int]` "
            "that returns (sorted_array, inversion_count) in O(n log n)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "merge_sort_count([3,1,2,4]) → ([1,2,3,4], 2)",
        "constraints": "O(n log n). Count inversions exactly during merge step.",
    },
    {
        "title": "Quick Sort with Median-of-Three",
        "math_problem": (
            "Quick sort expected O(n log n) with random pivot, worst O(n²) on sorted input. "
            "Median-of-three (first, middle, last) reduces worst-case probability. "
            "Derive that average comparisons ≈ 2n ln n."
        ),
        "programming_task": (
            "Implement `quicksort(arr: list[int]) -> list[int]` using median-of-three "
            "pivot selection and in-place Lomuto partition. "
            "Fallback to insertion sort for subarrays of size ≤ 10."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "quicksort([3,6,8,10,1,2,1]) → [1,1,2,3,6,8,10]",
        "constraints": "In-place. Median-of-three pivot. Insertion sort for small arrays.",
    },
    {
        "title": "Two Sum / K Sum",
        "math_problem": (
            "Two Sum in O(n) using hash table: for each x, check if (target - x) exists. "
            "Three Sum: fix one element, reduce to Two Sum. O(n²) time, O(n) space. "
            "General K Sum: O(n^(K-1)) with recursion."
        ),
        "programming_task": (
            "Implement `two_sum(nums: list[int], target: int) -> list[tuple[int,int]]` "
            "returning ALL unique pairs (value, value) that sum to target. "
            "Then `three_sum_zero(nums: list[int]) -> list[tuple]` finding all unique triplets "
            "summing to 0."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "two_sum([1,2,3,4], 5) → [(1,4),(2,3)]\nthree_sum_zero([-1,0,1,2,-1,-4]) → [(-1,-1,2),(-1,0,1)]",
        "constraints": "No duplicates in output. two_sum: O(n), three_sum: O(n²).",
    },
    {
        "title": "Sliding Window Maximum",
        "math_problem": (
            "A monotone deque maintains a decreasing sequence of indices. "
            "When window slides, remove indices out of window from front. "
            "Remove from back any index with value ≤ new element. "
            "Total operations: each index pushed/popped once → O(n)."
        ),
        "programming_task": (
            "Implement `sliding_window_max(nums: list[int], k: int) -> list[int]` "
            "returning the maximum of each window of size k. Use a deque."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "sliding_window_max([1,3,-1,-3,5,3,6,7], 3) → [3,3,5,5,6,7]",
        "constraints": "O(n) time using collections.deque. No nested loops.",
    },
    {
        "title": "Kadane's Algorithm",
        "math_problem": (
            "Kadane's: let dp[i] = max subarray ending at i. "
            "dp[i] = max(arr[i], dp[i-1] + arr[i]). "
            "Answer = max over all i. Prove: if dp[i-1] < 0, start fresh. "
            "Time O(n), space O(1)."
        ),
        "programming_task": (
            "Implement `max_subarray(nums: list[int]) -> tuple[int, int, int]` "
            "returning (max_sum, start_index, end_index). "
            "Handle all-negative arrays (return the maximum single element)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "max_subarray([-2,1,-3,4,-1,2,1,-5,4]) → (6, 3, 6)",
        "constraints": "O(n) time, O(1) space. Track indices.",
    },
    {
        "title": "BFS Shortest Path",
        "math_problem": (
            "BFS on an unweighted graph finds shortest paths. "
            "Show that BFS visits nodes in non-decreasing distance from source. "
            "Proof: all distance-d nodes are enqueued before any distance-(d+1) node. "
            "Time O(V+E)."
        ),
        "programming_task": (
            "Implement `bfs_shortest_path(graph: dict[int,list[int]], src: int, dst: int) -> list[int]` "
            "returning the shortest path as a list of nodes, or [] if unreachable. "
            "graph is an adjacency list."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "bfs_shortest_path({0:[1,2],1:[3],2:[3],3:[]}, 0, 3) → [0,1,3] or [0,2,3]",
        "constraints": "O(V+E). Use collections.deque. Return one valid shortest path.",
    },
    {
        "title": "Detect Cycle in Directed Graph",
        "math_problem": (
            "A directed graph has a cycle iff DFS finds a back edge "
            "(edge to an ancestor in the DFS tree). "
            "Use coloring: WHITE=unvisited, GRAY=in-stack, BLACK=done. "
            "A GRAY→GRAY edge indicates a cycle."
        ),
        "programming_task": (
            "Implement `has_cycle(graph: dict[int,list[int]]) -> bool` "
            "and `find_cycle(graph: dict[int,list[int]]) -> list[int]` "
            "returning one cycle as a list of nodes (empty if none)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "has_cycle({0:[1],1:[2],2:[0]}) → True\nhas_cycle({0:[1],1:[2]}) → False",
        "constraints": "O(V+E). Iterative DFS preferred.",
    },
    {
        "title": "Topological Sort",
        "math_problem": (
            "A DAG can be topologically sorted (Kahn's): "
            "repeatedly remove nodes with in-degree 0 and subtract from neighbors. "
            "If all nodes processed, valid sort exists; otherwise a cycle exists. "
            "Time O(V+E)."
        ),
        "programming_task": (
            "Implement `topological_sort(graph: dict[int,list[int]]) -> list[int]` "
            "using Kahn's (BFS) algorithm. Return [] if graph has a cycle."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "topological_sort({5:[2,0],4:[0,1],2:[3],3:[1]}) → [4,5,0,2,3,1] (one valid order)",
        "constraints": "O(V+E). Kahn's algorithm with in-degree array.",
    },
    {
        "title": "Min-Heap Implementation",
        "math_problem": (
            "A min-heap satisfies: parent ≤ children. "
            "Insert: add at end, sift-up O(log n). "
            "Extract-min: replace root with last, sift-down O(log n). "
            "Build-heap from array: O(n) using bottom-up sift-down."
        ),
        "programming_task": (
            "Implement a `MinHeap` class with `insert(val)`, `extract_min() -> int`, "
            "`peek() -> int`, `heapify(arr: list[int])` (build from list). "
            "Use a list internally."
        ),
        "difficulty": I, "category": "data-structures",
        "expected_output_example": "h=MinHeap(); h.heapify([5,3,8,1]); h.extract_min() → 1; h.extract_min() → 3",
        "constraints": "No heapq module. Manual sift-up and sift-down.",
    },
    {
        "title": "LRU Cache",
        "math_problem": (
            "LRU evicts the least-recently-used item. "
            "O(1) get and put require combining a hash map (key→node) "
            "with a doubly linked list (ordered by recency). "
            "On access: move node to head. On evict: remove tail."
        ),
        "programming_task": (
            "Implement `LRUCache(capacity: int)` with `get(key: int) -> int` "
            "(returns -1 if missing) and `put(key: int, value: int)`. "
            "Both must be O(1) amortized."
        ),
        "difficulty": I, "category": "data-structures",
        "expected_output_example": "c=LRUCache(2); c.put(1,1); c.put(2,2); c.get(1)→1; c.put(3,3); c.get(2)→-1",
        "constraints": "O(1) get and put. Use dict + doubly linked list (no OrderedDict).",
    },
    {
        "title": "Longest Palindromic Substring",
        "math_problem": (
            "Expand-around-center: for each position (and gap between positions), "
            "expand outward while characters match. "
            "2n-1 centers, O(n) expansion each → O(n²). "
            "Alternative: Manacher's runs in O(n) using symmetry."
        ),
        "programming_task": (
            "Implement `longest_palindrome(s: str) -> str` using expand-around-center. "
            "If ties, return the leftmost. Also return its length and start index."
        ),
        "difficulty": I, "category": "strings",
        "expected_output_example": "longest_palindrome('babad') → ('bab', 3, 0)\nlongest_palindrome('cbbd') → ('bb', 2, 1)",
        "constraints": "O(n²) time, O(1) space. Expand-around-center approach.",
    },
    {
        "title": "Edit Distance (Levenshtein)",
        "math_problem": (
            "dp[i][j] = min edits to convert s[0..i] to t[0..j]. "
            "Recurrence: if s[i]==t[j]: dp[i][j]=dp[i-1][j-1] "
            "else: dp[i][j]=1+min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]). "
            "Space can be reduced to O(min(m,n)) using rolling rows."
        ),
        "programming_task": (
            "Implement `edit_distance(s: str, t: str) -> int` using DP. "
            "Also implement `edit_distance_ops(s: str, t: str) -> list[str]` "
            "returning the actual sequence of operations."
        ),
        "difficulty": I, "category": "strings",
        "expected_output_example": "edit_distance('kitten','sitting') → 3\nedit_distance('','abc') → 3",
        "constraints": "O(mn) time. O(min(m,n)) space for the count version.",
    },
    {
        "title": "Word Frequency Counter",
        "math_problem": (
            "A hash map gives O(1) average insert/lookup. "
            "Top-K by frequency: use a min-heap of size K. "
            "Push each word; if heap > K, pop minimum. "
            "Final answer: O(n + n log K). Explain why heap beats full sort when K << n."
        ),
        "programming_task": (
            "Implement `top_k_words(text: str, k: int) -> list[tuple[str,int]]` "
            "returning the k most frequent words with counts, sorted by frequency desc. "
            "Ignore punctuation and case."
        ),
        "difficulty": I, "category": "strings",
        "expected_output_example": "top_k_words('the cat sat on the mat the', 2) → [('the',3),('cat',1)] (or similar)",
        "constraints": "O(n log k). Use heapq. Strip punctuation with str.translate.",
    },
    {
        "title": "Floyd-Warshall All-Pairs Shortest Paths",
        "math_problem": (
            "dp[k][i][j] = shortest path from i to j using only nodes {0..k} as intermediaries. "
            "dp[k][i][j] = min(dp[k-1][i][j], dp[k-1][i][k] + dp[k-1][k][j]). "
            "O(n³) time, O(n²) space. Detects negative cycles when dist[i][i] < 0."
        ),
        "programming_task": (
            "Implement `floyd_warshall(graph: list[list[float]]) -> tuple[list[list[float]], bool]` "
            "where graph[i][j] is edge weight (float('inf') if no edge). "
            "Return (dist_matrix, has_negative_cycle)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "floyd_warshall([[0,3,inf],[inf,0,1],[inf,inf,0]]) → ([[0,3,4],[inf,0,1],[inf,inf,0]], False)",
        "constraints": "O(n³). In-place update ok. Use float('inf') for infinity.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # ALGORITHMS — ADVANCED
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Longest Common Subsequence",
        "math_problem": (
            "dp[i][j] = LCS length of s[0..i] and t[0..j]. "
            "If s[i]==t[j]: dp[i][j]=dp[i-1][j-1]+1 else max(dp[i-1][j],dp[i][j-1]). "
            "Reconstruction: trace back from dp[m][n]. "
            "Space optimization: two-row DP reduces to O(min(m,n))."
        ),
        "programming_task": (
            "Implement `lcs(s: str, t: str) -> str` returning one actual LCS string. "
            "Also implement `lcs_length(s: str, t: str) -> int` in O(min(m,n)) space."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "lcs('ABCBDAB','BDCABA') → 'BCBA' (length 4)\nlcs_length('AGGTAB','GXTXAYB') → 4",
        "constraints": "lcs: O(mn) time+space. lcs_length: O(min(m,n)) space.",
    },
    {
        "title": "0/1 Knapsack with Item Reconstruction",
        "math_problem": (
            "dp[i][w] = max value using first i items with capacity w. "
            "dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt[i]] + val[i]) if wt[i]≤w. "
            "Space: O(W) by iterating w in reverse. "
            "Reconstruction requires the full dp table."
        ),
        "programming_task": (
            "Implement `knapsack(weights: list[int], values: list[int], capacity: int) "
            "-> tuple[int, list[int]]` returning (max_value, list_of_selected_indices)."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "knapsack([2,3,4,5],[3,4,5,6],5) → (7,[0,1])",
        "constraints": "O(nW) time. O(W) space for value; keep full table for reconstruction.",
    },
    {
        "title": "Segment Tree with Range Updates",
        "math_problem": (
            "A segment tree stores aggregates over intervals. "
            "With lazy propagation, range updates are deferred: "
            "tag the node, push down on access. "
            "Each update/query visits O(log n) nodes. "
            "Show that 4n nodes suffice for n-element array."
        ),
        "programming_task": (
            "Implement a `SegmentTree` supporting range sum query and range add update. "
            "`__init__(arr)`, `update(l, r, val)`, `query(l, r) -> int`. "
            "Use lazy propagation."
        ),
        "difficulty": A, "category": "data-structures",
        "expected_output_example": "t=SegmentTree([1,2,3,4,5]); t.update(1,3,2); t.query(0,4) → 21",
        "constraints": "O(log n) per operation. 1-indexed or 0-indexed consistently.",
    },
    {
        "title": "Dijkstra's Shortest Path",
        "math_problem": (
            "Dijkstra maintains a priority queue of (dist, node). "
            "Extract minimum, relax edges. With binary heap: O((V+E) log V). "
            "Correctness: when a node is extracted, its distance is final "
            "(only valid for non-negative weights). Explain why."
        ),
        "programming_task": (
            "Implement `dijkstra(graph: dict[int,list[tuple[int,int]]], src: int) -> dict[int,int]` "
            "where graph[u] = [(v, weight), ...]. Return dist map for all reachable nodes."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "dijkstra({0:[(1,4),(2,1)],1:[(3,1)],2:[(1,2),(3,5)],3:[]}, 0) → {0:0,1:3,2:1,3:4}",
        "constraints": "O((V+E) log V) with heapq. Handle disconnected nodes.",
    },
    {
        "title": "Trie (Prefix Tree)",
        "math_problem": (
            "A trie stores strings by shared prefixes. "
            "Each node branches on one character. "
            "Space: O(ALPHABET × total_chars) worst case. "
            "Insert/search/startsWith: O(L) where L=word length. "
            "Compared to hash set, trie supports prefix queries natively."
        ),
        "programming_task": (
            "Implement `Trie` with `insert(word)`, `search(word) -> bool`, "
            "`starts_with(prefix) -> bool`, and `count_with_prefix(prefix) -> int` "
            "(number of inserted words with that prefix)."
        ),
        "difficulty": A, "category": "data-structures",
        "expected_output_example": "t=Trie(); t.insert('apple'); t.search('apple')→True; t.starts_with('app')→True; t.count_with_prefix('app')→1",
        "constraints": "Use dict-based nodes (not fixed array). O(L) per operation.",
    },
    {
        "title": "KMP String Search",
        "math_problem": (
            "KMP builds a failure function f[i] = length of longest proper prefix of "
            "pattern[0..i] that is also a suffix. "
            "On mismatch at pattern[j], jump to pattern[f[j-1]]. "
            "Total comparisons O(n+m): each char is advanced and backtracked at most once."
        ),
        "programming_task": (
            "Implement `kmp_search(text: str, pattern: str) -> list[int]` "
            "returning all starting indices where pattern appears in text. "
            "Also expose `build_failure(pattern: str) -> list[int]`."
        ),
        "difficulty": A, "category": "strings",
        "expected_output_example": "kmp_search('AABAACAADAABAABA','AABA') → [0,9,12]",
        "constraints": "O(n+m) time. No built-in find/index.",
    },
    {
        "title": "Union-Find (Disjoint Set Union)",
        "math_problem": (
            "Union by rank + path compression gives nearly O(1) amortized per operation "
            "(inverse Ackermann α(n) time). "
            "Path compression: set each node's parent to root on find. "
            "Union by rank: attach smaller tree under larger."
        ),
        "programming_task": (
            "Implement `DSU(n: int)` with `union(a, b) -> bool` (returns False if already "
            "connected), `find(a) -> int`, `connected(a, b) -> bool`, `components() -> int`. "
            "Use path compression + union by rank."
        ),
        "difficulty": A, "category": "data-structures",
        "expected_output_example": "d=DSU(5); d.union(0,1); d.union(1,2); d.connected(0,2)→True; d.components()→3",
        "constraints": "Path compression + union by rank. Nearly O(1) amortized.",
    },
    {
        "title": "Matrix Exponentiation — Fibonacci",
        "math_problem": (
            "[[1,1],[1,0]]^n = [[F(n+1),F(n)],[F(n),F(n-1)]] (prove by induction). "
            "Matrix multiplication is O(2³)=O(1) for 2×2. "
            "Exponentiation by squaring: O(log n) matrix multiplications. "
            "Total: O(log n) for arbitrarily large Fibonacci numbers."
        ),
        "programming_task": (
            "Implement `fib(n: int) -> int` using matrix exponentiation (O(log n)). "
            "Also implement `fib_mod(n: int, mod: int) -> int` for very large n (n up to 10^18)."
        ),
        "difficulty": A, "category": "math",
        "expected_output_example": "fib(50) → 12586269025\nfib_mod(10**18, 10**9+7) → some value",
        "constraints": "No recursion. Matrix mult helper. O(log n).",
    },
    {
        "title": "Bellman-Ford with Negative Cycle Detection",
        "math_problem": (
            "Bellman-Ford relaxes all edges n-1 times. "
            "Proof: after k iterations, shortest paths using ≤k edges are found. "
            "A negative cycle exists iff a (n)th iteration still relaxes an edge. "
            "Time O(VE), space O(V)."
        ),
        "programming_task": (
            "Implement `bellman_ford(n: int, edges: list[tuple[int,int,int]], src: int) "
            "-> tuple[list[float], bool]` where edges are (u, v, weight). "
            "Return (dist_array, has_negative_cycle)."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "bellman_ford(4, [(0,1,1),(1,2,-2),(2,0,1),(2,3,3)], 0) → (dist, True) [negative cycle]",
        "constraints": "O(VE). float('inf') for unreachable. Detect cycle on n-th pass.",
    },
    {
        "title": "Longest Increasing Subsequence (O(n log n))",
        "math_problem": (
            "Patience sorting: maintain piles. Each new card goes on the leftmost pile "
            "whose top is ≥ card (binary search). "
            "Number of piles = LIS length. "
            "Proof uses Dilworth's theorem: minimum number of non-increasing subsequences "
            "equals the length of the longest increasing subsequence."
        ),
        "programming_task": (
            "Implement `lis_length(nums: list[int]) -> int` in O(n log n) "
            "and `lis(nums: list[int]) -> list[int]` reconstructing the actual subsequence."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "lis_length([10,9,2,5,3,7,101,18]) → 4\nlis([10,9,2,5,3,7,101,18]) → [2,5,7,101] or [2,3,7,101]",
        "constraints": "O(n log n) for length. Reconstruction may be O(n log n) total.",
    },
    {
        "title": "Minimum Spanning Tree — Kruskal's",
        "math_problem": (
            "Kruskal's: sort edges by weight, greedily add edge if it connects "
            "two different components (using DSU). "
            "Correctness: cut property — the minimum weight edge crossing any cut "
            "must be in some MST. Time O(E log E)."
        ),
        "programming_task": (
            "Implement `kruskal(n: int, edges: list[tuple[int,int,int]]) -> tuple[int, list[tuple]]` "
            "where edges are (u, v, weight). Return (total_weight, mst_edges)."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "kruskal(4, [(0,1,10),(0,2,6),(0,3,5),(1,3,15),(2,3,4)]) → (19, [(2,3,4),(0,3,5),(0,1,10)])",
        "constraints": "O(E log E). Use DSU from scratch.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # DATA STRUCTURES — BEGINNER
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Queue with Two Stacks",
        "math_problem": (
            "A queue can be simulated with two stacks (inbox + outbox). "
            "Enqueue pushes to inbox. Dequeue pops from outbox; if empty, "
            "move all inbox to outbox. "
            "Amortized O(1) per operation: each element moves at most twice."
        ),
        "programming_task": (
            "Implement `Queue` using exactly two lists (no deque) with "
            "`enqueue(val)`, `dequeue() -> int`, `peek() -> int`, `is_empty() -> bool`. "
            "Raise IndexError on empty dequeue/peek."
        ),
        "difficulty": B, "category": "data-structures",
        "expected_output_example": "q=Queue(); q.enqueue(1); q.enqueue(2); q.dequeue()→1; q.dequeue()→2",
        "constraints": "Exactly two list objects. No collections.deque.",
    },
    {
        "title": "Linked List Reversal",
        "math_problem": (
            "A singly linked list can be reversed in O(n) time and O(1) space "
            "by iteratively relinking pointers. "
            "Recursive reversal uses O(n) stack space. "
            "Show that the iterative approach uses exactly n pointer reassignments."
        ),
        "programming_task": (
            "Define `Node` with `val` and `next`. "
            "Implement `reverse_list(head: Node) -> Node` iteratively. "
            "Also `reverse_between(head: Node, left: int, right: int) -> Node` "
            "reversing only the sublist from position left to right (1-indexed)."
        ),
        "difficulty": B, "category": "data-structures",
        "expected_output_example": "reverse_list(1→2→3→4→5) → 5→4→3→2→1\nreverse_between(1→2→3→4→5, 2, 4) → 1→4→3→2→5",
        "constraints": "O(n) time, O(1) space. Iterative only.",
    },
    {
        "title": "Min Stack",
        "math_problem": (
            "Track the minimum in O(1) by maintaining an auxiliary stack of minimums. "
            "On push(x): push x to main; if x ≤ current min, push x to min_stack. "
            "On pop: if popped value == min_stack.top(), also pop min_stack. "
            "Prove this is correct: min_stack top always equals current minimum."
        ),
        "programming_task": (
            "Implement `MinStack` with `push(val)`, `pop()`, `top() -> int`, "
            "`get_min() -> int`. All operations O(1). "
            "Raise IndexError on pop/top/get_min of empty stack."
        ),
        "difficulty": B, "category": "data-structures",
        "expected_output_example": "s=MinStack(); s.push(3); s.push(1); s.push(2); s.get_min()→1; s.pop(); s.get_min()→1",
        "constraints": "O(1) all operations. Two lists allowed.",
    },
    {
        "title": "Binary Tree Traversals",
        "math_problem": (
            "In-order (left, root, right) of a BST yields sorted order. "
            "Pre-order (root, left, right) reconstructs the tree. "
            "Post-order (left, right, root) is used for deletion and expression evaluation. "
            "Level-order uses a queue; time and space O(n) for all traversals."
        ),
        "programming_task": (
            "Define `TreeNode(val, left=None, right=None)`. "
            "Implement iterative (no recursion) `inorder`, `preorder`, `postorder`, "
            "and `level_order` traversals, each returning list[int]."
        ),
        "difficulty": B, "category": "data-structures",
        "expected_output_example": "Tree: 1(2(4,5),3)\ninorder→[4,2,5,1,3], preorder→[1,2,4,5,3], postorder→[4,5,2,3,1]",
        "constraints": "Iterative only (explicit stack/queue). No recursion.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # DATA STRUCTURES — INTERMEDIATE
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Hash Map from Scratch",
        "math_problem": (
            "With a load factor α = n/m (n items, m buckets), chaining gives "
            "O(1+α) average search. Doubling when α>0.75 and halving when α<0.25 "
            "keeps α bounded. Amortized O(1) per insert. "
            "Explain why the choice of m as a prime reduces collisions."
        ),
        "programming_task": (
            "Implement `HashMap` with `put(key, value)`, `get(key) -> value|None`, "
            "`delete(key)`, `__len__`. Use separate chaining (list of lists). "
            "Auto-resize when load factor > 0.75."
        ),
        "difficulty": I, "category": "data-structures",
        "expected_output_example": "m=HashMap(); m.put('a',1); m.put('b',2); m.get('a')→1; m.delete('a'); m.get('a')→None",
        "constraints": "No built-in dict. Manual hash function. Resize doubles capacity.",
    },
    {
        "title": "Deque (Double-Ended Queue)",
        "math_problem": (
            "A deque supports O(1) push/pop at both ends. "
            "Implemented with a doubly linked list or a circular buffer. "
            "Circular buffer: front and back pointers mod capacity. "
            "Amortized O(1) with dynamic resizing."
        ),
        "programming_task": (
            "Implement `Deque` using a circular array (list of fixed size, then resize). "
            "`push_front(val)`, `push_back(val)`, `pop_front() -> int`, `pop_back() -> int`, "
            "`peek_front() -> int`, `peek_back() -> int`, `__len__`."
        ),
        "difficulty": I, "category": "data-structures",
        "expected_output_example": "d=Deque(); d.push_back(1); d.push_front(0); d.pop_back()→1; d.pop_front()→0",
        "constraints": "Circular array. No collections.deque. O(1) amortized operations.",
    },
    {
        "title": "BST — Insert, Search, Delete",
        "math_problem": (
            "BST property: left subtree < node < right subtree. "
            "Average O(log n) for balanced BST. "
            "Delete with two children: replace with in-order successor (smallest in right subtree). "
            "Height h can be O(n) worst case (degenerate)."
        ),
        "programming_task": (
            "Implement `BST` with `insert(val)`, `search(val) -> bool`, `delete(val)`, "
            "`height() -> int`, `is_valid_bst() -> bool` (checks BST property on the whole tree)."
        ),
        "difficulty": I, "category": "data-structures",
        "expected_output_example": "t=BST(); [t.insert(x) for x in [5,3,7,1,4]]; t.search(4)→True; t.height()→3",
        "constraints": "Recursive or iterative. Handle all delete cases (0,1,2 children).",
    },
    {
        "title": "Monotonic Stack Problems",
        "math_problem": (
            "A monotone stack processes elements so the stack remains sorted. "
            "For Next Greater Element: process right to left, pop elements ≤ current, "
            "top is the answer, push current. "
            "Total work O(n): each element pushed and popped exactly once."
        ),
        "programming_task": (
            "Implement `next_greater(nums: list[int]) -> list[int]` and "
            "`largest_rectangle_histogram(heights: list[int]) -> int` "
            "using a monotone stack. Both O(n)."
        ),
        "difficulty": I, "category": "data-structures",
        "expected_output_example": "next_greater([2,1,2,4,3]) → [4,2,4,-1,-1]\nlargest_rectangle_histogram([2,1,5,6,2,3]) → 10",
        "constraints": "O(n) both functions. Explicit stack only.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # DATA STRUCTURES — ADVANCED
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Fenwick Tree (Binary Indexed Tree)",
        "math_problem": (
            "A Fenwick tree stores partial sums. Node i is responsible for "
            "sum of arr[i - lowbit(i) + 1 .. i] where lowbit(i) = i & (-i). "
            "Prefix sum query: sum lowbit-ancestors in O(log n). "
            "Update: propagate up by i += lowbit(i). Both O(log n)."
        ),
        "programming_task": (
            "Implement `BIT(n: int)` with `update(i: int, delta: int)`, "
            "`query(i: int) -> int` (prefix sum [1..i]), "
            "and `range_query(l: int, r: int) -> int`. 1-indexed."
        ),
        "difficulty": A, "category": "data-structures",
        "expected_output_example": "t=BIT(5); t.update(1,3); t.update(3,2); t.range_query(1,3)→5",
        "constraints": "O(log n) per operation. 1-indexed. No segment tree.",
    },
    {
        "title": "Skip List",
        "math_problem": (
            "A skip list adds express lanes above the base linked list. "
            "Each node promoted to level k with probability p (typically 0.5). "
            "Expected O(log n) levels and O(log n) search/insert/delete. "
            "Derive that expected space is O(n) with p=0.5."
        ),
        "programming_task": (
            "Implement `SkipList` with `insert(val)`, `search(val) -> bool`, `delete(val)`. "
            "Max level = 16, p = 0.5. Use sentinel head node. "
            "Print the structure as levels."
        ),
        "difficulty": A, "category": "data-structures",
        "expected_output_example": "s=SkipList(); [s.insert(x) for x in [3,6,7,9,12]]; s.search(6)→True; s.delete(6); s.search(6)→False",
        "constraints": "Random level on insert. O(log n) expected. No array-based shortcut.",
    },
    {
        "title": "Bloom Filter",
        "math_problem": (
            "A Bloom filter uses k hash functions and a bit array of size m. "
            "False positive probability: (1 - e^(-kn/m))^k. "
            "Optimal k = (m/n) ln 2. "
            "No false negatives; deletion requires counting Bloom filter."
        ),
        "programming_task": (
            "Implement `BloomFilter(capacity: int, error_rate: float)` with "
            "`add(item: str)`, `might_contain(item: str) -> bool`. "
            "Auto-compute optimal m and k from capacity and error_rate."
        ),
        "difficulty": A, "category": "data-structures",
        "expected_output_example": "bf=BloomFilter(1000,0.01); bf.add('hello'); bf.might_contain('hello')→True; bf.might_contain('xyz') might→False",
        "constraints": "Use bytearray for bits. k independent hash functions via (hash1+i*hash2)%m.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # MATH — INTERMEDIATE
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Euler's Totient Function",
        "math_problem": (
            "φ(n) counts integers in [1,n] coprime to n. "
            "φ(p) = p-1 for prime p. "
            "φ(p^k) = p^k - p^(k-1). "
            "Multiplicative: φ(mn) = φ(m)φ(n) for gcd(m,n)=1. "
            "Product formula: φ(n) = n ∏(1 - 1/p) over distinct prime factors p."
        ),
        "programming_task": (
            "Implement `euler_totient(n: int) -> int` using the product formula. "
            "Also implement `totient_sieve(n: int) -> list[int]` computing φ(i) "
            "for all i in [1, n] in O(n log log n)."
        ),
        "difficulty": I, "category": "math",
        "expected_output_example": "euler_totient(12) → 4\ntotient_sieve(10) → [0,1,1,2,2,4,2,6,4,6,4]",
        "constraints": "Product formula for single. Sieve approach for all values.",
    },
    {
        "title": "Extended Euclidean Algorithm",
        "math_problem": (
            "Extended GCD finds x, y such that ax + by = gcd(a, b) (Bézout's identity). "
            "Recursive: if gcd(a,b) via gcd(b, a mod b) returns (g, x1, y1), "
            "then x = y1, y = x1 - (a÷b)·y1. "
            "Used for modular inverse: if gcd(a,m)=1, then a⁻¹ ≡ x (mod m)."
        ),
        "programming_task": (
            "Implement `extended_gcd(a: int, b: int) -> tuple[int,int,int]` returning (g, x, y). "
            "Then `mod_inverse(a: int, m: int) -> int` using extended GCD. "
            "Raise ValueError if inverse doesn't exist."
        ),
        "difficulty": I, "category": "math",
        "expected_output_example": "extended_gcd(35,15) → (5,1,-2)\nmod_inverse(3,7) → 5 (since 3*5=15≡1 mod 7)",
        "constraints": "Recursive extended GCD. mod_inverse raises ValueError if gcd≠1.",
    },
    {
        "title": "Chinese Remainder Theorem",
        "math_problem": (
            "CRT: given x ≡ r₁ (mod m₁), x ≡ r₂ (mod m₂), …, with pairwise coprime mᵢ, "
            "a unique solution exists mod M = ∏mᵢ. "
            "Solution: x = Σ rᵢ · Mᵢ · (Mᵢ⁻¹ mod mᵢ) where Mᵢ = M/mᵢ."
        ),
        "programming_task": (
            "Implement `crt(remainders: list[int], moduli: list[int]) -> int` "
            "returning the smallest non-negative x satisfying all congruences. "
            "Raise ValueError if moduli are not pairwise coprime."
        ),
        "difficulty": I, "category": "math",
        "expected_output_example": "crt([2,3,2],[3,5,7]) → 23 (23≡2 mod 3, 23≡3 mod 5, 23≡2 mod 7)",
        "constraints": "Use mod_inverse from extended GCD. Validate pairwise coprimality.",
    },
    {
        "title": "Combinations nCr Modulo Prime",
        "math_problem": (
            "C(n,r) = n! / (r! · (n-r)!). For large n with prime modulus p: "
            "precompute factorials and inverse factorials mod p. "
            "Inverse factorial: inv_fact[i] = pow(fact[i], p-2, p) by Fermat's little theorem "
            "(valid when p is prime and i < p)."
        ),
        "programming_task": (
            "Implement `CombMod(max_n: int, mod: int)` class with `C(n: int, r: int) -> int`. "
            "Precompute factorials in __init__. "
            "Also implement `count_paths(m: int, n: int, mod: int) -> int` "
            "(number of paths in m×n grid, only right/down moves)."
        ),
        "difficulty": I, "category": "math",
        "expected_output_example": "cm=CombMod(1000,10**9+7); cm.C(10,3)→120\ncount_paths(3,3,10**9+7)→6",
        "constraints": "Precompute O(n) factorials. C(n,r)=0 if r>n or r<0.",
    },
    {
        "title": "Prime Factorization with Smallest Prime Factor",
        "math_problem": (
            "Smallest prime factor (SPF) sieve: for each composite n, spf[n] = "
            "its smallest prime divisor. "
            "Build sieve in O(n log log n) similar to Eratosthenes. "
            "Factorize any n in O(log n) by repeatedly dividing by spf."
        ),
        "programming_task": (
            "Implement `spf_sieve(limit: int) -> list[int]` and "
            "`factorize(n: int, spf: list[int]) -> dict[int,int]` "
            "returning prime factor → exponent mapping. "
            "Also `num_divisors(n: int, spf: list[int]) -> int`."
        ),
        "difficulty": I, "category": "math",
        "expected_output_example": "spf=spf_sieve(20); factorize(12,spf)→{2:2,3:1}; num_divisors(12,spf)→6",
        "constraints": "O(n log log n) sieve. O(log n) factorize. spf[p]=p for primes.",
    },
    {
        "title": "Matrix Chain Multiplication",
        "math_problem": (
            "dp[i][j] = min multiplications to compute matrices i..j. "
            "dp[i][j] = min over k in [i,j-1] of dp[i][k] + dp[k+1][j] + dims[i]·dims[k+1]·dims[j+1]. "
            "Base: dp[i][i]=0. The number of parenthesizations = Catalan(n-1). "
            "DP avoids exponential search: O(n³) time."
        ),
        "programming_task": (
            "Implement `matrix_chain_order(dims: list[int]) -> tuple[int, str]` "
            "where dims[i] and dims[i+1] are rows and cols of matrix i. "
            "Return (min_multiplications, parenthesization_string)."
        ),
        "difficulty": I, "category": "math",
        "expected_output_example": "matrix_chain_order([40,20,30,10,30]) → (26000, '((A(BC))D)')",
        "constraints": "O(n³) DP. Reconstruct the optimal parenthesization.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # MATH — ADVANCED
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Miller-Rabin Primality Test",
        "math_problem": (
            "Write n-1 = 2^s · d. For witness a: compute a^d mod n. "
            "If not 1 or n-1, square up to s times; if n-1 never appears, composite. "
            "Using witnesses {2,3,5,7,11,13,17,19,23,29,31,37} gives deterministic "
            "results for n < 3.3×10²⁴."
        ),
        "programming_task": (
            "Implement `is_prime(n: int) -> bool` using deterministic Miller-Rabin "
            "with fixed witness set. Must handle n up to 10^18. "
            "Also `nth_prime(n: int) -> int` returning the n-th prime."
        ),
        "difficulty": A, "category": "math",
        "expected_output_example": "is_prime(10**18+9) → True\nnth_prime(10000) → 104729",
        "constraints": "Deterministic for n<3.3×10²⁴. No sympy or external libs.",
    },
    {
        "title": "Modular Square Root (Tonelli-Shanks)",
        "math_problem": (
            "Given a and prime p, find x such that x² ≡ a (mod p). "
            "First check Euler criterion: a^((p-1)/2) ≡ 1 (mod p). "
            "Tonelli-Shanks: write p-1 = Q·2^S, find a non-residue n, "
            "then iteratively reduce using the group structure."
        ),
        "programming_task": (
            "Implement `sqrt_mod(a: int, p: int) -> int | None` returning the smaller "
            "square root of a mod p, or None if it doesn't exist. "
            "Handle the case p ≡ 3 (mod 4) with the simpler formula too."
        ),
        "difficulty": A, "category": "math",
        "expected_output_example": "sqrt_mod(10, 13) → 6 (6²=36≡10 mod 13)\nsqrt_mod(5, 7) → None (5 is not a QR mod 7)",
        "constraints": "Tonelli-Shanks for general p. Direct formula when p≡3 mod 4.",
    },
    {
        "title": "Convex Hull — Graham Scan",
        "math_problem": (
            "The convex hull is the smallest convex polygon containing all points. "
            "Graham scan: sort by polar angle from lowest point, then process: "
            "maintain a stack; pop while last three points make a non-left turn "
            "(cross product ≤ 0). "
            "Time O(n log n), dominated by sorting."
        ),
        "programming_task": (
            "Implement `convex_hull(points: list[tuple[float,float]]) -> list[tuple[float,float]]` "
            "using Graham scan. Return hull vertices in counter-clockwise order. "
            "Handle collinear points (include or exclude boundary)."
        ),
        "difficulty": A, "category": "math",
        "expected_output_example": "convex_hull([(0,0),(1,1),(2,2),(0,2),(2,0)]) → [(0,0),(2,0),(2,2),(0,2)]",
        "constraints": "O(n log n). Cross product for turn detection. Handle n<3.",
    },
    {
        "title": "Fast Power Tower (Tetration mod m)",
        "math_problem": (
            "a↑↑b = a^(a^(a^...)) (b times). Direct computation impossible. "
            "Use Euler's theorem: a^φ(m) ≡ 1 (mod m) when gcd(a,m)=1. "
            "So a^x mod m = a^(x mod φ(m) + φ(m)) mod m when x ≥ log(m). "
            "Handle recursively with decreasing moduli."
        ),
        "programming_task": (
            "Implement `tetration_mod(a: int, b: int, m: int) -> int` computing a↑↑b mod m. "
            "a,b up to 10^9, m up to 10^9. "
            "Handle gcd(a,m) ≠ 1 via lifting the exponent."
        ),
        "difficulty": A, "category": "math",
        "expected_output_example": "tetration_mod(2,4,10) → 6 (2^(2^(2^2))=2^16=65536, 65536%10=6)",
        "constraints": "Recursive Euler theorem reduction. O(log m) depth.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # STRINGS — BEGINNER
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Run-Length Encoding",
        "math_problem": (
            "RLE compresses consecutive identical characters: 'aaabbc' → '3a2b1c'. "
            "Compression ratio depends on run structure. "
            "Worst case (no repetition): doubles size. "
            "Best case (all same): reduces to 2 characters."
        ),
        "programming_task": (
            "Implement `rle_encode(s: str) -> str` and `rle_decode(s: str) -> str`. "
            "Also `rle_compress(s: str) -> str` that only encodes if it saves space "
            "(returns original string if RLE is longer)."
        ),
        "difficulty": B, "category": "strings",
        "expected_output_example": "rle_encode('aaabbc') → '3a2b1c'\nrle_decode('3a2b1c') → 'aaabbc'",
        "constraints": "Counts can be multi-digit. Decode must handle counts > 9.",
    },
    {
        "title": "Caesar and Vigenère Cipher",
        "math_problem": (
            "Caesar shifts each letter by k positions: E(x) = (x+k) mod 26. "
            "Vigenère uses a key string: E(xᵢ) = (xᵢ + keyᵢ mod |key|) mod 26. "
            "Index of coincidence can break Vigenère (Kasiski test). "
            "Both are substitution ciphers; Caesar is a special case of Vigenère."
        ),
        "programming_task": (
            "Implement `caesar_encrypt(text: str, k: int) -> str`, `caesar_decrypt`, "
            "`vigenere_encrypt(text: str, key: str) -> str`, `vigenere_decrypt`. "
            "Preserve case and non-alpha characters."
        ),
        "difficulty": B, "category": "strings",
        "expected_output_example": "caesar_encrypt('Hello World', 3) → 'Khoor Zruog'\nvigenere_encrypt('ATTACKATDAWN','LEMON') → 'LXFOPVEFRNHR'",
        "constraints": "Preserve non-alpha. Uppercase and lowercase handled separately.",
    },
    {
        "title": "Anagram Groups",
        "math_problem": (
            "Two strings are anagrams iff their sorted characters are equal. "
            "Group n strings by anagram: hash each string's character frequency. "
            "Using sorted string as key: O(L log L) per string, O(nL log L) total. "
            "Using frequency tuple: O(L) per string, O(nL) total."
        ),
        "programming_task": (
            "Implement `group_anagrams(words: list[str]) -> list[list[str]]`. "
            "Return groups sorted by first word alphabetically. "
            "Use character frequency tuple as key (not sorted string)."
        ),
        "difficulty": B, "category": "strings",
        "expected_output_example": "group_anagrams(['eat','tea','tan','ate','nat','bat']) → [['bat'],['eat','tea','ate'],['tan','nat']]",
        "constraints": "O(nL) using frequency tuple keys. Output groups sorted.",
    },
    {
        "title": "Longest Common Prefix",
        "math_problem": (
            "Vertical scanning: compare characters column by column across all strings. "
            "Stop at first mismatch or string end. O(S) where S = sum of all lengths. "
            "Alternative: binary search on prefix length. O(S log minLen)."
        ),
        "programming_task": (
            "Implement `longest_common_prefix(strs: list[str]) -> str` "
            "using vertical scanning. Also `lcp_divide_conquer(strs: list[str]) -> str` "
            "using divide and conquer approach."
        ),
        "difficulty": B, "category": "strings",
        "expected_output_example": "longest_common_prefix(['flower','flow','flight']) → 'fl'\nlongest_common_prefix(['dog','racecar','car']) → ''",
        "constraints": "Vertical: O(S) total. Divide-conquer: same asymptotic but recursive.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # STRINGS — INTERMEDIATE
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Minimum Window Substring",
        "math_problem": (
            "Sliding window with two pointers. Expand right until window has all required chars; "
            "contract left while still valid. "
            "Each char is added/removed at most once → O(n). "
            "Track frequencies with a hash map and a 'have' counter."
        ),
        "programming_task": (
            "Implement `min_window(s: str, t: str) -> str` returning the shortest substring "
            "of s containing all characters of t (with duplicates). Return '' if impossible."
        ),
        "difficulty": I, "category": "strings",
        "expected_output_example": "min_window('ADOBECODEBANC','ABC') → 'BANC'\nmin_window('a','aa') → ''",
        "constraints": "O(n) time. Two-pointer sliding window. No regex.",
    },
    {
        "title": "Z-Algorithm for String Matching",
        "math_problem": (
            "Z[i] = length of longest substring starting at i that matches a prefix of s. "
            "Maintain Z-box [l, r]: current rightmost match window. "
            "O(n) total: each character is processed once in the Z-box and once outside. "
            "Find pattern in text: Z on (pattern + '#' + text)."
        ),
        "programming_task": (
            "Implement `z_function(s: str) -> list[int]` and "
            "`z_search(text: str, pattern: str) -> list[int]` "
            "returning all occurrence indices in O(n+m)."
        ),
        "difficulty": I, "category": "strings",
        "expected_output_example": "z_function('aabxaa') → [0,1,0,0,2,1]\nz_search('aabcaab','aab') → [0,4]",
        "constraints": "O(n+m). No built-in find/search.",
    },
    {
        "title": "Decode Ways",
        "math_problem": (
            "A message encoded as digits where 1→A, …, 26→Z. "
            "dp[i] = ways to decode s[0..i-1]. "
            "dp[i] += dp[i-1] if s[i-1] is valid single digit (non-zero). "
            "dp[i] += dp[i-2] if s[i-2..i-1] forms valid two-digit code (10-26). "
            "Leading zeros invalidate current choice."
        ),
        "programming_task": (
            "Implement `decode_ways(s: str) -> int` counting all valid decodings. "
            "Also `decode_ways_all(s: str) -> list[str]` returning all decoded strings."
        ),
        "difficulty": I, "category": "strings",
        "expected_output_example": "decode_ways('226') → 3 ('BZ','VF','BBF')\ndecode_ways('06') → 0",
        "constraints": "decode_ways: O(n) space O(1) (rolling dp). decode_ways_all: backtracking.",
    },
    {
        "title": "Wildcard Pattern Matching",
        "math_problem": (
            "Pattern has '?' (any single char) and '*' (any sequence including empty). "
            "dp[i][j] = True if pattern[0..i] matches text[0..j]. "
            "If pattern[i]='*': dp[i][j] = dp[i-1][j] (skip *) OR dp[i][j-1] (use * for text[j]). "
            "If '?': dp[i][j] = dp[i-1][j-1]. O(mn) time and space."
        ),
        "programming_task": (
            "Implement `wildcard_match(text: str, pattern: str) -> bool` using DP. "
            "Also optimize to O(m) space. "
            "Then `wildcard_match_greedy(text: str, pattern: str) -> bool` "
            "using a two-pointer greedy approach."
        ),
        "difficulty": I, "category": "strings",
        "expected_output_example": "wildcard_match('adceb','*a*b') → True\nwildcard_match('acdcb','a*c?b') → False",
        "constraints": "DP version: O(mn). Greedy version: O(n) time O(1) space.",
    },
    {
        "title": "Rabin-Karp Rolling Hash",
        "math_problem": (
            "Rolling hash: hash(s[i+1..i+m]) = (hash(s[i..i+m-1]) - s[i]·b^(m-1)) · b + s[i+m]. "
            "With base b and prime mod p. "
            "Expected O(n+m); worst case O(nm) due to collisions. "
            "Double hashing (two different mods) reduces collision probability."
        ),
        "programming_task": (
            "Implement `rabin_karp(text: str, pattern: str) -> list[int]` "
            "returning all occurrence positions. Use double hashing (two mod values). "
            "Also `find_duplicate_substring(s: str, length: int) -> str | None`."
        ),
        "difficulty": I, "category": "strings",
        "expected_output_example": "rabin_karp('abcabcabc','abc') → [0,3,6]",
        "constraints": "Double hashing. O(n+m) expected. Verify matches to avoid false positives.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # STRINGS — ADVANCED
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Manacher's Algorithm",
        "math_problem": (
            "Manacher computes p[i] = radius of longest palindrome centered at i "
            "in O(n) using the rightmost palindrome boundary [C, R]. "
            "For i inside the current palindrome: p[i] ≥ min(p[mirror], R-i). "
            "Expand from there and update C, R if i+p[i] > R. "
            "Transform s to '#a#b#a#' to unify even/odd cases."
        ),
        "programming_task": (
            "Implement `manacher(s: str) -> list[int]` returning the palindrome radii array. "
            "Then `longest_palindrome_manacher(s: str) -> str` and "
            "`count_palindromic_substrings(s: str) -> int` both O(n)."
        ),
        "difficulty": A, "category": "strings",
        "expected_output_example": "count_palindromic_substrings('aaa') → 6\nlongest_palindrome_manacher('cbbd') → 'bb'",
        "constraints": "O(n) time. Use transformed string with separators.",
    },
    {
        "title": "Suffix Array Construction",
        "math_problem": (
            "Suffix array SA[i] = index of i-th lexicographically smallest suffix. "
            "DC3 (Skew) algorithm runs in O(n). "
            "Prefix doubling (Manber-Myers): O(n log²n) or O(n log n) with radix sort. "
            "With LCP array, enables O(n) solutions to many string problems."
        ),
        "programming_task": (
            "Implement `build_suffix_array(s: str) -> list[int]` using prefix doubling. "
            "Also `build_lcp_array(s: str, sa: list[int]) -> list[int]` using Kasai's algorithm. "
            "Then `count_distinct_substrings(s: str) -> int` using both."
        ),
        "difficulty": A, "category": "strings",
        "expected_output_example": "build_suffix_array('banana') → [5,3,1,0,4,2]\ncount_distinct_substrings('abab') → 7",
        "constraints": "Prefix doubling O(n log²n). Kasai O(n). No built-in sort on suffix strings.",
    },
    {
        "title": "Regular Expression Engine",
        "math_problem": (
            "Implement '.' (any char) and '*' (zero or more of preceding). "
            "dp[i][j] = True if pattern[0..i] matches text[0..j]. "
            "If pattern[i]='*': dp[i][j] = dp[i-2][j] (zero occurrences) "
            "OR (match(pattern[i-1], text[j]) AND dp[i][j-1]). "
            "This is equivalent to NFA simulation."
        ),
        "programming_task": (
            "Implement `regex_match(text: str, pattern: str) -> bool` supporting "
            "'.' and '*'. The match must cover the entire text. "
            "Use DP approach. Patterns like 'a*b*c*' match empty string."
        ),
        "difficulty": A, "category": "strings",
        "expected_output_example": "regex_match('aa','a*') → True\nregex_match('aab','c*a*b') → True\nregex_match('mississippi','mis*is*p*.') → False",
        "constraints": "O(mn) DP. Full match (not substring). Only '.' and '*' special chars.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # SYSTEMS / BIT MANIPULATION — BEGINNER
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Bit Manipulation Fundamentals",
        "math_problem": (
            "Key identities: x & (x-1) clears lowest set bit. "
            "x & (-x) isolates lowest set bit. "
            "x ^ x = 0 and x ^ 0 = x. "
            "Count bits (Hamming weight): Brian Kernighan's O(set bits) algorithm. "
            "Number of bits to flip to convert a to b: popcount(a XOR b)."
        ),
        "programming_task": (
            "Implement `count_bits(n: int) -> int` (Hamming weight), "
            "`is_power_of_two(n: int) -> bool`, "
            "`bits_to_flip(a: int, b: int) -> int`, "
            "`next_power_of_two(n: int) -> int` (smallest 2^k ≥ n)."
        ),
        "difficulty": B, "category": "systems",
        "expected_output_example": "count_bits(13) → 3 (1101)\nis_power_of_two(16) → True\nbits_to_flip(29,15) → 2",
        "constraints": "No bin() for count_bits. No math.log for power_of_two.",
    },
    {
        "title": "Integer Encoding: Base Conversion",
        "math_problem": (
            "Any positive integer n has a unique representation in base b: "
            "n = Σ dᵢ · bⁱ. "
            "Convert by repeated division: n mod b gives the least significant digit, "
            "then divide by b. "
            "Bases 2,8,10,16 are common. Base 64 uses 6 bits per character."
        ),
        "programming_task": (
            "Implement `to_base(n: int, base: int) -> str` (base 2-36) and "
            "`from_base(s: str, base: int) -> int`. "
            "Use '0-9A-Z' for digits. "
            "Also implement `base64_encode(data: bytes) -> str` and `base64_decode` from scratch."
        ),
        "difficulty": B, "category": "systems",
        "expected_output_example": "to_base(255, 16) → 'FF'\nfrom_base('FF', 16) → 255\nto_base(10, 2) → '1010'",
        "constraints": "No int(s,base) or built-in base64. Negative numbers: prefix '-'.",
    },
    {
        "title": "XOR Tricks",
        "math_problem": (
            "XOR properties: commutative, associative, a^a=0, a^0=a. "
            "Single number: XOR all → duplicate pairs cancel → single remains. "
            "Two different singles: XOR all, find set bit, partition array, XOR each partition. "
            "Missing number: XOR(1..n) ^ XOR(array) = missing."
        ),
        "programming_task": (
            "Implement `single_number(nums: list[int]) -> int` (one element appears once, others twice). "
            "`two_singles(nums: list[int]) -> tuple[int,int]` (two appear once, rest twice). "
            "`missing_number(nums: list[int]) -> int` (0..n, one missing)."
        ),
        "difficulty": B, "category": "systems",
        "expected_output_example": "single_number([4,1,2,1,2]) → 4\ntwo_singles([1,2,1,3,2,5]) → (3,5)\nmissing_number([3,0,1]) → 2",
        "constraints": "O(n) time, O(1) space. No sorting or hash sets.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # SYSTEMS / BIT MANIPULATION — INTERMEDIATE
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Fixed-Point Arithmetic",
        "math_problem": (
            "Fixed-point represents fractions as integers scaled by 2^f. "
            "Multiply: (a * b) >> f. Add: a + b (same scale). "
            "Q16.16 uses 16 bits integer, 16 bits fraction: range ±32767.9999. "
            "Compared to float: deterministic, faster on systems without FPU."
        ),
        "programming_task": (
            "Implement `Fixed(value: float, frac_bits: int = 16)` with "
            "`__add__`, `__sub__`, `__mul__`, `__truediv__`, `to_float() -> float`. "
            "Detect overflow. Also compute sqrt using Newton's method in fixed-point."
        ),
        "difficulty": I, "category": "systems",
        "expected_output_example": "a=Fixed(1.5); b=Fixed(2.5); (a*b).to_float() → 3.75\nFixed(2.0).sqrt().to_float() ≈ 1.4142",
        "constraints": "Internal representation: int only. Overflow raises OverflowError.",
    },
    {
        "title": "Memory Pool Allocator",
        "math_problem": (
            "A fixed-size memory pool pre-allocates a large block and manages it. "
            "A free list of fixed-size chunks avoids fragmentation. "
            "Allocation: pop from free list O(1). Free: push to free list O(1). "
            "Compared to general malloc: no external fragmentation, O(1) alloc/free."
        ),
        "programming_task": (
            "Implement `MemoryPool(block_size: int, num_blocks: int)` with "
            "`allocate() -> int` (returns block id, raises MemoryError if full), "
            "`free(block_id: int)`, "
            "`usage() -> tuple[int,int]` (used, total)."
        ),
        "difficulty": I, "category": "systems",
        "expected_output_example": "p=MemoryPool(64,10); a=p.allocate(); p.usage()→(1,10); p.free(a); p.usage()→(0,10)",
        "constraints": "Use bytearray for backing store. Free list as Python list of ints.",
    },
    {
        "title": "Bit Reversal and Endianness",
        "math_problem": (
            "Reverse bits of 32-bit integer in O(log 32) steps using divide-and-conquer: "
            "swap nibbles, then bytes, then half-words. "
            "Big-endian stores MSB first; little-endian stores LSB first. "
            "Network byte order is big-endian (IETF RFC 1700)."
        ),
        "programming_task": (
            "Implement `reverse_bits_32(n: int) -> int` in O(log 32) via bit manipulation. "
            "`to_big_endian(n: int, bytes: int) -> bytes` and "
            "`from_little_endian(b: bytes) -> int` without struct module."
        ),
        "difficulty": I, "category": "systems",
        "expected_output_example": "reverse_bits_32(0b00000010100101000001111010011100) → 0b00111001011110000010100101000000",
        "constraints": "O(log 32) for reverse_bits. No struct.pack. Manual byte operations.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # SYSTEMS — ADVANCED
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Lock-Free Stack",
        "math_problem": (
            "Compare-and-swap (CAS) is an atomic operation: "
            "CAS(ptr, expected, desired) swaps only if *ptr == expected. "
            "Lock-free stack: push reads head, creates new node pointing to head, "
            "CAS(head, old_head, new_node). Retry on failure. "
            "ABA problem: node reuse can fool CAS; solved with tagged pointers."
        ),
        "programming_task": (
            "Simulate a lock-free stack in Python using `threading` and `ctypes` "
            "(or simulate CAS with a threading.Lock as oracle). "
            "Implement `LockFreeStack` with `push(val)` and `pop() -> int | None`. "
            "Verify correctness under concurrent access with threading tests."
        ),
        "difficulty": A, "category": "systems",
        "expected_output_example": "Run 10 threads each pushing 100 items; total items popped should equal 1000.",
        "constraints": "Use threading. Simulate CAS with atomic compare via a Lock. No high-level queues.",
    },
    {
        "title": "Cache-Friendly Matrix Multiplication",
        "math_problem": (
            "Naïve C = A·B: for each i,j,k: C[i][j] += A[i][k] * B[k][j]. "
            "B is accessed column-wise → cache misses. "
            "Tiled (blocked) version: process b×b tiles; B access becomes row-wise. "
            "With tile size b = sqrt(cache_size/3), reduces cache misses from O(n³) to O(n³/b)."
        ),
        "programming_task": (
            "Implement `matmul_naive(A, B)` and `matmul_tiled(A, B, tile: int = 32)` "
            "for n×n integer matrices. "
            "Time both for n=512 and report speedup. "
            "Also verify correctness: results must be equal."
        ),
        "difficulty": A, "category": "systems",
        "expected_output_example": "Both produce same result for random 64x64 matrices. Tiled is faster for large n.",
        "constraints": "Plain lists of lists. No numpy. Measure with time.perf_counter.",
    },
    {
        "title": "Virtual Address Translation Simulation",
        "math_problem": (
            "Virtual address split: page number (upper bits) + offset (lower bits). "
            "Page size 4KB = 2^12 bytes → 12 offset bits. "
            "With 32-bit address space: 20 bits for page number (2^20 = 1M pages). "
            "Two-level page table reduces memory: only present pages allocated. "
            "TLB hit: O(1); miss: page walk O(levels)."
        ),
        "programming_task": (
            "Implement `MMU(page_bits: int = 12, levels: int = 2)` simulating "
            "two-level page table. `map_page(vpn: int, pfn: int)`, "
            "`translate(virtual_addr: int) -> int`, "
            "`tlb_stats() -> tuple[int,int]` (hits, misses)."
        ),
        "difficulty": A, "category": "systems",
        "expected_output_example": "m=MMU(); m.map_page(0,5); m.translate(0x0ABC) → 0x5ABC (offset preserved)",
        "constraints": "Simulate TLB as fixed-size LRU dict. Two-level PT as nested dicts.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # ALGORITHMS — MORE INTERMEDIATE
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Coin Change — Minimum Coins",
        "math_problem": (
            "dp[i] = minimum coins to make amount i. "
            "dp[i] = min(dp[i - coin] + 1) for each coin ≤ i. "
            "Base: dp[0]=0, dp[i]=∞ initially. "
            "For counting ways: dp[i] += dp[i - coin] (unbounded knapsack). "
            "Both are O(amount × #coins)."
        ),
        "programming_task": (
            "Implement `min_coins(coins: list[int], amount: int) -> int` (-1 if impossible). "
            "And `count_coin_ways(coins: list[int], amount: int) -> int`. "
            "Also `coin_change_combinations(coins, amount) -> list[list[int]]` "
            "returning all combinations (not permutations)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "min_coins([1,5,6,9], 11) → 2 (5+6)\ncount_coin_ways([1,2,5],5) → 4",
        "constraints": "O(amount × len(coins)). No recursion for min_coins/count.",
    },
    {
        "title": "Word Break Problem",
        "math_problem": (
            "dp[i] = True if s[0..i] can be segmented using dictionary. "
            "dp[i] = OR over j<i of (dp[j] AND s[j..i] in dictionary). "
            "With trie for dictionary: O(n²) average. "
            "Word Break II (all sentences): backtracking with memoization."
        ),
        "programming_task": (
            "Implement `word_break(s: str, word_dict: list[str]) -> bool`. "
            "And `word_break_all(s: str, word_dict: list[str]) -> list[str]` "
            "returning all possible sentences."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "word_break('leetcode',['leet','code']) → True\nword_break_all('catsanddog',['cat','cats','and','sand','dog']) → ['cat sand dog','cats and dog']",
        "constraints": "word_break: O(n² · max_word) DP. word_break_all: memo backtracking.",
    },
    {
        "title": "Interval Scheduling and Merging",
        "math_problem": (
            "Activity selection: greedily pick the activity finishing earliest "
            "that doesn't conflict with last selected. "
            "Proof: greedy stays ahead — optimal solution can always be transformed "
            "to include the earliest-finishing activity. "
            "Merge intervals: sort by start, merge overlapping pairs in O(n log n)."
        ),
        "programming_task": (
            "Implement `merge_intervals(intervals: list[tuple[int,int]]) -> list[tuple[int,int]]`. "
            "`max_non_overlapping(intervals) -> int` (greedy). "
            "`min_meeting_rooms(intervals) -> int` (min rooms for all to run concurrently)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "merge_intervals([(1,3),(2,6),(8,10),(15,18)]) → [(1,6),(8,10),(15,18)]\nmin_meeting_rooms([(0,30),(5,10),(15,20)]) → 2",
        "constraints": "O(n log n). merge: sort by start. min_rooms: sweep line or sorted events.",
    },
    {
        "title": "Rotate Image / Spiral Matrix",
        "math_problem": (
            "Rotate n×n matrix 90° clockwise: first transpose (swap a[i][j] and a[j][i]), "
            "then reverse each row. In-place O(n²) time, O(1) space. "
            "Spiral traversal: maintain boundaries (top, bottom, left, right) and shrink inward."
        ),
        "programming_task": (
            "Implement `rotate_90(matrix: list[list[int]])` in-place (clockwise). "
            "`rotate_180`, `rotate_270` reusing rotate_90. "
            "`spiral_order(matrix: list[list[int]]) -> list[int]`."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "rotate_90([[1,2],[3,4]]) → [[3,1],[4,2]]\nspiral_order([[1,2,3],[4,5,6],[7,8,9]]) → [1,2,3,6,9,8,7,4,5]",
        "constraints": "rotate: O(n²) in-place. spiral: O(mn) time O(1) extra space.",
    },
    {
        "title": "Dutch National Flag (3-Way Partition)",
        "math_problem": (
            "Partition array into three groups (< pivot, == pivot, > pivot) in O(n), O(1). "
            "Dijkstra's DNF: maintain pointers lo, mid, hi. "
            "If arr[mid] < pivot: swap(lo, mid), advance both. "
            "If arr[mid] > pivot: swap(mid, hi), retreat hi only (mid stays). "
            "If ==: advance mid."
        ),
        "programming_task": (
            "Implement `dutch_flag(arr: list[int], pivot: int) -> list[int]` returning "
            "the partitioned array. "
            "Also `sort_colors(arr: list[int]) -> list[int]` (sort 0s, 1s, 2s in O(n), O(1))."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "dutch_flag([3,1,2,1,3,2,1], 2) → [1,1,1,2,2,3,3] (stable not required)\nsort_colors([2,0,2,1,1,0]) → [0,0,1,1,2,2]",
        "constraints": "Single pass O(n). O(1) extra space. In-place.",
    },
    {
        "title": "Counting Inversions via Merge Sort",
        "math_problem": (
            "An inversion: pair (i,j) with i<j and arr[i]>arr[j]. "
            "Maximum inversions in array of n elements: n(n-1)/2. "
            "Merge sort counts inversions in O(n log n): during merge, when left[i] > right[j], "
            "all remaining left elements form inversions with right[j]."
        ),
        "programming_task": (
            "Implement `count_inversions(arr: list[int]) -> int` in O(n log n). "
            "Also `inversion_distance(arr: list[int]) -> float` "
            "normalizing to [0,1] (0=sorted, 1=reversed)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "count_inversions([5,4,3,2,1]) → 10\ncount_inversions([1,2,3,4,5]) → 0\ninversion_distance([3,1,2]) → 2/3",
        "constraints": "O(n log n) merge sort approach. No O(n²) brute force.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # ALGORITHMS — MORE ADVANCED
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Maximum Flow — Ford-Fulkerson / BFS (Edmonds-Karp)",
        "math_problem": (
            "Max-flow min-cut theorem: max flow = min cut capacity. "
            "Edmonds-Karp (BFS augmenting paths): O(VE²). "
            "Each BFS finds shortest augmenting path; each edge becomes critical at most V/2 times. "
            "Residual graph: for each edge u→v with capacity c and flow f, "
            "add reverse edge v→u with capacity f."
        ),
        "programming_task": (
            "Implement `max_flow(graph: list[list[int]], source: int, sink: int) -> int` "
            "using Edmonds-Karp. graph[u][v] = capacity. "
            "Also return `min_cut(graph, source, sink) -> list[tuple[int,int]]`."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "max_flow([[0,16,13,0,0,0],[0,0,10,12,0,0],[0,4,0,0,14,0],[0,0,9,0,0,20],[0,0,0,7,0,4],[0,0,0,0,0,0]],0,5) → 23",
        "constraints": "O(VE²). BFS for augmenting paths. Residual graph using adjacency matrix.",
    },
    {
        "title": "Strongly Connected Components — Tarjan's",
        "math_problem": (
            "Tarjan's SCC: DFS assigns discovery time disc[v] and low[v] "
            "(min disc reachable via DFS + one back edge). "
            "v is SCC root if disc[v]==low[v]. "
            "Use a stack to track current DFS path. "
            "O(V+E). One DFS pass, unlike Kosaraju's two-pass."
        ),
        "programming_task": (
            "Implement `tarjan_scc(graph: dict[int,list[int]]) -> list[list[int]]` "
            "returning all SCCs as lists of nodes (each SCC sorted ascending). "
            "Condensation DAG: `condensation(graph) -> dict[int,list[int]]`."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "tarjan_scc({0:[1],1:[2],2:[0],3:[1,2,4],4:[3,5],5:[2,6],6:[5]}) → [[0,1,2],[3,4],[5,6]] (order may vary)",
        "constraints": "O(V+E). Iterative implementation preferred (avoid recursion limit).",
    },
    {
        "title": "Balanced Partition — Number Partition DP",
        "math_problem": (
            "Given S = Σaᵢ, find subset with sum closest to S/2. "
            "Bitset DP: maintain bitmask of achievable sums; for each element, "
            "OR with left-shifted version. "
            "O(nS/64) using 64-bit integers as bitmask words. "
            "NP-hard in general; pseudo-polynomial in sum."
        ),
        "programming_task": (
            "Implement `partition_difference(nums: list[int]) -> int` "
            "returning minimum |S1 - S2| when splitting into two subsets. "
            "Also `can_partition_equal(nums: list[int]) -> bool` (equal sum subsets)."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "partition_difference([1,6,11,5]) → 1\ncan_partition_equal([1,5,11,5]) → True\ncan_partition_equal([1,2,3,5]) → False",
        "constraints": "O(n·S) DP using int as bitmask for Python large integers.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # MATH — MORE PROBLEMS
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Pascal's Triangle and Catalan Numbers",
        "math_problem": (
            "Pascal's triangle: C(n,k) = C(n-1,k-1) + C(n-1,k). "
            "Catalan numbers: Cₙ = C(2n,n)/(n+1) = Σ CᵢC(n-1-i). "
            "C₀=1,C₁=1,C₂=2,C₃=5,C₄=14… "
            "Count: valid bracket sequences, BST shapes, polygon triangulations."
        ),
        "programming_task": (
            "Implement `pascal_triangle(n: int) -> list[list[int]]` (first n rows). "
            "`catalan(n: int) -> int` using DP (O(n²)). "
            "`count_bst_shapes(n: int) -> int` (distinct BST structures with n nodes)."
        ),
        "difficulty": B, "category": "math",
        "expected_output_example": "catalan(5) → 42\ncount_bst_shapes(3) → 5\npascal_triangle(4) → [[1],[1,1],[1,2,1],[1,3,3,1]]",
        "constraints": "No math.comb for catalan. DP approach. count_bst_shapes === catalan.",
    },
    {
        "title": "Probability — Birthday Problem",
        "math_problem": (
            "P(no collision in n people, 365 days) = ∏(k=0 to n-1) (365-k)/365. "
            "P(collision) = 1 - P(no collision). "
            "For P(collision) > 0.5: n ≈ 23 (birthday paradox). "
            "Generalize: given k bins and n throws, expected first collision at n ≈ √(πk/2)."
        ),
        "programming_task": (
            "Implement `birthday_probability(n: int, days: int = 365) -> float` "
            "returning probability of at least two people sharing a birthday. "
            "`min_people_for_prob(p: float, days: int = 365) -> int` "
            "returning minimum n for P(collision) ≥ p."
        ),
        "difficulty": B, "category": "math",
        "expected_output_example": "birthday_probability(23) ≈ 0.5073\nmin_people_for_prob(0.99) → 57",
        "constraints": "Use log probabilities to avoid underflow. Return float rounded to 4 decimals.",
    },
    {
        "title": "Linear Recurrence — Nth Term",
        "math_problem": (
            "A linear recurrence: a[n] = c₁a[n-1] + c₂a[n-2] + … + cₖa[n-k]. "
            "Companion matrix approach: multiply [a[n],…,a[n-k+1]] by companion matrix M. "
            "After r steps: M^r × initial_vector. "
            "Matrix exponentiation gives O(k³ log n). "
            "Tribonacci: a[n]=a[n-1]+a[n-2]+a[n-3] as example."
        ),
        "programming_task": (
            "Implement `linear_recurrence_nth(coeffs: list[int], initial: list[int], n: int, mod: int) -> int` "
            "using matrix exponentiation. "
            "Test with Tribonacci (coeffs=[1,1,1], initial=[0,0,1])."
        ),
        "difficulty": A, "category": "math",
        "expected_output_example": "tribonacci(10) → 44 using linear_recurrence_nth([1,1,1],[0,0,1],10,10**18)",
        "constraints": "O(k³ log n). General for any k. Matrix mult with mod.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # ORIGINAL PHYSICS (kept from original bank)
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Projectile Range Optimizer",
        "math_problem": (
            "Given initial velocity v and angle θ, derive the formula for maximum "
            "horizontal range R. Show that R is maximized when θ = 45°."
        ),
        "programming_task": (
            "Implement a function `max_range(v: float) -> float` in Python that returns "
            "the maximum horizontal range for a given initial velocity. Use g = 9.8 m/s²."
        ),
        "difficulty": B, "category": "math",
        "expected_output_example": "max_range(10) → 10.2",
        "constraints": "Do not use any libraries. Only math operations.",
    },
    {
        "title": "Newton's Square Root",
        "math_problem": (
            "Derive the Newton-Raphson iteration formula for computing √a, starting "
            "from f(x) = x² − a. Show the update rule x_{n+1} = (x_n + a/x_n) / 2."
        ),
        "programming_task": (
            "Implement `newton_sqrt(a: float, eps: float = 1e-9) -> float` in Python "
            "using the derived iteration. Do not use math.sqrt or **0.5."
        ),
        "difficulty": I, "category": "math",
        "expected_output_example": "newton_sqrt(2) → 1.41421356...",
        "constraints": "No math.sqrt, no exponent operator for roots.",
    },
    {
        "title": "Orbital Velocity",
        "math_problem": (
            "Equate gravitational force and centripetal force to derive the circular "
            "orbital velocity v = sqrt(GM/r) for a satellite at radius r."
        ),
        "programming_task": (
            "Implement `orbital_velocity(r: float) -> float` in Python for Earth "
            "(GM = 3.986e14 m³/s²), returning velocity in m/s for orbital radius r meters."
        ),
        "difficulty": I, "category": "math",
        "expected_output_example": "orbital_velocity(6.771e6) → 7672.6",
        "constraints": "Only the math module is allowed.",
    },
    {
        "title": "Damped Oscillator Energy",
        "math_problem": (
            "For a damped harmonic oscillator x(t) = A·e^(−γt)·cos(ωt), derive the "
            "envelope of the mechanical energy over time and show E(t) ≈ E₀·e^(−2γt)."
        ),
        "programming_task": (
            "Implement `energy(t: float, e0: float, gamma: float) -> float` in Python "
            "and a function `half_life(gamma: float) -> float` returning the time for "
            "the energy to halve."
        ),
        "difficulty": A, "category": "math",
        "expected_output_example": "half_life(0.5) → 0.693",
        "constraints": "Only the math module is allowed.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # DYNAMIC PROGRAMMING — EXTRA
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "House Robber I & II",
        "math_problem": (
            "House Robber I: dp[i] = max(dp[i-2]+nums[i], dp[i-1]). "
            "Proof: at each house, either rob it (add to dp[i-2]) or skip (take dp[i-1]). "
            "House Robber II (circular): split into two linear subproblems "
            "[0..n-2] and [1..n-1], take the max."
        ),
        "programming_task": (
            "Implement `rob(nums: list[int]) -> int` (linear) and "
            "`rob_circular(nums: list[int]) -> int` (circular street). "
            "Also `rob_tree(root) -> int` where you cannot rob parent and child simultaneously."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "rob([2,7,9,3,1]) → 12\nrob_circular([2,3,2]) → 3",
        "constraints": "O(n) time O(1) space (rolling vars). rob_tree: post-order DFS.",
    },
    {
        "title": "Unique Paths in Grid",
        "math_problem": (
            "Robot moves only right or down in m×n grid. "
            "dp[i][j] = dp[i-1][j] + dp[i][j-1]. "
            "Closed form: C(m+n-2, m-1). "
            "With obstacles: cells with obstacle get dp=0. "
            "Space O(n) using single row."
        ),
        "programming_task": (
            "Implement `unique_paths(m: int, n: int) -> int` using combination formula. "
            "`unique_paths_obstacles(grid: list[list[int]]) -> int` where 1=obstacle. "
            "`min_path_sum(grid: list[list[int]]) -> int` (sum of values along shortest path)."
        ),
        "difficulty": B, "category": "algorithms",
        "expected_output_example": "unique_paths(3,7) → 28\nmin_path_sum([[1,3,1],[1,5,1],[4,2,1]]) → 7",
        "constraints": "unique_paths: O(1) via math. Others: O(mn) DP, O(n) space.",
    },
    {
        "title": "Jump Game I & II",
        "math_problem": (
            "Jump Game I: can you reach last index? Greedily track max reachable index. "
            "O(n) one pass. "
            "Jump Game II: minimum jumps to reach end. "
            "Greedy BFS levels: current reach and next reach. "
            "At each step boundary, increment jump count. O(n)."
        ),
        "programming_task": (
            "Implement `can_jump(nums: list[int]) -> bool` and "
            "`min_jumps(nums: list[int]) -> int`. "
            "Also `jump_game_iii(arr: list[int], start: int) -> bool` "
            "where from index i you can go to i+arr[i] or i-arr[i]; reach any zero."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "can_jump([2,3,1,1,4]) → True\nmin_jumps([2,3,1,1,4]) → 2\ncan_jump([3,2,1,0,4]) → False",
        "constraints": "All three O(n). No DP for can_jump and min_jumps (greedy).",
    },
    {
        "title": "Egg Drop Problem",
        "math_problem": (
            "With k eggs and n floors, minimize worst-case trials. "
            "dp[t][k] = max floors testable in t trials with k eggs. "
            "dp[t][k] = dp[t-1][k-1] + dp[t-1][k] + 1 (floor below + floor above + current). "
            "Find minimum t such that dp[t][k] ≥ n. "
            "Time O(k log n), space O(k)."
        ),
        "programming_task": (
            "Implement `egg_drop(k: int, n: int) -> int` returning minimum trials "
            "in worst case. Use the binary-search-on-trials approach for efficiency."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "egg_drop(1,100) → 100\negg_drop(2,100) → 14\negg_drop(3,14) → 4",
        "constraints": "O(k log n). Not O(kn²). Use the dp[t][k] inversion.",
    },
    {
        "title": "Longest Bitonic Subsequence",
        "math_problem": (
            "A bitonic sequence first increases then decreases. "
            "Compute LIS ending at each index (left pass) and LDS starting at each index (right pass). "
            "Answer = max over i of (LIS[i] + LDS[i] - 1). "
            "Each pass is O(n log n) with patience sorting."
        ),
        "programming_task": (
            "Implement `longest_bitonic(nums: list[int]) -> int`. "
            "Also `longest_mountain(nums: list[int]) -> int` "
            "(contiguous subarray that is bitonic, length ≥ 3)."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "longest_bitonic([1,11,2,10,4,5,2,1]) → 6\nlongest_mountain([2,1,4,7,3,2,5]) → 5",
        "constraints": "O(n log n) for bitonic. O(n) two-pass for mountain.",
    },
    {
        "title": "Palindrome Partitioning",
        "math_problem": (
            "Min cuts to partition s into palindromes: "
            "dp[i] = min cuts for s[0..i]. "
            "dp[i] = min(dp[j-1] + 1) for all j ≤ i where s[j..i] is palindrome. "
            "Precompute is_palindrome[i][j] in O(n²). "
            "Total O(n²) time and space."
        ),
        "programming_task": (
            "Implement `min_cut(s: str) -> int`. "
            "Also `all_partitions(s: str) -> list[list[str]]` "
            "returning all ways to partition into palindromes (backtracking)."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "min_cut('aab') → 1\nall_partitions('aab') → [['a','a','b'],['aa','b']]",
        "constraints": "min_cut: O(n²). all_partitions: backtracking with memoized palindrome check.",
    },
    {
        "title": "Wildcard to NFA Simulation",
        "math_problem": (
            "An NFA (non-deterministic finite automaton) can simulate wildcards. "
            "State = set of current NFA positions. '.' matches any char (advance one). "
            "'*' creates epsilon transitions (stay or advance). "
            "O(mn) like DP but using set of states explicitly."
        ),
        "programming_task": (
            "Implement `nfa_match(text: str, pattern: str) -> bool` "
            "simulating an NFA for patterns with '.' and '*'. "
            "States are sets of indices into pattern. "
            "Compare result with DP approach for verification."
        ),
        "difficulty": A, "category": "strings",
        "expected_output_example": "nfa_match('aab','c*a*b') → True\nnfa_match('ab','.*') → True",
        "constraints": "NFA simulation using frozenset of states. Must agree with DP.",
    },
    {
        "title": "Buy and Sell Stocks — All Variants",
        "math_problem": (
            "Single transaction: track min price seen; profit = price - min_price. O(n). "
            "Unlimited: sum all positive differences (greedy). O(n). "
            "K transactions: dp[k][i] = max profit using k transactions up to day i. O(kn). "
            "With cooldown: dp[held][i], dp[sold][i], dp[cool][i]. O(n)."
        ),
        "programming_task": (
            "Implement `max_profit_once(prices) -> int`, "
            "`max_profit_unlimited(prices) -> int`, "
            "`max_profit_k(prices, k: int) -> int`, "
            "`max_profit_cooldown(prices) -> int`."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "max_profit_once([7,1,5,3,6,4]) → 5\nmax_profit_unlimited([1,2,3,4,5]) → 4\nmax_profit_cooldown([1,2,3,0,2]) → 3",
        "constraints": "once: O(n) O(1). unlimited: greedy O(n). k: O(kn). cooldown: O(n).",
    },
    {
        "title": "Interleaving Strings",
        "math_problem": (
            "s3 is an interleaving of s1 and s2 if s3 uses all chars of s1 and s2 "
            "maintaining relative order in each. "
            "dp[i][j] = True if s1[0..i]+s2[0..j] forms s3[0..i+j]. "
            "Transition: dp[i][j] = (dp[i-1][j] AND s1[i-1]==s3[i+j-1]) "
            "OR (dp[i][j-1] AND s2[j-1]==s3[i+j-1])."
        ),
        "programming_task": (
            "Implement `is_interleave(s1: str, s2: str, s3: str) -> bool`. "
            "Also `count_interleavings(s1: str, s2: str) -> int` "
            "counting distinct interleavings (mod 10^9+7)."
        ),
        "difficulty": I, "category": "strings",
        "expected_output_example": "is_interleave('aabcc','dbbca','aadbbcbcac') → True\nis_interleave('aabcc','dbbca','aadbbbaccc') → False",
        "constraints": "O(mn) DP. O(n) space rolling row.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # GRAPH — EXTRA
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Number of Islands (BFS/DFS Flood Fill)",
        "math_problem": (
            "Each connected component of '1' cells is an island. "
            "DFS/BFS marks visited cells (flood fill). "
            "Count how many times we start a new DFS from an unvisited '1'. "
            "Time O(mn), space O(mn) worst case for DFS stack."
        ),
        "programming_task": (
            "Implement `num_islands(grid: list[list[str]]) -> int`. "
            "Also `largest_island(grid: list[list[int]]) -> int` "
            "(can flip one 0 to 1; return size of largest island after flip)."
        ),
        "difficulty": B, "category": "algorithms",
        "expected_output_example": "num_islands([['1','1','0'],['1','0','0'],['0','0','1']]) → 2",
        "constraints": "O(mn). Modify grid in-place to mark visited (or use separate set).",
    },
    {
        "title": "Word Ladder — BFS Transformation",
        "math_problem": (
            "Transform beginWord to endWord changing one letter at a time, "
            "each intermediate must be in wordList. "
            "BFS on implicit graph where edges connect words differing by one letter. "
            "Each level = one transformation. Shortest path = min transformations. "
            "Pre-build adjacency using wildcard patterns: 'hot'→'*ot','h*t','ho*'."
        ),
        "programming_task": (
            "Implement `word_ladder(begin: str, end: str, word_list: list[str]) -> int` "
            "returning minimum steps (0 if unreachable). "
            "Also `word_ladder_ii(begin, end, word_list) -> list[list[str]]` "
            "returning all shortest transformation sequences."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "word_ladder('hit','cog',['hot','dot','dog','lot','log','cog']) → 5",
        "constraints": "BFS with pattern grouping. word_ladder_ii: BFS + DFS backtrack.",
    },
    {
        "title": "Clone Graph",
        "math_problem": (
            "Deep copy of an undirected graph. "
            "Use BFS/DFS; maintain a map from original node to its clone. "
            "When visiting neighbors: if neighbor already cloned, use existing clone; "
            "else create new clone and enqueue. "
            "Time O(V+E), space O(V)."
        ),
        "programming_task": (
            "Define `Node(val: int, neighbors: list['Node'])`. "
            "Implement `clone_graph(node: Node) -> Node` using BFS. "
            "Verify the clone is completely independent (no shared references)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "Clone of node 1 in [[1,2],[2,3],[3,4],[4,1]] graph; original and clone are independent.",
        "constraints": "O(V+E). BFS preferred. No recursion limit issues.",
    },
    {
        "title": "Course Schedule — Prerequisite Detection",
        "math_problem": (
            "Course prerequisites form a directed graph. "
            "Can finish all courses iff graph is a DAG (no cycles). "
            "Kahn's algorithm: process nodes with in-degree 0. "
            "If all nodes processed → no cycle. "
            "Course Schedule II: return topological order."
        ),
        "programming_task": (
            "Implement `can_finish(num_courses: int, prerequisites: list[tuple]) -> bool`. "
            "`find_order(num_courses: int, prerequisites: list[tuple]) -> list[int]` "
            "(empty list if impossible)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "can_finish(2,[(1,0)]) → True\ncan_finish(2,[(1,0),(0,1)]) → False\nfind_order(4,[(1,0),(2,0),(3,1),(3,2)]) → [0,1,2,3]",
        "constraints": "Kahn's O(V+E). find_order: same, return empty [] if cycle.",
    },
    {
        "title": "Network Delay Time (Dijkstra)",
        "math_problem": (
            "Minimum time for signal to reach all nodes from source k. "
            "Dijkstra from k; answer = max(dist) over all nodes. "
            "If any node unreachable: return -1. "
            "Weighted directed graph: O((V+E) log V)."
        ),
        "programming_task": (
            "Implement `network_delay(times: list[tuple[int,int,int]], n: int, k: int) -> int`. "
            "times[i] = (source, target, time). "
            "Also `cheapest_flights(n, flights, src, dst, max_stops) -> int` "
            "using Bellman-Ford with at most max_stops+1 relaxations."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "network_delay([(2,1,1),(2,3,1),(3,4,1)],4,2) → 2",
        "constraints": "Dijkstra: O((V+E)logV). cheapest_flights: Bellman-Ford k+1 iterations.",
    },
    {
        "title": "Bipartite Graph Check",
        "math_problem": (
            "A graph is bipartite iff it has no odd-length cycles, "
            "equivalently iff it is 2-colorable. "
            "BFS/DFS 2-coloring: assign color 0 to start, color neighbors with 1, etc. "
            "Conflict (neighbor same color as current) → not bipartite."
        ),
        "programming_task": (
            "Implement `is_bipartite(graph: list[list[int]]) -> bool` "
            "(adjacency list, 0-indexed). "
            "Also return `get_partition(graph) -> tuple[set, set] | None` "
            "(two sets, or None if not bipartite)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "is_bipartite([[1,3],[0,2],[1,3],[0,2]]) → True\nis_bipartite([[1,2,3],[0,2],[0,1,3],[0,2]]) → False",
        "constraints": "O(V+E). BFS coloring. Handle disconnected graph.",
    },
    {
        "title": "Redundant Connection — Cycle in Undirected Graph",
        "math_problem": (
            "Adding edge (u,v) creates a cycle if u and v are already in the same component. "
            "Use DSU: process edges in order; first edge where both endpoints share a root "
            "is the redundant edge. "
            "For directed graph: find edge creating a cycle using DFS or in-degree analysis."
        ),
        "programming_task": (
            "Implement `find_redundant_connection(edges: list[tuple[int,int]]) -> tuple[int,int]` "
            "for undirected graph using DSU. "
            "If multiple answers, return last one in input order."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "find_redundant_connection([(1,2),(1,3),(2,3)]) → (2,3)",
        "constraints": "O(n α(n)) using DSU. Return last redundant edge.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # GREEDY — EXTRA
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Huffman Encoding",
        "math_problem": (
            "Huffman builds optimal prefix-free code using a min-heap. "
            "Merge two lowest-frequency nodes repeatedly. "
            "Expected codeword length = H(X) ≤ L < H(X)+1 where H is Shannon entropy. "
            "Proof: Huffman is optimal by exchange argument."
        ),
        "programming_task": (
            "Implement `huffman_encode(text: str) -> tuple[dict[str,str], str]` "
            "returning (codebook, encoded_bitstring). "
            "`huffman_decode(encoded: str, codebook: dict) -> str`."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "text='aaabbc'; encode and decode must round-trip correctly.",
        "constraints": "Min-heap via heapq. O(n log n). Codebook maps char→binary string.",
    },
    {
        "title": "Task Scheduler with Cooldown",
        "math_problem": (
            "With cooldown n, same task can't run within n intervals. "
            "Minimum time = max(len(tasks), (max_freq-1)*(n+1) + count_of_max_freq). "
            "Derivation: place most frequent task in slots, fill gaps with others or idle. "
            "O(1) formula once frequencies are computed."
        ),
        "programming_task": (
            "Implement `least_interval(tasks: list[str], n: int) -> int`. "
            "Also simulate and return the actual task order "
            "`task_schedule(tasks: list[str], n: int) -> list[str]`."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "least_interval(['A','A','A','B','B','B'],2) → 8\ntask_schedule → ['A','B','_','A','B','_','A','B']",
        "constraints": "least_interval: O(1) formula. task_schedule: greedy with max-heap.",
    },
    {
        "title": "Gas Station — Circular Route",
        "math_problem": (
            "If total gas ≥ total cost, a solution always exists and is unique. "
            "Proof by contradiction: if we run out at station i starting from 0, "
            "start from i+1 instead (all partial sums before i are negative, "
            "so none of those starting points work). O(n) one pass."
        ),
        "programming_task": (
            "Implement `can_complete_circuit(gas: list[int], cost: list[int]) -> int` "
            "returning starting index, or -1 if impossible."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "can_complete_circuit([1,2,3,4,5],[3,4,5,1,2]) → 3",
        "constraints": "O(n) one pass. O(1) space. No brute force O(n²).",
    },
    {
        "title": "Fractional Knapsack",
        "math_problem": (
            "Sort items by value/weight ratio descending. "
            "Greedily take as much of highest-ratio item as possible. "
            "Unlike 0/1 knapsack, fractional is solvable greedily in O(n log n). "
            "Prove exchange argument: replacing any other item with more of the best-ratio item "
            "can only improve or maintain value."
        ),
        "programming_task": (
            "Implement `fractional_knapsack(weights: list[float], values: list[float], "
            "capacity: float) -> float` returning max value achievable. "
            "Also return `items_taken: list[tuple[int, float]]` (index, fraction_taken)."
        ),
        "difficulty": B, "category": "algorithms",
        "expected_output_example": "fractional_knapsack([10,20,30],[60,100,120],50) → 240.0",
        "constraints": "O(n log n). Sort by ratio. Handle capacity exactly.",
    },
    {
        "title": "Meeting Rooms — Interval Overlap",
        "math_problem": (
            "Can one person attend all meetings? Sort by start; check if end[i] > start[i+1]. "
            "Min rooms needed: sweep line — count max concurrent meetings. "
            "Events: +1 at start, -1 at end. Sort events, scan. "
            "Or: sort ends separately and use two-pointer approach."
        ),
        "programming_task": (
            "Implement `can_attend_all(intervals: list[tuple[int,int]]) -> bool`. "
            "`min_rooms(intervals: list[tuple[int,int]]) -> int`. "
            "`free_slots(busy: list[tuple[int,int]], duration: int, "
            "work_start: int, work_end: int) -> list[tuple[int,int]]`."
        ),
        "difficulty": B, "category": "algorithms",
        "expected_output_example": "can_attend_all([(0,30),(5,10),(15,20)]) → False\nmin_rooms([(0,30),(5,10),(15,20)]) → 2",
        "constraints": "All O(n log n). free_slots: merge busy, find gaps ≥ duration.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # TREES — EXTRA
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Lowest Common Ancestor",
        "math_problem": (
            "LCA(u,v) in a rooted tree: first common ancestor. "
            "Naive: O(n) traversal. "
            "Binary lifting: precompute ancestor[i][j] = 2^j-th ancestor of i in O(n log n). "
            "LCA query in O(log n). "
            "Euler tour + RMQ gives O(n) preprocessing, O(1) query."
        ),
        "programming_task": (
            "Implement `lca_naive(root: TreeNode, p: int, q: int) -> int` O(n) "
            "and `lca_binary_lifting(root: TreeNode, p: int, q: int) -> int` O(log n) per query. "
            "Binary lifting: preprocess with `build(root)` first."
        ),
        "difficulty": A, "category": "data-structures",
        "expected_output_example": "Tree: 3(5(6,2(7,4)),1(0,8)); lca(5,1)→3; lca(5,4)→5",
        "constraints": "naive: O(n). binary_lifting: O(n log n) build, O(log n) query.",
    },
    {
        "title": "Serialize and Deserialize Binary Tree",
        "math_problem": (
            "Serialize: pre-order DFS with null markers. "
            "Deserialize: parse tokens, recursively build. "
            "Pre-order with nulls uniquely determines the tree (unlike in-order alone). "
            "Level-order BFS serialization is also common (LeetCode format)."
        ),
        "programming_task": (
            "Implement `serialize(root: TreeNode) -> str` (pre-order with '#' for null). "
            "`deserialize(data: str) -> TreeNode`. "
            "Round-trip: `deserialize(serialize(tree))` must reconstruct exactly."
        ),
        "difficulty": I, "category": "data-structures",
        "expected_output_example": "serialize(1(2,3)) → '1,2,#,#,3,#,#'\ndeserialize('1,2,#,#,3,#,#') reconstructs same tree",
        "constraints": "Pre-order + null markers. O(n) both directions.",
    },
    {
        "title": "Path Sum Variants",
        "math_problem": (
            "Path sum I: does any root-to-leaf path sum to target? DFS O(n). "
            "Path sum II: find all such paths. DFS with backtracking. "
            "Path sum III: count paths (not root-to-leaf) summing to target. "
            "Prefix sum + hash map: O(n)."
        ),
        "programming_task": (
            "Implement `has_path_sum(root, target: int) -> bool`. "
            "`all_path_sums(root, target: int) -> list[list[int]]`. "
            "`count_paths(root, target: int) -> int` (any path, not just root-to-leaf)."
        ),
        "difficulty": I, "category": "data-structures",
        "expected_output_example": "has_path_sum(5(4(11(7,2)),8(13,4(5,1))),22) → True\ncount_paths(tree,8) → 3",
        "constraints": "has_path_sum O(n). all_path_sums backtrack. count_paths prefix-sum O(n).",
    },
    {
        "title": "AVL Tree — Balanced BST",
        "math_problem": (
            "AVL invariant: |height(left) - height(right)| ≤ 1 for every node. "
            "4 rotation cases: LL, RR, LR, RL. "
            "Height h = O(log n). "
            "Search, insert, delete: O(log n) guaranteed. "
            "Rotation preserves BST order and restores AVL property."
        ),
        "programming_task": (
            "Implement `AVLTree` with `insert(val)`, `delete(val)`, `search(val) -> bool`, "
            "`height() -> int`. "
            "All four rotations as private methods. "
            "Verify balance factor maintained after each operation."
        ),
        "difficulty": A, "category": "data-structures",
        "expected_output_example": "t=AVLTree(); [t.insert(i) for i in [10,20,30,40,50]]; t.height() → 3 (not 5)",
        "constraints": "All operations O(log n). Balance factor in each node.",
    },
    {
        "title": "Construct BST from Preorder",
        "math_problem": (
            "Given preorder traversal, first element is root. "
            "Elements < root form left subtree preorder, rest form right subtree. "
            "Naive O(n²). "
            "Optimized: use monotone stack with upper bound O(n). "
            "Alternatively, build using BST insert in O(n log n)."
        ),
        "programming_task": (
            "Implement `bst_from_preorder(preorder: list[int]) -> TreeNode` in O(n). "
            "Verify result is valid BST with correct structure. "
            "Also `bst_from_inorder_preorder(inorder, preorder) -> TreeNode`."
        ),
        "difficulty": I, "category": "data-structures",
        "expected_output_example": "bst_from_preorder([8,5,1,7,10,12]) → BST with root 8",
        "constraints": "O(n) via stack. bst_from_inorder_preorder: O(n) with hashmap.",
    },
    {
        "title": "Diameter of Binary Tree",
        "math_problem": (
            "Diameter = longest path between any two nodes (may not pass through root). "
            "At each node: diameter through it = left_height + right_height. "
            "Single DFS pass: return height, update global max diameter. "
            "Time O(n), space O(h)."
        ),
        "programming_task": (
            "Implement `diameter(root: TreeNode) -> int`. "
            "Also `max_path_sum(root: TreeNode) -> int` "
            "(maximum path sum; path can start and end at any node)."
        ),
        "difficulty": I, "category": "data-structures",
        "expected_output_example": "diameter(1(2(4,5),3)) → 3\nmax_path_sum(-10(9,20(15,7))) → 42",
        "constraints": "Both O(n) single pass. Track max in outer scope.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # STRINGS — EXTRA
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Valid Parentheses and Generation",
        "math_problem": (
            "Valid brackets: stack-based O(n). "
            "Number of valid bracket sequences of length 2n = Catalan(n). "
            "Generation (all valid combos): backtracking with open/close counters. "
            "At each step: add '(' if open < n; add ')' if close < open."
        ),
        "programming_task": (
            "Implement `is_valid(s: str) -> bool` (supports '()', '[]', '{}'). "
            "`generate_parentheses(n: int) -> list[str]` all valid sequences. "
            "`min_remove_to_valid(s: str) -> str` (remove min chars to make valid)."
        ),
        "difficulty": B, "category": "strings",
        "expected_output_example": "is_valid('()[{}]') → True\ngenerate_parentheses(2) → ['(())','()()']",
        "constraints": "is_valid: O(n) stack. generate: backtrack O(4^n/√n). min_remove: O(n).",
    },
    {
        "title": "Count and Say Sequence",
        "math_problem": (
            "Count and Say: describe the previous term's digit runs. "
            "'1' → '11' → '21' → '1211' → '111221'. "
            "Each step: scan runs of identical digits, write count+digit. "
            "Term length grows exponentially (Conway's constant ≈ 1.303)."
        ),
        "programming_task": (
            "Implement `count_and_say(n: int) -> str` returning nth term. "
            "Also `count_and_say_iter(n: int) -> Iterator[str]` "
            "yielding terms lazily. Use run-length compression."
        ),
        "difficulty": B, "category": "strings",
        "expected_output_example": "count_and_say(5) → '111221'\ncount_and_say(6) → '312211'",
        "constraints": "O(L) per step where L is term length. No recursion deeper than n.",
    },
    {
        "title": "String Compression and Decompression",
        "math_problem": (
            "Nested compression: '3[a2[bc]]' → 'abcbcabcbcabcbc'. "
            "Stack-based: push count and current string when '[' seen; "
            "pop and multiply when ']' seen. "
            "Nesting depth d; time O(n·max_value^d)."
        ),
        "programming_task": (
            "Implement `decode_string(s: str) -> str` (LeetCode-style nested encoding). "
            "`encode_string(s: str) -> str` finding a compressed form (not necessarily optimal). "
            "`shortest_encoding(s: str) -> str` trying common repeated substrings."
        ),
        "difficulty": I, "category": "strings",
        "expected_output_example": "decode_string('3[a]2[bc]') → 'aaabcbc'\ndecode_string('3[a2[c]]') → 'accaccacc'",
        "constraints": "decode: O(output_len) stack-based. No eval().",
    },
    {
        "title": "Scramble String",
        "math_problem": (
            "A string can be scrambled by recursively swapping children in its binary split tree. "
            "s1 scrambles s2 iff ∃ split point k: "
            "(scramble(s1[:k], s2[:k]) AND scramble(s1[k:], s2[k:])) "
            "OR (scramble(s1[:k], s2[-k:]) AND scramble(s1[k:], s2[:-k])). "
            "Memoized recursion: O(n⁴) states."
        ),
        "programming_task": (
            "Implement `is_scramble(s1: str, s2: str) -> bool` using memoization. "
            "Prune early: if sorted(s1) != sorted(s2), return False."
        ),
        "difficulty": A, "category": "strings",
        "expected_output_example": "is_scramble('great','rgeat') → True\nis_scramble('abcde','caebd') → False",
        "constraints": "Memoized recursion. O(n⁴) states. Pruning with anagram check.",
    },
    {
        "title": "Text Justification",
        "math_problem": (
            "Fill words into lines of width maxWidth with justified spacing. "
            "Greedy: fit as many words as possible per line. "
            "Distribute spaces evenly; extra spaces go left-to-right. "
            "Last line: left-justified (single spaces between words, pad right)."
        ),
        "programming_task": (
            "Implement `full_justify(words: list[str], max_width: int) -> list[str]`."
        ),
        "difficulty": I, "category": "strings",
        "expected_output_example": "full_justify(['This','is','an','example','of','text','justification'],16) → ['This    is    an','example  of text','justification   ']",
        "constraints": "O(n) greedy. Handle single-word lines and last line separately.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # MATH — EXTRA
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Sum of Arithmetic and Geometric Series",
        "math_problem": (
            "Arithmetic: Sₙ = n(a₁+aₙ)/2 = n(2a₁+(n-1)d)/2. "
            "Geometric: Sₙ = a(rⁿ-1)/(r-1) for r≠1. "
            "Infinite geometric: S = a/(1-r) for |r|<1. "
            "Mixed: Σ k·rᵏ = r·d/dr(Σ rᵏ). Differentiate geometric sum."
        ),
        "programming_task": (
            "Implement `arith_sum(a1: float, d: float, n: int) -> float`, "
            "`geo_sum(a: float, r: float, n: int) -> float`, "
            "`geo_infinite(a: float, r: float) -> float` (raises ValueError if |r|≥1), "
            "`arithmetico_geometric_sum(a: float, d: float, r: float, n: int) -> float`."
        ),
        "difficulty": B, "category": "math",
        "expected_output_example": "arith_sum(1,1,100) → 5050\ngeo_sum(1,2,10) → 1023\ngeo_infinite(1,0.5) → 2.0",
        "constraints": "No loops for arith_sum and geo_sum — use closed forms.",
    },
    {
        "title": "Numerical Integration — Simpson's Rule",
        "math_problem": (
            "Simpson's 1/3 rule: ∫f dx ≈ (h/3)[f(a) + 4f(a+h) + 2f(a+2h) + … + f(b)] "
            "where h=(b-a)/n, n even. "
            "Error O(h⁴). Compare with Trapezoidal O(h²). "
            "Adaptive Simpson: recursively halve intervals where error is large."
        ),
        "programming_task": (
            "Implement `trapezoidal(f, a: float, b: float, n: int) -> float`, "
            "`simpsons(f, a: float, b: float, n: int) -> float`, "
            "`adaptive_simpsons(f, a: float, b: float, tol: float = 1e-6) -> float`."
        ),
        "difficulty": I, "category": "math",
        "expected_output_example": "simpsons(lambda x: x**2, 0, 1, 100) ≈ 0.33333\nsimpsons(math.sin, 0, math.pi, 100) ≈ 2.0",
        "constraints": "f is a callable. n must be even for Simpson. Recursive adaptive.",
    },
    {
        "title": "Complex Numbers and Roots of Unity",
        "math_problem": (
            "n-th roots of unity: ωₖ = e^(2πik/n) = cos(2πk/n) + i·sin(2πk/n). "
            "Product of all roots = (-1)^(n+1). Sum = 0 for n>1. "
            "DFT uses all n-th roots of unity. "
            "Fundamental theorem: ωₖⁿ = 1, distinct for k=0..n-1."
        ),
        "programming_task": (
            "Implement `Complex(re: float, im: float)` with `__add__`, `__mul__`, `__abs__`, "
            "`conjugate()`, `__pow__(n: int)` using De Moivre. "
            "`roots_of_unity(n: int) -> list[Complex]` returning all n-th roots."
        ),
        "difficulty": I, "category": "math",
        "expected_output_example": "roots_of_unity(4) → [1+0i, 0+1i, -1+0i, 0-1i] (approx)",
        "constraints": "No complex built-in. Manual polar/rectangular conversion.",
    },
    {
        "title": "Polynomial Multiplication via FFT (Conceptual)",
        "math_problem": (
            "Convolve two polynomials A, B naively O(n²). "
            "FFT evaluates at n roots of unity in O(n log n). "
            "Pointwise multiply: O(n). "
            "Inverse FFT: O(n log n). "
            "Cooley-Tukey: DFT(x) splits into even/odd subproblems. "
            "T(n) = 2T(n/2) + O(n) → O(n log n)."
        ),
        "programming_task": (
            "Implement `fft(a: list[complex]) -> list[complex]` (Cooley-Tukey, n=power of 2). "
            "`poly_multiply(A: list[int], B: list[int]) -> list[int]` using FFT. "
            "Verify against naive multiplication."
        ),
        "difficulty": A, "category": "math",
        "expected_output_example": "poly_multiply([1,2,3],[4,5]) → [4,13,22,15] (1+2x+3x²)*(4+5x)",
        "constraints": "Recursive FFT. Pad to next power of 2. Round ifft results to int.",
    },
    {
        "title": "Monte Carlo Simulations",
        "math_problem": (
            "Estimate π: throw darts uniformly in [-1,1]² unit square. "
            "P(inside unit circle) = π/4. "
            "By LLN: fraction inside → π/4 as n→∞. "
            "Error O(1/√n) by CLT. "
            "General MC integration: ∫f(x)dx ≈ V·mean(f) with std/√n error."
        ),
        "programming_task": (
            "Implement `estimate_pi(n_samples: int, seed: int = 42) -> float`. "
            "`monte_carlo_integral(f, domain: list[tuple], n_samples: int) -> float` "
            "for arbitrary function over hypercube domain."
        ),
        "difficulty": B, "category": "math",
        "expected_output_example": "estimate_pi(1_000_000) ≈ 3.1416 (within 0.01)",
        "constraints": "Use random.Random(seed) for reproducibility. No numpy.",
    },
    {
        "title": "Combinatorics — Permutations and Derangements",
        "math_problem": (
            "Permutations of n: n!. "
            "Derangement Dₙ = (n-1)(D(n-1)+D(n-2)); D₁=0, D₂=1. "
            "Alternatively: Dₙ = n! Σ(-1)^k/k! for k=0..n ≈ n!/e. "
            "Partial derangement: exactly k fixed points = C(n,k)·D(n-k)."
        ),
        "programming_task": (
            "Implement `derangement_count(n: int) -> int`, "
            "`all_derangements(perm: list[int]) -> list[list[int]]`, "
            "`partial_derangement(n: int, k: int) -> int` (exactly k fixed points)."
        ),
        "difficulty": I, "category": "math",
        "expected_output_example": "derangement_count(4) → 9\npartial_derangement(5,2) → 20",
        "constraints": "derangement_count: DP O(n). all_derangements: backtracking.",
    },
    {
        "title": "Continued Fractions",
        "math_problem": (
            "Every rational p/q has a finite continued fraction [a₀;a₁,…,aₙ]. "
            "Compute via Euclidean algorithm. "
            "Convergents pₖ/qₖ are best rational approximations: "
            "pₖ = aₖpₖ₋₁ + pₖ₋₂, qₖ = aₖqₖ₋₁ + qₖ₋₂. "
            "√2 = [1;2,2,2,…] (infinite periodic)."
        ),
        "programming_task": (
            "Implement `to_continued_fraction(p: int, q: int) -> list[int]`. "
            "`convergents(cf: list[int]) -> list[tuple[int,int]]` returning (p,q) pairs. "
            "`best_rational_approx(x: float, max_denom: int) -> tuple[int,int]`."
        ),
        "difficulty": A, "category": "math",
        "expected_output_example": "to_continued_fraction(415,93) → [4,2,6,7]\nbest_rational_approx(3.14159,100) → (22,7)",
        "constraints": "Euclidean-based. convergents up to requested terms.",
    },
    {
        "title": "Josephus Problem",
        "math_problem": (
            "n people in a circle, every k-th is eliminated. "
            "Recursive formula: J(n,k) = (J(n-1,k) + k) mod n, base J(1,k)=0. "
            "For k=2: J(n) = 2L+1 where n=2^m+L. "
            "Generalization: find position of last survivor. O(n) for general k."
        ),
        "programming_task": (
            "Implement `josephus(n: int, k: int) -> int` (0-indexed survivor position). "
            "`josephus_order(n: int, k: int) -> list[int]` full elimination order. "
            "`josephus_k2(n: int) -> int` using the bit-manipulation formula."
        ),
        "difficulty": I, "category": "math",
        "expected_output_example": "josephus(7,3) → 3 (0-indexed)\njosephus_k2(6) → 4",
        "constraints": "josephus: O(n). josephus_order: O(n²) or O(n log n) with order-stat tree.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # SYSTEMS — EXTRA
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Simple Interpreter / Expression Evaluator",
        "math_problem": (
            "Operator precedence: * and / before + and -. "
            "Shunting-yard algorithm converts infix to postfix using an operator stack. "
            "Two-stack evaluation: operand stack + operator stack. "
            "Both O(n). Recursive descent parser is cleaner but uses O(n) stack."
        ),
        "programming_task": (
            "Implement `evaluate(expr: str) -> int` for expressions with +,-,*,/ "
            "and parentheses. No eval(). "
            "Also support variables: `evaluate_with_vars(expr: str, vars: dict[str,int]) -> int`."
        ),
        "difficulty": I, "category": "systems",
        "expected_output_example": "evaluate('3+2*2') → 7\nevaluate('(2+3)*4') → 20\nevaluate_with_vars('a+b*2',{'a':3,'b':4}) → 11",
        "constraints": "No eval(). Integer division truncates toward zero. O(n).",
    },
    {
        "title": "LFU Cache",
        "math_problem": (
            "LFU evicts least-frequently used item; ties broken by LRU. "
            "Requires: key→value, key→freq, freq→ordered_set_of_keys, min_freq tracker. "
            "get: update freq, move to freq+1 bucket. O(1). "
            "put: if full, evict from min_freq bucket (oldest in that freq). O(1)."
        ),
        "programming_task": (
            "Implement `LFUCache(capacity: int)` with `get(key: int) -> int` (or -1) "
            "and `put(key: int, value: int)`. Both O(1). "
            "Use three dicts: values, freqs, freq_to_keys (OrderedDict per freq)."
        ),
        "difficulty": A, "category": "data-structures",
        "expected_output_example": "c=LFUCache(2); c.put(1,1); c.put(2,2); c.get(1)→1; c.put(3,3); c.get(2)→-1; c.get(3)→3",
        "constraints": "O(1) both ops. collections.OrderedDict for insertion order within freq.",
    },
    {
        "title": "Consistent Hashing Ring",
        "math_problem": (
            "Consistent hashing: hash nodes and keys onto [0, 2^32). "
            "Key maps to first node clockwise on ring. "
            "Adding/removing node: only ~K/n keys reassigned (vs K/n_old in naive). "
            "Virtual nodes improve load distribution: each server → v virtual nodes."
        ),
        "programming_task": (
            "Implement `ConsistentHashRing` with `add_node(name: str)`, "
            "`remove_node(name: str)`, `get_node(key: str) -> str`. "
            "Support virtual nodes (default 150). Use SHA1 for hashing."
        ),
        "difficulty": A, "category": "systems",
        "expected_output_example": "r=ConsistentHashRing(); r.add_node('A'); r.add_node('B'); r.get_node('hello') → 'A' or 'B'",
        "constraints": "Sorted list of virtual node positions. bisect for O(log n) lookup.",
    },
    {
        "title": "Event-Driven Simulation",
        "math_problem": (
            "Discrete event simulation: priority queue of events by time. "
            "Process minimum-time event, generate new events. "
            "Example: M/M/1 queue — Poisson arrivals (rate λ), exponential service (rate μ). "
            "Server utilization ρ = λ/μ. Mean queue length = ρ/(1-ρ) for ρ<1."
        ),
        "programming_task": (
            "Implement `simulate_mm1(arrival_rate: float, service_rate: float, "
            "duration: float, seed: int = 0) -> dict` returning "
            "{avg_queue_length, avg_wait_time, utilization, num_served}."
        ),
        "difficulty": A, "category": "systems",
        "expected_output_example": "simulate_mm1(0.8, 1.0, 10000) → utilization ≈ 0.8, avg_queue ≈ 3.2",
        "constraints": "heapq-based event queue. Exponential via -log(U)/rate. No external libs.",
    },
    {
        "title": "Rate Limiter — Token Bucket and Sliding Window",
        "math_problem": (
            "Token bucket: tokens refill at rate r, max capacity c. "
            "Request consumes 1 token; rejected if empty. "
            "Sliding window log: keep timestamps of requests in window. "
            "Sliding window counter: approximate using current+previous bucket weighted. "
            "Memory: O(1) token bucket vs O(requests_per_window) log."
        ),
        "programming_task": (
            "Implement `TokenBucket(capacity: int, refill_rate: float)` with "
            "`allow(timestamp: float) -> bool`. "
            "`SlidingWindowLog(limit: int, window_sec: float)` with `allow(timestamp) -> bool`. "
            "`SlidingWindowCounter(limit: int, window_sec: float)` with `allow(timestamp) -> bool`."
        ),
        "difficulty": I, "category": "systems",
        "expected_output_example": "tb=TokenBucket(5,1.0); [tb.allow(i) for i in range(7)] → [T,T,T,T,T,F,T] approx",
        "constraints": "Token bucket: O(1). SlidingWindowLog: O(requests) per window.",
    },
    {
        "title": "Rope Data Structure",
        "math_problem": (
            "A rope stores a long string as a binary tree of shorter strings. "
            "Concat: O(1) — just create new root pointing to both. "
            "Split at index i: O(log n). "
            "Index[i]: O(log n) — traverse by cumulative weight. "
            "Rebalance via Fibonacci number criterion."
        ),
        "programming_task": (
            "Implement `Rope` with `__init__(s: str)`, `index(i: int) -> str`, "
            "`concat(other: 'Rope') -> 'Rope'`, `split(i: int) -> tuple['Rope','Rope']`, "
            "`to_string() -> str`."
        ),
        "difficulty": A, "category": "data-structures",
        "expected_output_example": "r=Rope('Hello'); r2=Rope(' World'); r3=r.concat(r2); r3.to_string() → 'Hello World'",
        "constraints": "Leaf max 10 chars. Concat O(1). Index O(log n).",
    },

    # ══════════════════════════════════════════════════════════════════════
    # CONCURRENCY / OS CONCEPTS — BEGINNER/INTERMEDIATE
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Producer-Consumer with Semaphores",
        "math_problem": (
            "Semaphore S: P(S) decrements (blocks if 0), V(S) increments. "
            "Bounded buffer: empty=N, full=0, mutex=1. "
            "Producer: P(empty), P(mutex), add, V(mutex), V(full). "
            "Consumer: P(full), P(mutex), remove, V(mutex), V(empty). "
            "Correctness: mutual exclusion + no deadlock."
        ),
        "programming_task": (
            "Implement `BoundedBuffer(capacity: int)` with `put(item)` and `get() -> item` "
            "using `threading.Semaphore` and `threading.Lock`. "
            "Test with 4 producers and 4 consumers adding 100 items each."
        ),
        "difficulty": I, "category": "systems",
        "expected_output_example": "All 400 items produced are eventually consumed; no deadlock; no race conditions.",
        "constraints": "Use threading.Semaphore only. No queue.Queue. Verify item count.",
    },
    {
        "title": "Readers-Writers Lock",
        "math_problem": (
            "Multiple readers may read simultaneously; writer needs exclusive access. "
            "First readers-writers: readers never wait if another reader holds lock. "
            "Risk: writer starvation. "
            "Second solution: no writer waits more than one reader passes. "
            "Third: prioritize writers — no new reader starts if writer waiting."
        ),
        "programming_task": (
            "Implement `RWLock` with `read_acquire()`, `read_release()`, "
            "`write_acquire()`, `write_release()`. "
            "Variant 1: reader-priority. Test with concurrent readers and writers."
        ),
        "difficulty": I, "category": "systems",
        "expected_output_example": "Multiple threads reading simultaneously allowed; write is exclusive.",
        "constraints": "Only threading.Lock and threading.Semaphore. Verify invariants.",
    },
    {
        "title": "Dining Philosophers",
        "math_problem": (
            "5 philosophers, 5 forks. Each needs 2 forks to eat. "
            "Naïve: all pick left fork → deadlock. "
            "Solutions: resource ordering (number forks, always pick lower first); "
            "Chandy/Misra (message passing); "
            "Arbitrator (waiter semaphore). "
            "Prove resource ordering prevents circular wait."
        ),
        "programming_task": (
            "Implement `dining_philosophers(n: int, meals: int)` using resource ordering. "
            "Each philosopher eats `meals` times. No deadlock, no starvation. "
            "Print events: 'P{i} eating', 'P{i} thinking'."
        ),
        "difficulty": I, "category": "systems",
        "expected_output_example": "5 philosophers each eat 3 times without deadlock.",
        "constraints": "n forks as threading.Lock. Resource ordering: pick min(i,(i+1)%n) first.",
    },
    {
        "title": "Thread Pool Implementation",
        "math_problem": (
            "Thread pool reuses a fixed number of worker threads. "
            "Work queue holds pending tasks. "
            "Workers loop: dequeue task, execute, repeat. "
            "Shutdown: signal workers to stop (sentinel or event). "
            "Max throughput when #threads ≈ #CPUs for CPU-bound; more for I/O-bound."
        ),
        "programming_task": (
            "Implement `ThreadPool(num_workers: int)` with "
            "`submit(fn, *args) -> Future`, `shutdown(wait: bool = True)`. "
            "Future: `result(timeout=None)`, `done() -> bool`. "
            "Test with 100 tasks summing arrays."
        ),
        "difficulty": A, "category": "systems",
        "expected_output_example": "pool=ThreadPool(4); futures=[pool.submit(sum,range(i)) for i in range(100)]; all results correct.",
        "constraints": "No concurrent.futures. Manual threading.Thread workers. queue.Queue ok.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # BACKTRACKING — EXTRA
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "N-Queens Problem",
        "math_problem": (
            "Place n queens on n×n board; none attack each other. "
            "Backtrack: place queen in each row, check column+diagonal conflicts. "
            "Track sets: cols, diag1 (r-c), diag2 (r+c). O(1) conflict check. "
            "Distinct solutions for n=8: 92. Time O(n!)."
        ),
        "programming_task": (
            "Implement `solve_n_queens(n: int) -> list[list[str]]` returning all solutions "
            "as board representations. "
            "Also `count_n_queens(n: int) -> int` (faster, no board storage)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "count_n_queens(8) → 92\nlen(solve_n_queens(4)) → 2",
        "constraints": "O(n!) backtracking. O(1) attack check with sets.",
    },
    {
        "title": "Sudoku Solver",
        "math_problem": (
            "Constraint propagation + backtracking. "
            "Arc consistency: if a cell has 1 possible value, assign and propagate. "
            "MRV heuristic: choose the cell with fewest remaining values. "
            "Exact cover formulation reduces to Algorithm X / DLX."
        ),
        "programming_task": (
            "Implement `solve_sudoku(board: list[list[str]]) -> bool` "
            "modifying board in-place. '.' represents empty cells. "
            "Use backtracking with MRV (choose cell with fewest options first)."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "Solve standard 9x9 sudoku. Returns True if solvable, modifies board in-place.",
        "constraints": "Backtracking + constraint checking. MRV heuristic. O(9^81) worst (practical: fast).",
    },
    {
        "title": "Subsets and Permutations",
        "math_problem": (
            "Subsets of n elements: 2^n total. Bitmask enumeration or backtracking. "
            "Permutations: n! total. Heap's algorithm generates all in O(n!). "
            "Next permutation: find rightmost ascending pair, swap with successor, reverse suffix. "
            "Combination sum: backtracking with pruning when sum exceeds target."
        ),
        "programming_task": (
            "Implement `all_subsets(nums: list[int]) -> list[list[int]]` (handles duplicates). "
            "`all_permutations(nums: list[int]) -> list[list[int]]` (handles duplicates). "
            "`next_permutation(nums: list[int]) -> list[int]` in O(n) O(1) extra."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "all_subsets([1,2,2]) → [[],[1],[2],[1,2],[2,2],[1,2,2]]\nnext_permutation([1,2,3]) → [1,3,2]",
        "constraints": "all_subsets with duplicates: sort first. next_perm: O(n) in-place.",
    },
    {
        "title": "Combination Sum I & II & III",
        "math_problem": (
            "I: candidates can reuse, find all combos summing to target. "
            "II: each candidate used once (duplicates in input allowed). "
            "III: use only 1-9, exactly k numbers, sum to n. "
            "All: backtracking with sort-and-prune when branch sum > target."
        ),
        "programming_task": (
            "Implement `combination_sum(candidates: list[int], target: int) -> list[list[int]]`. "
            "`combination_sum_ii(candidates: list[int], target: int) -> list[list[int]]`. "
            "`combination_sum_iii(k: int, n: int) -> list[list[int]]`."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "combination_sum([2,3,6,7],7) → [[2,2,3],[7]]\ncombination_sum_iii(3,9) → [[1,2,6],[1,3,5],[2,3,4]]",
        "constraints": "Sort candidates. Prune when sum > target. Skip duplicates in II.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # INTERVALS AND SWEEP LINE
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Skyline Problem",
        "math_problem": (
            "Buildings as [left, right, height]. Find the skyline contour. "
            "Events: at left edge height goes up, at right edge height goes down. "
            "Sweep from left: use max-heap of active heights. "
            "Skyline point when current max height changes. "
            "Time O(n log n) with heap."
        ),
        "programming_task": (
            "Implement `get_skyline(buildings: list[tuple[int,int,int]]) -> list[tuple[int,int]]` "
            "returning critical points [x, height]. "
            "Use event-based sweep with heap."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "get_skyline([(2,9,10),(3,7,15),(5,12,12),(15,20,10),(19,24,8)]) → [(2,10),(3,15),(7,12),(12,0),(15,10),(20,8),(24,0)]",
        "constraints": "O(n log n). Handle ties at same x properly. Use sorted events.",
    },
    {
        "title": "Rectangle Area Union",
        "math_problem": (
            "Area of union of rectangles. Coordinate compression + sweep line. "
            "Sort by x. At each x-segment, compute active y-intervals union length. "
            "Area += (x_next - x_curr) × y_union_length. "
            "Y-union length via segment tree with lazy propagation. "
            "Total O(n log n)."
        ),
        "programming_task": (
            "Implement `rectangle_union_area(rects: list[tuple[int,int,int,int]]) -> int` "
            "where each rect is (x1,y1,x2,y2). "
            "Also `rectangle_intersection_count(rects) -> list[int]` "
            "counting how many rectangles cover each grid cell."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "rectangle_union_area([(0,0,2,2),(1,1,3,3)]) → 7",
        "constraints": "Coordinate compression + sweep line. O(n log n).",
    },

    # ══════════════════════════════════════════════════════════════════════
    # NETWORK / PROTOCOL SIMULATION
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "HTTP/1.1 Request Parser",
        "math_problem": (
            "HTTP/1.1 request format: 'METHOD PATH HTTP/1.1\\r\\n' "
            "followed by 'Header: Value\\r\\n' lines, empty line, optional body. "
            "Content-Length determines body size. "
            "Chunked transfer: each chunk prefixed with hex size + \\r\\n."
        ),
        "programming_task": (
            "Implement `parse_http_request(raw: bytes) -> dict` returning "
            "{method, path, version, headers, body}. "
            "Also `build_http_response(status: int, headers: dict, body: bytes) -> bytes`."
        ),
        "difficulty": I, "category": "systems",
        "expected_output_example": "parse_http_request(b'GET /index HTTP/1.1\\r\\nHost: example.com\\r\\n\\r\\n') → {method:'GET',path:'/index',...}",
        "constraints": "No http.server or urllib. Manual byte parsing. Handle CRLF.",
    },
    {
        "title": "LZ77 Compression",
        "math_problem": (
            "LZ77 compresses by replacing repeated sequences with (offset, length, next_char). "
            "Sliding window: look-ahead buffer searched in history window. "
            "Best match: longest substring in history matching lookahead. "
            "Output: (0,0,char) for new chars; (dist, len, char) for matches. "
            "Decompression: O(output) by copying back-references."
        ),
        "programming_task": (
            "Implement `lz77_compress(data: str, window: int = 255, lookahead: int = 15) "
            "-> list[tuple]` and `lz77_decompress(tokens: list[tuple]) -> str`. "
            "Round-trip must be lossless."
        ),
        "difficulty": A, "category": "systems",
        "expected_output_example": "lz77_compress('abracadabra') → tokens; lz77_decompress(tokens) → 'abracadabra'",
        "constraints": "Naive O(n × window) search is fine. Exact round-trip required.",
    },
    {
        "title": "CRC32 Checksum",
        "math_problem": (
            "CRC treats data as polynomial over GF(2). "
            "Divide by generator polynomial G(x) (degree 32); CRC = remainder. "
            "Table-based CRC: precompute 256-entry table for 8-bit byte processing. "
            "Polynomial for CRC-32: 0xEDB88320 (reflected)."
        ),
        "programming_task": (
            "Implement `crc32_table() -> list[int]` (256 entries). "
            "`crc32(data: bytes) -> int` using the table. "
            "Verify against `binascii.crc32`."
        ),
        "difficulty": I, "category": "systems",
        "expected_output_example": "crc32(b'hello') → 907060870 (same as binascii.crc32(b'hello') & 0xFFFFFFFF)",
        "constraints": "Table-based O(n). No binascii in implementation. Verify with it.",
    },

    # ══════════════════════════════════════════════════════════════════════
    # MISCELLANEOUS CLASSICS
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Reservoir Sampling",
        "math_problem": (
            "Sample k items uniformly from stream of unknown size n. "
            "Algorithm R: fill reservoir with first k; for i>k, keep item with prob k/i, "
            "replacing random item. "
            "Proof: each item has equal probability k/n at end. "
            "O(n) time, O(k) space."
        ),
        "programming_task": (
            "Implement `reservoir_sample(stream: Iterator, k: int, seed: int = 0) -> list`. "
            "Verify uniform distribution empirically over 10^5 trials."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "reservoir_sample(range(100), 10) returns 10 distinct items from 0-99.",
        "constraints": "Single pass over stream. O(k) memory. random.Random(seed).",
    },
    {
        "title": "Fisher-Yates Shuffle",
        "math_problem": (
            "Fisher-Yates produces uniform random permutation. "
            "For i from n-1 down to 1: swap arr[i] with arr[random(0..i)]. "
            "Proof: n! possible permutations, each chosen with probability 1/n!. "
            "In-place O(n). Naïve sort-by-random is O(n log n) and biased."
        ),
        "programming_task": (
            "Implement `fisher_yates(arr: list, seed: int = 0) -> list`. "
            "Test uniformity: shuffle [0,1,2] 60000 times; each of 6 permutations ≈10000. "
            "Also implement `shuffle_deck() -> list[str]` for standard 52-card deck."
        ),
        "difficulty": B, "category": "algorithms",
        "expected_output_example": "Each permutation of [0,1,2] appears ~10000/60000 ≈ 1/6 of shuffles.",
        "constraints": "O(n) in-place. Only random.Random(seed). No random.shuffle.",
    },
    {
        "title": "Median of Two Sorted Arrays",
        "math_problem": (
            "Binary search on smaller array: partition both into left halves of same total size. "
            "Valid partition: maxLeft1 ≤ minRight2 AND maxLeft2 ≤ minRight1. "
            "O(log(min(m,n))). "
            "Median = avg(maxLeft, minRight) for even total, maxLeft for odd."
        ),
        "programming_task": (
            "Implement `find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float`. "
            "Must be O(log(min(m,n))). "
            "Also `kth_of_two_sorted(nums1, nums2, k: int) -> int` returning k-th smallest."
        ),
        "difficulty": A, "category": "algorithms",
        "expected_output_example": "find_median_sorted_arrays([1,3],[2]) → 2.0\nfind_median_sorted_arrays([1,2],[3,4]) → 2.5",
        "constraints": "O(log(min(m,n))). Binary search on smaller array. No merge.",
    },
    {
        "title": "Trapping Rain Water",
        "math_problem": (
            "Water at position i = min(max_left[i], max_right[i]) - height[i]. "
            "Precompute prefix max and suffix max: O(n) time, O(n) space. "
            "Two-pointer O(n) O(1): if left_max < right_max, process left; else right. "
            "Proof: the smaller side determines water level regardless of what's between."
        ),
        "programming_task": (
            "Implement `trap(height: list[int]) -> int` two-pointer O(1) space. "
            "Also `trap_3d(heightMap: list[list[int]]) -> int` (3D variant using min-heap BFS)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "trap([0,1,0,2,1,0,1,3,2,1,2,1]) → 6\ntrap([4,2,0,3,2,5]) → 9",
        "constraints": "trap: O(n) O(1) two-pointer. trap_3d: O(mn log(mn)) min-heap.",
    },
    {
        "title": "Largest Rectangle in Histogram (Stack)",
        "math_problem": (
            "For each bar as the minimum, find widest span. "
            "Monotone stack: maintain increasing heights. "
            "When smaller bar found, pop and compute area = h * (right - left - 1). "
            "Append sentinel 0 to flush stack. O(n) — each bar pushed/popped once."
        ),
        "programming_task": (
            "Implement `largest_rectangle(heights: list[int]) -> int`. "
            "Also `maximal_rectangle(matrix: list[list[str]]) -> int` "
            "(convert each column to histogram, apply largest_rectangle per row)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "largest_rectangle([2,1,5,6,2,3]) → 10\nmaximal_rectangle([['1','0','1','0'],['1','0','1','1'],['1','1','1','1']]) → 6",
        "constraints": "Both O(mn). Stack-based. No O(n²) brute force.",
    },
    {
        "title": "4Sum and K-Sum General",
        "math_problem": (
            "2Sum: O(n) hash. 3Sum: O(n²) fix one, 2-pointer rest. "
            "4Sum: O(n³). K-Sum recursive: reduce to (K-1)-Sum. "
            "Base case K=2: two-pointer O(n). "
            "Duplicate skipping: skip equal values after sorting. "
            "Total O(n^(K-1))."
        ),
        "programming_task": (
            "Implement `four_sum(nums: list[int], target: int) -> list[list[int]]`. "
            "`k_sum(nums: list[int], target: int, k: int) -> list[list[int]]` "
            "(general recursive solution)."
        ),
        "difficulty": I, "category": "algorithms",
        "expected_output_example": "four_sum([1,0,-1,0,-2,2],0) → [[-2,-1,1,2],[-2,0,0,2],[-1,0,0,1]]",
        "constraints": "No duplicate tuples. k_sum: O(n^(k-1)). Sort first.",
    },
]


def seed() -> None:
    db = SessionLocal()
    try:
        # Trail phases — upsert by number
        for phase in PHASES:
            existing = db.scalar(select(TrailPhase).where(TrailPhase.number == phase["number"]))
            if existing is None:
                db.add(TrailPhase(**phase))

        # Fallback challenges — upsert by title (idempotent additions)
        existing_titles = {
            c.title for c in db.scalars(select(FallbackChallenge)).all()
        }
        added = 0
        for challenge in FALLBACK_CHALLENGES:
            if challenge["title"] not in existing_titles:
                db.add(FallbackChallenge(**challenge))
                added += 1

        db.commit()
        print(f"Seed complete. Added {added} new fallback challenge(s). Total defined: {len(FALLBACK_CHALLENGES)}.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
