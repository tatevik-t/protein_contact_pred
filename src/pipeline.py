import yaml
import logging
from src.data_preparation import LoadPDB, ProteinDataPreparation, DownloadUniRef50
from src.esm2_integration import ESMContactPrediction
from src.utils import setup_logging

class Pipeline:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file)

        self.tasks = []

        if 'load_pdb' in self.config['types']:
            self.tasks.append(LoadPDB(self.config['load_pdb']))

        if 'download_uniref50' in self.config['types']:
            self.tasks.append(DownloadUniRef50(self.config['download_uniref50']))

        if 'esm_contact_prediction' in self.config['types']:
            self.tasks.append(ESMContactPrediction(self.config['esm_contact_prediction']))

        if 'prepare_data' in self.config['types']:
            self.tasks.append(ProteinDataPreparation(
                raw_data_path=self.config['prepare_data']['raw_data_path'],
                processed_data_path=self.config['prepare_data']['processed_data_path']
            ))

    def run(self):
        setup_logging(self.config['logging']['output_dir'])
        logger = logging.getLogger(__name__)
        for task in self.tasks:
            logger.info("Starting task: %s", task.__class__.__name__)
            task.run()
            logger.info("Finished task: %s", task.__class__.__name__)