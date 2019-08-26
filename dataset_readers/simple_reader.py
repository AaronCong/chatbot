from typing import Dict, List

from deeppavlov.dataset_readers.dstc2_reader import DSTC2DatasetReader
from deeppavlov.core.common.registry import register


@register('simple_reader')
class SimpleReader(DSTC2DatasetReader):
    @staticmethod
    def _data_fname(datatype):
        return super()._data_fname(datatype)

    @classmethod
    def read(self, data_path: str, dialogs: bool = False) -> Dict[str, List]:
        return super().read(data_path, dialogs)

    @classmethod
    def _read_from_file(cls, file_path, dialogs=False):
        return super()._read_from_file(file_path, dialogs)

    @staticmethod
    def _format_turn(turn):
        return super()._format_turn(turn)

    @staticmethod
    def _iter_file(file_path):
        return super()._iter_file(file_path)

    @staticmethod
    def _get_turns(data, with_indices=False):
        return super()._get_turns(data, with_indices)
