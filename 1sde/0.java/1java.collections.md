# Java Collections & Generics — Interview Study Guide

Same structure as the messaging guide:
- **Part 1** — question index only (self-test: read the question, answer aloud, then check).
- **Part 2** — answers at two levels. `L4` = correct + mechanism-aware. `L5` = adds tradeoff, failure mode, ownership.
- **Part 3** — runnable reference code (Java 17).
- **Part 4** — Generics quick view.

Baseline: **Java 17**, with Java 8 vs 7 differences called out where interviewers still probe them.

---

# PART 1 — QUESTION INDEX

## System 1 — Contracts & hierarchy (`CH-`)
- `CH-1` Sketch the Collection/Map hierarchy. Why is `Map` not a `Collection`?
- `CH-2` State the `equals`/`hashCode` contract. What breaks when it's violated?
- `CH-3` What makes a good hash key? Why must it be effectively immutable?
- `CH-4` `Comparable` vs `Comparator`. What does "consistent with equals" mean and where does it bite?
- `CH-5` Fail-fast vs weakly-consistent vs snapshot iterators — which collections give which?
- `CH-6` What causes `ConcurrentModificationException` in a *single* thread?
- `CH-7` Which collections accept `null` keys/values, which don't, and why?
- `CH-8` Views vs copies — `subList`, `keySet`, `values`, `entrySet`, `Arrays.asList`.
- `CH-9` Unmodifiable vs immutable vs `List.of` — what's actually different?
- `CH-10` Why return `Collections.emptyList()` instead of `null`?

## System 2 — List (`LI-`)
- `LI-1` `ArrayList` internals: growth policy, copy mechanics, default capacity.
- `LI-2` `ArrayList` vs `LinkedList` — is `LinkedList` ever the right answer?
- `LI-3` What does the `RandomAccess` marker interface change?
- `LI-4` `remove(int)` vs `remove(Object)` on `List<Integer>` — the classic trap.
- `LI-5` `Arrays.asList` pitfalls.
- `LI-6` `subList` mechanics and its CME risk.
- `LI-7` `CopyOnWriteArrayList` — cost model and correct use cases.
- `LI-8` `Vector`/`Stack` — why they're effectively dead.
- `LI-9` Safe ways to remove while iterating.
- `LI-10` Presizing and `trimToSize` — when does it actually matter?

## System 3 — Map (`MP-`)
- `MP-1` Walk `HashMap.put` end to end: hash → index → bucket → resize.
- `MP-2` Why `h ^ (h >>> 16)` and why `(n-1) & hash` instead of `%`?
- `MP-3` Resize mechanics. What changed in Java 8's lo/hi split?
- `MP-4` Treeification: why 8, why 64, why untreeify at 6?
- `MP-5` Load factor 0.75 — what's the tradeoff being priced?
- `MP-6` What happens if a key's `hashCode` changes after insertion?
- `MP-7` `HashMap` under concurrent writes — Java 7 infinite loop vs Java 8 behavior.
- `MP-8` `LinkedHashMap` — insertion vs access order. How do you build an LRU?
- `MP-9` `TreeMap`/`NavigableMap` — API surface and when to reach for it.
- `MP-10` `ConcurrentHashMap` (Java 8) design: CAS, per-bin lock, lock-free reads.
- `MP-11` Why is `CHM.size()` approximate? What is `mappingCount()`?
- `MP-12` How does CHM resize concurrently (`ForwardingNode`, `helpTransfer`)?
- `MP-13` `computeIfAbsent` — what's atomic, and what's the recursive-update trap?
- `MP-14` `Collections.synchronizedMap` vs `ConcurrentHashMap`.
- `MP-15` `ConcurrentSkipListMap` — when over CHM?
- `MP-16` `EnumMap` / `EnumSet` internals.
- `MP-17` `WeakHashMap` semantics. Which leak does it *not* fix?
- `MP-18` `IdentityHashMap` — when is `==` semantics correct?
- `MP-19` `Hashtable` vs `HashMap`.
- `MP-20` Hash-collision DoS — the attack and the mitigation.
- `MP-21` Build an LRU cache. What would you actually ship?
- `MP-22` Presizing a `HashMap` for *n* entries — what number do you pass?

## System 4 — Set (`ST-`)
- `ST-1` `HashSet`/`LinkedHashSet`/`TreeSet` — what backs each?
- `ST-2` Why does `HashSet` store a dummy `PRESENT` object?
- `ST-3` `TreeSet` ordering vs `equals` — duplicates that aren't duplicates.
- `ST-4` Concurrent set options and how to get one from any map.
- `ST-5` `Set.of` — duplicate rejection and randomized iteration order.

## System 5 — Queue & Deque (`QD-`)
- `QD-1` Queue vs Deque vs Stack. What replaces `java.util.Stack`?
- `QD-2` `ArrayDeque` internals — why it beats `LinkedList` for both stack and queue.
- `QD-3` `PriorityQueue` internals, iteration order, `remove(Object)` cost.
- `QD-4` Top-K with a heap — which direction of comparator, and why?
- `QD-5` The `BlockingQueue` family and a selection framework.
- `QD-6` `ArrayBlockingQueue` vs `LinkedBlockingQueue` lock design.
- `QD-7` `SynchronousQueue` and `newCachedThreadPool`.
- `QD-8` `DelayQueue` and scheduled/retry work.
- `QD-9` Unbounded queue + fixed thread pool = the classic OOM. Explain.
- `QD-10` `ConcurrentLinkedQueue` vs `LinkedBlockingQueue`.
- `QD-11` `add/offer`, `remove/poll`, `element/peek` — three families, three failure behaviors.

## System 6 — Concurrency & memory model (`CC-`)
- `CC-1` How do you safely publish a collection to other threads?
- `CC-2` Which compound operations are still unsafe on a `ConcurrentHashMap`?
- `CC-3` Iterator guarantees across the concurrent collections.
- `CC-4` Defensive copies at API boundaries — when are they worth it?
- `CC-5` Why are immutable collections thread-safe without synchronization?

## System 7 — Streams & bulk operations (`SB-`)
- `SB-1` `Collectors.toMap` — duplicate key and null value traps.
- `SB-2` `groupingBy` vs `toMap` vs `partitioningBy`; downstream collectors.
- `SB-3` `Collectors.toList()` vs `Stream.toList()` — mutability contract.
- `SB-4` When is a parallel stream over a collection actually faster?
- `SB-5` What is a `Spliterator` and why do its characteristics matter?

## System 8 — Performance & memory (`PF-`)
- `PF-1` Big-O cheat sheet — and where constants dominate the asymptotics.
- `PF-2` Boxing and object-header overhead; when to reach for primitive collections.
- `PF-3` Cache locality: `ArrayList` vs `LinkedList` in the real world.
- `PF-4` Decision framework: how do you pick a collection in a design round?

## System 9 — Production failure modes (`FM-`)
- `FM-1` What are the collection-related incidents you'd actually expect in production?
- `FM-2` Mutable-key defects — how do they present?
- `FM-3` Unbounded growth via collections — the leak patterns.
- `FM-4` `ThreadLocal` + map leaks in application containers.

---

# PART 2 — ANSWERS

---

## System 1 — Contracts & hierarchy

### `CH-1` Hierarchy; why Map isn't a Collection

**L4**
- `Iterable` → `Collection` → `List`, `Set`, `Queue`. `Deque extends Queue`. `SortedSet` → `NavigableSet`.
- `Map` is a separate root: `Map` → `SortedMap` → `NavigableMap`. `ConcurrentMap` is a sibling interface.
- `Map` is not a `Collection` because a `Collection` is a collection of single elements; a map is a collection of *pairs*. `add(E)` has no sensible meaning.
- A map exposes three collection *views*: `keySet()`, `values()`, `entrySet()`.

**L5**
- The split is a deliberate API design decision, not an oversight — Josh Bloch has said forcing `Map extends Collection<Map.Entry>` would have made every `Collection` operation ambiguous on maps.
- The interesting consequence is the *view* contract: the views are live and backed by the map, so `map.keySet().remove(k)` mutates the map. That's the thing juniors get wrong.
- `Set` is essentially `Map` with the values discarded — `HashSet` literally wraps a `HashMap`. Recognizing that means every `HashMap` tuning answer transfers to `HashSet` for free.

### `CH-2` equals/hashCode contract

**L4**
- `equals` must be: reflexive, symmetric, transitive, consistent, and `x.equals(null) == false`.
- `hashCode`: equal objects **must** have equal hash codes. Unequal objects *may* collide.
- Violation → an object put into a `HashMap` cannot be found by an equal key, or duplicates appear in a `HashSet`.

**L5**
- The asymmetric direction matters: breaking `equals ⇒ same hashCode` silently loses data. Breaking the reverse only costs performance.
- Symmetry breaks in practice with `instanceof`-based `equals` across a subclass — `super.equals(sub)` true, `sub.equals(super)` false. Use `getClass()` comparison or composition instead of inheritance (Effective Java Item 10).
- Records and Lombok `@EqualsAndHashCode` generate both together, which removes the most common class of bug. In JPA entities, prefer a business key or a UUID assigned before persist — never the generated ID, because it's null before flush and the hash changes after.
- Ownership framing: I treat `equals`/`hashCode` on any type that enters a `Set` or a map key position as a review-blocking concern.

### `CH-3` Good hash keys

**L4**
- Immutable (or at least: the fields used by `hashCode` never change while the object is in a collection).
- Well-distributed `hashCode`, cheap to compute, `equals` cheap to compute.
- `String`, boxed primitives, enums, records over immutable components, and UUIDs are all good defaults.

**L5**
- `String` caches its hash (`hash` field, computed lazily), so repeated lookups are cheap — that's part of why string keys are fine in hot paths.
- Enums are the best key type available: `EnumMap` skips hashing entirely and indexes an array by `ordinal()`.
- Failure mode when the key is mutable: the entry stays in the old bucket, so `get` computes a new index, misses, and the entry becomes unreachable *but still retained* — a lookup failure and a memory leak at the same time.
- Watch mutable collections used as keys (`List`, `Set` hash over contents). Legal, but a landmine.

### `CH-4` Comparable vs Comparator, consistency with equals

**L4**
- `Comparable<T>.compareTo` = natural ordering, defined on the type itself. `Comparator<T>.compare` = external ordering, pluggable, and composable via `comparing(...).thenComparing(...).reversed()`.
- "Consistent with equals" means `a.compareTo(b) == 0` iff `a.equals(b)`.
- Sorted collections (`TreeMap`, `TreeSet`) use *comparison*, not `equals`. If they disagree, the set will treat comparison-equal but non-`equals` items as duplicates.

**L5**
- Concrete bite: `TreeSet<Person>` with a comparator on `lastName` only will silently drop every person after the first with a given surname. `contains` also uses comparison, so a hash-equal object may report absent.
- `BigDecimal` is the canonical example in the JDK: `new BigDecimal("1.0").equals(new BigDecimal("1.00"))` is false but `compareTo` is 0 — so `HashSet` and `TreeSet` disagree on the same data. In money-handling code this is a real defect class.
- Comparators must be *transitive and total*, or `Arrays.sort`'s TimSort will throw `IllegalArgumentException: Comparison method violates its general contract!` at some data-dependent size. Classic cause: subtracting ints (`a.id - b.id`) and overflowing. Use `Integer.compare`.

### `CH-5` Iterator semantics

**L4**
- **Fail-fast** — `ArrayList`, `HashMap`, `TreeMap`, `ArrayDeque`, `PriorityQueue`. Track `modCount`; structural modification during iteration throws `ConcurrentModificationException`.
- **Weakly consistent** — `ConcurrentHashMap`, `ConcurrentSkipListMap`, `ConcurrentLinkedQueue`, `LinkedBlockingQueue`. Never throw CME; reflect some state at or after construction; may or may not see concurrent updates.
- **Snapshot** — `CopyOnWriteArrayList`/`CopyOnWriteArraySet`. Iterate a frozen array; never see later writes; `iterator.remove()` throws `UnsupportedOperationException`.

**L5**
- CME is *best-effort* by contract — `modCount` is not volatile, so you cannot rely on it as a correctness mechanism across threads. It's a debugging aid, not a guard.
- Weakly consistent means you cannot compute a consistent aggregate by iterating a live CHM. If you need a point-in-time total, you need an external snapshot or an accumulator maintained under the same update path.
- This is the single most useful classification to have memorized — it answers "is this safe?" for almost every concurrent-collection question.

### `CH-6` Single-threaded CME

