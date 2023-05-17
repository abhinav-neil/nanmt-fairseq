import math

import torch
import torch.nn.functional as F
from fairseq import utils
from fairseq.logging import metrics
from fairseq.criterions import FairseqCriterion, register_criterion
from fairseq.dataclass import FairseqDataclass
from torch import Tensor

from dataclasses import dataclass, field

@dataclass
class RLCriterionConfig(FairseqDataclass):
    sentence_level_metric: str = field(default="bleu",
                                       metadata={"help": "sentence level metric"})


@register_criterion("rl_loss", dataclass=RLCriterionConfig)
class RLCriterion(FairseqCriterion):
    def __init__(self, task, sentence_level_metric):
        super().__init__(task)
        self.metric = sentence_level_metric

    def _compute_loss(
        self, outputs, targets, masks=None, label_smoothing=0.0, name="loss", factor=1.0
    ):
        """
        outputs: batch x len x d_model
        targets: batch x len
        masks:   batch x len
        """

        #padding mask
        ##If you take mask before you do sampling: you sample over a BATCH and your reward is on token level
        #if you take mask after, you sample SENTENCES and calculate reward on a sentence level 
        #but make sure you apply padding mask after both on log prob outputs, reward and id's (you might need them for gather function to           extract log_probs of the samples)

        #Example 1: mask before sampling
        #if masks is not None:
        #    outputs, targets = outputs[masks], targets[masks]

        #we take a softmax over outputs
        #argmax over the softmax \ sampling (e.g. multinomial)
        #sampled_sentence = [4, 17, 18, 19, 20]
        #sampled_sentence_string = tgt_dict.string([4, 17, 18, 19, 20])
        #target_sentence = "I am a sentence"
        #with torch.no_grad()
            #R(*) = eval_metric(sampled_sentence_string, target_sentence)
            #R(*) is a number, BLEU, сhrf, etc.

        #loss = -log_prob(outputs)*R()
        #loss = loss.mean()
        
        #Example 2: mask after sampling
        #bsz = outputs.size(0)
        #seq_len = outputs.size(1)
        #vocab_size = outputs.size(2)
        #with torch.no_grad():
        #probs = F.softmax(outputs, dim=-1).view(-1, vocab_size)
        #sample_idx  = torch.multinomial(probs, 1,replacement=True).view(bsz, seq_len)
        #print(sample_idx.shape)
        #self.tgt_dict = task.tgt_dict in __init__()
        #sampled_sentence_string = self.tgt_dict.string(sample_idx) #here you might also want to remove tokenization and bpe
        #print(sampled_sentence_string) --> if you apply mask before, you get a sentence which is one token 
        #imagine output[mask]=[MxV] where M is a sequence of all tokens in batch excluding padding symbols
        #now you sample 1 vocabulary index for each token, so you end up in [Mx1] matrix
        #when you apply string, it treats every token as a separate sentence --> hence you calc token-level metric. SO it makes much more sense to apply mask after sampling(!)

        ####HERE calculate metric###
        #with torch.no_grad()
        #reward = eval_metric(sampled_sentence_string, target_sentence)
        #reward is a number, BLEU, сhrf, etc.
        #expand it to make it of a shape BxT - each token gets the same reward value (e.g. bleu is 20, so each token gets reward of 20 [20,20,20,20,20])
    
        #now you need to apply mask on both outputs and reward
        #if masks is not None:
        #    outputs, targets = outputs[masks], targets[masks]
        #    reward, sample_idx = reward[mask], sample_idx[mask]
        #log_probs = F.log_probs(outputs, dim=-1)
        #log_probs_of_samples = torch.gather(...)
        #loss = -log_probs*reward
        # loss = loss.mean()
        
        #For more about mask see notes on NLP2-notes-on-mask

    return loss