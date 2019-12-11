#! /usr/bin/python
'''
This module provides 2 classes:
    ValidateCard => uses .get staticmethod to accept incoming urls and their
        request data and sends them to the class's __repr__ method which parses
        out the different sections of the card # and checks the last digit of
        the card against Luhn's algorithm in the __bool__ method. Passing an
        object of this class inside repr inside HttpResponse returns a JSON
        response that the framework can display as JSON.
    CreateCard => uses .get staticmethod to accept incoming urls and their
        request data and instantiates an instance of itself to call its __repr__
        method to generate a credit card number. It then calls bool on itself
        to check if the number created is valid since it inherits from
        ValidateCard and is able to check itself for validity. The class's
        .get method finally returns a JSON string of the response dictionary
        similar to ValidateCard's response.

Note: `.get` is used as a static method because the url resolver needs to pass
    a request object to the view. Using a class as the view accpeting the
    incoming request would need to pass in the class's object as `self`. A
    staticmethod in the class gets around this and keeps it logically bound to
    class processing the request. There are probably many ways to do this and
    ones that are more Django approved, but this works well and helps to
    preserve encapsulation.

'''
import os
from json import dumps
from django.http import HttpResponse


class ValidateCard:
    '''
    Receives a credit card number and uses Luhn's algorithm to make sure it is
    valid.
    '''
    major_map = {
        '1': 'Airline industry',
        '2': 'Airline industry',
        '3': 'Travel/Entertainment',
        '4': 'Banking/Financial',
        '5': 'Banking/Financial',
        '6': 'Merchandising & Banking/Financial',
        '7': 'Petroleum industries',
        '8': 'Health, telecomm and future',
        '9': 'For assignment by standards bodies'}
    issuer_map = {
        'Diners Club': ('30',),
        'American Express': ('34', '37'),
        'JCB': ('35',),
        'AAA': ('620',),
        'Discover': (['6011', '64', '65'] +
                     [str(n) for n in range(622126, 622925)] +
                     [str(n) for n in range(624000, 626999)] +
                     [str(n) for n in range(628200, 628899)]),
        'Mastercard': ([str(n) for n in range(2221, 2720)] +
                       ['51', '52', '53', '55']),
        'Visa': ('4',)}

    def __init__(self, card_number):
        self.card_number = card_number
        bool(self)

    def __bool__(self):
        '''
        Checks card number against check digit using Luhn's and allows the
        class to be used as a boolean based on this check. Also set the
        .checksum value for later use.
        '''
        self.checksum = self._checksum()
        self.valid = self.card_number[-1] == self.checksum
        return self.valid

    def __repr__(self):
        '''
        Creates a response dict and returns a serialized version of it to be
        passed to the HttpResponse object.
        '''
        response = {
            'valid': self.valid,
            'major industry': self.major_map[self.card_number[0]],
            'card issuer': (f'The card issuer for <b><i>{self.card_number[:6]}'
                            f'</i></b>{self.card_number[6:]} could not be found'),
            'personal digits': self.card_number[7:-1],
            'check digit': self.checksum}
        issuer = self._get_issuer()
        if issuer:
            response.update({'card issuer': issuer})
        return dumps(response)

    def _get_issuer(self):
        '''
        Checks the self.issuer_map dict to see if any of the issuer are a match
        for this card #. Return None if not.
        '''
        stack = []
        for i in range(len(self.card_number)):
            stack += [self.card_number[i]]
            for issuer in self.issuer_map:
                if ''.join(stack) in self.issuer_map[issuer]:
                    return issuer

    def _checksum(self):
        '''
        Uses Luhn's algorithm to check the credit card number against the last
        digit.

        Luhn's algorithm extrapolated from
            https://en.wikipedia.org/wiki/Luhn_algorithm
        '''
        enum = list(enumerate([int(d) for d in self.card_number[:-1][::-1]]))
        memo = dict(enum)
        for pair in enum:
            if pair[0] % 2 == 0:
                digit = pair[1]
                memo[pair[0]] = digit * 2
                if memo[pair[0]] > 9:
                    memo[pair[0]] = (digit * 2) - 9
        _sum = sum(memo.values()) * 9
        return list(str(_sum))[-1]

    @staticmethod
    def get(request, cc_num):
        '''
        Accepts the incoming request without needing to instantiate a class.
        This allows the first arg to be the request object. A pre-defined
        representation of the class is passed to the HttpResponse object,
        provided by Django, and returned as a response Django can understand.
        '''
        return HttpResponse(repr(ValidateCard(cc_num)))


