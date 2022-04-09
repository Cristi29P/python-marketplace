"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import logging
import time
from threading import Lock, current_thread
from logging.handlers import RotatingFileHandler


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

        # Mutexes
        self.register_producer_lock = Lock()
        self.register_cart_semaphore = Lock()

        self.logger = logging.getLogger("myLogger")
        self.handler = RotatingFileHandler('marketplace.log', maxBytes=25000, backupCount=10)
        self.handler.setLevel(logging.INFO)
        self.handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)8s: %(message)s'))
        logging.Formatter.converter = time.gmtime
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)

    def register_producer(self):

        """
        Returns an id for the producer that calls this.
        """

        with self.register_producer_lock:
            id_producer = self.number_of_producers
            self.producers_queues[id_producer] = []
            self.number_of_producers += 1
            self.logger.info('Producer id returned: %d for thread %s',
                             id_producer, current_thread().name)

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

        if len(self.producers_queues[int(producer_id)]) < self.queue_size_per_producer:
            self.logger.info('Producer %s with id %d published %s',
                             current_thread().name, producer_id, product)
            self.producers_queues[int(producer_id)].append(product)
            self.products_avail.append(product)
            self.products[product] = int(producer_id)
            return True

        return False

    def new_cart(self):

        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """

        with self.register_cart_semaphore:
            id_cart = self.number_of_carts
            self.logger.info('New_cart with id %d for consumer %s ',
                             id_cart, current_thread().name)
            self.carts[id_cart] = []
            self.number_of_carts += 1

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

        with self.register_cart_semaphore:
            self.logger.info('Product %s bought by consumer %s and added to cart %d',
                             product, current_thread().name, cart_id)
            if product not in self.products_avail:
                return False

            self.products_avail.remove(product)
            self.carts[cart_id].append(product)
            for prod_queue in self.producers_queues.values():
                if product in prod_queue:
                    prod_queue.remove(product)
                    break
        return True

    def remove_from_cart(self, cart_id, product):

        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """

        self.logger.info('Removed product %s from cart %d by consumer %s',
                         product, cart_id, current_thread().name)
        if product in self.carts[cart_id]:
            self.products_avail.append(self.carts[cart_id].pop(self.carts[cart_id].index(product)))

    def place_order(self, cart_id):

        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        popped = self.carts.pop(cart_id)
        with self.register_producer_lock:
            self.logger.info('Ordered placed for cart %d by consumer %s for product list %s',
                             cart_id, current_thread().name, popped)
            for item in popped:
                print(f"{current_thread().name} bought {item}")
        return popped
