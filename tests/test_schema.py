import unittest
import os
import sys

# Add parent dir to path so we can import mage2gen
sys.path.insert(0, os.path.abspath('..'))

from mage2gen.schema import Table, Constraint
from mage2gen.module import Xmlnode

class TestSchema(unittest.TestCase):

    def test_table_generation(self):
        table = Table('test_table', comment="Test Table")
        
        # Add ID column
        table.add_column('entity_id', 'integer', unsigned=True, identity=True, nullable=False, comment="Entity ID")
        table.add_primary_key('entity_id')
        
        # Add standard column
        table.add_column('title', 'varchar', nullable=True, comment="Title")
        
        # Generate XML
        node = table.to_xml_node()
        xml_output = node.generate()
        
        # Assertions - Check attributes individually to be safe against attribute order/xmlns insertion
        self.assertIn('name="test_table"', xml_output)
        self.assertIn('resource="default"', xml_output)
        self.assertIn('engine="innodb"', xml_output)
        self.assertIn('comment="Test Table"', xml_output)
        
        # Check integer column mapping
        self.assertIn('xsi:type="int"', xml_output)
        self.assertIn('name="entity_id"', xml_output)
        self.assertIn('unsigned="true"', xml_output)
        
        # Check varchar default length
        self.assertIn('xsi:type="varchar"', xml_output)
        self.assertIn('length="255"', xml_output)
        
        # Check Primary Key
        self.assertIn('xsi:type="primary"', xml_output)
        self.assertIn('referenceId="PRIMARY"', xml_output)
        
    def test_foreign_key(self):
        fk = Constraint(Constraint.FOREIGN, referenceId="FK_TEST")
        fk.attributes['table'] = 'test_table'
        fk.attributes['column'] = 'user_id'
        fk.attributes['referenceTable'] = 'admin_user'
        fk.attributes['referenceColumn'] = 'user_id'
        fk.add_column('user_id')
        
        node = fk.to_xml_node()
        xml_output = node.generate()
        
        self.assertIn('xsi:type="foreign"', xml_output)
        self.assertIn('referenceTable="admin_user"', xml_output)
        self.assertIn('referenceId="FK_TEST"', xml_output)

if __name__ == '__main__':
    unittest.main()