import os
from json import dumps
from django.http import HttpResponse


class ValidateCard:
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
        self.checksum = self._checksum()
        self.valid = self.card_number[-1] == self.checksum
        return self.valid

    def __repr__(self):
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
        stack = []
        for i in range(len(self.card_number)):
            stack += [self.card_number[i]]
            for issuer in self.issuer_map:
                if ''.join(stack) in self.issuer_map[issuer]:
                    return issuer

    def _checksum(self):
        # Luhn's Algorithm pulled from https://en.wikipedia.org/wiki/Luhn_algorithm
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
        return HttpResponse(repr(ValidateCard(cc_num)))


class CreateCard(ValidateCard):
    digit_count = 16

    def __init__(self, major_identifier):
        self.major_identifier = major_identifier

    def __repr__(self):
        self._generate()
        return self.card_number

    def _generate(self):
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
        credit_card = CreateCard(major_identifier)
        credit_card.card_number = credit_card.major_identifier[:]
        issuer = credit_card._get_issuer()
        issuer_map = {'Diners Club': DinersClub, 'American Express': Amex}
        if issuer in issuer_map:
            credit_card = issuer_map[issuer](major_identifier)
            credit_card.card_number = credit_card.major_identifier[:]
        credit_card.card_number = repr(credit_card)
        bool(credit_card)
        response = {
            'valid': credit_card.valid,
            'major industry': credit_card.major_map[credit_card.card_number[0]],
            'card issuer': issuer, 'card number': repr(credit_card),
            'personal digits': credit_card.card_number[7:-1],
            'check digit': credit_card.checksum}
        return HttpResponse(dumps(response))


class DinersClub(CreateCard):
    digit_count = 14


class Amex(CreateCard):
    digit_count = 15
