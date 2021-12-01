import click
from openmm.app import *
from openmm import *
from openmm.unit import *

@click.command()
@click.option('--pdb', help='pdb file to clean')
def clean(pdb: str):
    pdb = PDBFile(pdb)
    modeller = Modeller(pdb.topology, pdb.positions)
    modeller.deleteWater()

if __name__ == '__main__':
    clean()