# create a df from the proteins in data/pdb/00
import pandas as pd
import os
from Bio.PDB import PDBParser
import numpy
from tqdm import tqdm


def get_protein_residue_contacts(file_path):
    parser = PDBParser()
    structure = parser.get_structure("", file_path)
    residues = [
        residue for residue in structure.get_residues() if residue.get_id()[0] == " "
    ]
    protein = "".join(
        [
            residue.get_resname()
            for residue in structure.get_residues()
            if residue.get_id()[0] == " "
        ]
    )
    residue_id_to_index = {residue.get_id()[1]: i for i, residue in enumerate(residues)}
    contacts = numpy.zeros((len(residues), len(residues)))
    for model in structure:
        for chain in model:
            for residue1 in chain:
                if residue1.get_id()[0] == " " and "CA" in residue1:
                    for residue2 in chain:
                        if residue2.get_id()[0] == " " and "CA" in residue2:
                            index1 = residue_id_to_index[residue1.get_id()[1]]
                            index2 = residue_id_to_index[residue2.get_id()[1]]
                            contacts[index1, index2] = (
                                1 if residue1["CA"] - residue2["CA"] < 8 else 0
                            )
    return protein, contacts


def make_protein_df(df_path, folder, n_files):
    pdb_files = [f for f in os.listdir(folder)[:n_files] if f.endswith(".ent")]
    proteins = []
    contact_maps = []
    for file in tqdm(pdb_files):
        protein, contacts = get_protein_residue_contacts(folder + "/" + file)
        proteins.append(protein)
        contact_maps.append(contacts.tolist())
    df = pd.DataFrame({"protein": proteins, "contact_map": contact_maps})
    print(df.head())
    df.to_csv(df_path, index=False)


if __name__ == "__main__":
    make_protein_df("data/proteins.csv", "data/processed", n_files=300)
