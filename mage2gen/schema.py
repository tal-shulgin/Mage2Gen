# mage2gen/schema.py
from .module import Xmlnode

class SchemaComponent:
    """Base class for all schema components."""
    def to_xml_node(self):
        raise NotImplementedError("Subclasses must implement to_xml_node")

class Column(SchemaComponent):
    """Represents a column in a db_schema.xml table."""
    
    # Map Mage2Gen/Python types to Magento XML types
    TYPE_MAP = {
        'integer': 'int',
        'bigint': 'bigint',
        'smallint': 'smallint',
        'boolean': 'smallint', # Boolean is usually smallint in DB
        'tinyint': 'tinyint',
        'float': 'float',
        'decimal': 'decimal',
        'numeric': 'real',
        'date': 'date',
        'datetime': 'datetime',
        'timestamp': 'timestamp',
        'text': 'text',
        'mediumtext': 'mediumtext',
        'longtext': 'longtext',
        'blob': 'blob',
        'varchar': 'varchar',
        'varbinary': 'varbinary',
    }

    def __init__(self, name, type, **kwargs):
        self.name = name
        self.xsi_type = self.TYPE_MAP.get(type, type)
        self.attributes = kwargs
        
        # Set defaults based on type
        if self.xsi_type == 'int' and 'padding' not in self.attributes:
            self.attributes['padding'] = '10'
        
        if self.xsi_type == 'varchar' and 'length' not in self.attributes:
            self.attributes['length'] = '255'
            
        if self.xsi_type == 'decimal':
            if 'scale' not in self.attributes:
                self.attributes['scale'] = '4'
            if 'precision' not in self.attributes:
                self.attributes['precision'] = '12'

    def to_xml_node(self):
        attrs = {
            'xsi:type': self.xsi_type,
            'name': self.name,
        }
        
        # Convert python boolean to xml string 'true'/'false'
        for key, value in self.attributes.items():
            if isinstance(value, bool):
                attrs[key] = 'true' if value else 'false'
            else:
                attrs[key] = str(value)
                
        return Xmlnode('column', attributes=attrs)

class Constraint(SchemaComponent):
    """Represents a constraint (primary, foreign, unique) in db_schema.xml."""
    
    PRIMARY = 'primary'
    FOREIGN = 'foreign'
    UNIQUE = 'unique'

    def __init__(self, type, referenceId=None, **kwargs):
        self.type = type
        self.referenceId = referenceId
        self.attributes = kwargs
        self.columns = []

    def add_column(self, name):
        self.columns.append(name)
        return self

    def to_xml_node(self):
        attrs = {
            'xsi:type': self.type,
            'referenceId': self.referenceId
        }
        
        # Add extra attributes (like table, column, referenceTable for FKs)
        for key, value in self.attributes.items():
            attrs[key] = str(value)

        column_nodes = []
        for col in self.columns:
            column_nodes.append(Xmlnode('column', attributes={'name': col}))

        return Xmlnode('constraint', attributes=attrs, nodes=column_nodes)

class Index(SchemaComponent):
    """Represents an index in db_schema.xml."""
    
    BTREE = 'btree'
    FULLTEXT = 'fulltext'

    def __init__(self, referenceId, indexType=BTREE):
        self.referenceId = referenceId
        self.indexType = indexType
        self.columns = []

    def add_column(self, name):
        self.columns.append(name)
        return self

    def to_xml_node(self):
        attrs = {
            'referenceId': self.referenceId,
            'indexType': self.indexType
        }
        
        column_nodes = []
        for col in self.columns:
            column_nodes.append(Xmlnode('column', attributes={'name': col}))

        return Xmlnode('index', attributes=attrs, nodes=column_nodes)

class Table(SchemaComponent):
    """Represents a table in db_schema.xml."""

    def __init__(self, name, resource="default", engine="innodb", comment=""):
        self.name = name
        self.attributes = {
            'name': name,
            'resource': resource,
            'engine': engine,
            'comment': comment
        }
        self.columns = []
        self.constraints = []
        self.indexes = []

    def add_column(self, name, type, **kwargs):
        col = Column(name, type, **kwargs)
        self.columns.append(col)
        return self

    def add_primary_key(self, column_name):
        constraint = Constraint(Constraint.PRIMARY, referenceId='PRIMARY')
        constraint.add_column(column_name)
        self.constraints.append(constraint)
        return self

    def add_constraint(self, constraint):
        self.constraints.append(constraint)
        return self
        
    def add_index(self, index):
        self.indexes.append(index)
        return self

    def to_xml_node(self):
        nodes = []
        for col in self.columns:
            nodes.append(col.to_xml_node())
        for const in self.constraints:
            nodes.append(const.to_xml_node())
        for idx in self.indexes:
            nodes.append(idx.to_xml_node())

        return Xmlnode('table', attributes=self.attributes, nodes=nodes)