**L4**
- Cause: structurally modifying the collection (`add`/`remove`) through the collection reference while a for-each loop's iterator is live. The iterator's `expectedModCount` no longer matches `modCount`.
- Safe options: `Iterator.remove()`, `Collection.removeIf(pred)`, iterate a copy, or collect-then-remove.
- `set(i, v)` on a `List` is not a structural modification and is fine.

**L5**
- There's a notorious near-miss: removing the second-to-last element does *not* throw, because `hasNext()` is `cursor != size` and the size change makes it return false early. So the bug is data-dependent and escapes tests. This is why "it worked in dev" is not evidence.
- `removeIf` is not just cleaner — `ArrayList` overrides it to do a single bitset pass plus one compaction, so it's O(n) instead of O(n²) for repeated `remove(int)`.
- On a `Map`, remove via `map.entrySet().removeIf(...)` or `map.values().removeIf(...)` — the views are live, which is `CH-1` paying off.

### `CH-7` Null tolerance

**L4**

| Collection | null key | null value |
|---|---|---|
| `HashMap` / `LinkedHashMap` | one allowed (bucket 0) | allowed |
| `TreeMap` | no (NPE, unless comparator allows) | allowed |
| `Hashtable` | no | no |
| `ConcurrentHashMap` | no | no |
| `ArrayList` / `LinkedList` | — | allowed |
| `ArrayDeque` / `PriorityQueue` | — | **no** |
| `List.of` / `Map.of` / `Set.of` | no | no |

**L5**
- CHM rejects nulls because `get(k) == null` would be ambiguous between "absent" and "mapped to null", and in a concurrent map you can't disambiguate with a follow-up `containsKey` — the state may have changed between calls. Doug Lea's stated reasoning.
- `ArrayDeque`/`PriorityQueue` reject nulls because `null` is the sentinel for "empty" in `poll`/`peek`.
- `List.of(...)` is null-*hostile*, not merely null-rejecting: `List.of(1,2).contains(null)` throws NPE, which surprises code that migrated from `Arrays.asList`. That's a real migration hazard.
- Practical rule I use: don't put nulls in collections at all. Use `Optional` at the boundary or a sentinel; a null in a collection is almost always a design smell that shows up later as an NPE three layers away.

### `CH-8` Views vs copies

**L4**
- **Views** (live, write-through): `map.keySet()`, `map.values()`, `map.entrySet()`, `list.subList(a,b)`, `Arrays.asList(arr)`, `Collections.unmodifiableList(l)`, `Map.headMap/tailMap/subMap`.
- **Copies**: `new ArrayList<>(c)`, `List.copyOf(c)`, `stream().toList()`, `Collections.unmodifiableList(new ArrayList<>(l))`.
- Mutating a view mutates the backing structure; mutating the backing structure invalidates the view (or throws CME).

**L5**
- `Arrays.asList` is a two-way view over the array: `set()` writes through to the array, `add`/`remove` throw `UnsupportedOperationException`. If you then hand that list to a library that wants to sort in place, it works; if it wants to add, it blows up at runtime.
- `Collections.unmodifiableList(l)` is an unmodifiable *view*, not an immutable list — the caller can't mutate through it, but anyone holding `l` still can, and the "immutable" copy changes underneath. If you're returning it from an API, copy first.
- `subList` retains a reference to the whole backing array — a 10-element sublist of a million-element list keeps the million alive. Same shape as the old `String.substring` leak. Copy if the sublist outlives the parent.

### `CH-9` Unmodifiable vs immutable vs `List.of`

**L4**
- `Collections.unmodifiableX(c)` — view; blocks mutation *through this reference only*; backing collection can still change.
- `List.of` / `Set.of` / `Map.of` (Java 9) — genuinely immutable, null-hostile, no defensive-copy overhead, more compact representation for small sizes.
- `List.copyOf(c)` — immutable copy, and a no-op if `c` is already one of these immutable types.
- Elements are still mutable in all cases — these are shallow guarantees.

**L5**
- `Set.of`/`Map.of` iteration order is deliberately randomized per JVM run (a `SALT` computed at class init) to stop code from depending on unspecified order. That means a test that passes locally can fail in CI. Good design, occasionally infuriating.
- `Map.of` throws `IllegalArgumentException` on duplicate keys; `Map.ofEntries` is the >10-entry form.
- For API boundaries: return `List.copyOf(internal)` — immutable, and free when the input is already immutable. That's my default for getters returning collections.

### `CH-10` Empty collections over null

**L4**
- Returning `null` forces every caller to null-check; forgetting is an NPE at the call site, far from the cause.
- `Collections.emptyList()` / `List.of()` are singletons — zero allocation.
- For-each over an empty collection is a no-op, so callers just work.

**L5**
- `Optional<Collection>` is an anti-pattern — two ways to say "nothing." Return the empty collection.
- The exception: if "no data" and "empty result" are semantically different to the caller (e.g. cache miss vs cached empty result), you need a distinguishing type, not a null.

---

## System 2 — List

### `LI-1` ArrayList internals

**L4**
- Backed by `Object[] elementData` plus an `int size`.
- Default-constructed with a shared empty array; first `add` inflates to capacity 10.
- Growth: `newCapacity = oldCapacity + (oldCapacity >> 1)` — 1.5×. Then `Arrays.copyOf` (an intrinsified `System.arraycopy`).
- `get`/`set` O(1). `add` at end amortized O(1). `add`/`remove` at index i → O(n) shift.

**L5**
- Amortized O(1) hides a latency spike: a growth at 1M elements copies 1M references in one go. In a latency-sensitive path with a known bound, presize.
- 1.5× rather than 2× is a memory/copy tradeoff, and it has a nice property: the sum of freed blocks eventually exceeds the next request, so the allocator can reuse space. 2× never can.
- `remove` nulls the trailing slot to avoid a leak — but the *array itself* never shrinks. A list that peaked at 1M and now holds 10 still holds a 1M array. `trimToSize()` or reallocate.
- Max capacity is bounded near `Integer.MAX_VALUE - 8`; past that you need a different structure entirely.

### `LI-2` ArrayList vs LinkedList

**L4**
- `ArrayList`: contiguous array, O(1) index access, cache-friendly, ~4–8 bytes overhead per element (reference only).
- `LinkedList`: doubly-linked nodes, O(1) insert/remove *given a node reference*, O(n) to reach an index, ~40 bytes overhead per node.
- Default to `ArrayList`. Always.

**L5**
- The classic "LinkedList is better for inserts" claim is almost always wrong, because you must *traverse* to the insertion point — O(n) pointer chases with cache misses — and then the O(1) splice is free. `ArrayList`'s O(n) `arraycopy` is a single sequential memmove and typically wins even at n in the tens of thousands.
- The honest use case is `LinkedList` as a `Deque` — and `ArrayDeque` beats it there too.
- Where a linked structure genuinely wins: when you hold node references and splice repeatedly, which the JDK `LinkedList` API doesn't expose. So you'd write your own.
- Interview-safe answer: "I use `ArrayList` unless I have a measured reason not to; for queue/stack semantics I use `ArrayDeque`. I've never shipped a `LinkedList`."

### `LI-3` RandomAccess

**L4**
- Empty marker interface on `ArrayList`, `Vector`, `CopyOnWriteArrayList`, `Arrays.asList` results.
- Signals that index access is roughly constant-time.
- Algorithms branch on it: `Collections.binarySearch`, `shuffle`, `reverse` use an index loop for `RandomAccess` lists and an iterator/`ListIterator` loop otherwise.

**L5**
- The reason it exists is that the alternative — an index loop over a `LinkedList` — is O(n²). The marker lets generic algorithms avoid a pathological case without instanceof-checking concrete types.
- If you write a library method taking `List<T>`, mirror the JDK: `if (list instanceof RandomAccess) { index loop } else { iterator loop }`.

### `LI-4` remove(int) vs remove(Object)

**L4**
- `List<Integer> l = new ArrayList<>(List.of(10,20,30));`
- `l.remove(1)` → removes **index 1** (the value 20), because `remove(int)` is an exact match and no boxing is needed.
- `l.remove(Integer.valueOf(1))` → removes the *value* 1.
- Overload resolution prefers the primitive form; boxing is only considered in a later phase.

**L5**
- Same trap in `Collection.remove` on `Set<Integer>`? No — `Set` has no `remove(int)`, so it's unambiguous. The bug is `List`-specific.
- This is a genuine production bug generator when a `List<Integer>` holds IDs. Mitigation: don't use `List<Integer>` for IDs; wrap in a domain type, or use `removeIf(x -> x == id)`.

### `LI-5` Arrays.asList pitfalls

**L4**
1. Fixed size — `add`/`remove` throw `UnsupportedOperationException`; `set` works.
2. Write-through to the source array in both directions.
3. `Arrays.asList(intArray)` returns `List<int[]>` of size 1, not `List<Integer>` — varargs sees one object. Use `Arrays.stream(intArray).boxed().toList()`.
4. Allows nulls (unlike `List.of`).

**L5**
- `new ArrayList<>(Arrays.asList(...))` is the mutable-copy idiom; `List.of(...)` is the immutable one. Post-Java-9 there's no reason to use `Arrays.asList` unless you specifically want the array view or need nulls.
- The int[] trap survives because it compiles cleanly and fails at runtime with a confusing `ClassCastException` somewhere downstream — worth a static-analysis rule.

### `LI-6` subList

**L4**
- Returns a *view* over `[from, to)`. Mutations propagate both ways.
- Structurally modifying the *backing* list after taking the sublist makes the sublist throw CME on next use.
- `list.subList(a,b).clear()` is the idiomatic range-removal.

**L5**
- The retention issue from `CH-8`: the view holds the parent, so a small sublist pins a large array. `new ArrayList<>(list.subList(a,b))` if it escapes the local scope.
- The view's `modCount` check is against the parent, so the failure is non-local — the code that breaks is not the code that changed anything. Painful to debug.

### `LI-7` CopyOnWriteArrayList

**L4**
- Every mutation copies the entire backing array under a `ReentrantLock`; readers see a stable volatile array reference with no locking at all.
- Reads O(1) and contention-free. Writes O(n) *and* allocate O(n).
- Iterators are snapshots — no CME, but `iterator.remove()` throws.
- Fit: read-mostly, small, mutation-rare. Listener lists, config snapshots, feature-flag sets.

**L5**
- The cost model is the whole answer: n writes to an n-element list is O(n²) allocation. Put one on a hot write path and you'll see GC pressure before you see the bug.
- Real fit at JPMC-shaped systems: a set of registered event handlers or a cached permission ruleset refreshed every few minutes and read on every request. That's exactly its niche.
- Alternative for the same shape at larger sizes: hold an immutable `Map`/`List` in a `volatile` field and replace the whole reference on refresh. Same semantics, explicit, and you control the copy.

### `LI-8` Vector / Stack

**L4**
- `Vector` synchronizes every method — coarse-grained, and useless because compound operations still need external locking.
- `Stack extends Vector` and its iteration order is *bottom-to-top*, i.e. the opposite of pop order. Genuine bug source.
- Replacements: `ArrayList` (+ `Collections.synchronizedList` or a concurrent type if needed), `ArrayDeque` for stack semantics.

**L5**
- The deeper point: per-method synchronization is the wrong granularity for any real usage. `if (!v.contains(x)) v.add(x)` is still racy. Once you need external locking anyway, the internal locking is pure overhead.
- `ArrayDeque` as a stack is also faster — no synchronization, and `push`/`pop` at the head of a circular array.

### `LI-9` Safe removal while iterating
**L4** — `removeIf` (best), `Iterator.remove()`, iterate a copy, or use a concurrent collection. For maps: `entrySet().removeIf(...)`.
**L5** — `removeIf` is overridden in `ArrayList` for a single-pass bitset implementation → O(n) vs O(n²). Under concurrency, none of these are sufficient; you need CHM/COW or external locking. And note `Iterator.remove()` is optional in the contract — it throws on immutable and COW collections.

### `LI-10` Presizing and trimToSize

**L4**
- `new ArrayList<>(expectedSize)` avoids repeated grow-and-copy. Worth it when the size is known and large.
- `trimToSize()` shrinks capacity to size — for long-lived lists that peaked.

**L5**
- Presizing matters most where the allocation is in a loop: a per-request list sized 10 that grows to 500 does ~15 array copies per request. At 1000 rps that's measurable GC.
- Don't over-apply. For lists under ~100 elements the JIT and TLAB allocation make this noise. Measure before you clutter code with capacity hints.

---

## System 3 — Map

### `MP-1` HashMap.put end to end

