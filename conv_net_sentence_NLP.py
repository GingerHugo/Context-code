"""
Sample code for
Convolutional Neural Networks for Sentence Classification
http://arxiv.org/pdf/1408.5882v2.pdf
Much of the code is modified from
- deeplearning.net (for ConvNet classes)
- https://github.com/mdenil/dropout (for dropout)
- https://groups.google.com/forum/#!topic/pylearn-dev/3QbKtCumAW4 (for Adadelta)
"""
import cPickle
import numpy as np
from collections import defaultdict, OrderedDict
import theano
import theano.tensor as T
import re
import warnings
import sys
warnings.filterwarnings("ignore")   

#different non-linearities
def ReLU(x):
        y = T.maximum(0.0, x)
        return(y)
def Sigmoid(x):
        y = T.nnet.sigmoid(x)
        return(y)
def Tanh(x):
        y = T.tanh(x)
        return(y)
def Iden(x):
        y = x
        return(y)
           
def train_conv_net(datasets,
                                   U,
                                   img_w=300, 
                                   filter_hs=[3,4,5],
                                   hidden_units=[100,2], 
                                   dropout_rate=[0.5],
                                   shuffle_batch=True,
                                   n_epochs=25, 
                                   batch_size=50, 
                                   lr_decay = 0.95,
                                   conv_non_linear="relu",
                                   activations=[Iden],
                                   sqr_norm_lim=9,
                                   non_static=True):
        """
        Train a simple conv net
        img_h = sentence length (padded where necessary)
        img_w = word vector length (300 for word2vec)
        filter_hs = filter window sizes    
        hidden_units = [x,y] x is the number of feature maps (per filter window), and y is the penultimate layer
        sqr_norm_lim = s^2 in the paper
        lr_decay = adadelta decay parameter
        """    
        rng = np.random.RandomState(3435)
        img_h = len(datasets[0][0])-1
        print "sentence length =  ", img_h  
        filter_w = img_w    
        feature_maps = hidden_units[0]
        filter_shapes = []
        pool_sizes = []
        for filter_h in filter_hs:
                filter_shapes.append((feature_maps, 1, filter_h, filter_w))
                pool_sizes.append((img_h-filter_h+1, img_w-filter_w+1))
        parameters = [("image shape",img_h,img_w),("filter shape",filter_shapes), ("hidden_units",hidden_units),
                                  ("dropout", dropout_rate), ("batch_size",batch_size),("non_static", non_static),
                                        ("learn_decay",lr_decay), ("conv_non_linear", conv_non_linear), ("non_static", non_static)
                                        ,("sqr_norm_lim",sqr_norm_lim),("shuffle_batch",shuffle_batch)]
        print parameters    
        
        #define model architecture
        index = T.lscalar()
        x = T.matrix('x')   
        y = T.ivector('y')
        Words = theano.shared(value = U.astype(np.float32, copy=False), name = "Words")
        zero_vec_tensor = T.vector()
        zero_vec = np.zeros(img_w, dtype="float32")
        set_zero = theano.function([zero_vec_tensor], updates=[(Words, T.set_subtensor(Words[0,:], zero_vec_tensor))])
        layer0_input = Words[T.cast(x.flatten(),dtype="int32")].reshape((x.shape[0],1,x.shape[1],Words.shape[1]))                                  
        conv_layers = []
        layer1_inputs = []
        for i in xrange(len(filter_hs)):
                filter_shape = filter_shapes[i]
                pool_size = pool_sizes[i]
                conv_layer = LeNetConvPoolLayer(rng, input=layer0_input,image_shape=(batch_size, 1, img_h, img_w),
                                                                filter_shape=filter_shape, poolsize=pool_size, non_linear=conv_non_linear)
                layer1_input = conv_layer.output.flatten(2)
                conv_layers.append(conv_layer)
                layer1_inputs.append(layer1_input)
        layer1_input = T.concatenate(layer1_inputs,1)
        hidden_units[0] = feature_maps*len(filter_hs)    
        classifier = MLPDropout(rng, input=layer1_input, layer_sizes=hidden_units, activations=activations, dropout_rates=dropout_rate)
        
        #define parameters of the model and update functions using adadelta
        params = classifier.params     
        for conv_layer in conv_layers:
                params += conv_layer.params
        if non_static:
                #if word vectors are allowed to change, add them as model parameters
                params += [Words]
        cost = classifier.negative_log_likelihood(y) 
        dropout_cost = classifier.dropout_negative_log_likelihood(y)           
        grad_updates = sgd_updates_adadelta(params, dropout_cost, lr_decay, 1e-6, sqr_norm_lim)
        
        #shuffle dataset and assign to mini batches. if dataset size is not a multiple of mini batches, replicate 
        #extra data (at random)
        np.random.seed(3435)
        if datasets[0].shape[0] % batch_size > 0:
                extra_data_num = batch_size - datasets[0].shape[0] % batch_size
                train_set = np.random.permutation(datasets[0])   
                extra_data = train_set[:extra_data_num]
                new_data=np.append(datasets[0],extra_data,axis=0)
        else:
                new_data = datasets[0]
        new_data = np.random.permutation(new_data)
        n_batches = new_data.shape[0]/batch_size
        n_train_batches = int(np.round(n_batches*0.9))
        #divide train set into train/val sets 
        train_set = new_data[:n_train_batches*batch_size,:]
        val_set = new_data[n_train_batches*batch_size:,:]     
        train_set_x, train_set_y = shared_dataset((train_set[:,:img_h],train_set[:,-1]))
        val_set_x, val_set_y = shared_dataset((val_set[:,:img_h],val_set[:,-1]))
        n_val_batches = n_batches - n_train_batches
        val_model = theano.function([index], classifier.errors(y),
                 givens={
                        x: val_set_x[index * batch_size: (index + 1) * batch_size],
                        y: val_set_y[index * batch_size: (index + 1) * batch_size]})
                        
        #compile theano functions to get train/val/test errors
        test_model = theano.function([index], classifier.errors(y),
                         givens={
                                x: train_set_x[index * batch_size: (index + 1) * batch_size],
                                y: train_set_y[index * batch_size: (index + 1) * batch_size]})               
        train_model = theano.function([index], cost, updates=grad_updates,
                  givens={
                        x: train_set_x[index*batch_size:(index+1)*batch_size],
                        y: train_set_y[index*batch_size:(index+1)*batch_size]})

        # test_set_x = datasets[1][:,:img_h]
        # test_set_y = np.asarray(datasets[1][:,-1],"int32")
        # test_set_x = test_set_x.astype("float32") 
        # test_pred_layers = []
        # test_size = test_set_x.shape[0]
        # test_layer0_input = Words[T.cast(x.flatten(),dtype="int32")].reshape((test_size,1,img_h,Words.shape[1]))
        # for conv_layer in conv_layers:
        #         test_layer0_output = conv_layer.predict(test_layer0_input, test_size)
        #         test_pred_layers.append(test_layer0_output.flatten(2))
        # test_layer1_input = T.concatenate(test_pred_layers, 1)
        # test_y_pred = classifier.predict(test_layer1_input)
        # test_error = T.mean(T.neq(test_y_pred, y))
        # test_model_all = theano.function([x,y], test_error)

        #start training over mini-batches
        print '... training'
        epoch = 0
        best_val_perf = 0
        val_perf = 0
        test_perf = 0       
        cost_epoch = 0    
        while (epoch < n_epochs):        
                epoch = epoch + 1
                if shuffle_batch:
                        for minibatch_index in np.random.permutation(range(n_train_batches)):
                                cost_epoch = train_model(minibatch_index)
                                set_zero(zero_vec)
                else:
                        for minibatch_index in xrange(n_train_batches):
                                cost_epoch = train_model(minibatch_index)  
                                set_zero(zero_vec)
                train_losses = [test_model(i) for i in xrange(n_train_batches)]
                train_perf = 1 - np.mean(train_losses)
                val_losses = [val_model(i) for i in xrange(n_val_batches)]
                val_perf = 1- np.mean(val_losses)                        
                print('epoch %i, train perf %f %%, val perf %f' % (epoch, train_perf * 100., val_perf*100.))
                if val_perf >= best_val_perf:
                        best_val_perf = val_perf
        
        # Maximum data size that will not be out of memory
        Maximum_Batch_Size = 5000
        print '... testing context testing'

        # Batch testing only because of memory shortage
        size = datasets[1].shape[0]
        result_vector = np.ones(size, dtype = 'int32')
        CountMax = size // Maximum_Batch_Size
        CountLeft = size % Maximum_Batch_Size
        for x_index in xrange(0, CountMax + 1):
                if x_index != CountMax:
                        test_set_x = datasets[1][(x_index * Maximum_Batch_Size):((x_index + 1) * Maximum_Batch_Size),:img_h]
                        test_set_y = np.asarray(datasets[1][(x_index * Maximum_Batch_Size):((x_index + 1) * Maximum_Batch_Size),-1],"int32")
                elif CountLeft != 0:
                        test_set_x = datasets[1][(x_index * Maximum_Batch_Size):(x_index * Maximum_Batch_Size + CountLeft),:img_h]
                        test_set_y = np.asarray(datasets[1][(x_index * Maximum_Batch_Size):(x_index * Maximum_Batch_Size + CountLeft),-1],"int32")
                else:
                        break
                test_set_x = test_set_x.astype("float32") 
                # predict_test_model = theano.function([], classifier.errors(y),
                #          givens={
                #                 x: test_set_x[:],
                #                 y: test_set_y[:]})   
                # predict_result = [predict_test_model()]
                # print 'predict y'
                # print predict_result
                test_pred_layers = []
                test_size = test_set_x.shape[0]
                test_layer0_input = Words[T.cast(x.flatten(),dtype="int32")].reshape((test_size,1,img_h,Words.shape[1]))
                for conv_layer in conv_layers:
                        test_layer0_output = conv_layer.predict(test_layer0_input, test_size)
                        test_pred_layers.append(test_layer0_output.flatten(2))
                test_layer1_input = T.concatenate(test_pred_layers, 1)
                test_y_pred = classifier.predict(test_layer1_input)
                # print 'predict y'
                # print test_y_pred.shape
                # print test_y_pred[0]
                # test_error = T.mean(T.neq(test_y_pred, y))
                # test_model_all = theano.function([x,y], test_error)
                test_result = T.neq(test_y_pred, y)
                get_predict_y = theano.function([x,y], test_result)
                predict_y = get_predict_y(test_set_x, test_set_y)
                # test_loss = test_model_all(test_set_x,test_set_y)        
                # test_perf = 1- test_loss
                if x_index != CountMax:
                        result_vector[(x_index * Maximum_Batch_Size):((x_index + 1) * Maximum_Batch_Size)] = predict_y[:]
                else:
                        result_vector[(x_index * Maximum_Batch_Size):(x_index * Maximum_Batch_Size + CountLeft)] = predict_y[:]

        print '... testing context entry'
        size = datasets[2].shape[0]
        correct_total = 0
        total_whole = 0
        Y = np.asarray(datasets[2][:,-1],"int32")
        positive_case = sum(Y[Y == 1])
        negative_case = size - positive_case
        for index_temp in xrange(0,2):
                if index_temp:
                        # negative case
                        TempVector = datasets[2][positive_case:,:]
                        size = negative_case
                else:
                        # positive case
                        TempVector = datasets[2][:positive_case,:]
                        size = positive_case
                # result_vector = np.zeros(size, dtype = 'int32')
                CountMax = size // Maximum_Batch_Size
                CountLeft = size % Maximum_Batch_Size
                errorCase = 0
                for x_index in xrange(0, CountMax + 1):
                        if x_index != CountMax:
                                test_set_x = TempVector[(x_index * Maximum_Batch_Size):((x_index + 1) * Maximum_Batch_Size),:img_h]
                                test_set_y = np.asarray(TempVector[(x_index * Maximum_Batch_Size):((x_index + 1) * Maximum_Batch_Size),-1],"int32")
                        elif CountLeft != 0:
                                test_set_x = TempVector[(x_index * Maximum_Batch_Size):(x_index * Maximum_Batch_Size + CountLeft),:img_h]
                                test_set_y = np.asarray(TempVector[(x_index * Maximum_Batch_Size):(x_index * Maximum_Batch_Size + CountLeft),-1],"int32")
                        else:
                                break
                        test_set_x = test_set_x.astype("float32") 
                        test_pred_layers = []
                        test_size = test_set_x.shape[0]
                        test_layer0_input = Words[T.cast(x.flatten(),dtype="int32")].reshape((test_size,1,img_h,Words.shape[1]))
                        for conv_layer in conv_layers:
                                test_layer0_output = conv_layer.predict(test_layer0_input, test_size)
                                test_pred_layers.append(test_layer0_output.flatten(2))
                        test_layer1_input = T.concatenate(test_pred_layers, 1)
                        test_y_pred = classifier.predict(test_layer1_input)
                        # test_error = T.mean(T.neq(test_y_pred, y))
                        # test_model_all = theano.function([x,y], test_error)
                        test_result = T.neq(test_y_pred, y)
                        get_predict_y = theano.function([x,y], test_result)
                        # test_loss = test_model_all(test_set_x,test_set_y)        
                        # test_perf = 1- test_loss
                        predict_y = get_predict_y(test_set_x, test_set_y)
                        result = predict_y
                        result = result.astype("int32")
                        errorCase += result.sum()
                correct = size - errorCase
                test_perf = float(correct) / float(size)
                if index_temp:
                        print 'test_perf for negative context entry is {}, with {} in {}'.format(test_perf, correct, size)
                else:
                        print 'test_perf for positive context entry is {}, with {} in {}'.format(test_perf, correct, size)
                correct_total += correct
                total_whole += size
        test_perf = float(correct_total) / float(total_whole)
        print 'test_perf for context entry is {}, with {} in {}'.format(test_perf, correct_total, total_whole)


        print '... testing document entry'
        size = datasets[3].shape[0]
        correct_total = 0
        total_whole = 0
        Y = np.asarray(datasets[3][:,-1],"int32")
        positive_case = sum(Y[Y == 1])
        negative_case = size - positive_case
        for index_temp in xrange(0,2):
                if index_temp:
                        # negative case
                        TempVector = datasets[3][positive_case:,:]
                        size = negative_case
                else:
                        # positive case
                        TempVector = datasets[3][:positive_case,:]
                        size = positive_case
                # result_vector = np.zeros(size, dtype = 'int32')
                CountMax = size // Maximum_Batch_Size
                CountLeft = size % Maximum_Batch_Size
                errorCase = 0
                for x_index in xrange(0, CountMax + 1):
                        if x_index != CountMax:
                                test_set_x = TempVector[(x_index * Maximum_Batch_Size):((x_index + 1) * Maximum_Batch_Size),:img_h]
                                test_set_y = np.asarray(TempVector[(x_index * Maximum_Batch_Size):((x_index + 1) * Maximum_Batch_Size),-1],"int32")
                        elif CountLeft != 0:
                                test_set_x = TempVector[(x_index * Maximum_Batch_Size):(x_index * Maximum_Batch_Size + CountLeft),:img_h]
                                test_set_y = np.asarray(TempVector[(x_index * Maximum_Batch_Size):(x_index * Maximum_Batch_Size + CountLeft),-1],"int32")
                        else:
                                break
                        test_set_x = test_set_x.astype("float32") 
                        test_pred_layers = []
                        test_size = test_set_x.shape[0]
                        test_layer0_input = Words[T.cast(x.flatten(),dtype="int32")].reshape((test_size,1,img_h,Words.shape[1]))
                        for conv_layer in conv_layers:
                                test_layer0_output = conv_layer.predict(test_layer0_input, test_size)
                                test_pred_layers.append(test_layer0_output.flatten(2))
                        test_layer1_input = T.concatenate(test_pred_layers, 1)
                        test_y_pred = classifier.predict(test_layer1_input)
                        # test_error = T.mean(T.neq(test_y_pred, y))
                        # test_model_all = theano.function([x,y], test_error)
                        test_result = T.neq(test_y_pred, y)
                        get_predict_y = theano.function([x,y], test_result)
                        # test_loss = test_model_all(test_set_x,test_set_y)        
                        # test_perf = 1- test_loss
                        predict_y = get_predict_y(test_set_x, test_set_y)
                        result = predict_y
                        result = result.astype("int32")
                        errorCase += result.sum()
                correct = size - errorCase
                test_perf = float(correct) / float(size)
                if index_temp:
                        print 'test_perf for negative testing document entry is {}, with {} in {}'.format(test_perf, correct, size)
                else:
                        print 'test_perf for positive testing document entry is {}, with {} in {}'.format(test_perf, correct, size)
                correct_total += correct
                total_whole += size
        test_perf = float(correct_total) / float(total_whole)
        print 'test_perf for testing document entry is {}, with {} in {}'.format(test_perf, correct_total, total_whole)
        return result_vector

