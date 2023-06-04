"""
Contains functions that provide ease to programmers
"""
import json


def write_to_file(products):
    """
    This function writes the jsonArray self.products to the file products.json
    Returns:
        None
    """
    with open("products.json", "w", encoding="UTF-8") as file:
        json.dump(products, file, indent=4)
