import csv
import os
from datetime import datetime

from src.movie_list_tools.dataclass_helpers import CombinedListDiaryObject, DiaryMovieObject
from src.movie_list_tools.movie_list_sorter import MovieSorterBaseClass


class SortListDiary(MovieSorterBaseClass):

    def __init__(self, file_location: str, list_name: str, col: str, reverse: bool = False):
        super().__init__(file_location, list_name)
        self.diary_file_location = os.path.join(file_location, "diary.csv")
        self.diary_items = dict()
        self.combined_dicts = dict()
        self.col = self._check_col(col)
        self._perform_sort_list(reverse=reverse)

    @staticmethod
    def _check_col(col: str) -> str:
        """
        Checks if specified col can be joined with list object
        """
        columns_available = {"name", "year", "rating", "watched_date"}
        if col not in columns_available:
            raise Exception(f"Mentioned column name is not usable. Please use one of {columns_available}")
        return col

    def _read_diary_csv(self):
        """
        Reads diary csv creates a neat dict with all items.
        """
        with open(self.diary_file_location) as csvfile:
            contents = csv.reader(csvfile, delimiter=',')
            headers = next(contents)
            for line in contents:
                if line[1] not in self.diary_items:
                    key = line[1]
                else:
                    suffix_int = 1
                    while f"{line[1]} ({str(suffix_int)})" in self.diary_items:
                        suffix_int += 1
                    key = f"{line[1]} ({str(suffix_int)})"
                    self.rewatch_dict[line[1]].append(key)

                self.diary_items[key] = DiaryMovieObject(date_=datetime.strptime(line[0], '%Y-%m-%d').date(),
                                                         name=line[1], year=int(line[2]), url=line[3],
                                                         rating=float(line[4]), rewatch=line[5] == "Yes",
                                                         tags=line[6].split(","),
                                                         watched_date=datetime.strptime(line[7], '%Y-%m-%d').date())

    def _combine_dicts(self):
        """
        Combines details from list csv and diary csv -> self.combined_dict
        """
        for movie in self.movie_names:
            if self.diary_items.get(movie):
                diary_list = [movie]
                if self.rewatch_dict.get(movie):
                    diary_list.extend(self.rewatch_dict.get(movie))

                self.combined_dicts[movie] = CombinedListDiaryObject(rewatch=self.diary_items.get(movie).rewatch,
                                                                     listobj=self.list_item_dicts.get(movie),
                                                                     diaryobjs=[self.diary_items.get(i) for i in
                                                                                diary_list])
            else:
                self.combined_dicts[movie] = CombinedListDiaryObject(rewatch=False,
                                                                     listobj=self.list_item_dicts.get(movie))

    def _sorter(self, movie_list: list = None, reverse: bool = False):
        """
        Sorts the list of movie names using self.combined_dict
        """
        self.movie_names = sorted(self.movie_names, reverse=reverse,
                                  key=lambda x: getattr(self.combined_dicts.get(x).diaryobjs[-1], self.col))

    def _movie_object_sorter(self):
        """
        Sorts items from self.item_dicts into self.sorted_dict (contains MovieObjects) based on order of
        self.movie_names.
        """
        for i, val in enumerate(self.movie_names):
            item = self.list_item_dicts.get(val)
            item.position = i + 1
            self.sorted_dict[val] = item

    def _perform_sort_list(self, reverse: bool = False):
        """
        The whole operation from top to bottom.
        """
        self._read_list_csv()
        self._read_diary_csv()
        self._combine_dicts()
        self._sorter(reverse=reverse)
        self._movie_object_sorter()
        self._write_list_csv()


if __name__ == '__main__':
    SortListDiary("E:\\Movie Data\\letterboxd-naveenpiedy-jun", "watched-in-2020.csv", col="rating", reverse=False)
