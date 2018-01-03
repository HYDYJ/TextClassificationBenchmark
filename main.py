# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import torch
from torch.autograd import Variable
import torch.optim as optim
import numpy as np


from six.moves import cPickle

import opts
import models
import torch.nn as nn
import utils
import torch.nn.functional as F
from torchtext import data
from torchtext import datasets
from torchtext.vocab import Vectors, GloVe, CharNGram, FastText
from torch.nn.modules.loss import NLLLoss,MultiLabelSoftMarginLoss,MultiLabelMarginLoss,BCELoss
import os,time


from_torchtext = False

opt = opts.parse_opt()
if "CUDA_VISIBLE_DEVICES" not in os.environ.keys():
    os.environ["CUDA_VISIBLE_DEVICES"] =opt.gpu

#opt.model ='fasttext'
if from_torchtext:
    train_iter, test_iter = utils.loadData(opt)
else:
    import dataHelper as helper
    train_iter, test_iter = helper.loadData(opt)

model=models.setup(opt)
if torch.cuda.is_available():
    model.cuda()
model.train()
print("# parameters:", sum(param.numel() for param in model.parameters()))
optimizer = optim.Adam(model.parameters(), lr=opt.learning_rate)
optimizer.zero_grad()
loss_fun = BCELoss()

#batch = next(iter(train_iter))
#x=batch.text[0]
#print(utils.evaluation(model,test_iter))
for i in range(opt.max_epoch):
    for epoch,batch in enumerate(train_iter):
        start= time.time()
        text = batch.text[0] if from_torchtext else batch.text
        predicted = model(text)

        loss= F.cross_entropy(predicted,batch.label)

        loss.backward()
        utils.clip_gradient(optimizer, opt.grad_clip)
        optimizer.step()
        if epoch% 100==0:
            if  torch.cuda.is_available():
                print("%d ieration %d epoch with loss : %.5f in %.4f seconds" % (i,epoch,loss.cpu().data.numpy()[0],time.time()-start))
            else:
                print("%d ieration %d epoch with loss : %.5f in %.4f seconds" % (i,epoch,loss.data.numpy()[0],time.time()-start))
    percision=utils.evaluation(model,test_iter,from_torchtext=from_torchtext)
    print("%d ieration with percision %.4f" % (i,percision))


        














    
    







