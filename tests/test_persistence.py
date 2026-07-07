import json
import os
import tempfile
import unittest
from unittest.mock import patch

from inventorySys import inventorySystem
from models import Parts, Machine, Room, categories


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        os.environ['INVENTORY_DATA_KEY'] = 'unit-test-data-key'

    def test_add_part_auto_saves_to_json(self):
        inventory = inventorySystem()
        inventory.categoriesList['C001'] = categories(
            categoryID='C001',
            categoryName='Mechanical',
            categoryDescription='Mechanical parts',
            specList=[]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'inventory_data.json')
            inventory.saveData(file_path)
            inventory.file_path = file_path

            with patch('builtins.input', side_effect=[
                'gm-1',
                'Y',
                'Gear',
                '',
                'Acme',
                '5',
                'A1',
                '',
                '1',
            ]):
                inventory.addPart(actor_role='admin')

            self.assertTrue(os.path.exists(file_path))
            with open(file_path, 'r') as handle:
                saved_data = json.load(handle)

            self.assertEqual(saved_data.get('__enc__'), 'invsys-v1')
            self.assertIn('ciphertext', saved_data)
            self.assertNotIn('parts', saved_data)

            restored = inventorySystem()
            restored.loadData(file_path)
            self.assertIn('P001', restored.partsList)
            self.assertEqual(restored.partsList['P001'].partName, 'Gear')

    def test_round_trip_persists_inventory_objects(self):
        inventory = inventorySystem()
        inventory.partsList['P001'] = Parts(
            partID='P001',
            partName='Gear',
            partDescription='Spur gear',
            modelNumber='GM-1',
            manufacturer='Acme',
            stock={'new': 5, 'used': 0, 'installed': 0},
            location='A1',
            notes='',
            category='Mechanical',
            specs={'material': 'steel'}
        )
        inventory.machineList['M001'] = Machine(
            machineID='M001',
            machineName='Laser Cutter',
            machineDescription='Cuts sheet metal',
            machineLocation='Room 2'
        )
        inventory.roomList['R001'] = Room(
            roomID='R001',
            roomName='Assembly',
            roomDescription='Main assembly area',
        )
        inventory.categoriesList['C001'] = categories(
            categoryID='C001',
            categoryName='Mechanical',
            categoryDescription='Mechanical parts',
            specList=[]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'inventory_data.json')
            inventory.saveData(file_path)

            with open(file_path, 'r') as handle:
                saved_data = json.load(handle)
            self.assertEqual(saved_data.get('__enc__'), 'invsys-v1')

            restored = inventorySystem()
            restored.loadData(file_path)

            self.assertIn('P001', restored.partsList)
            self.assertEqual(restored.partsList['P001'].partName, 'Gear')
            self.assertIn('M001', restored.machineList)
            self.assertEqual(restored.machineList['M001'].machineName, 'Laser Cutter')
            self.assertEqual(restored.partsList['P001'].modelNumber, 'GM-1')
            self.assertEqual(restored.machineList['M001'].machineLocation, 'Room 2')


if __name__ == '__main__':
    unittest.main()
