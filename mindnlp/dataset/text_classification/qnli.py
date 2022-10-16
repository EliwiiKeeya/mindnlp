# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""
QNLI dataset
"""
# pylint: disable=C0103

import os
from typing import Union, Tuple
from mindspore.dataset import GeneratorDataset
from mindnlp.utils.download import cache_file
from mindnlp.dataset.register import load
from mindnlp.configs import DEFAULT_ROOT
from mindnlp.utils import unzip

URL = "https://dl.fbaipublicfiles.com/glue/data/QNLIv2.zip"

MD5 = "b4efd6554440de1712e9b54e14760e82"


class Qnli:
    """
    QNLI dataset source
    """

    label_map = {
        "not_entailment": 1,
        "entailment": 0
    }

    def __init__(self, path) -> None:
        self.path: str = path
        self._label, self._question, self._sentence = [], [], []
        self._load()

    def _load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            dataset = f.read()
        lines = dataset.split("\n")
        lines.pop(0)
        lines.pop(len(lines)-1)
        for line in lines:
            l = line.split("\t")
            self._question.append(l[1])
            self._sentence.append(l[2])
            if not self.path.endswith("test.tsv"):
                self._label.append(self.label_map[l[3]])

    def __getitem__(self, index):
        if not self.path.endswith("test.tsv"):
            return self._label[index], self._question[index], self._sentence[index]
        return self._question[index], self._sentence[index]

    def __len__(self):
        return len(self._sentence)


@load.register
def QNLI(
    root: str = DEFAULT_ROOT, split: Union[Tuple[str], str] = ("train", "dev", "test"), proxies=None
):
    r"""
    Load the QNLI dataset
    Args:
        root (str): Directory where the datasets are saved.
            Default:~/.mindnlp
        split (str|Tuple[str]): Split or splits to be returned.
            Default:('train', 'dev', 'test').
        proxies (dict): a dict to identify proxies,for example: {"https": "https://127.0.0.1:7890"}.

    Returns:
        - **datasets_list** (list) -A list of loaded datasets.
            If only one type of dataset is specified,such as 'trian',
            this dataset is returned instead of a list of datasets.

    Examples:
        >>> dataset_train,dataset_dev,dataset_test = QNLI()
        >>> train_iter = dataset_train.create_tuple_iterator()
        >>> print(next(train_iter))
    """
    cache_dir = os.path.join(root, "datasets", "QNLI")
    path_dict = {
        "train": "train.tsv",
        "dev": "dev.tsv",
        "test": "test.tsv",
    }
    column_names = {
        "train": ["label", "question", "sentence"],
        "dev": ["label", "question", "sentence"],
        "test": ["question", "sentence"],
    }
    path_list = []
    column_names_list = []
    datasets_list = []
    path, _ = cache_file(None, url=URL, cache_dir=cache_dir, md5sum=MD5, proxies=proxies)
    unzip(path, cache_dir)
    if isinstance(split, str):
        path_list.append(
            os.path.join(cache_dir, "QNLI", path_dict[split])
        )
        column_names_list.append(column_names[split])
    else:
        for s in split:
            path_list.append(
                os.path.join(cache_dir, "QNLI", path_dict[s])
            )
            column_names_list.append(column_names[s])
    for idx, path in enumerate(path_list):
        datasets_list.append(
            GeneratorDataset(
                source=Qnli(path), column_names=column_names_list[idx], shuffle=False
            )
        )
    if len(path_list) == 1:
        return datasets_list[0]
    return datasets_list
