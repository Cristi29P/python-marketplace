"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import BoundedSemaphore, current_thread


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        # Internal counter used for assigning different id's to each producer
        self.number_of_producers = 0
        # Internal counter used for assigning different id's to each cart
        self.number_of_carts = 0

        # All the producers' queues
        self.producers_queues = {}
        # Products available in the marketplace
        self.products_avail = []
        # Products added by each producer (product, id_prod)
        self.products = {}
        # All the carts issued in the marketplace (id_cart, [products])
        self.carts = {}

        # Binary semaphores used as mutexes
        self.register_producer_semaphore = BoundedSemaphore()
        self.register_cart_semaphore = BoundedSemaphore()
        self.add_to_cart_semaphore = BoundedSemaphore()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.register_producer_semaphore:
            id_producer = self.number_of_producers
            self.number_of_producers += 1

        self.producers_queues[id_producer] = []
        return id_producer

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

        if len(self.producers_queues[int(producer_id)]) == self.queue_size_per_producer:
            return False

        self.producers_queues[int(producer_id)].append(product)
        self.products_avail.append(product)
        self.products[product] = int(producer_id)

        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        with self.register_cart_semaphore:
            id_cart = self.number_of_carts
            self.number_of_carts += 1

        self.carts[id_cart] = []
        return id_cart

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        with self.add_to_cart_semaphore:
            if product in self.products_avail:

                self.products_avail.remove(product)

                for (producer, p_list) in self.producers_queues.items():
                    # Remove the product from the producer's queue
                    if product in p_list:
                        p_list.remove(product)
                        self.products[product] = producer
                        break

                self.carts[cart_id].append(product)
                return True

            return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        if product in self.carts[cart_id]:
            producer_id = self.products[product]
            if not len(self.producers_queues[producer_id]) == self.queue_size_per_producer:
                self.carts[cart_id].remove(product)
                self.products_avail.append(product)

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        popped = self.carts.pop(cart_id)
        with self.register_producer_semaphore:
            for item in popped:
                print(f"{current_thread().name} bought {item}")
            return popped
