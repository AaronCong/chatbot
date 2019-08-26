from deeppavlov.dataset_iterators.dialog_iterator import DialogDatasetIterator, DialogDBResultDatasetIterator
from deeppavlov.core.common.registry import register


@register('simple_iterator')
class SimpleIterator(DialogDatasetIterator):
    def preprocess(self, data, *args, **kwargs):
        return super().preprocess(data, *args, **kwargs)