**L4**
1. `hash = h ^ (h >>> 16)` where `h = key.hashCode()`.
2. `index = (n - 1) & hash`, n = table length (always a power of two).
3. Empty bin → place a new `Node`.
4. Occupied → compare `hash` first, then `==`, then `equals`. Match → replace value. No match → append to list, or insert into the red-black tree if already treeified.
5. If the bin list length reaches 8 → `treeifyBin` (which *resizes instead* if table length < 64).
6. `if (++size > threshold) resize()` where `threshold = capacity * loadFactor`.

**L5**
- The `hash == hash && (k == key || key.equals(k))` ordering is a deliberate cheap-check-first: int comparison, then reference identity, then the potentially expensive `equals`. Worth naming — it shows you've read the source.
- Insertion is *tail* insertion since Java 8 (head insertion in 7), which is what removed the resize cycle in `MP-7`.
- `putIfAbsent`, `merge`, `compute*` all go through the same `putVal`/`computeIfAbsent` machinery — they're not layered helpers, they're single-traversal operations. That's why `merge` beats `get`-then-`put`.

### `MP-2` Hash spreading and masking

**L4**
- `(n-1) & hash` only uses the low bits of the hash. With small tables, two keys differing only in high bits would collide.
- `h ^ (h >>> 16)` XORs the high 16 bits down into the low 16, so high-bit entropy participates in bucket selection.
- `&` instead of `%` because the table size is a power of two, making the mask exactly equivalent and far cheaper than division.

**L5**
- It's a deliberately *cheap* spread — one shift, one XOR — not a full avalanche. The JDK authors traded quality for speed because treeification now bounds the worst case anyway. Before Java 8, `HashMap` used four shifts and XORs.
- Power-of-two sizing also makes resize cheap: an element's new index is either `i` or `i + oldCap`, decided by one bit (`hash & oldCap`). That's the whole trick behind `MP-3`.
- If a user supplies a non-power-of-two initial capacity, `tableSizeFor` rounds up to the next power of two.

### `MP-3` Resize mechanics

**L4**
- Triggered when `size > capacity * loadFactor`. Capacity doubles.
- Java 8 split: for each bin, elements go to either the `lo` list (index `i`) or the `hi` list (index `i + oldCap`), decided by `(e.hash & oldCap) == 0`.
- No rehashing needed — the hash is stored in the node.
- Relative order within a bin is preserved.

**L5**
- Java 7 rehashed and *reversed* order via head insertion, which under concurrency could form a cycle in the linked list → 100% CPU in `get()`. Java 8's order-preserving split eliminated that specific failure.
- Resize is O(n) and single-threaded; a map that grows to millions pays repeated full rehashes. Presize (`MP-22`).
- Treeified bins are split too, and untreeify back to a list if the resulting half is ≤ `UNTREEIFY_THRESHOLD` (6).

### `MP-4` Treeification thresholds

**L4**
- `TREEIFY_THRESHOLD = 8` — bin converts list → red-black tree.
- `MIN_TREEIFY_CAPACITY = 64` — if the table is smaller, resize instead of treeifying (a short table is the more likely cause of long bins).
- `UNTREEIFY_THRESHOLD = 6` — during resize, a tree bin with ≤6 nodes reverts to a list.
- Effect: worst-case bin lookup goes from O(n) to O(log n).

**L5**
- 8 comes from a Poisson argument in the JDK source comments: with a good hash and load factor 0.75, the probability of a bin reaching 8 is roughly 1 in 10⁷. So treeification is effectively an adversarial/bad-hash safety net, not a normal-path optimization.
- The 8/6 gap is hysteresis — a single threshold would thrash convert/revert around the boundary.
- Tree bins require an ordering: they use hash, then `Comparable` if the key implements it, then a tie-break on identity hash. So treeified performance is better for `Comparable` keys.
- The real significance: this is the **hash-collision DoS mitigation** (`MP-20`).

### `MP-5` Load factor 0.75

**L4**
- Threshold = capacity × load factor. Lower → fewer collisions, more memory, more frequent resize. Higher → denser table, longer bins.
- 0.75 is the empirical balance point; the JDK docs state it offers a good tradeoff between time and space costs.

**L5**
- With load factor 0.75 and a good hash, bin occupancy follows a Poisson(0.5) distribution — most bins hold 0 or 1 entries. That's the number the treeify probability is computed from.
- Raising it to 1.0 to "save memory" is usually a false economy: you save one array of references but lengthen every lookup, and you've disabled the resize that would break up long bins.
- Almost never worth tuning. Presizing (`MP-22`) is the lever that actually matters.

### `MP-6` Mutated key hashCode

**L4**
- The entry stays physically in its original bucket.
- A subsequent `get(key)` computes the new hash → wrong bucket → miss.
- The entry is unreachable via `get`/`remove`/`containsKey` but still occupies memory and still appears during iteration.

**L5**
- It's a leak *and* a correctness bug simultaneously, and it's invisible in tests unless you mutate between put and get.
- Presents in production as "the cache entry exists in the heap dump but the service says cache miss" — an incident I'd expect to take hours to diagnose without knowing this mechanism.
- Prevention: immutable key types, records, or defensive copy on insert. Static analysis can flag non-final fields in classes used as map keys.

### `MP-7` HashMap under concurrent writes

**L4**
- Not thread-safe. Lost updates, corrupted size, and CME during iteration.
- **Java 7**: concurrent `resize` with head-insertion could produce a circular linked list → `get()` spins forever, pinning a CPU core at 100%.
- **Java 8**: the lo/hi split preserves order and doesn't create cycles, so the infinite loop is gone — but you still get lost entries, wrong `size`, and possible lost nodes.
- Fix: `ConcurrentHashMap`.

**L5**
- The Java 7 infinite loop was one of the most-reported production incidents in the Java world — worth naming explicitly because it's a favorite interview follow-up and a good "I know why this changed" signal.
- Java 8 not throwing is arguably worse operationally: silent data loss instead of an obvious pegged CPU. Absence of a symptom isn't safety.
- The correct posture: a `HashMap` reachable from more than one thread is a review-blocking defect, full stop. Not "probably fine because it's read-mostly" — unsafe publication means readers can see a partially constructed table.

### `MP-8` LinkedHashMap and LRU

**L4**
- `LinkedHashMap extends HashMap` and adds a doubly-linked list across all entries → predictable iteration order.
- Two modes: insertion-order (default) and **access-order** (`new LinkedHashMap<>(cap, 0.75f, true)`), where `get` moves the entry to the tail.
- Override `removeEldestEntry(eldest)` to return `true` past a size cap → LRU eviction, in ~10 lines.

**L5**
- Cost: two extra references per entry vs `HashMap`. Iteration is O(size) rather than O(capacity), so it's actually *faster* to iterate a sparse map.
- In access-order mode `get()` is a structural modification — so a "read-only" thread mutates the list and CME becomes possible from a getter. Surprising and a real bug source.
- Not thread-safe; wrapping in `synchronizedMap` gives you a global lock on every read. For a real cache use **Caffeine** — W-TinyLFU admission, per-entry TTL/TTI, async loading, and eviction stats. `LinkedHashMap` LRU is the right answer for "implement it on a whiteboard," not for "what would you ship."

### `MP-9` TreeMap / NavigableMap

**L4**
- Red-black tree (self-balancing BST). `get`/`put`/`remove` O(log n). Sorted iteration for free.
- `NavigableMap` API is the reason to use it: `floorKey`, `ceilingKey`, `higherKey`, `lowerKey`, `firstEntry`, `lastEntry`, `headMap`, `tailMap`, `subMap`, `descendingMap`.
- Uses `compareTo`/`Comparator`, never `equals` — see `CH-4`.

**L5**
- The real-world justification is *range and nearest-key queries*, not sorted iteration. Examples: time-bucketed metrics lookup ("value at or before timestamp t"), tiered pricing/fee schedules ("rate for the bracket containing this amount"), IP-range or version-range lookup. Those are one `floorEntry` call and O(n) with a `HashMap`.
- The pricing-bracket example lands well in a fintech interview and maps to instrument/tier logic.
- Cost vs `HashMap`: ~2–5× slower point lookups and more per-node memory. Only pay for it if you use the ordering.

### `MP-10` ConcurrentHashMap (Java 8) design

**L4**
- Java 7: 16 (default) independent `Segment`s, each a `ReentrantLock`-guarded mini-map → concurrency capped at the segment count.
- Java 8: segments gone. Same table as `HashMap`, plus:
  - **Empty bin** → `casTabAt` to install the first node — lock-free.
  - **Non-empty bin** → `synchronized` on the bin's head node. Lock granularity = one bucket.
  - **Reads** → fully lock-free; `Node.val` and `Node.next` are `volatile`.
- Bins treeify at 8 just like `HashMap`. No null keys or values.

**L5**
- Effective concurrency scales with table size rather than a fixed segment count, so a large CHM has thousands of independent locks. That's the whole point of the rewrite.
- Using the bin head as the monitor is elegant — the lock object is exactly the data it guards, no extra allocation.
- Biased/thin locking means the uncontended `synchronized` path is nearly free, which is why they chose it over `ReentrantLock`.
- Reads being lock-free is what makes CHM the right default even for read-heavy workloads — you don't need `COW` semantics to get contention-free reads.

### `MP-11` size() vs mappingCount()

**L4**
- CHM doesn't maintain a single counter — that would be a global contention point defeating the per-bin locking.
- It uses a striped counter: a `baseCount` plus a `CounterCell[]` array (same idea as `LongAdder`). `size()` sums them.
- The sum is therefore a snapshot that may be stale the moment it returns.
- `mappingCount()` returns `long` — use it, since a CHM can exceed `Integer.MAX_VALUE` entries.

**L5**
- Consequence for design: never write `if (map.size() < limit) map.put(...)` and expect a hard cap. That's a check-then-act race. If you need a bounded map you need an explicit semaphore or an atomic counter with CAS on the limit.
- Same reasoning applies to `isEmpty()`.
- The `LongAdder` pattern generalizes: any hot counter under contention should be a `LongAdder`, not an `AtomicLong`. Good thing to volunteer.

### `MP-12` Concurrent resize

**L4**
- Resize is *cooperative*. A thread that triggers it claims a range of bins to transfer.
- Transferred bins are replaced with a `ForwardingNode` pointing at the new table.
- A thread that encounters a `ForwardingNode` during `put` calls `helpTransfer` and joins the resize instead of blocking.
- Readers hitting a `ForwardingNode` are redirected to the new table.

**L5**
- This is why CHM doesn't have a stop-the-world resize pause the way `HashMap` does — the cost is spread across the threads causing it, which is nicely self-regulating under load.
- It's also why `size()` can't be exact mid-resize.
- Detail worth knowing: `sizeCtl` is the coordination field — negative means resizing, and its low bits encode the number of helping threads.

### `MP-13` computeIfAbsent atomicity and traps

**L4**
- On CHM, `computeIfAbsent` is atomic: the check and the insert happen under the bin lock, so the mapping function runs at most once per absent key.
- That makes it the correct idiom for lazy initialization — `get`-then-`putIfAbsent` may construct the value more than once.
- Trap: the mapping function must be short and must not modify the same map. Recursive update throws `IllegalStateException` on CHM, and CME on `HashMap` (Java 9+).

**L5**
- The function runs while **holding the bin lock**. A slow function (I/O, a remote call, a DB fetch) blocks every other thread hashing to that bin. I've seen this exact pattern used as a "cache loader" and become a throughput cliff. If loading is expensive, store a `CompletableFuture` or a memoizing supplier as the value and complete it outside the lock.
- On plain `HashMap` before Java 9, recursive `computeIfAbsent` could silently corrupt the table rather than throw — one of those "upgrade fixed a bug we didn't know we had" cases.
- `merge` is the better idiom for counters: `map.merge(k, 1L, Long::sum)` — one traversal, atomic on CHM, and no boxing dance.

### `MP-14` synchronizedMap vs ConcurrentHashMap

**L4**

| | `Collections.synchronizedMap` | `ConcurrentHashMap` |
|---|---|---|
| Locking | one global mutex | per-bin, reads lock-free |
| Reads | blocked by writes | never blocked |
| Iteration | must be manually synchronized by the caller, or CME | weakly consistent, no CME |
| Nulls | allowed (delegates to `HashMap`) | rejected |
| Atomic compounds | none | `putIfAbsent`, `compute*`, `merge` |

**L5**
- The killer detail on `synchronizedMap` is that iteration is **not** covered by the wrapper — you must `synchronized (map) { for (...) }` yourself, which the Javadoc says and everyone ignores. That's a latent CME.
- `synchronizedMap` still has one use: when you need null keys/values *and* thread safety. Rare, and usually a sign the model is wrong.
- Ownership: I'd treat any `synchronizedMap` in new code as a review comment with "why not CHM?"

