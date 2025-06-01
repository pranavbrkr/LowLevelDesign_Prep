from enum import Enum
from abc import ABC, abstractmethod


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
    self.children = children or []

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

class NotADirectory(Exception):
  pass

class FindCommand:
  def findWithFilters(self, directory: File, filters):
    if not directory.is_directory:
      raise NotADirectory(f"{directory.name} is not a directory")
    search_results = []
    self.recurse(directory, filters, search_results)
    return search_results

  def recurse(self, directory, filters, search_results):
    for child in directory.children:
      if child.is_directory:
        self.recurse(child, filters, search_results)
      else:
        if all(filter.apply(child) for filter in filters):
          search_results.append(child)


if __name__ == "__main__":
  root = File("root", 0, FileType.DIRECTORY, True, [
    File("a.txt", 1000, FileType.TEXT),
    File("b.log", 800, FileType.LOG),
    File("c.bin", 600, FileType.BINARY),
    File("sub_dir", 0, FileType.DIRECTORY, True, [
      File("d.log", 1100, FileType.LOG),
      File("e.txt", 110, FileType.TEXT),
    ])
  ])

  cmd = FindCommand()

  filters = [MinSizeFilter(400), FileTypeFilter(FileType.LOG)]

  matches = cmd.findWithFilters(root, filters)
  print(matches)