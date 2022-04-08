#!/usr/bin/env python

import click
from mdtraj.reporters import *
from openmm.app import *
from pycomfort.files import *
from openmmtools.utils import with_timer
from openmm.openmm import *
from openmm.unit import *

script_folder = Path(__file__).parent.resolve()
print(script_folder)

def make_simulation(pdb_path: Path, delete_water: bool = True, add_hydrogens: bool = True):
    '''
    :param pdb_path: path to the pdb file to make a model from
    :param delete_water: if we should delete the water for further implicit solvent simulation
    :param add_hydrogens:
    :return:
    '''
    pdb = PDBFile(pdb_path.as_posix())
    modeller = Modeller(pdb.topology, pdb.positions)
    forcefield = ForceField('amber14/protein.ff14SB.xml',  'implicit/gbn2.xml')
    temperature = 310 * kelvin
    integrator = LangevinMiddleIntegrator(temperature, 1 / picoseconds, 0.002 * picoseconds)
    if delete_water:
        modeller.deleteWater()
    if add_hydrogens:
        modeller.addHydrogens(forcefield)
        #forcefield = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
    system = forcefield.createSystem(modeller.topology,
                                     nonbondedMethod=CutoffNonPeriodic,
                                     nonbondedCutoff=1.2*nanometer,
                                     switchDistance=1.0*nanometer,
                                     constraints=HBonds
                                     #implicitSolvent=app.GBn2, implicitSolventSaltConc=0.15*moles/liter
                                     )
    simulation = Simulation(pdb.topology, system, integrator)
    simulation.context.setPositions(modeller.positions)
    simulation.minimizeEnergy()
    return simulation


def with_reporters(simulation: Simulation, pdb: Path, where: Path,
                   report_interval: int = 1000, checkpoint_interval: int = 10000,
                   #report_pdb: bool = True #pdb reporter can be heavy
                   ):
    #simulation.reporters.append(PDBReporter((where / f'{pdb.stem}.dcd').as_posix(), report_interval))
    if not where.exists():
        where.mkdir()
    simulation.reporters.append(DCDReporter((where / f'{pdb.stem}.dcd').as_posix(), report_interval))
    simulation.reporters.append(StateDataReporter((where / f'{pdb.stem}_log.tsv').as_posix(), report_interval, potentialEnergy=True, kineticEnergy=True, totalEnergy=True, step=True,temperature=True, separator='\t'))
    simulation.reporters.append(HDF5Reporter((where / f'{pdb.stem}_log.h5').as_posix(), report_interval, coordinates=True, time=True, cell=True, potentialEnergy=True, kineticEnergy=True, temperature=True))
    simulation.reporters.append(CheckpointReporter((where / f'{pdb.stem}_results.chk').as_posix(), checkpoint_interval))
    return simulation


def save_results(sim: Simulation, pdb: Path, where: Path) -> Simulation:
    if not where.exists():
        where.mkdir()
    finalpositions = sim.context.getState(getPositions=True).getPositions()
    PDBFile.writeFile(sim.topology, finalpositions, open((where / f'{pdb.stem}.pdb').as_posix(), 'w'))
    sim.saveState((where/ f'{pdb.stem}_results.xml').as_posix())
    sim.saveCheckpoint((where / f'{pdb.stem}_results.chk').as_posix())
    return sim


@with_timer("molecular dynamics simulation")
def simulate(pdb_path: Path,  output: Path, nano: int):
    print(f"starting the simulation with {pdb_path} , results will be saved to {output} for {nano} nanoseconds")
    initial_sim = make_simulation(pdb_path)
    sim = with_reporters(initial_sim, pdb_path, output)
    steps = round(nano / 2 * 5000000)
    print(f"number of steps is {steps}")
    sim.step(steps)
    print("SAVING RESULTS:")
    save_results(sim, output)
    print("output folder is:")
    tprint(output)
    return output.as_posix()


@click.command()
@click.option('--pdb', type=click.Path(exists=True), help='antibody path')
@click.option('--output', type=click.Path(exists=False), default="/data/docking/", help='output')
@click.option('--nano',  type=click.INT, default=10, help="nanoseconds")
def cli(pdb: str, output, nano: int):
    out = Path(output)
    out.mkdir(exist_ok=True)
    simulate(Path(pdb),  out, nano)


if __name__ == '__main__':
    cli()
