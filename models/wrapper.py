# Copyright 2017 Neural Networks and Deep Learning lab, MIPT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Iterable

from deeppavlov.core.models.component import Component
from deeppavlov.models.go_bot.wrapper import DialogComponentWrapper

class SimpleComponentWrapper(DialogComponentWrapper):

    def __init__(self, component: Component, **kwargs):
        super().__init__(component, **kwargs)

    @staticmethod
    def _get_text(utter):
        return super()._get_text(utter)

    def __call__(self, batch):
        return super().__call__(batch)

    def fit(self, data):
        super().fit(data)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def load(self, *args, **kwargs):
        super().load(*args, **kwargs)