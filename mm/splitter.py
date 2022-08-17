import numpy as np
import pandas as pd
from biopandas.pdb import PandasPdb
from pycomfort.files import *


def read_pdb(p: Path) -> PandasPdb:
    from biopandas.pdb import PandasPdb
    return PandasPdb().read_pdb(str(p))


def split(p: Path) -> tuple[PandasPdb, PandasPdb, PandasPdb]:
    # load antibody key dataframes
    antibody = read_pdb(p)  # ugly, TODO: fix
    antibody_atoms = antibody.df["ATOM"][antibody.df["ATOM"]["chain_id"] =="B"]
    antibody_ids = antibody_atoms["atom_number"].values
    antibody_others = antibody.df["OTHERS"]
    antibody_ids_concat = "|".join(antibody_ids.astype(str))

    # load key antigen dataframes
    antigen = read_pdb(p) # ugly, TODO: fix
    antigen_atoms = antigen.df["ATOM"][antibody.df["ATOM"]["chain_id"] =="A"]
    antigen_ids = antigen_atoms["atom_number"].values
    antigen_others = antigen.df["OTHERS"]
    antigen_ids_concat = "|".join(antigen_ids.astype(str))

    #fixing issues in antibody
    antibody_others_good_ter = antibody_others[~((antibody_others["record_name"] == "TER") & (antibody_others["entry"].str.contains("A")))]
    antibody_others_updated = antibody_others_good_ter[~((antibody_others_good_ter["record_name"] == "CONECT") & (antibody_others_good_ter["entry"].str.contains(antigen_ids_concat)))]


    #fixing issues in antigen
    antigen_others_good_ter = antigen_others[~((antigen_others["record_name"] == "TER") & (antigen_others["entry"].str.contains("B")))]
    antigen_others_updated = antigen_others_good_ter[~((antigen_others_good_ter["record_name"] == "CONECT") & (antigen_others_good_ter["entry"].str.contains(antibody_ids_concat)))]

    #updating antibody and antigen frames

    antibody.df["ATOM"] = antibody_atoms
    antibody.df["OTHERS"] = antibody_others_updated

    antigen.df["ATOM"] = antigen_atoms
    antigen.df["OTHERS"] = antigen_others_updated
    return antibody, antigen, read_pdb(p)


def split_and_write(p: Path, where: Path = None) -> Path:
    if where is None:
        where = p.parent / p.stem
    where.mkdir(exist_ok=True, parents=True)
    antibody, antigen, both = split(p)
    antibody_path = str(where / p.name.replace(".pdb", "_antibody.pdb"))
    print(f"writing antibody to {antibody_path}")
    antibody.to_pdb(antibody_path)
    antigen_path = str(where / p.name.replace(".pdb", "_antigen.pdb"))
    print(f"writing antigen to {antigen_path}")
    antigen.to_pdb(antigen_path)
    print(f"writing antibody_antigen_complex to {antigen_path}")
    both_path = str(where / p.name.replace(".pdb", "_antibody_antigen_complex.pdb"))
    both.to_pdb(both_path)
    return where
