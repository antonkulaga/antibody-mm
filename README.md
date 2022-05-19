# Antibody Moleculare Modeling and docking preprocessing repository

This repository is devoted to two purposes:
* preprocessing data for docking and further molecular dynamics
* molecular modeling simulations

## Command line

It also contains command line arguments to make simulations of the proteins

## Running simulations from the command line

Running simulation of the complex 

```bash
python mm/simulate.py --pdb /data/samples/docking/RA/results/best/S5205Nr1-P2_IgG1Fc_H_top_30_heavy_chains/FIXED_1_35744_H_1_energy_-254.21349.pdb --output /data/docking
```

Running simulation of the components:

```bash
python mm/simulate.py --pdb /data/samples/docking/RA/results/best/S5205Nr1-P2_IgG1Fc_H_top_30_heavy_chains/FIXED_1_35744_H_1_energy_-254.21349/FIXED_1_35744_H_1_energy_-254.21349_antibody.pdb --output /data/docking
```


python mm/simulate.py --pdb /data/samples/docking/RA/results/best/S5205Nr1-P2_IgG1Fc_H_top_30_heavy_chains/1_35744_H_1_energy_-254.21349/1_35744_H_1_energy_-254.21349_antibody.pdb --output /data/docking
