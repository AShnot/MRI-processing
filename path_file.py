import os

class Base():
	project_dir: str = os.path.dirname(os.path.abspath(__file__))

	marked_mri_path: str = project_dir + r"\data"
	processed_data_path: str = project_dir + r"\processed_data"


path_routing = Base()
