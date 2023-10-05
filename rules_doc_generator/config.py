from dataclasses import dataclass

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
  effective_year: str
  effective_month: str
  effective_day: str
  generate_php: bool
  php_base_path: str
  
  def not_annotated(self):
    return Config(False, self.effective_year, self.effective_month, self.effective_day, self.generate_php, self.php_base_path)
  
  def not_php(self):
    return Config(self.annotated, self.effective_year, self.effective_month, self.effective_day, False, self.php_base_path)

  def version_string(self):
    return f'{self.effective_year[2:]}.{self.effective_month}'
  
  def effective_date_str(self):
    if not self.effective_month in short_month_to_full:
      raise Exception(f'Not a valid month string: {self.effective_month}')
    return f'{self.effective_day} {short_month_to_full[self.effective_month]} {self.effective_year}'


