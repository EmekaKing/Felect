# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
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
"""Transformer-based text encoder network."""
# pylint: disable=g-classes-have-attributes

import tensorflow as tf

from official.modeling import activations
from official.nlp import keras_nlp


@tf.keras.utils.register_keras_serializable(package='Text')
class BertEncoder(tf.keras.Model):
  """Bi-directional Transformer-based encoder network.

  This network implements a bi-directional Transformer-based encoder as
  described in "BERT: Pre-training of Deep Bidirectional Transformers for
  Language Understanding" (https://arxiv.org/abs/1810.04805). It includes the
  embedding lookups and transformer layers, but not the masked language model
  or classification task networks.

  The default values for this object are taken from the BERT-Base implementation
  in "BERT: Pre-training of Deep Bidirectional Transformers for Language
  Understanding".

  *Note* that the network is constructed by
  [Keras Functional API](https://keras.io/guides/functional_api/).

  Arguments:
    vocab_size: The size of the token vocabulary.
    hidden_size: The size of the transformer hidden layers.
    num_layers: The number of transformer layers.
    num_attention_heads: The number of attention heads for each transformer. The
      hidden size must be divisible by the number of attention heads.
    sequence_length: [Deprecated]. TODO(hongkuny): remove this argument once no
      user is using it.
    max_sequence_length: The maximum sequence length that this encoder can
      consume. If None, max_sequence_length uses the value from sequence length.
      This determines the variable shape for positional embeddings.
    type_vocab_size: The number of types that the 'type_ids' input can take.
    intermediate_size: The intermediate size for the transformer layers.
    activation: The activation to use for the transformer layers.
    dropout_rate: The dropout rate to use for the transformer layers.
    attention_dropout_rate: The dropout rate to use for the attention layers
      within the transformer layers.
    initializer: The initialzer to use for all weights in this encoder.
    return_all_encoder_outputs: Whether to output sequence embedding outputs of
      all encoder transformer layers.
    output_range: The sequence output range, [0, output_range), by slicing the
      target sequence of the last transformer layer. `None` means the entire
      target sequence will attend to the source sequence, which yeilds the full
      output.
    embedding_width: The width of the word embeddings. If the embedding width is
      not equal to hidden size, embedding parameters will be factorized into two
      matrices in the shape of ['vocab_size', 'embedding_width'] and
      ['embedding_width', 'hidden_size'] ('embedding_width' is usually much
      smaller than 'hidden_size').
    embedding_layer: The word embedding layer. `None` means we will create a new
      embedding layer. Otherwise, we will reuse the given embedding layer. This
      parameter is originally added for ELECTRA model which needs to tie the
      generator embeddings with the discriminator embeddings.
    dict_outputs: Whether to use a dictionary as the model outputs.
  """

  def __init__(self,
               vocab_size,
               hidden_size=768,
               num_layers=12,
               num_attention_heads=12,
               sequence_length=None,
               max_sequence_length=512,
               type_vocab_size=16,
               intermediate_size=3072,
               activation=activations.gelu,
               dropout_rate=0.1,
               attention_dropout_rate=0.1,
               initializer=tf.keras.initializers.TruncatedNormal(stddev=0.02),
               return_all_encoder_outputs=False,
               output_range=None,
               embedding_width=None,
               embedding_layer=None,
               dict_outputs=False,
               **kwargs):
    activation = tf.keras.activations.get(activation)
    initializer = tf.keras.initializers.get(initializer)

    self._self_setattr_tracking = False
    self._config_dict = {
        'vocab_size': vocab_size,
        'hidden_size': hidden_size,
        'num_layers': num_layers,
        'num_attention_heads': num_attention_heads,
        'max_sequence_length': max_sequence_length,
        'type_vocab_size': type_vocab_size,
        'intermediate_size': intermediate_size,
        'activation': tf.keras.activations.serialize(activation),
        'dropout_rate': dropout_rate,
        'attention_dropout_rate': attention_dropout_rate,
        'initializer': tf.keras.initializers.serialize(initializer),
        'return_all_encoder_outputs': return_all_encoder_outputs,
        'output_range': output_range,
        'embedding_width': embedding_width,
        'dict_outputs': dict_outputs,
    }

    word_ids = tf.keras.layers.Input(
        shape=(None,), dtype=tf.int32, name='input_word_ids')
    mask = tf.keras.layers.Input(
        shape=(None,), dtype=tf.int32, name='input_mask')
    type_ids = tf.keras.layers.Input(
        shape=(None,), dtype=tf.int32, name='input_type_ids')

    if embedding_width is None:
      embedding_width = hidden_size
    if embedding_layer is None:
      self._embedding_layer = keras_nlp.layers.OnDeviceEmbedding(
          vocab_size=vocab_size,
          embedding_width=embedding_width,
          initializer=initializer,
          name='word_embeddings')
    else:
      self._embedding_layer = embedding_layer
    word_embeddings = self._embedding_layer(word_ids)

    # Always uses dynamic slicing for simplicity.
    self._position_embedding_layer = keras_nlp.layers.PositionEmbedding(
        initializer=initializer,
        max_length=max_sequence_length,
        name='position_embedding')
    position_embeddings = self._position_embedding_layer(word_embeddings)
    self._type_embedding_layer = keras_nlp.layers.OnDeviceEmbedding(
        vocab_size=type_vocab_size,
        embedding_width=embedding_width,
        initializer=initializer,
        use_one_hot=True,
        name='type_embeddings')
    type_embeddings = self._type_embedding_layer(type_ids)

    embeddings = tf.keras.layers.Add()(
        [word_embeddings, position_embeddings, type_embeddings])

    self._embedding_norm_layer = tf.keras.layers.LayerNormalization(
        name='embeddings/layer_norm', axis=-1, epsilon=1e-12, dtype=tf.float32)

    embeddings = self._embedding_norm_layer(embeddings)
    embeddings = (tf.keras.layers.Dropout(rate=dropout_rate)(embeddings))

    # We project the 'embedding' output to 'hidden_size' if it is not already
    # 'hidden_size'.
    if embedding_width != hidden_size:
      self._embedding_projection = tf.keras.layers.experimental.EinsumDense(
          '...x,xy->...y',
          output_shape=hidden_size,
          bias_axes='y',
          kernel_initializer=initializer,
          name='embedding_projection')
      embeddings = self._embedding_projection(embeddings)

    self._transformer_layers = []
    data = embeddings
    attention_mask = keras_nlp.layers.SelfAttentionMask()(data, mask)
    encoder_outputs = []
    for i in range(num_layers):
      if i == num_layers - 1 and output_range is not None:
        transformer_output_range = output_range
      else:
        transformer_output_range = None
      layer = keras_nlp.layers.TransformerEncoderBlock(
          num_attention_heads=num_attention_heads,
          inner_dim=intermediate_size,
          inner_activation=activation,
          output_dropout=dropout_rate,
          attention_dropout=attention_dropout_rate,
          output_range=transformer_output_range,
          kernel_initializer=initializer,
          name='transformer/layer_%d' % i)
      self._transformer_layers.append(layer)
      data = layer([data, attention_mask])
      encoder_outputs.append(data)

    first_token_tensor = (
        tf.keras.layers.Lambda(lambda x: tf.squeeze(x[:, 0:1, :], axis=1))(
            encoder_outputs[-1]))
    self._pooler_layer = tf.keras.layers.Dense(
        units=hidden_size,
        activation='tanh',
        kernel_initializer=initializer,
        name='pooler_transform')
    cls_output = self._pooler_layer(first_token_tensor)

    if dict_outputs:
      outputs = dict(
          sequence_output=encoder_outputs[-1],
          pooled_output=cls_output,
          encoder_outputs=encoder_outputs,
      )
    elif return_all_encoder_outputs:
      outputs = [encoder_outputs, cls_output]
    else:
      outputs = [encoder_outputs[-1], cls_output]
    super(BertEncoder, self).__init__(
        inputs=[word_ids, mask, type_ids], outputs=outputs, **kwargs)

  def get_embedding_table(self):
    return self._embedding_layer.embeddings

  def get_embedding_layer(self):
    return self._embedding_layer

  def get_config(self):
    return self._config_dict

  @property
  def transformer_layers(self):
    """List of Transformer layers in the encoder."""
    return self._transformer_layers

  @property
  def pooler_layer(self):
    """The pooler dense layer after the transformer layers."""
    return self._pooler_layer

  @classmethod
  def from_config(cls, config, custom_objects=None):
    return cls(**config)
