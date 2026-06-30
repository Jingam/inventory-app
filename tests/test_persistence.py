import json
import os
import tempfile
import unittest
from unittest.mock import patch

from inventorySys import inventorySystem
from models import Parts, Machine, Room, categories


class PersistenceTests(unittest.TestCase):
    def test_add_part_auto_saves_to_json(self):
        inventory = inventorySystem()

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'inventory_data.json')
            inventory.saveData(file_path)

            with patch('builtins.input', side_effect=[
                'gm-1',
                'Gear',
                '',
                'Acme',
                '5',
                'A1',
                '',
                'Mechanical',
            ]):
                inventory.addPart()

            self.assertTrue(os.path.exists(file_path))
            with open(file_path, 'r') as handle:
                saved_data = json.load(handle)

            self.assertIn('P001', saved_data['parts'])
            self.assertEqual(saved_data['parts']['P001']['partName'], 'Gear')

    def test_round_trip_persists_inventory_objects(self):
        inventory = inventorySystem()
        inventory.partsList['P001'] = Parts(
            partID='P001',
            partName='Gear',
            partDescription='Spur gear',
            modelNumber='GM-1',
            manufacturer='Acme',
            quantity=5,
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
        inventory.roomList.append(Room(
            roomID='R001',
            roomName='Assembly',
            roomDescription='Main assembly area',
            machineList=['M001']
        ))
        inventory.categoriesList.append(categories(
            categoryID='C001',
            categoryName='Mechanical',
            categoryDescription='Mechanical parts',
            partList=['P001']
        ))

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'inventory_data.json')
            inventory.saveData(file_path)

            with open(file_path, 'r') as handle:
                saved_data = json.load(handle)

            restored = inventorySystem()
            restored.loadData(file_path)

            self.assertIn('P001', restored.partsList)
            self.assertEqual(restored.partsList['P001'].partName, 'Gear')
            self.assertIn('M001', restored.machineList)
            self.assertEqual(restored.machineList['M001'].machineName, 'Laser Cutter')
            self.assertEqual(saved_data['parts']['P001']['partName'], 'Gear')
            self.assertEqual(saved_data['machines']['M001']['machineName'], 'Laser Cutter')


if __name__ == '__main__':
    unittest.main()
