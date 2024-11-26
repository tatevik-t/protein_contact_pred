import os
import logging
from Bio import PDB
import numpy as np
import urllib.request
import gzip
import shutil

class DownloadUniRef50:
    def __init__(self, config):
        self.url = config['url']
        self.output_dir = config['output_dir']
        self.output_file = os.path.join(self.output_dir, 'uniref50.fasta.gz')
        self.extracted_file = os.path.join(self.output_dir, 'uniref50.fasta')
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self):
        """Download and extract UniRef50 dataset."""
        logger = logging.getLogger(__name__)
        logger.info("[DownloadUniRef50] Downloading UniRef50 dataset from: %s", self.url)
        
        # Download the file
        urllib.request.urlretrieve(self.url, self.output_file)
        logger.info("[DownloadUniRef50] Downloaded UniRef50 dataset to: %s", self.output_file)
        
        # Extract the file
        with gzip.open(self.output_file, 'rb') as f_in:
            with open(self.extracted_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        logger.info("[DownloadUniRef50] Extracted UniRef50 dataset to: %s", self.extracted_file)


class LoadPDB:
    def __init__(self, config):
        self.pdb_ids = config['pdb_ids']
        self.output_dir = config['output_dir']
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self):
        """Download PDB files."""
        logger = logging.getLogger(__name__)
        pdbl = PDB.PDBList()
        for pdb_id in self.pdb_ids:
            logger.info("[LoadPDB] Downloading PDB file: %s", pdb_id)
            pdbl.retrieve_pdb_file(pdb_id, pdir=self.output_dir, file_format='pdb',
                                   overwrite=True)
            logger.info("[LoadPDB] Downloaded PDB file: %s", pdb_id)

class ProteinDataPreparation:
    def __init__(self, raw_data_path="data/raw", processed_data_path="data/processed"):
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path
        
        # Create directories if they don't exist
        os.makedirs(raw_data_path, exist_ok=True)
        os.makedirs(processed_data_path, exist_ok=True)
        
        self.parser = PDB.PDBParser(QUIET=True)
        
    def compute_contact_map(self, structure, threshold=8.0):
        """Compute binary contact map from 3D coordinates."""
        atoms = [atom for atom in structure.get_atoms() if atom.name == "CA"]
        n_residues = len(atoms)
        
        contact_map = np.zeros((n_residues, n_residues))
        
        for i, atom1 in enumerate(atoms):
            for j, atom2 in enumerate(atoms):
                if i != j and atom1 - atom2 < threshold:
                    contact_map[i, j] = 1
        
        return contact_map

    def run(self):
        """Process all PDB files in the raw data directory."""
        logger = logging.getLogger(__name__)
        for pdb_file in os.listdir(self.raw_data_path):
            if pdb_file.endswith(".pdb"):
                logger.info("Processing PDB file: %s", pdb_file)
                structure = self.parser.get_structure(pdb_file, os.path.join(self.raw_data_path, pdb_file))
                contact_map = self.compute_contact_map(structure[0])
                output_file = os.path.join(self.processed_data_path, f"{pdb_file.split('.')[0]}_contacts.npy")
                np.save(output_file, contact_map)
                logger.info("Saved contact map to: %s", output_file)
