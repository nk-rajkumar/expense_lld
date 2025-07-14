from base.utils.snowflake import get_snowflake_generator

base63_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
snowflake_generator = None


def int_to_base63(snowflake_int):
    """Converts a positive integer into a base63 string."""
    assert snowflake_int >= 0
    base63_string = []
    while snowflake_int > 0:
        snowflake_int, remainder = divmod(snowflake_int, 63)
        base63_string.append(base63_chars[remainder])
    return "".join(base63_string)


def generate_primary_key(prefix=""):
    """
    :type prefix: str
    :param prefix: prefix of model
    :return: str
    """
    return prefix + "_" + get_short_id()


def get_short_id():
    """
    Gets the next integer snowflake id from the generator and converts it to base63
    """
    return int_to_base63(next(get_snowflake_generator()))