def shared_dataset(data_xy, borrow=True):
                """ Function that loads the dataset into shared variables
                The reason we store our dataset in shared variables is to allow
                Theano to copy it into the GPU memory (when code is run on GPU).
                Since copying data into the GPU is slow, copying a minibatch everytime
                is needed (the default behaviour if the data is not in a shared
                variable) would lead to a large decrease in performance.
                """
                data_x, data_y = data_xy
                shared_x = theano.shared(np.asarray(data_x,
                                                                                           dtype=theano.config.floatX),
                                                                 borrow=borrow)
                shared_y = theano.shared(np.asarray(data_y,
                                                                                           dtype=theano.config.floatX),
                                                                 borrow=borrow)
                return shared_x, T.cast(shared_y, 'int32')
                
def sgd_updates_adadelta(params,cost,rho=0.95,epsilon=1e-6,norm_lim=9,word_vec_name='Words'):
        """
        adadelta update rule, mostly from
        https://groups.google.com/forum/#!topic/pylearn-dev/3QbKtCumAW4 (for Adadelta)
        """
        updates = OrderedDict({})
        exp_sqr_grads = OrderedDict({})
        exp_sqr_ups = OrderedDict({})
        gparams = []
        for param in params:
                empty = np.zeros_like(param.get_value())
                exp_sqr_grads[param] = theano.shared(value=as_floatX(empty),name="exp_grad_%s" % param.name)
                gp = T.grad(cost, param)
                exp_sqr_ups[param] = theano.shared(value=as_floatX(empty), name="exp_grad_%s" % param.name)
                gparams.append(gp)
        for param, gp in zip(params, gparams):
                exp_sg = exp_sqr_grads[param]
                exp_su = exp_sqr_ups[param]
                up_exp_sg = rho * exp_sg + (1 - rho) * T.sqr(gp)
                updates[exp_sg] = up_exp_sg
                step =  -(T.sqrt(exp_su + epsilon) / T.sqrt(up_exp_sg + epsilon)) * gp
                updates[exp_su] = rho * exp_su + (1 - rho) * T.sqr(step)
                stepped_param = param + step
                if (param.get_value(borrow=True).ndim == 2) and (param.name!='Words'):
                        col_norms = T.sqrt(T.sum(T.sqr(stepped_param), axis=0))
                        desired_norms = T.clip(col_norms, 0, T.sqrt(norm_lim))
                        scale = desired_norms / (1e-7 + col_norms)
                        updates[param] = stepped_param * scale
                else:
                        updates[param] = stepped_param      
        return updates 