class CreateCard(ValidateCard):
    '''
    Receives a major industry number (as little as 1 digit) and begins adding
    new digits from a set of randomly generated digits (hexed string of
    os.urandom(40) with alphas removed). As each new digit is added, a check
    digit (0 - 9) is added to the end. The entire number is checked against
    Luhn's algorithm. If the entire number is valid, a new digit is added.
    Otherwise, the check digit is removed and new one is added. When the
    desired amount of digits is reached, the process is complete.

    Time complexity is quadratic, but since the largest possible set of numbers
    is small (16 [max possible card digits] x 10 [max possible check digits]
    = 160), the speed impact is negligible. If the set of input numbers were
    unlimited, a way to make this a constant time operation would be to reverse
    engineer Luhn's check algorithm to create a generation algorithm (assuming
    no array variables are needed to loop through as in searching or sorting
    algorithms).
    '''
    digit_count = 16  # max number of digits the card will have

    def __init__(self, major_identifier):
        self.major_identifier = major_identifier

    def __repr__(self):
        '''
        Generates a credit card number, then calls the parent's bool method.
        The check is not necessary, but doing so sets the .valid attr to use
        in returning that field in the response body.
        '''
        self._generate()
        bool(self)
        return self.card_number

    def _generate(self):
        '''
        Takes the incoming major_identifier value and begins adding digits.
        Each new digit has a check digit appended to it, then the whole new
        number is checked against Luhn's. Each time the check passes, a new
        digit is added until the desired length of the credit card is reached.
        '''
        new_digits = [c for c in os.urandom(40).hex() if c.isdigit()]
        while len(self.card_number) < self.digit_count:
            self.card_number += new_digits.pop()
            for j in range(10):
                self.card_number += str(j)
                if self:
                    break
                self.card_number = self.card_number[:-1]

    @staticmethod
    def get(request, major_identifier):
        '''
        Accepts the incoming request without needing to instantiate a class.
        This allows the first arg to be the request object. The second arg is
        the major identifier which is passed into the class's constructor. A
        response is created using internal method's (including parent methods)
        and serialized using Python's json package (json.dumps) and passed to
        the HttpResponse object, provided by Django, and returned as a
        response Django can understand.
        '''
        credit_card = CreateCard(major_identifier)
        credit_card.card_number = credit_card.major_identifier[:]
        issuer = credit_card._get_issuer()
        issuer_map = {'Diners Club': DinersClub, 'American Express': Amex}
        if issuer in issuer_map:
            credit_card = issuer_map[issuer](major_identifier)
            credit_card.card_number = credit_card.major_identifier[:]
        credit_card.card_number = repr(credit_card)
        response = {
            'valid': credit_card.valid,
            'major industry': credit_card.major_map[credit_card.card_number[0]],
            'card issuer': issuer, 'card number': repr(credit_card),
            'personal digits': credit_card.card_number[7:-1],
            'check digit': credit_card.checksum}
        return HttpResponse(dumps(response))


class DinersClub(CreateCard):
    '''
    Exists to distinguish digit count from other card types. This class could
    be used to handle other dinstictions in the future.
    '''
    digit_count = 14


class Amex(CreateCard):
    '''
    Exists to distinguish digit count from other card types. This class could
    be used to handle other dinstictions in the future.
    '''
    digit_count = 15
