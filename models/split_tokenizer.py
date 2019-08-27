from typing import List

from deeppavlov.core.common.registry import register
from deeppavlov.models.tokenizers.split_tokenizer import SplitTokenizer

@register('simple_tokenizer')
class SimpleTokenizer(SplitTokenizer):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def __call__(self, batch: List[str]) -> List[List[str]]:
        return super().__call__(batch)