def as_floatX(variable):
        if isinstance(variable, float):
                return np.cast[theano.config.floatX](variable)

        if isinstance(variable, np.ndarray):
                return np.cast[theano.config.floatX](variable)
        return theano.tensor.cast(variable, theano.config.floatX)
        
def safe_update(dict_to, dict_from):
        """
        re-make update dictionary for safe updating
        """
        for key, val in dict(dict_from).iteritems():
                if key in dict_to:
                        raise KeyError(key)
                dict_to[key] = val
        return dict_to
        
def getSentenceList(outputList, inputList):
        """
        Get the padded vector
        """
        for element in inputList:
                result = element[1]
                result.append(element[0])
                # result = element["vector"]
                # result.append(element["y"])
                outputList.append(result)

def OrganizeData(training, testing, testingEntry):
        """
        Transforms sentences into a 2-d matrix and add label
        """
        train, test, testEntry = [], [], []
        train = getSentenceList(train, training)
        test = getSentenceList(test, testing)
        testEntry = getSentenceList(testEntry, testingEntry)
        train = np.array(train, dtype="int")
        test = np.array(test, dtype="int")
        testEntry = np.array(testingEntry, dtype = "int")
        return [train, test, testingEntry]     

# def loadVector(vectorAddress):
#         vector = []
#         fp = open(vectorAddress, 'r')
#         for line in fp:
#                 temp.append(np.fromstring(line[1:-2], sep=' '))
#         # print a
# print(np.array(temp, dtype = "float32"))
   