### `MP-15` ConcurrentSkipListMap

**L4**
- Lock-free (CAS-based) concurrent skip list. Implements `ConcurrentNavigableMap` — sorted, with the full navigable API.
- O(log n) for get/put/remove, weakly consistent iterators.
- Use it when you need **both** concurrency **and** ordering/range queries. CHM has no ordering; `TreeMap` has no concurrency.
- `size()` is **O(n)** — it traverses. Don't call it in a loop.

**L5**
- The lock-free property means no thread can block another, which matters for latency tails more than throughput. Under low contention CHM is faster; skip list wins on predictability plus ordering.
- Skip lists are chosen over concurrent balanced trees because rebalancing is hard to do lock-free — probabilistic balancing is CAS-friendly. Good "why this data structure" answer.
- Realistic use: an in-memory time-ordered index (event timestamps → payload) that's written by ingestion threads and range-queried by readers. Maps directly onto a pipeline story.

### `MP-16` EnumMap / EnumSet

**L4**
- `EnumMap` is backed by a plain `Object[]` indexed by `ordinal()`. No hashing, no collisions, natural (declaration) ordering, extremely compact.
- `EnumSet` is a **bit vector**: `RegularEnumSet` uses a single `long` for ≤64 constants; `JumboEnumSet` uses a `long[]`.
- Both are dramatically faster and smaller than `HashMap`/`HashSet` with enum keys. Neither is thread-safe.

**L5**
- `EnumSet` set operations (union, intersection, complement) are single bitwise instructions. `EnumSet.complementOf`, `range`, `noneOf` are the idioms.
- This is my go-to for permission/flag sets and state-machine transition tables — small, fast, self-documenting, and it makes illegal states unrepresentable compared to a `Set<String>`.
- Concrete framing for the RBAC work: a `Map<DocumentType, EnumSet<Permission>>` is both faster and clearer than nested string maps.

### `MP-17` WeakHashMap

**L4**
- Keys are held by `WeakReference`. When a key has no strong reference elsewhere, GC can reclaim it and the entry is eventually removed.
- Cleanup is lazy — stale entries are expunged during subsequent `get`/`put`/`size`, drained from a `ReferenceQueue`.
- Uses `equals`, not identity, unless you also want `IdentityHashMap` semantics.

**L5**
- The trap: **values** are strongly referenced. If a value references its own key (directly or transitively), the key is never weakly reachable and nothing is ever collected. This is why `WeakHashMap` doesn't fix the classic cases people reach for it for.
- It's also not a cache — you have no control over *when* entries vanish, so hit rate is at the GC's mercy. Use a real cache with a size bound.
- Legitimate use: metadata keyed by an object you don't own the lifecycle of, e.g. per-`Class` or per-`ClassLoader` state. That's what the JDK uses it for internally.

### `MP-18` IdentityHashMap

**L4**
- Compares keys with `==` and uses `System.identityHashCode`, ignoring overridden `equals`/`hashCode`.
- Linear-probing open-addressed table, not chaining.
- Deliberately violates the general `Map` contract — the Javadoc says so.

**L5**
- Correct uses: object-graph traversal (serializers, deep-copy, cycle detection), where two `equals` objects are genuinely distinct nodes. Jackson and JAXB both use this internally.
- Using it as a general-purpose "fast map" is a bug factory — `map.get(new String("a"))` misses.
- Good signal question: it shows whether the candidate understands that `equals` semantics are a *choice*, not a law.

### `MP-19` Hashtable vs HashMap

**L4**
- `Hashtable` is a legacy synchronized-on-every-method class; `HashMap` is unsynchronized.
- `Hashtable` rejects nulls; `HashMap` allows one null key and null values.
- `Hashtable` uses `%` on a non-power-of-two capacity, grows `2n+1`; `HashMap` masks a power of two.
- `Hashtable` iteration uses the legacy `Enumeration` (not fail-fast) as well as an iterator.

**L5**
- The real answer to "which do I use" is neither — `HashMap` or `ConcurrentHashMap`. `Hashtable` has the worst of both: global locking *and* no atomic compound operations.
- Still relevant because `Properties extends Hashtable`, so it shows up in legacy config code.

### `MP-20` Hash-collision DoS

**L4**
- Attack: an attacker sends JSON/form data with thousands of keys engineered to collide in the same `HashMap` bucket. Every insert becomes an O(n) list scan → O(n²) total → CPU exhaustion from a single small request.
- Practical because `String.hashCode` is a published, trivially invertible function.
- Mitigation in Java 8+: treeification bounds a degenerate bin to O(log n).

**L5**
- Treeification is a *mitigation*, not a fix — O(n log n) is still an amplification, just a survivable one. Real defenses are upstream: cap request body size, cap parameter count (Tomcat's `maxParameterCount`, Spring's multipart limits), and never build an unbounded map from untrusted input.
- Java 7 shipped a randomized `altHashing` for String keys as an emergency mitigation (`jdk.map.althashing.threshold`); it was removed in 8 once treeify landed.
- This is a good answer to volunteer in a security-flavored round — it connects data structures to an actual CVE class (CVE-2012-2739 and relatives).

### `MP-21` LRU cache — whiteboard vs production

**L4**
- Whiteboard: `LinkedHashMap` in access-order mode with `removeEldestEntry`, or a `HashMap<K, Node>` + manual doubly-linked list (that's LeetCode 146 — O(1) get and put).
- Production: **Caffeine**. Size/weight bounds, TTL and TTI, refresh-after-write, async loading, stats, and W-TinyLFU which beats plain LRU on hit rate for skewed workloads.
- Distributed: Redis/ElastiCache with `maxmemory-policy allkeys-lru`.

**L5**
- Name the failure modes you'd guard: unbounded growth (always set a bound), stampede on a cold key (use `AsyncLoadingCache` or a per-key lock so one loader wins), and stale-data blast radius (TTL sized against the downstream's change rate).
- Local vs distributed is the real tradeoff question: local is faster and has no network failure mode, but each instance has an independent view — unacceptable if the cached data drives authorization decisions. That's the version of this question a bank asks.
- LRU vs LFU vs W-TinyLFU: LRU is vulnerable to a scan wiping the working set; TinyLFU adds a frequency sketch as an admission filter to prevent exactly that.

### `MP-22` Presizing a HashMap

**L4**
- `new HashMap<>(n)` sets *capacity*, not expected entry count. With load factor 0.75, a map created with capacity `n` resizes after `0.75n` entries.
- To hold `n` entries without a resize: `new HashMap<>((int) Math.ceil(n / 0.75))`.
- Java 19+: `HashMap.newHashMap(n)` does this for you. Guava has `Maps.newHashMapWithExpectedSize(n)`.

**L5**
- `new HashMap<>(expectedSize)` — passing the raw count — is one of the most common "optimization" bugs in Java code. It guarantees exactly one resize, which is the thing you were trying to avoid.
- Note the constructor rounds up to a power of two, so the effective threshold is often higher than the naive calculation suggests — the correction still matters at the boundary.
- Worth doing when building a map from a known-size collection in a hot path (e.g. converting a 30k-record batch), noise otherwise.

---

## System 4 — Set

### `ST-1` Set implementations

**L4**
- `HashSet` → `HashMap` internally. O(1) average, no order.
- `LinkedHashSet` → `LinkedHashMap`. Insertion order, slight memory cost.
- `TreeSet` → `TreeMap`. Sorted, O(log n), `NavigableSet` API.
- Everything about `HashMap` tuning applies directly.

**L5**
- `LinkedHashSet` is underused: it gives deterministic iteration for free, which makes tests reproducible and log output stable. I default to it wherever a set is iterated and the output is observed.
- `HashSet` iteration order is *unspecified*, not random — it's stable for the same insertion sequence on the same JVM, which is exactly enough to lull you into depending on it before it changes on upgrade.

### `ST-2` The PRESENT dummy

**L4**
- `HashSet` stores each element as a `HashMap` key with a shared static `Object PRESENT` as the value.
- One shared singleton, so the cost is one reference per entry, not one object.
- `add` returns `map.put(e, PRESENT) == null`.

**L5**
- The cost of the reuse is a full `HashMap.Node` per element (hash, key, value, next) where a dedicated set would need three fields. Roughly 32 bytes/element vs the ~16 a specialized implementation would use.
- For large primitive sets, that's a real argument for Eclipse Collections/fastutil (`IntOpenHashSet`) — order-of-magnitude memory difference.

### `ST-3` TreeSet ordering vs equals

**L4**
- `TreeSet` decides membership by `compareTo`/`compare` returning 0 — `equals` is never consulted.
- A comparator over a partial key silently drops elements that are distinct by `equals`.
- `contains`/`remove` also use comparison, so lookups can miss objects that are in the set by `equals`.

**L5**
- Fix: make the comparator total by chaining a tie-break to a unique field — `comparing(Person::lastName).thenComparing(Person::id)`.
- The `BigDecimal` case from `CH-4`: `HashSet` keeps `1.0` and `1.00` as two elements, `TreeSet` keeps one. Same data, two answers, in monetary code.
- Interview framing: "sorted collections use a different equality relation than hashed collections; if they disagree the same data has two different set semantics."

### `ST-4` Concurrent sets

**L4**
- `ConcurrentHashMap.newKeySet()` — the standard concurrent hash set. Backed by CHM, all its properties.
- `Collections.newSetFromMap(anyMap)` — makes a set from any map implementation.
- `CopyOnWriteArraySet` — snapshot semantics, `contains` is O(n). Small read-mostly sets only.
- `ConcurrentSkipListSet` — sorted concurrent set.

**L5**
- `CopyOnWriteArraySet` is backed by `CopyOnWriteArrayList`, so `contains` is a linear scan *and* every add scans for duplicates → O(n) per add, O(n²) to build. Fine at 10 elements, terrible at 10,000.
- `newSetFromMap` is the trick for getting a weak set (`newSetFromMap(new WeakHashMap<>())`) or an identity set — no dedicated JDK class exists for either.

### `ST-5` Set.of

**L4**
- Duplicate elements throw `IllegalArgumentException` at construction (unlike `new HashSet<>(List.of(...))`, which silently dedupes).
- Null-hostile: `contains(null)` throws NPE.
- Iteration order is randomized per JVM run.

**L5**
- The randomization is intentional (`ImmutableCollections.SALT`, seeded from `System.nanoTime` at class init) to break code that depends on unspecified order. It will surface as a flaky test in CI, which is the point.
- The duplicate-rejection difference bites during refactors from `Arrays.asList` → `List.of` when the source data legitimately contains duplicates.

---

## System 5 — Queue & Deque

### `QD-1` Queue vs Deque vs Stack

**L4**
- `Queue` — FIFO, `offer`/`poll`/`peek`.
- `Deque` — both ends: `addFirst/addLast`, `pollFirst/pollLast`, plus `push`/`pop` for stack semantics.
- `java.util.Stack` is legacy (synchronized, and iterates bottom-to-top). Replace with `ArrayDeque` used as a stack.
- `PriorityQueue` implements `Queue` but is ordered by priority, not FIFO.

**L5**
- `Deque` subsumes both, which is why `ArrayDeque` is the single default for both stack and queue in single-threaded code.
- The `Stack` iteration-order bug is worth naming — `for (x : stack)` gives you the reverse of pop order, and it's silently wrong rather than an exception.

### `QD-2` ArrayDeque internals

**L4**
- Circular array with `head` and `tail` indices; capacity is always a power of two so wraparound is `(i + 1) & (n - 1)`.
- Doubles when full. Amortized O(1) at both ends.
- No nulls (null is the empty sentinel). Not thread-safe.
- Faster than `LinkedList` for both stack and queue: contiguous memory, no per-node allocation.

**L5**
- Per-element cost is one reference vs `LinkedList`'s ~40-byte node — plus sequential access patterns the prefetcher likes. The JDK Javadoc explicitly says it's faster than `Stack` as a stack and `LinkedList` as a queue.
- No capacity bound and no blocking, so it's not a backpressure mechanism. For producer/consumer across threads you want a `BlockingQueue` (`QD-5`).
- `removeFirstOccurrence` / `remove(Object)` are O(n) — fine, but don't build an algorithm on it.

### `QD-3` PriorityQueue internals

**L4**
- Binary min-heap in an array. `offer`/`poll` O(log n), `peek` O(1), `remove(Object)`/`contains` **O(n)**.
- Ordered by natural ordering or a supplied `Comparator`.
- **Iteration order is not sorted** — `toString`, `forEach`, and streams give heap-array order. Only repeated `poll()` gives sorted output.
- Unbounded, grows automatically. Not thread-safe (use `PriorityBlockingQueue`).

