# Copyright (c) Alibaba, Inc. and its affiliates.

from typing import Any, Dict, Optional, Union

import torch

from modelscope.metainfo import Pipelines
from modelscope.models import Model
from modelscope.models.nlp import BartForTextErrorCorrection
from modelscope.outputs import OutputKeys
from modelscope.pipelines.base import Pipeline, Tensor
from modelscope.pipelines.builder import PIPELINES
from modelscope.preprocessors import Preprocessor
from modelscope.utils.constant import Tasks

__all__ = ['TextErrorCorrectionPipeline']


@PIPELINES.register_module(
    Tasks.text_error_correction, module_name=Pipelines.text_error_correction)
class TextErrorCorrectionPipeline(Pipeline):

    def __init__(self,
                 model: Union[Model, str],
                 preprocessor: Optional[Preprocessor] = None,
                 config_file: str = None,
                 device: str = 'gpu',
                 auto_collate=True,
                 **kwargs):
        """use `model` and `preprocessor` to create a nlp text correction pipeline.

        Args:
            model (BartForTextErrorCorrection): A model instance, or a model local dir, or a model id in the model hub.
            preprocessor (TextErrorCorrectionPreprocessor): An optional preprocessor instance.
            kwargs (dict, `optional`):
                Extra kwargs passed into the preprocessor's constructor.
        Example:
        >>> from modelscope.pipelines import pipeline
        >>> pipeline_ins = pipeline(
        >>>    task='text-error-correction', model='damo/nlp_bart_text-error-correction_chinese')
        >>> sentence1 = '随着中国经济突飞猛近，建造工业与日俱增'
        >>> print(pipeline_ins(sentence1))

        To view other examples plese check tests/pipelines/test_text_error_correction.py.
        """
        super().__init__(
            model=model,
            preprocessor=preprocessor,
            config_file=config_file,
            device=device,
            auto_collate=auto_collate)
        if preprocessor is None:
            self.preprocessor = Preprocessor.from_pretrained(
                self.model.model_dir, **kwargs)
        self.vocab = self.preprocessor.vocab

    def forward(self, inputs: Dict[str, Any],
                **forward_params) -> Dict[str, Any]:
        with torch.no_grad():
            return super().forward(inputs, **forward_params)

    def postprocess(self, inputs: Dict[str, Tensor],
                    **postprocess_params) -> Dict[str, str]:
        """
        Args:
            inputs (Dict[str, Tensor])
            Example:
                {
                    'predictions': Tensor([1377, 4959, 2785, 6392...]), # tokens need to be decode by tokenizer
                }
        Returns:
            Dict[str, str]
            Example:
            {
                'output': '随着中国经济突飞猛进，建造工业与日俱增'
            }


        """

        sc_sent = []
        for sent in inputs['predictions']:
            pred_str = self.vocab.string(
                sent, '@@', extra_symbols_to_ignore={self.vocab.pad()})
            sc_sent.append(''.join(pred_str.split()))

        # for  consistent with old version
        if len(sc_sent) == 1:
            sc_sent = sc_sent[0]

        return {OutputKeys.OUTPUT: sc_sent}
