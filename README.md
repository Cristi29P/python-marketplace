Name: Cristian-Tanase Paris 331CAb

# Homework 2 (python-marketplace)

General structure
-

* The producer threads continuously try to produce and add products to their marketplace queues.
If there is no empty slot, then we sleep and try at the next iteration. If the producer was successful,
he waits `republish_wait_time` before doing the next transaction. In this class we do not require any
synchronization primitives.
* The consumer threads have a list of tasks called `carts`, which represent the addition/removal of certain
products from the marketplace. If the requested action could not been fulfilled, the consumer waits `retry_wait_time`
before trying again. After filling up its internal `cart`, the consumer places an order which removes
the requested products from the marketplace. In this class we do not require any
synchronization primitives.
* The marketplace represents the shared space that needs synchronization primitives. I've chosen to use two plain
old Locks() because they are similar to the pthread mutexes, and I did not see the need for more advanced or complex
primitives. 
* We had to use mutexes in the following methods:
  * In `register_producer` because we need to increment the `number of producers` variable (operation which is not atomic), in order
    to get the next id for each requesting producer thread.
  * In `new_cart` because we need to increment the `number_of_carts` variable (operation which is not atomic),
    in order to get the next cart id for each requesting consumer thread.
  * In `add_to_cart` to prevent the following event: two consumers see a product as being available, they
    try to add it to their cart but one is faster and the second thread would give an error when trying to remove
    that product from the producer's queue.
  * In `place_order`, to prevent concurrent writing to the output file, which would result in unknown characters
    appearing.
* A word on unit testing:
    * I had to create a class with methods that test each of marketplace's functionalities.
    * The methods have a lot of boilerplate code, because each time when a unit test is called I have
      to recreate some id's and carts in order to run the test.
    * The tests pretty much test all the functionality in a sequential and single threaded environment.
* A word on logging:
    * In the marketplace constructor I've added the logger object which I then call throughout the program
      to print all the inputs/outputs variables of the methods.
    * The logger files are kinda big, so run it at your own risk.

* This homework greatly helped me understand the logic behind Python's concurrency and threading
workflow, which proved to be useful in some interviews I had recently :).
* I think that I could have done this more efficiently If I had chosen a different approach (opting for priority queues)
or getting rid of that list of available products because always doing a query there takes O(n) time.
* Either way, while the actual code base is very small (don't count the docstrings and the logging/unit tests),
I don't consider this implementation naive. If the test cases were complex, maybe it would have been, who knows?


Implementation
-

* The entire requested functionality has been implemented, including the unit tests and logging
capabilities.
* Technical difficulties:
  * Solving the homework on Windows with WSL2 proved to be a challenge, because the
    testing script has Windows style line terminators which had to be removed.
  * The .ref files also had to be converted to Linux style line terminators.
  * Pylint is extremely slow and sometimes incredibly dumb (why would I only have 10 class
    attributes for example?)
  * Installing pylint also proved to be a challenge because we had to use the requested settings
    and sometimes pylint wouldn't give a damn about those.
* Interesting facts:
  * Logging multiple threads to the same file is thread safe! Found out too late...
  * Unit testing is actually very useful but requires a lot of boilerplate code.
  * The fact that the majority of Python's data structures are thread safe greatly reduced
    the amount of code written and the number of Locks() used. This way the checker should
    run a bit faster.
  * From 

Resources
-

* [ASC Lab1](https://ocw.cs.pub.ro/courses/asc/laboratoare/01)
* [ASC Lab2](https://ocw.cs.pub.ro/courses/asc/laboratoare/02)
* [ASC Lab3](https://ocw.cs.pub.ro/courses/asc/laboratoare/03)
* [Python vs Java](https://realpython.com/oop-in-python-vs-java/)
* [Thread safety](https://docs.python.org/3/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe)
* [Python thread sync](http://dabeaz.blogspot.com/2009/09/python-thread-synchronization.html)

Git
-
1. Link: [python-marketplace](https://github.com/Cristi29P/python-marketplace.git)
2. The repository should go public after the homework's hard deadline (18th of April). Otherwise,
please let me know on e-mail or Microsoft Teams if any problems were encountered.