**L5**
- The iteration-order surprise is a common production bug — someone logs the queue or streams it into a list and gets near-sorted-looking output that's wrong in the middle. Only the head is guaranteed.
- No stability guarantee for equal priorities. If FIFO-within-priority matters (a job scheduler), add a monotonically increasing sequence number as the comparator tie-break. This is a good detail to volunteer in a design round.
- Heapify from an existing collection (`new PriorityQueue<>(collection)`) is O(n), not O(n log n) — worth knowing when building from a batch.

### `QD-4` Top-K with a heap

**L4**
- Top-K **largest** → maintain a **min**-heap of size K. Push each element; if size > K, `poll()` (removes the smallest). What survives is the K largest.
- Top-K smallest → max-heap of size K, i.e. `Comparator.reverseOrder()`.
- Complexity O(n log K), memory O(K) — the point is that it works when n doesn't fit in memory.
- Alternative: quickselect O(n) average, but destroys input and has O(n²) worst case.

**L5**
- The direction confuses people because it's counterintuitive; the anchor is "the heap's root is the element you're willing to evict."
- At scale (streaming, distributed), you'd do a per-partition top-K and merge — that's the map-reduce shape and it's what an interviewer wants after the single-machine version.
- For approximate top-K over a high-cardinality stream, Count-Min Sketch + a small heap is the standard answer. Worth naming if the question drifts toward "trending items."

### `QD-5` BlockingQueue family

**L4**

| Queue | Bounded | Notes |
|---|---|---|
| `ArrayBlockingQueue` | yes, fixed at construction | single lock, optional fairness |
| `LinkedBlockingQueue` | optional (default `Integer.MAX_VALUE`) | two locks (put/take) → higher throughput |
| `SynchronousQueue` | capacity 0 | direct handoff, every put waits for a take |
| `PriorityBlockingQueue` | unbounded | priority-ordered, no blocking put |
| `DelayQueue` | unbounded | elements only available after their delay expires |
| `LinkedTransferQueue` | unbounded | `transfer()` waits for a consumer |

- Four method families: throws (`add`/`remove`), returns special value (`offer`/`poll`), blocks (`put`/`take`), times out (`offer(t,u)`/`poll(t,u)`).

**L5**
- Selection rule: **bounded by default**. The bound *is* the backpressure mechanism — an unbounded queue converts a downstream slowdown into an OOM (`QD-9`).
- `SynchronousQueue` + `newCachedThreadPool` means "never queue, always spawn" — unbounded thread growth under load. Fine for short-lived I/O tasks, dangerous for anything else.
- `LinkedTransferQueue` is the best general-purpose unbounded choice performance-wise, but I'd still reach for a bounded queue in a service.
- This maps directly onto the SQS visibility-timeout/DLQ story — same backpressure reasoning, different layer.

### `QD-6` ArrayBlockingQueue vs LinkedBlockingQueue

**L4**
- `ABQ`: one `ReentrantLock` guarding both ends, two `Condition`s (`notEmpty`, `notFull`). Producers and consumers contend on the same lock. Pre-allocated array, no per-element allocation.
- `LBQ`: separate `putLock` and `takeLock`, so a producer and a consumer can proceed simultaneously. Allocates a node per element, and an `AtomicInteger` count shared across both locks.
- `LBQ` generally higher throughput under contention; `ABQ` lower and more predictable memory, optional fairness.

**L5**
- `ABQ` supports a fair mode (FIFO among waiting threads) at a throughput cost; `LBQ` doesn't. Fairness matters if starvation is a real risk, which it usually isn't.
- `ABQ`'s pre-allocated array is the better fit for latency-sensitive work — no allocation, no GC contribution per element.
- Default recommendation: `LinkedBlockingQueue` **with an explicit capacity**. You get the two-lock throughput and the bound.

### `QD-7` SynchronousQueue and cached pools

**L4**
- Capacity zero — it's a handoff point, not storage. `put` blocks until a `take` arrives and vice versa.
- `Executors.newCachedThreadPool()` uses it: if no idle thread takes the task immediately, the pool creates a new thread. Max pool size is `Integer.MAX_VALUE`.
- Fair mode uses a FIFO queue of waiting threads; unfair (default) uses a stack, which has better throughput but can starve.

**L5**
- The consequence of `newCachedThreadPool` is unbounded thread creation → `OutOfMemoryError: unable to create new native thread` under a traffic spike. It's one of the two "never use the `Executors` factory methods" cases (the other is `QD-9`).
- Correct posture: always construct `ThreadPoolExecutor` directly with an explicit core/max/queue/rejection policy. Same argument as the `Executors` caveat in Effective Java.
- Legitimate use of `SynchronousQueue`: when you genuinely want zero buffering because the producer must feel the consumer's latency immediately.

### `QD-8` DelayQueue

**L4**
- Unbounded queue of `Delayed` elements; `take()` returns an element only once its `getDelay()` ≤ 0.
- Internally a `PriorityQueue` ordered by expiry plus a leader-follower waiting scheme to avoid a thundering herd.
- Use: scheduled retries, TTL expiry, delayed task execution.

**L5**
- `ScheduledThreadPoolExecutor` uses the same idea internally (`DelayedWorkQueue`) and is usually the better API — you rarely want to manage the polling loop yourself.
- The real-system caveat: in-memory delayed work is lost on restart and doesn't coordinate across instances. For a distributed retry, the answer is SQS delay seconds / message timers, or a persisted schedule table with a claim-based poller — which is exactly the pattern I'd argue for in a service.

### `QD-9` Unbounded queue + fixed pool = OOM

**L4**
- `Executors.newFixedThreadPool(n)` uses a `LinkedBlockingQueue` with `Integer.MAX_VALUE` capacity.
- If arrival rate exceeds service rate, the queue grows without bound. Heap fills, GC thrashes, then OOM.
- The pool never grows past `n` — `maximumPoolSize` is only consulted when the queue is *full*, and an unbounded queue is never full.
- Fix: construct `ThreadPoolExecutor` with a bounded queue and an explicit `RejectedExecutionHandler`.

**L5**
- The second-order effect is worse than the OOM: latency grows unboundedly *before* the crash, so every queued request is already timed out by the time it's serviced. You're burning CPU on work nobody is waiting for. A bounded queue plus fast rejection is strictly better — fail fast, shed load, keep the successful requests fast.
- Rejection policy choice is the design decision: `AbortPolicy` (throw — usually right for a service, surfaces as a 503), `CallerRunsPolicy` (natural backpressure onto the caller thread — good for a batch pipeline, bad for a request thread since it blocks your HTTP worker), `DiscardOldestPolicy` (only if data is genuinely droppable).
- Direct parallel to the queue-depth alarms on the SQS side — same failure shape, and the same answer: bound it and alarm on depth *and* age.

### `QD-10` ConcurrentLinkedQueue vs LinkedBlockingQueue

**L4**
- `CLQ`: unbounded, non-blocking, lock-free (Michael–Scott algorithm, CAS-based). `poll()` returns `null` when empty — the consumer must spin or back off.
- `LBQ`: optionally bounded, blocking `put`/`take`, lock-based.
- `CLQ.size()` is **O(n)** and not atomic — never use it in a condition.

**L5**
- Use `CLQ` only when the consumer already has its own event loop and you never want to block. Use `LBQ` when you want a consumer thread to park while idle and you want backpressure.
- In practice, blocking is a feature — a parked thread costs nothing, and spinning burns CPU. `LBQ` with a bound is the default.
- `CLQ`'s lock-free property means it makes progress even if a producer thread is descheduled mid-operation, which matters in a real-time-ish context and almost never in a web service.

### `QD-11` The three method families

**L4**

| Operation | Throws | Returns special | Blocks | Times out |
|---|---|---|---|---|
| Insert | `add` | `offer` | `put` | `offer(e,t,u)` |
| Remove | `remove` | `poll` | `take` | `poll(t,u)` |
| Examine | `element` | `peek` | — | — |

- `add` throws `IllegalStateException` on a full bounded queue; `offer` returns `false`.
- `remove`/`element` throw `NoSuchElementException` on empty; `poll`/`peek` return `null`.

**L5**
- Almost always use `offer`/`poll` and check the result, or `put`/`take` when you want blocking. Using `add` on a bounded queue is how you get an unhandled `IllegalStateException` on a traffic spike.
- Ignoring `offer`'s return value is a silent-data-loss bug — worth a lint rule.

---

## System 6 — Concurrency & memory model

### `CC-1` Safe publication

**L4**
- Building a `HashMap` in one thread and reading it in another without synchronization is unsafe even if nobody writes afterward — the reader may see a partially constructed table.
- Safe publication mechanisms: initialize in a static initializer, store into a `final` field, store into a `volatile` field, publish via a concurrent collection, or guard with a lock.
- `final` fields get freeze semantics at the end of the constructor, so a fully-populated immutable map in a `final` field is safe.

**L5**
- This is the part people miss when they argue "it's read-only after startup so it's fine." Without a happens-before edge, there's no guarantee the reader sees the writes at all.
- Practical idiom for a refreshed lookup table: build a new immutable `Map`, assign it to a `volatile` field, and let readers read the field. Copy-on-write at the reference level — no locking, no CHM, trivially correct.
- `List.of`/`Map.of` results are safe to publish through a data race because their fields are final. Not something to rely on casually, but it's the underlying reason immutability buys thread safety.

### `CC-2` Unsafe compounds on CHM

**L4**
- Individual operations are atomic; sequences are not.
- Unsafe: `if (!map.containsKey(k)) map.put(k, v)`, `map.put(k, map.get(k) + 1)`, `if (map.size() < N) map.put(...)`.
- Safe replacements: `putIfAbsent`, `merge`, `compute`, `computeIfAbsent`, `replace(k, old, new)`.
- Bulk operations (`forEach`, `search`, `reduce`) are not atomic snapshots.

**L5**
- Counters: `map.merge(k, 1L, Long::sum)` is atomic and single-traversal. Better still for hot counters: `map.computeIfAbsent(k, x -> new LongAdder()).increment()` — the map operation happens once per key, then increments are uncontended.
- There's no atomic way to enforce a size bound on a CHM (`MP-11`) — if you need one, use a `Semaphore` alongside, or Caffeine, which handles it.
- The general principle to state: "concurrent collections give you atomic *operations*, not atomic *transactions*. If the invariant spans two operations, you need external coordination."

### `CC-3` Iterator guarantees table

**L4**

| Collection | Iterator | `iterator.remove()` |
|---|---|---|
| `ArrayList`, `HashMap`, `TreeMap`, `ArrayDeque` | fail-fast (CME) | supported |
| `ConcurrentHashMap`, `ConcurrentSkipListMap`, `ConcurrentLinkedQueue`, `LinkedBlockingQueue` | weakly consistent | supported |
| `CopyOnWriteArrayList/Set` | snapshot | throws `UnsupportedOperationException` |
| `List.of`, `Map.of`, `Collections.unmodifiable*` | — | throws `UnsupportedOperationException` |

**L5**
- Weakly consistent means: no CME, each element traversed at most once, and updates *may* be visible. You cannot derive a consistent aggregate.
- If you need a consistent snapshot of a CHM, you need to either serialize writes behind a lock during the read, or maintain an immutable snapshot reference you swap atomically (`CC-1`).

### `CC-4` Defensive copies

**L4**
- Copy on the way in (constructor/setter) so the caller can't mutate your internal state afterwards.
- Copy or wrap on the way out (getter) so the caller can't mutate your internals.
- `List.copyOf(x)` on both sides is the modern one-liner; it's free when the input is already immutable.

**L5**
- Cost matters: copying a 100k-element list on every getter call is a real regression. For large internal state, prefer an immutable type internally so the getter is a free reference return.
- Copying is shallow — copying a `List<MutableThing>` protects the list structure, not the elements. Say this explicitly; it's the follow-up.
- My default at a service boundary: internal state is an immutable collection of immutable records, so getters copy nothing and there's no aliasing question at all.

### `CC-5` Immutability and thread safety

**L4**
- No mutation → no data races on the object's own state.
- Needs: all fields final, no leaked references to mutable internals, safe construction (no `this` escaping the constructor).
- Records give you most of this, but a record holding a `List` field must still copy the list in a compact constructor.

**L5**
- Final-field freeze semantics mean a properly constructed immutable object is safe to publish even via a data race. That's the JMM guarantee that makes immutability *actually* free rather than "safe if you also synchronize."
- The engineering tradeoff is allocation: immutable updates copy. That's why persistent data structures (structural sharing, e.g. Vavr, or Clojure's) exist. Rarely worth introducing to a Java service.

