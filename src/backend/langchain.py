from langchain.document_loaders.csv_loader import CSVLoader


loader = CSVLoader(file_path='./example_data/mlb_teams_2012.csv')
data = loader.load()