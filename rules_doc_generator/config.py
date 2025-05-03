from dataclasses import dataclass

import argparse
import os

short_month_to_full = {
  'XX': 'XX',
  '01': 'January',
  '02': 'February',
  '03': 'March',
  '04': 'April',
  '05': 'May',
  '06': 'June',
  '07': 'July',
  '08': 'August',
  '09': 'September',
  '10': 'October',
  '11': 'November',
  '12': 'December',
}

@dataclass
class Config:
  annotated: bool
  generate_nrdb_info: bool
  nrdb_info_folder: str
  effective_year: str
  effective_month: str
  effective_day: str
  php_base_path: str
  output_types: list[str]
  
  def not_annotated(self):
    return Config(False, self.generate_nrdb_info, self.nrdb_info_folder, self.effective_year, self.effective_month, self.effective_day, self.php_base_path, self.output_types)
  
  def without_opengraph(self):
    without_opengraph = list(filter(lambda x: x != "opengraph", self.output_types))
    return Config(self.annotated, self.generate_nrdb_info, self.nrdb_info_folder, self.effective_year, self.effective_month, self.effective_day, self.php_base_path, without_opengraph)

  def version_string(self):
    return f'{self.effective_year[2:]}.{self.effective_month}'
  
  def effective_date_str(self):
    if not self.effective_month in short_month_to_full:
      raise Exception(f'Not a valid month string: {self.effective_month}')
    return f'{self.effective_day} {short_month_to_full[self.effective_month]} {self.effective_year}'
  
def parse_output_types(arguments: list[str]):
  lowercase_arguments = list(map(lambda x: x.lower(), arguments))
  if "all" in lowercase_arguments:
    return ["pdf", "web", "opengraph", "json"]
  return list(filter(lambda x: x == "pdf" or x == "web" or x == "opengraph" or x == "json", lowercase_arguments))

def validate_nrdb_info_folder(file: str):
    if not os.path.exists(file):
        raise argparse.ArgumentTypeError(f"{file} does not exist")
    return file
