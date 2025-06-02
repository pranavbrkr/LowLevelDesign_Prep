from enum import Enum
from abc import ABC, abstractmethod
from typing import List


# FileType Enum for type of files
class FileType(Enum):
  DIRECTORY = 0
  TEXT = 1
  LOG = 2
  BINARY = 3

# File class with necessary details
class File:
  def __init__(self, name, size, type, is_directory = False, children = None):
    self.name = name
    self.size = size
    self.type = type
    self.is_directory = is_directory
    self.children = children or {}

  def __repr__(self):
    return f"<Name: {self.name}, size: {self.size}, type: {self.type.name}>"
  

# Filter interface
class Filter(ABC):
  @abstractmethod
  def apply(self):
    pass

# Individual filters, which implement above interface
class MinSizeFilter(Filter):
  def __init__(self, min_size):
    self.min_size = min_size
  
  def apply(self, file: File):
    return file.size >= self.min_size
  

class FileTypeFilter(Filter):
  def __init__(self, file_type):
    self.file_type = file_type
  
  def apply(self, file: File):
    return file.type == self.file_type

# Combination filters
class AndFilter(Filter):
  def __init__(self, filters: List[Filter]):
    self.filters = filters
  
  def apply(self, file: File):
    return all(filter.apply(file) for filter in self.filters)

class OrFilter(Filter):
  def __init__(self, filters: List[Filter]):
    self.filters = filters
  
  def apply(self, file: File):
    return any(filter.apply(file) for filter in self.filters)

class NotFilter(Filter):
  def __init__(self, filter: Filter):
    self.filter = filter
  
  def apply(self, file: File):
    return not self.filter.apply(file)

class NotADirectory(Exception):
  pass

class FindCommand:
  def findWithFilters(self, directory: File, root_filter: Filter):
    if not directory.is_directory:
      raise NotADirectory(f"{directory.name} is not a directory")
    search_results = []
    self.recurse(directory, root_filter, search_results)
    return search_results

  def recurse(self, directory: File, root_filter: Filter, search_results):
    for child in directory.children.values():
      if child.is_directory:
        self.recurse(child, root_filter, search_results)
      else:
        if root_filter.apply(child):
          search_results.append(child)


if __name__ == "__main__":
  root = File("root", 0, FileType.DIRECTORY, True, {
    "a.txt": File("a.txt", 1000, FileType.TEXT),
    "b.log": File("b.log", 800, FileType.LOG),
    "c.bin": File("c.bin", 600, FileType.BINARY),
    "sub_dir": File("sub_dir", 0, FileType.DIRECTORY, True, {
      "d.log": File("d.log", 1100, FileType.LOG),
      "e.txt": File("e.txt", 110, FileType.TEXT),
    })
  })

  base_filters = [MinSizeFilter(400), FileTypeFilter(FileType.LOG)]

  mode = "NOT"

  if mode == "AND":
    combined_filter = AndFilter(base_filters)
  elif mode == "OR":
    combined_filter = OrFilter(base_filters)
  elif mode == "NOT":
    combined_filter = NotFilter(AndFilter(base_filters))

  cmd = FindCommand()

  matches = cmd.findWithFilters(root, combined_filter)
  print(matches)