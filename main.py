import argparse
import yaml
from src.pipeline import Pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Protein Contact Prediction Pipeline')
    parser.add_argument('-c', '--config', type=str,
                        help='Path to the configuration YAML file',
                        default='experiments/download_data.yaml')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    pipe = Pipeline(args.config)
    pipe.run()


'''
to use vanilla esm2 contact predictor head
python3 main.py -c experiments/e0_vanilla_esm_head/config.yaml
'''