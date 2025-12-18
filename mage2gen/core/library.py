class StandardLibrary:
    """
    Registry of standard Magento 2 Source Models and patterns.
    Derived from the legacy Mage2Gen web definitions.
    """
    
    SOURCE_MODELS = {
        # Boolean / Logic
        'yesno': 'Magento\\Config\\Model\\Config\\Source\\Yesno',
        'enabledisable': 'Magento\\Config\\Model\\Config\\Source\\Enabledisable',
        'nooptreq': 'Magento\\Config\\Model\\Config\\Source\\Nooptreq',
        
        # Scopes & Setup
        'store': 'Magento\\Config\\Model\\Config\\Source\\Store',
        'website': 'Magento\\Config\\Model\\Config\\Source\\Website',
        'locale': 'Magento\\Config\\Model\\Config\\Source\\Locale',
        'currency': 'Magento\\Config\\Model\\Config\\Source\\Locale\\Currency',
        'countries': 'Magento\\Directory\\Model\\Config\\Source\\Country',
        'email_template': 'Magento\\Config\\Model\\Config\\Source\\Email\\Template',
        'email_identity': 'Magento\\Config\\Model\\Config\\Source\\Email\\Identity',
        
        # Sales & Catalog
        'order_status_new': 'Magento\\Sales\\Model\\Config\\Source\\Order\\Status\\NewStatus',
        'order_status_processing': 'Magento\\Sales\\Model\\Config\\Source\\Order\\Status\\Processing',
        'product_type': 'Magento\\Catalog\\Model\\Product\\Type',
        'customer_group': 'Magento\\Customer\\Model\\Customer\\Attribute\\Source\\Group',
        
        # Category
        'category_mode': 'Magento\\Catalog\\Model\\Category\\Attribute\\Source\\Mode',
        'category_layout': 'Magento\\Catalog\\Model\\Category\\Attribute\\Source\\Layout',
        'category_sortby': 'Magento\\Catalog\\Model\\Category\\Attribute\\Source\\Sortby',
        
        # Product
        'product_status': 'Magento\\Catalog\\Model\\Product\\Attribute\\Source\\Status',
        'product_layout': 'Magento\\Catalog\\Model\\Product\\Attribute\\Source\\Layout',
    }

    @staticmethod
    def resolve_source(alias_or_class):
        """Returns the full class name if alias found, otherwise returns input."""
        if not alias_or_class:
            return None
        
        key = alias_or_class.lower()
        return StandardLibrary.SOURCE_MODELS.get(key, alias_or_class)