if __name__=="__main__":
        fileAddress = {('rule-based', 'naive_'), ('discourse', 'discourse_')}
        TypeSet = {'automatic_', 'manual_corrected_'}
        path = sys.argv[1]              # by default = ./Entry_processed/CNN_Feature_Py
        featureType = sys.argv[3]
        preposfix = featureType + '_Feature_'
        vectorAddress = "{}/{}lexicon.txt".format(path, preposfix)
        print "loading word vector..."
        U = np.loadtxt(vectorAddress, dtype = "float32")
        print "loading testing vector..."
        vectorAddress = "{}/{}testingDocument.txt".format(path, preposfix)
        DocumentTesting = np.loadtxt(vectorAddress, dtype = "int32")
        print "loading testing entry vector..."
        File3 = "{}/{}testingEntry.txt".format(path, preposfix)
        testingEntry = np.loadtxt(File3, dtype = "int32")
        # print U.shape
        mode= sys.argv[2]
        # word_vectors = sys.argv[2]    
        if mode=="-nonstatic":
                print "model architecture: CNN-non-static"
                non_static=True
        elif mode=="-static":
                print "model architecture: CNN-static"
                non_static=False
        execfile("conv_net_classes.py")
        Times_of_epochs = 5 
        for lexiconType in TypeSet:
                for methodType in fileAddress:
                        print "loading data..."
                        # dumpFileName = "{}/{}/{}{}package.p".format(path, methodType[0], methodType[1], lexiconType)
                        # x = cPickle.load(open(dumpFileName,"rb"))
                        # W, training, testing, testingEntry = x[0], x[1], x[2], x[3]
                        File1 = "{}/{}/{}{}{}training.txt".format(path, methodType[0], preposfix, methodType[1], lexiconType)
                        training = np.loadtxt(File1, dtype = "int32")
                        File2 = "{}/{}/{}{}{}testing.txt".format(path, methodType[0], preposfix, methodType[1], lexiconType)
                        testing = np.loadtxt(File2, dtype = "int32")
                        print "data loaded!"
                        print "{}{} model is being training".format(methodType[1], lexiconType[:-1])   
                        # if word_vectors=="-rand":
                        #         print "using: random vectors"
                        #         U = W2
                        # elif word_vectors=="-word2vec":
                        #         print "using: word2vec vectors"
                        #         U = W

                        # datasets = OrganizeData(training, testing, testingEntry)
                        datasets = [training, testing, testingEntry, DocumentTesting]
                        # print datasets[0].shape
                        # print datasets[1].shape
                        # print datasets[2].shape
                        result_vector = train_conv_net(datasets,
                                                                                  U,
                                                                                  img_w=400, 
                                                                                  lr_decay=0.95,
                                                                                  filter_hs=[3,4,5],
                                                                                  conv_non_linear="relu",
                                                                                  hidden_units=[100,2], 
                                                                                  shuffle_batch=True, 
                                                                                  n_epochs=Times_of_epochs, 
                                                                                  sqr_norm_lim=9,
                                                                                  non_static=non_static,
                                                                                  batch_size=50,
                                                                                  dropout_rate=[0.5])
                        
                        outputFeatureAddress = "./result/{}{}{}testing_{}epochs_Result.txt".format(preposfix, methodType[1], lexiconType, Times_of_epochs)
                        np.savetxt(outputFeatureAddress, result_vector, fmt='%i',)
        print "loading training vector..."
        vectorAddress = "{}/{}trainingDocument.txt".format(path, preposfix)
        DocumentTraining = np.loadtxt(vectorAddress, dtype = "int32")
        datasets = [DocumentTraining, testing, testingEntry, DocumentTesting]
        print "training CNN using whole entry ..."
        Times_of_epochs = 5
        result_vector = train_conv_net(datasets,
                                                                  U,
                                                                  img_w=400, 
                                                                  lr_decay=0.95,
                                                                  filter_hs=[3,4,5],
                                                                  conv_non_linear="relu",
                                                                  hidden_units=[100,2], 
                                                                  shuffle_batch=True, 
                                                                  n_epochs=Times_of_epochs, 
                                                                  sqr_norm_lim=9,
                                                                  non_static=non_static,
                                                                  batch_size=50,
                                                                  dropout_rate=[0.5])
        
        print "loading context training vector..."
        vectorAddress = "{}/{}trainingDocEntry.txt".format(path, preposfix)
        DocumentTraining = np.loadtxt(vectorAddress, dtype = "int32")
        datasets = [DocumentTraining, testing, testingEntry, DocumentTesting]
        print "training CNN using whole context entry ..."
        Times_of_epochs = 5
        result_vector = train_conv_net(datasets,
                                                                  U,
                                                                  img_w=400, 
                                                                  lr_decay=0.95,
                                                                  filter_hs=[3,4,5],
                                                                  conv_non_linear="relu",
                                                                  hidden_units=[100,2], 
                                                                  shuffle_batch=True, 
                                                                  n_epochs=Times_of_epochs, 
                                                                  sqr_norm_lim=9,
                                                                  non_static=non_static,
                                                                  batch_size=50,
                                                                  dropout_rate=[0.5])
                        # results = []
                        # r = range(0,10)    
                        # for i in r:
                        #         datasets = make_idx_data_cv(revs, word_idx_map, i, max_l=56,k=300, filter_h=5)
                        #         perf = train_conv_net(datasets,
                        #                                                   U,
                        #                                                   lr_decay=0.95,
                        #                                                   filter_hs=[3,4,5],
                        #                                                   conv_non_linear="relu",
                        #                                                   hidden_units=[100,2], 
                        #                                                   shuffle_batch=True, 
                        #                                                   n_epochs=25, 
                        #                                                   sqr_norm_lim=9,
                        #                                                   non_static=non_static,
                        #                                                   batch_size=50,
                        #                                                   dropout_rate=[0.5])
                        #         print "cv: " + str(i) + ", perf: " + str(perf)
                        #         results.append(perf)  
                        # print str(np.mean(results))