---

## System 7 — Streams & bulk operations

### `SB-1` Collectors.toMap traps

**L4**
- Duplicate key → `IllegalStateException: Duplicate key`. Supply a merge function: `toMap(k, v, (a, b) -> b)`.
- A **null value** → `NullPointerException`, because `toMap` uses `map.merge` internally, which is null-hostile. Even the 3-arg form.
- Fourth arg is a map supplier: `toMap(k, v, merge, TreeMap::new)` or `LinkedHashMap::new` for ordered output.

**L5**
- The null-value NPE is nastier than it looks: the exception says nothing about which key, and it only fires when your data happens to contain a null. Workaround is `Collectors.toMap` with a wrapper, or a plain `forEach` loop with `put`.
- The duplicate-key exception is arguably a feature — it surfaces a data assumption you didn't know you were making. When I hit it I check whether the key is genuinely unique before reaching for a merge function.
- `groupingBy` has neither problem, which is why it's the safer default when uniqueness isn't guaranteed.

### `SB-2` groupingBy / toMap / partitioningBy

**L4**
- `toMap` → key must be unique, value is the mapped element.
- `groupingBy(classifier)` → `Map<K, List<T>>`; default `HashMap` + `toList()` downstream.
- `partitioningBy(predicate)` → `Map<Boolean, List<T>>`, always both keys present.
- Downstream collectors compose: `groupingBy(X::type, counting())`, `groupingBy(X::type, mapping(X::id, toSet()))`, `groupingBy(X::type, TreeMap::new, summingLong(X::amount))`.

**L5**
- `partitioningBy` is faster than `groupingBy` on a boolean because it uses a fixed two-slot map — trivial, but it also documents intent better.
- `groupingBy` returns mutable `HashMap`/`ArrayList` by default; use `collectingAndThen(toList(), List::copyOf)` if the result escapes.
- Composed downstreams (`mapping`, `flatMapping`, `filtering`, `teeing`) replace most nested-loop aggregation code. `teeing` (Java 12) computes two collectors in one pass — good for "count and sum in one traversal."

### `SB-3` toList() vs Stream.toList()

**L4**
- `Collectors.toList()` — mutability, serializability, and thread-safety are *unspecified*; in practice an `ArrayList`. Allows nulls.
- `Collectors.toUnmodifiableList()` — guaranteed unmodifiable, null-hostile.
- `Stream.toList()` (Java 16) — returns an unmodifiable list, but **does allow nulls**, unlike `toUnmodifiableList()`.

**L5**
- That null difference is the one people trip on when mass-migrating `.collect(toList())` → `.toList()`: the mutability change breaks code that sorted the result in place, but the null behavior is *more* permissive, so it hides rather than reveals.
- Default going forward: `.toList()` when you don't need to mutate, `.collect(toCollection(ArrayList::new))` when you explicitly do.

### `SB-4` When parallel streams actually help

**L4**
- Needs: large N, per-element work that isn't trivial, a splittable source, and no shared mutable state.
- Splits well: `ArrayList`, arrays, `IntStream.range`, `HashMap` (sized). Splits badly: `LinkedList`, `Iterator`-based sources, `BufferedReader.lines()`.
- Uses the common `ForkJoinPool` — shared process-wide.

**L5**
- The common-pool sharing is the operational landmine: one parallel stream doing blocking I/O starves every other parallel stream in the JVM, including framework internals. In a Spring Boot service under load I'd treat `parallelStream()` in request-handling code as a defect. Submit to a dedicated `ForkJoinPool` if you must.
- Rough heuristic (from Brian Goetz): `N × Q` should exceed ~10⁴ elementary operations before parallelism pays for the fork/join overhead.
- Ordered operations (`findFirst`, `limit`, `forEachOrdered`) reintroduce sequencing costs and can make parallel *slower* than sequential.
- Honest interview answer: "I've almost never had a workload where parallel streams were the right tool — a service is already parallel at the request level, so the cores are busy."

### `SB-5` Spliterator

**L4**
- The parallel-capable iterator: `tryAdvance` (one element), `trySplit` (hand off a chunk), `estimateSize`, `characteristics`.
- Characteristics: `ORDERED`, `DISTINCT`, `SORTED`, `SIZED`, `NONNULL`, `IMMUTABLE`, `CONCURRENT`, `SUBSIZED`.
- The stream pipeline uses them to skip work — e.g. `distinct()` is a no-op on a `DISTINCT` source; `SIZED` lets `toArray` presize.

**L5**
- This is *why* `ArrayList` parallelizes well and `LinkedList` doesn't: `ArrayList`'s spliterator is `SIZED | SUBSIZED | ORDERED` and splits by index in O(1); `LinkedList`'s must walk.
- Writing a custom `Spliterator` is the right move when you're wrapping a paged API into a stream — implement `trySplit` returning `null` if you can't split, and you still get a correct sequential stream.
- Declaring characteristics you don't actually satisfy causes silently wrong results, not exceptions. It's a contract, not a hint.

---

## System 8 — Performance & memory

### `PF-1` Big-O cheat sheet

**L4**

| Structure | get/contains | add | remove | Notes |
|---|---|---|---|---|
| `ArrayList` | O(1) index / O(n) contains | O(1)* end | O(n) | *amortized |
| `LinkedList` | O(n) | O(1) ends | O(1) w/ node, O(n) by value | |
| `ArrayDeque` | O(n) contains | O(1)* both ends | O(1)* ends | |
| `HashMap`/`HashSet` | O(1) avg, O(log n) worst | O(1) avg | O(1) avg | worst since treeify |
| `LinkedHashMap` | O(1) avg | O(1) avg | O(1) avg | + order |
| `TreeMap`/`TreeSet` | O(log n) | O(log n) | O(log n) | sorted |
| `PriorityQueue` | O(1) peek, O(n) contains | O(log n) | O(log n) poll, O(n) by value | |
| `CopyOnWriteArrayList` | O(1) get, O(n) contains | O(n) | O(n) | snapshot reads |
| `ConcurrentSkipListMap` | O(log n) | O(log n) | O(log n) | size O(n) |

**L5**
- The constants dominate below ~10k elements. A `LinkedList` insert is asymptotically better and empirically worse because of pointer chasing and allocation.
- Watch the O(n) operations hiding in "fast" structures: `PriorityQueue.remove(Object)`, `CLQ.size()`, `ConcurrentSkipListMap.size()`, `CopyOnWriteArraySet.add`. Those are where an innocent-looking loop becomes O(n²).
- The number I'd actually quote in a design round is memory, not time — see `PF-2`.

### `PF-2` Memory overhead and boxing

**L4**
- Object header ~12–16 bytes; references 4 bytes with compressed oops (heap < 32 GB), 8 without.
- `Integer` ≈ 16 bytes + 4 for the reference vs 4 for an `int`. `HashMap.Node` ≈ 32 bytes on top of key and value.
- `Map<Integer, Integer>` with 1M entries ≈ 60–80 MB vs ~8 MB for two `int[]`.
- `Integer.valueOf` caches −128..127, which is why `==` on small boxed ints "works" and then doesn't.

**L5**
- The autoboxing cache is a genuine bug source: `Integer a = 127, b = 127; a == b` is true; at 128 it's false. Always `.equals` or unbox.
- When memory actually matters (large in-memory indexes, caches), primitive collections — Eclipse Collections, fastutil, HPPC — are a 5–10× win in both footprint and speed. That's a real build-vs-buy call worth naming.
- The counter-argument I'd give: adding a collections library for a 100-entry map is over-engineering. The threshold is roughly "does this structure show up in a heap dump's top 10."

### `PF-3` Cache locality

**L4**
- `ArrayList` elements are contiguous *references*; the objects themselves may be scattered, but the reference scan is sequential and prefetch-friendly.
- `LinkedList` nodes are allocated independently — each traversal step is a potential cache miss.
- A cache miss is ~100ns vs ~1ns for L1. That's the 100× constant the Big-O table doesn't show.

**L5**
- This is why `ArrayList` beats `LinkedList` on insertion-in-the-middle benchmarks at surprising sizes — `System.arraycopy` is a vectorized sequential memmove and the traversal to find the position dominates for the linked list.
- Escape-analysis and allocation locality mean freshly built object graphs are often contiguous anyway, so `ArrayList` of recently-allocated objects behaves better than the theory suggests.
- The honest engineering statement: "I choose `ArrayList` by default and only change on a profile, because memory layout matters more than asymptotics at the sizes I actually see."

### `PF-4` Decision framework

**L4** — Ask in order:
1. **Key-value or elements?** → `Map` family vs `Collection` family.
2. **Duplicates allowed?** → `List` vs `Set`.
3. **Ordering needed?** none → hash; insertion → `Linked*`; sorted/range → `Tree*`/skip list; priority → heap.
4. **Access pattern?** index → `ArrayList`; ends only → `ArrayDeque`; lookup by key → hash map.
5. **Concurrency?** none → plain; concurrent → `ConcurrentHashMap`/`newKeySet`/`BlockingQueue`; read-mostly & tiny → `CopyOnWrite*`.
6. **Bounded?** any cross-thread queue → bounded, always.
7. **Key type is an enum?** → `EnumMap`/`EnumSet`.

**L5**
- Add: **who owns the lifetime?** Any long-lived collection needs an eviction or bound story, or it's a leak waiting for a traffic pattern (`FM-3`).
- Add: **does it cross an API boundary?** Then it should be immutable, and the interface type should be `List`/`Map`, not the implementation.
- Say the tradeoff out loud in interviews: "`HashMap` unless I need ordering; `ArrayList` unless I need queue semantics; `ConcurrentHashMap` the moment two threads touch it; bounded `LinkedBlockingQueue` for handoff. Everything else needs a specific justification."

---

## System 9 — Production failure modes

### `FM-1` Realistic incident catalogue

**L4**
1. Unbounded collection → heap exhaustion → OOM or GC death spiral.
2. `HashMap` shared across threads → lost updates / corrupted state.
3. `CME` from removal during iteration, often only on specific data.
4. Unbounded executor queue → latency collapse then OOM (`QD-9`).
5. Mutable key → entries become unreachable (`MP-6`).
6. `Collectors.toMap` duplicate-key exception on production data that dev data didn't have.
7. Code depending on `HashMap` iteration order, breaking on a JDK upgrade.

