# Maps Mage2Gen CLI types to PHP strict types
PHP_TYPE_MAP = {
    'boolean': 'bool',
    'smallint': 'int',
    'integer': 'int',
    'int': 'int',
    'bigint': 'int',
    'float': 'float',
    'numeric': 'float',
    'decimal': 'float',
    'date': 'string',      # Magento usually treats dates as strings in Data Interfaces
    'datetime': 'string',
    'timestamp': 'string',
    'text': 'string',
    'blob': 'string',
    'varchar': 'string',
    'select': 'string',    # Defaults to string values usually
    'multiselect': 'string', # Comma separated string usually
}

def get_php_type(input_type, required=True):
    """
    Returns the PHP type hint for a given input type.
    
    Args:
        input_type (str): The Mage2Gen field type (e.g. 'integer')
        required (bool): If False, the type will be nullable (e.g. ?int)
        
    Returns:
        str: The PHP type hint (e.g. 'int', '?string', 'bool')
    """
    php_type = PHP_TYPE_MAP.get(input_type, 'string')
    
    if not required:
        return "?{}".format(php_type)
        
    return php_type

def get_php_doc_type(input_type, required=True):
    """
    Returns the PHP DocBlock type.
    
    Args:
        input_type (str): The Mage2Gen field type
        required (bool): If False, adds '|null'
    
    Returns:
        str: DocBlock type (e.g. 'int|null')
    """
    php_type = PHP_TYPE_MAP.get(input_type, 'string')
    
    if not required:
        return "{}|null".format(php_type)
        
    return php_type