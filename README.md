# Credit Card Validator

## Setup

### Check Python installation
1. `python -V`
> If your Python version is 2.x.x, please visit [Python downloads](https://www.python.org/downloads/) and get the latest Python 3!

### Install Django
1. `python -m pip install Django`
1. To check your version and ensure Django is installed: `python -m django --version`

## Running the application
> To run the web application (API), perform the following steps:

1. `cd cc_validation`
1. `python manage.py runserver`
1. Open your favorite browser to [http://localhost:8000](http://localhost:8000)

### Validation
> To validate a credit card number, use the following endpoint: `http://localhost:8000/validate/<card_number>`.
> This will return the following values:

* `valid`: Whether or not the credit card # you supplied is valid according to Luhn's algorithm
* `major industry`: This value is the MII, or Major Industry Identifier, and maps to one of several major credit card categories
* `card issuer`: This value is the IIN, or Issuing Identifier Number, and shows which credit card company issued the card number
* `personal digits`: This value is the set of numbers on the card that relate directly to the card holder and represent their account number with the issuer
* `check digit`: This value is the single, last digit and is used to validate the previous numbers on the card using Luhn's algorithm

### Generation
> To generate a valid credit card number, use the following endpoint: `http://localhost:8000/generate/<major_identifier>`.
> This will return:

* `valid`: Whether or not the credit card # generated is valid according to Luhn's algorithm
* `major industry`: This value is the MII you supplied, or Major Industry Identifier, and maps to one of several major credit card categories
* `card issuer`: This value is the IIN, or Issuing Identifier Number, and shows which credit card company issued the card number
* `personal digits`: This value is the set of numbers on the card that relate directly to the card holder and represent their account number with the issuer
* `check digit`: This value is the single, last digit and is used to validate the previous numbers on the card using Luhn's algorithm
