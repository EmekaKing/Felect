# Lint as: python3
# Copyright 2020 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""Decoders configurations."""
from typing import Optional

# Import libraries
import dataclasses

from official.modeling import hyperparams


@dataclasses.dataclass
class Identity(hyperparams.Config):
  """Identity config."""
  pass


@dataclasses.dataclass
class FPN(hyperparams.Config):
  """FPN config."""
  num_filters: int = 256
  use_separable_conv: bool = False


@dataclasses.dataclass
class Decoder(hyperparams.OneOfConfig):
  """Configuration for decoders.

  Attributes:
    type: 'str', type of decoder be used, on the of fields below.
    fpn: fpn config.
  """
  type: Optional[str] = None
  fpn: FPN = FPN()
  identity: Identity = Identity()