**L5**
- The pattern across all of these: they're *load-* or *data-dependent*, so they pass tests and fail in production. That's why the mitigations are structural (bounds, immutability, concurrent types) rather than test-based.
- Detection: heap dump + a histogram (`jmap -histo`, or Eclipse MAT's dominator tree) finds #1 and #5 in minutes if you know what you're looking at. Datadog JVM metrics on old-gen occupancy after GC is the leading indicator.
- The one I'd flag in a code review before it ever ships: any `Map` or `List` field on a singleton bean with no eviction. That's the JPMC-shaped version — a per-request cache on a `@Service` bean is a leak by construction.

### `FM-2` Mutable-key defects

**L4**
- Symptom: `map.containsKey(k)` false immediately after `map.put(k, v)` with the same reference.
- Also: `map.size()` grows but `get` always misses; duplicates appear in a `Set`.
- Cause: a field used by `hashCode` changed while the object was in the collection.

**L5**
- Especially common with JPA entities as map keys, because Hibernate populates the ID after flush — the hash changes mid-transaction.
- Also common with DTOs that a mapper mutates after collection insertion.
- Prevention I'd enforce: records or explicitly immutable value types for anything that can be a key, and an ArchUnit/Checkstyle rule if the codebase has been burned.

### `FM-3` Unbounded growth patterns

**L4**
- Static `Map` used as a cache with no eviction.
- Per-request data accumulated on a singleton-scoped bean.
- Listener/callback registries where `unregister` is never called on the failure path.
- Retry/dedup sets keyed by request ID with no TTL.
- Unbounded queues in producer/consumer pipelines.

**L5**
- The dedup-set case is the one that connects to the messaging work: an idempotency key set held in memory grows with traffic forever. The right answer is a TTL'd store — DynamoDB with TTL, Redis with EXPIRE, or a Postgres table with a cleanup job — not a `HashSet`.
- Rule I'd state as a principle: *every* long-lived collection needs one of a hard size bound, a TTL, or a documented natural bound (e.g. "one entry per configured instrument type, ~200"). "It shouldn't get big" is not a bound.
- Detection is easier than prevention: alert on old-gen occupancy after full GC trending up over days, not on heap usage, which is noisy.

### `FM-4` ThreadLocal leaks

**L4**
- `ThreadLocal` values live in a `ThreadLocalMap` on the `Thread` object. In a pooled-thread environment (Tomcat, `ThreadPoolExecutor`), threads are reused indefinitely, so a value set and never removed lives forever.
- The map's *keys* are weak references to the `ThreadLocal`, but the **values are strong** — same shape as `MP-17`.
- Fix: always `remove()` in a `finally`, or use a filter/interceptor that clears the context after each request.

**L5**
- The classic severe version is a classloader leak: a `ThreadLocal` holding an application-classloader object on a container thread prevents the entire webapp classloader from being collected on redeploy → `Metaspace` OOM after a few redeploys.
- MDC (logging context), security context, and tenant/trace context are the usual culprits — all of them are `ThreadLocal`-backed and all of them need explicit cleanup. Spring's `RequestContextHolder` and Sleuth/Micrometer do this for you; hand-rolled context does not.
- With virtual threads (Java 21+), threads aren't pooled, so the leak shape changes — but `ScopedValue` is the intended replacement and it's structurally scoped, which removes the class of bug.

---

# PART 3 — CODE

All Java 17 unless noted.

## 3.1 Correct `equals`/`hashCode` + composable comparators

```java
// Prefer a record — equals/hashCode/toString generated, fields final.
public record InstrumentKey(String isin, String venue) implements Comparable<InstrumentKey> {

    public InstrumentKey {
        Objects.requireNonNull(isin);
        Objects.requireNonNull(venue);
    }

    private static final Comparator<InstrumentKey> ORDER =
            Comparator.comparing(InstrumentKey::isin)
                      .thenComparing(InstrumentKey::venue);   // total order: safe for TreeSet

    @Override public int compareTo(InstrumentKey o) { return ORDER.compare(this, o); }
}

// Hand-written class version (when you can't use a record).
public final class Offering {
    private final String id;          // final: safe as a map key
    private final BigDecimal amount;

    Offering(String id, BigDecimal amount) {
        this.id = Objects.requireNonNull(id);
        this.amount = Objects.requireNonNull(amount);
    }

    @Override public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;   // getClass, not instanceof: preserves symmetry
        Offering that = (Offering) o;
        return id.equals(that.id) && amount.compareTo(that.amount) == 0; // compareTo: 1.0 == 1.00
    }

    // NOTE: because equals uses compareTo on BigDecimal, hashCode must NOT use amount.hashCode().
    @Override public int hashCode() { return id.hashCode(); }
}

// Comparator composition, including null handling and reverse.
Comparator<Offering> byAmountDescThenId =
        Comparator.comparing(Offering::amount, Comparator.nullsLast(Comparator.reverseOrder()))
                  .thenComparing(Offering::id);

// NEVER: (a, b) -> a.getCount() - b.getCount()   // int overflow -> TimSort contract violation
Comparator<Offering> safe = Comparator.comparingInt(o -> o.id().length());
```

## 3.2 LRU cache: whiteboard version and production version

```java
// (a) LinkedHashMap access-order LRU — the interview answer.
public final class LruCache<K, V> extends LinkedHashMap<K, V> {
    private final int maxEntries;

    public LruCache(int maxEntries) {
        super(HashMap.newHashMap(maxEntries), 0.75f, true); // true = ACCESS order (Java 19+ sizing helper)
        this.maxEntries = maxEntries;
    }

    @Override protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > maxEntries;
    }
}
// Not thread-safe. get() structurally modifies (access order) -> CME from a "reader".
// Wrap: Collections.synchronizedMap(new LruCache<>(1000)) — global lock, acceptable only at low QPS.

// (b) Manual HashMap + doubly-linked list — LeetCode 146 shape, O(1) get/put.
final class Node<K, V> { K k; V v; Node<K,V> prev, next; Node(K k, V v){this.k=k;this.v=v;} }

public final class ManualLru<K, V> {
    private final int cap;
    private final Map<K, Node<K,V>> index;
    private final Node<K,V> head = new Node<>(null, null);  // MRU sentinel
    private final Node<K,V> tail = new Node<>(null, null);  // LRU sentinel

    public ManualLru(int cap) {
        this.cap = cap;
        this.index = HashMap.newHashMap(cap);
        head.next = tail; tail.prev = head;
    }

    public V get(K k) {
        Node<K,V> n = index.get(k);
        if (n == null) return null;
        unlink(n); linkFirst(n);
        return n.v;
    }

    public void put(K k, V v) {
        Node<K,V> n = index.get(k);
        if (n != null) { n.v = v; unlink(n); linkFirst(n); return; }
        if (index.size() == cap) { Node<K,V> lru = tail.prev; unlink(lru); index.remove(lru.k); }
        n = new Node<>(k, v);
        index.put(k, n); linkFirst(n);
    }

    private void unlink(Node<K,V> n)    { n.prev.next = n.next; n.next.prev = n.prev; }
    private void linkFirst(Node<K,V> n) { n.next = head.next; n.prev = head;
                                          head.next.prev = n; head.next = n; }
}
```

```java
// (c) What I'd actually ship: Caffeine.
// build.gradle: implementation 'com.github.ben-manes.caffeine:caffeine:3.1.8'
LoadingCache<String, Instrument> cache = Caffeine.newBuilder()
        .maximumSize(10_000)
        .expireAfterWrite(Duration.ofMinutes(10))
        .refreshAfterWrite(Duration.ofMinutes(2))    // serve stale, refresh in background
        .recordStats()                                // export hitRate to Datadog
        .build(key -> instrumentClient.fetch(key));   // loader; stampede-protected per key

Instrument i = cache.get("US0378331005");
```

## 3.3 ConcurrentHashMap idioms

```java
ConcurrentMap<String, LongAdder> counters = new ConcurrentHashMap<>();

// WRONG — check-then-act, lost updates.
if (!counters.containsKey(k)) counters.put(k, new LongAdder());
counters.get(k).increment();

// RIGHT — atomic, and the adder makes the increment itself contention-free.
counters.computeIfAbsent(k, x -> new LongAdder()).increment();

// Simple counting without an adder:
ConcurrentMap<String, Long> counts = new ConcurrentHashMap<>();
counts.merge(k, 1L, Long::sum);                    // atomic, one traversal

// Conditional replace (CAS on value):
boolean applied = map.replace(key, expectedOld, newValue);

// TRAP: expensive loader holds the BIN LOCK for every thread hashing to that bin.
cache.computeIfAbsent(key, k -> httpClient.fetch(k));    // <-- do not do this

// Fix: store a future; the fetch happens outside the map's lock.
ConcurrentMap<String, CompletableFuture<Instrument>> futures = new ConcurrentHashMap<>();
CompletableFuture<Instrument> f = futures.computeIfAbsent(
        key, k -> CompletableFuture.supplyAsync(() -> httpClient.fetch(k), ioPool));
Instrument value = f.join();
// (Caffeine's AsyncLoadingCache does exactly this, with eviction. Prefer it.)

// TRAP: recursive update -> IllegalStateException on CHM, CME on HashMap (Java 9+).
map.computeIfAbsent(a, k -> { map.put(b, v); return compute(k); });   // <-- throws

// Concurrent set:
Set<String> seen = ConcurrentHashMap.newKeySet();
if (seen.add(messageId)) { process(msg); }    // atomic dedup — but see FM-3: needs a TTL
```

## 3.4 Safe iteration and removal

```java
List<Order> orders = new ArrayList<>(source);

// BEST: single pass, O(n) in ArrayList's override.
orders.removeIf(o -> o.status() == CANCELLED);

// When you need the element during removal:
for (Iterator<Order> it = orders.iterator(); it.hasNext(); ) {
    Order o = it.next();
    if (o.isExpired()) { audit(o); it.remove(); }
}

// Map removal via the live views (CH-1):
map.entrySet().removeIf(e -> e.getValue().isStale());
map.values().removeIf(Objects::isNull);
map.keySet().retainAll(activeKeys);

// synchronizedMap: the WRAPPER DOES NOT COVER ITERATION.
Map<String, V> sync = Collections.synchronizedMap(new HashMap<>());
synchronized (sync) {                       // required, or CME
    for (var e : sync.entrySet()) { ... }
}
// ...which is exactly why you use ConcurrentHashMap instead.
```

## 3.5 Top-K with a heap

```java
/** Top K largest by amount. Min-heap of size K: the root is what we're willing to evict. */
static List<Trade> topK(Iterable<Trade> stream, int k) {
    PriorityQueue<Trade> heap = new PriorityQueue<>(k, Comparator.comparing(Trade::amount));
    for (Trade t : stream) {
        heap.offer(t);
        if (heap.size() > k) heap.poll();          // drop the current smallest
    }
    List<Trade> out = new ArrayList<>(heap);        // NOTE: heap order, NOT sorted
    out.sort(Comparator.comparing(Trade::amount).reversed());
    return out;
}

/** FIFO tie-break within equal priority — PriorityQueue is NOT stable. */
record Job(int priority, long seq, Runnable task) {}
AtomicLong seq = new AtomicLong();
PriorityQueue<Job> scheduler = new PriorityQueue<>(
        Comparator.comparingInt(Job::priority).thenComparingLong(Job::seq));
scheduler.offer(new Job(1, seq.getAndIncrement(), task));
```

## 3.6 Bounded producer/consumer with real backpressure

```java
BlockingQueue<Record> queue = new LinkedBlockingQueue<>(10_000);   // ALWAYS bounded
ExecutorService consumers = Executors.newFixedThreadPool(8);
final Record POISON = Record.poison();

// Producer: put() blocks when full -> upstream feels the pressure. That is the point.
void ingest(Record r) throws InterruptedException {
    if (!queue.offer(r, 500, TimeUnit.MILLISECONDS)) {
        droppedCounter.increment();          // or: throw and let the caller retry/DLQ
        throw new BackpressureException("ingest queue full");
    }
}

// Consumer with drain-to-batch (far fewer lock acquisitions than take()-per-element).
Runnable consumer = () -> {
    List<Record> batch = new ArrayList<>(500);
    try {
        while (!Thread.currentThread().isInterrupted()) {
            Record first = queue.take();                 // blocks; parked thread costs nothing
            if (first == POISON) { queue.put(POISON); break; }   // repost for siblings
            batch.add(first);
            queue.drainTo(batch, 499);
            persist(batch);
            batch.clear();
        }
    } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
};
```

## 3.7 ThreadPoolExecutor built correctly (never `Executors.*`)

```java
ThreadPoolExecutor pool = new ThreadPoolExecutor(
        8, 32,                                          // core, max
        60L, TimeUnit.SECONDS,                          // keep-alive for non-core
        new LinkedBlockingQueue<>(1_000),               // BOUNDED — or max is never reached (QD-9)
        new ThreadFactoryBuilder().setNameFormat("ingest-%d").build(),   // named threads = usable dumps
        new ThreadPoolExecutor.AbortPolicy());          // fail fast -> 503, not an unbounded latency queue

// Rejection policy is the design decision:
//   AbortPolicy        -> throws RejectedExecutionException. Right for a request-serving service.
//   CallerRunsPolicy   -> backpressure onto the caller. Right for a batch pipeline; BAD on an HTTP thread.
//   DiscardOldestPolicy-> only when data is genuinely droppable (e.g. metrics samples).

// Instrument it — queue depth is the leading indicator, before latency moves.
Gauge.builder("pool.queue.depth", pool, p -> p.getQueue().size()).register(meterRegistry);
Gauge.builder("pool.active",      pool, ThreadPoolExecutor::getActiveCount).register(meterRegistry);
```

## 3.8 Collector patterns

```java
// toMap with an explicit merge + an ordered result map.
Map<String, Offering> byIsin = offerings.stream()
        .collect(Collectors.toMap(
                Offering::isin,
                Function.identity(),
                (a, b) -> a.version() >= b.version() ? a : b,   // deterministic conflict rule
                LinkedHashMap::new));

// groupingBy with a downstream, into a sorted map.
Map<InstrumentType, BigDecimal> notionalByType = trades.stream()
        .collect(Collectors.groupingBy(
                Trade::type,
                () -> new EnumMap<>(InstrumentType.class),        // enum key -> EnumMap (MP-16)
                Collectors.reducing(BigDecimal.ZERO, Trade::notional, BigDecimal::add)));

// Two aggregations in ONE pass (Java 12+).
record Summary(long count, BigDecimal total) {}
Summary s = trades.stream().collect(Collectors.teeing(
        Collectors.counting(),
        Collectors.reducing(BigDecimal.ZERO, Trade::notional, BigDecimal::add),
        Summary::new));

// Immutable result at the API boundary.
List<String> ids = trades.stream()
        .map(Trade::id)
        .collect(Collectors.collectingAndThen(Collectors.toList(), List::copyOf));

// TRAP: toMap NPEs on a null value even with a merge function (it uses Map.merge).
// Use a loop, or map nulls to a sentinel first.
```

## 3.9 EnumMap / EnumSet for permissions and routing

```java
enum Permission { READ, WRITE, DELETE, SHARE, AUDIT }
enum DocumentType { CONTRACT, PROSPECTUS, TERM_SHEET }

// Bit-vector sets; union/intersection are single bitwise ops.
static final Map<Role, EnumSet<Permission>> ROLE_GRANTS = new EnumMap<>(Map.of(
        Role.VIEWER, EnumSet.of(Permission.READ),
        Role.EDITOR, EnumSet.of(Permission.READ, Permission.WRITE),
        Role.ADMIN,  EnumSet.allOf(Permission.class)));

static final Map<DocumentType, EnumSet<Permission>> TYPE_LIMITS = new EnumMap<>(Map.of(
        DocumentType.CONTRACT,   EnumSet.complementOf(EnumSet.of(Permission.DELETE)),
        DocumentType.PROSPECTUS, EnumSet.allOf(Permission.class),
        DocumentType.TERM_SHEET, EnumSet.of(Permission.READ, Permission.SHARE)));

static boolean allowed(Role role, DocumentType type, Permission p) {
    EnumSet<Permission> effective = EnumSet.copyOf(ROLE_GRANTS.get(role)); // copy: EnumSet is mutable
    effective.retainAll(TYPE_LIMITS.get(type));                            // one AND over a long
    return effective.contains(p);
}
// EnumMap: Object[] indexed by ordinal(). No hashing, no collisions, iteration in declaration order.
```

## 3.10 NavigableMap for range/nearest lookups

```java
// Fee schedule: "which bracket does this notional fall into?" — one O(log n) call.
NavigableMap<BigDecimal, BigDecimal> feeSchedule = new TreeMap<>(Map.of(
        new BigDecimal("0"),         new BigDecimal("0.0030"),
        new BigDecimal("1000000"),   new BigDecimal("0.0020"),
        new BigDecimal("10000000"),  new BigDecimal("0.0010")));

BigDecimal rate = feeSchedule.floorEntry(notional).getValue();   // greatest key <= notional

// Time-bucketed lookup: "value as of timestamp t".
NavigableMap<Instant, Quote> quotes = new TreeMap<>();
Quote asOf = quotes.floorEntry(t).getValue();

// Range scan (view — no copy):
SortedMap<Instant, Quote> window = quotes.subMap(from, true, to, false);

// Concurrent version, same API:
ConcurrentNavigableMap<Instant, Quote> live = new ConcurrentSkipListMap<>();
// NOTE: live.size() is O(n). Track a separate LongAdder if you need a count.
```

## 3.11 Immutable state at the API boundary

```java
public final class RuleSet {
    private final Map<DocumentType, List<Rule>> rules;    // immutable internals

    public RuleSet(Map<DocumentType, List<Rule>> input) {
        Map<DocumentType, List<Rule>> copy = new EnumMap<>(DocumentType.class);
        input.forEach((k, v) -> copy.put(k, List.copyOf(v)));   // deep-ish copy on the way IN
        this.rules = Collections.unmodifiableMap(copy);
    }

    public List<Rule> rulesFor(DocumentType t) {
        return rules.getOrDefault(t, List.of());          // free: already immutable, no copy on get
    }
}

// Hot-swap pattern for a periodically refreshed lookup table.
// No locks, no ConcurrentHashMap — publication safety comes from the volatile write.
public final class RuleCache {
    private volatile RuleSet current = new RuleSet(Map.of());

    public RuleSet get() { return current; }                     // lock-free read

    @Scheduled(fixedDelay = 300_000)
    void refresh() { current = new RuleSet(repository.loadAll()); }   // atomic reference swap
}
```

## 3.12 Presizing helper

```java
// Java 19+:
Map<String, Row> m = HashMap.newHashMap(expectedSize);      // handles the /0.75 for you
Set<String> s = HashSet.newHashSet(expectedSize);

// Java 17 and below:
static int mapCapacity(int expectedEntries) {
    return (int) Math.ceil(expectedEntries / 0.75d);
}
Map<String, Row> m17 = new HashMap<>(mapCapacity(30_000));

// WRONG — resizes at 22,500 entries, which is exactly what you were avoiding.
Map<String, Row> bad = new HashMap<>(30_000);
```

---

# PART 4 — GENERICS QUICK VIEW

## 4.1 The one thing that explains everything: erasure

- Generics are **compile-time only**. `javac` checks types, erases the type parameters, and inserts casts.
- `List<String>` and `List<Integer>` are the same class at runtime: `list1.getClass() == list2.getClass()` is `true`.
- Unbounded `T` erases to `Object`; bounded `<T extends Number>` erases to `Number`.
- Chosen for **migration compatibility** — pre-generics code had to keep working. That decision is the source of every limitation below.

```java
List<String> a = new ArrayList<>();
List<Integer> b = new ArrayList<>();
a.getClass() == b.getClass();          // true — same runtime class
```

## 4.2 What erasure forbids

| Illegal | Why | Workaround |
|---|---|---|
| `new T()` | no runtime type | pass a `Supplier<T>` or `Class<T>` |
| `new T[10]` | can't allocate an erased type | `(T[]) new Object[10]` + `@SuppressWarnings`, or `List<T>` |
| `x instanceof List<String>` | erased | `x instanceof List<?>` |
| `List<String>.class` | one class object for all | `List.class` |
| `static T field;` | T is per-instance | make the method generic, or a static factory |
| `class MyEx<T> extends Exception` | catch matching needs reification | non-generic exception + a typed payload |
| `List<int>` | primitives aren't objects | `List<Integer>`, or a primitive-collection library |
| overloads differing only in `List<String>` vs `List<Integer>` | same erasure | rename the methods |

## 4.3 Arrays vs generics — the two axes

- **Arrays are covariant and reified.** `Object[] o = new String[1];` compiles, then `o[0] = 1;` throws `ArrayStoreException` at runtime.
- **Generics are invariant and erased.** `List<Object> l = new ArrayList<String>();` doesn't compile — the error moves to compile time, which is the point.
- Because they mix badly, you can't create `new List<String>[10]`. Prefer `List<List<String>>` over an array of generics.

## 4.4 Wildcards — PECS

> **P**roducer **E**xtends, **C**onsumer **S**uper.

```java
// Producer: you READ T out of it.
void printAll(List<? extends Number> src) {
    for (Number n : src) { ... }        // read OK
    // src.add(1);                      // COMPILE ERROR — could be List<Double>
}

// Consumer: you WRITE T into it.
void fill(List<? super Integer> dst) {
    dst.add(1);                          // write OK
    Object o = dst.get(0);               // reads come back as Object only
}

// The JDK's own signature is the canonical example:
public static <T> void copy(List<? super T> dest, List<? extends T> src)

// Both read and write -> exact type, no wildcard:
void swap(List<T> list, int i, int j)
```

- `List<?>` (unbounded) — you can read `Object` and `add(null)`, nothing else. Use for "I only care about size/clear/iteration."
- Rule of thumb: **wildcards on parameters, never on return types.** A wildcard return type forces every caller to deal with wildcards.

## 4.5 Generic methods & bounds

```java
// Type parameter goes before the return type.
static <T extends Comparable<? super T>> T max(Collection<? extends T> c) { ... }
//        ^ bound       ^ super: allows T whose *superclass* implements Comparable

// Multiple bounds — class first, then interfaces.
static <T extends Number & Comparable<T>> T clamp(T v, T lo, T hi) { ... }

// Recursive (self-referential) bound — the Enum idiom.
static <E extends Enum<E>> EnumSet<E> allOf(Class<E> type) { ... }

// Type token — recovers the type erasure removed.
static <T> T parse(String json, Class<T> type) { return mapper.readValue(json, type); }
// For generic targets you need a super type token (Jackson's TypeReference):
List<Trade> trades = mapper.readValue(json, new TypeReference<List<Trade>>() {});
```

`<? super T>` in `Comparable<? super T>` matters: it lets `max()` accept a `Dog` whose ordering is defined on `Animal`. Without it, the signature is needlessly restrictive — this is what "flexible API design" means in practice.

## 4.6 Heap pollution & `@SafeVarargs`

```java
@SafeVarargs                 // static, final, or private methods only (private since Java 9)
static <T> List<T> listOf(T... items) { return List.of(items); }

// The danger — a generic varargs param is an array of an erased type:
static <T> T[] toArray(T... args) { return args; }
static <T> T[] pick(T a, T b) { return toArray(a, b); }   // creates Object[] at runtime
String[] s = pick("x", "y");                              // ClassCastException at runtime
```

Rule: only add `@SafeVarargs` if the method never stores into the varargs array and never lets it escape.

## 4.7 Raw types and unchecked warnings

- A raw `List` disables **all** generic checking in that expression, including for unrelated type parameters. Never use raw types in new code.
- `@SuppressWarnings("unchecked")` goes on the **narrowest possible** declaration — ideally a local variable, never a class.
- Bridge methods: the compiler synthesizes them so covariant overrides work after erasure (`Comparable.compareTo(Object)` delegating to `compareTo(Foo)`). You'll see them in stack traces; that's all you need to know.

## 4.8 Quick self-test

1. Why is `List<String>` not a subtype of `List<Object>`? → Invariance; otherwise you could `add(1)` through the supertype reference and break type safety.
2. What does `List<?>` let you add? → Only `null`.
3. Why can't you create `new T[n]`? → Erasure: no runtime type to allocate. Use `(T[]) new Object[n]` internally, or `List<T>`.
4. PECS on `Collections.copy`? → `dest` is `? super T` (consumer), `src` is `? extends T` (producer).
5. Why can't a generic class extend `Throwable`? → `catch` matching requires reified types.
6. Two methods `f(List<String>)` and `f(List<Integer>)`? → Same erasure `f(List)`, won't compile.
7. `List<Object>` vs `List<?>` vs raw `List`? → Holds anything (invariant, unusable as `List<String>`) / unknown type, read-only / no checking at all, never use.
8. Does `getClass()` distinguish `ArrayList<String>` from `ArrayList<Integer>`? → No.
9. When would you take `Class<T>` as a parameter? → Whenever you need the runtime type erasure removed: deserialization, reflection, `EnumSet.allOf`.
10. Why does `Collections.max` use `<T extends Comparable<? super T>>`? → So a subtype ordered by its supertype's `compareTo` still qualifies.

---

## Study sequencing

1. `MP-1` → `MP-7` (HashMap internals). Highest question density in both bank screens and big-tech phone screens.
2. `CH-2`, `CH-4`, `CH-5`, `CH-6` (contracts + iterator semantics). These unlock most follow-ups.
3. `MP-10` → `MP-14`, `CC-1` → `CC-3` (CHM + concurrency). This is the L4/L5 separator.
4. `QD-5`, `QD-9` (bounded queues + pool sizing). Bridges directly into your SQS/backpressure story — reuse the same framing.
5. Part 4 generics — one pass, then the self-test. Bank screens ask 4.1/4.2/4.4 verbatim.

`MP-6`, `MP-13`, `FM-3`, `FM-4` are the ones to volunteer unprompted when an interviewer asks "tell me about a bug you'd worry about" — they show operational thinking rather than recall.

---

## References

1. **[OpenJDK `HashMap.java`](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/HashMap.java)** — read the class-level comment block; the Poisson distribution justification for `TREEIFY_THRESHOLD = 8` is right there. Then `ConcurrentHashMap.java` in the same directory for the CAS/bin-lock design.
2. **[Java 17 Collections Framework Overview](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/doc-files/coll-index.html)** and the **[`java.util.concurrent` package summary](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/package-summary.html)** — the concurrent package summary is where the weakly-consistent iterator contract is actually defined.
3. **[The Java Tutorials — Generics](https://docs.oracle.com/javase/tutorial/java/generics/index.html)** — the "Restrictions on Generics" and "Wildcards" pages cover Part 4 completely.
4. **[Caffeine](https://github.com/ben-manes/caffeine)** — read the wiki's "Efficiency" page for the W-TinyLFU vs LRU hit-rate comparison. This is the production answer to `MP-21`.
5. *Effective Java* 3rd ed. — Items 10–14 (equals/hashCode/Comparable), 26–33 (generics), 78–84 (concurrency). Item 28 (lists over arrays) is the cleanest explanation of covariance vs erasure in print.
6. *Java Concurrency in Practice* — Ch. 5 (building blocks) and Ch. 8 (thread pool sizing / rejection policies) are the source material for `QD-5` through `QD-9`.
