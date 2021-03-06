from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import multiprocessing

import tensorflow as tf

flags = tf.flags


# command-line config
flags.DEFINE_string ("data_path",      "data/mimic",          "Data path")
flags.DEFINE_string ("save_file",      "saved/recent.dat",    "Save file")
flags.DEFINE_string ("best_save_file", "",                    "Save file for best validation "
                                                              "losses (empty for save_file)")
flags.DEFINE_string ("load_file",      "",                    "File to load model from")
flags.DEFINE_string ("base_file",      "",                    "File to load base BOW model from "
                                                              "for baseline2grnn")
flags.DEFINE_string ("emb_file",       "",                    "File to load embeddings from")
flags.DEFINE_string ("note_type",      "Discharge_summary",   "The type of notes to consider")
flags.DEFINE_string ("data_storage",   "pickle",              "Format to store data "
                                                              "(shelve or pickle)")
flags.DEFINE_string ("runner",         "",                    "The Runner class to run")
flags.DEFINE_string ("plot_file",      "",                    "File to dump plot info to")
flags.DEFINE_string ("vis_file",       "",                    "File to dump visualization info to")
flags.DEFINE_string ("plot_name",      "",                    "Name for plot info")

flags.DEFINE_integer("batch_size",     32,        "Batch size")
flags.DEFINE_float  ("l1_reg",         0.0,       "L1-regularization scale")
flags.DEFINE_float  ("l2_reg",         0.0,       "L2-regularization scale")
flags.DEFINE_string ("grnn_loss",      "ce",      "ce/l1")
flags.DEFINE_string ("pr_at_k",        "8,24,40", "Compute precision and recall at these values "
                                                  "of k")
flags.DEFINE_bool   ("length_sort",    True,      "Ensure similar note lengths in a batch")
flags.DEFINE_integer("word_emb_size",  192,       "Word embedding size")
flags.DEFINE_integer("label_emb_size", 128,       "Label embedding size (if applicable)")
flags.DEFINE_integer("layers",         20,        "Convolutional layers")
flags.DEFINE_string ("rnn_type",       "gru",     "gru/lstm/entnet")
flags.DEFINE_bool   ("rnn_grnn_size",  False,     "Train RNN with GRNN's number of parameters")
flags.DEFINE_string ("encoder",       "gru",      "gru/attnbow/conv/embs")
flags.DEFINE_string ("readout",       "grnn",     "grnn/lrgrnn/reggrnn/max/mean/hmax/hmean")
flags.DEFINE_bool   ("train_base",     True,      "Train the base model for baseline2grnn")
flags.DEFINE_bool   ("multilayer",     False,     "2-layer RNN. Needs to be true for bidirectional")
flags.DEFINE_bool   ("bidirectional",  False,     "Bidirectional RNN")
flags.DEFINE_bool   ("reconcat_input", True,      "Concatenate the input to the first layer output "
                                                  "for multilayer")
flags.DEFINE_bool   ("positive_diag",  False,     "Ensure positive diagonal in semidiagonal GRNN")
flags.DEFINE_bool   ("biased_sigmoid", True,      "Biased re-sigmoid for GRNN output")
flags.DEFINE_bool   ("g_to_h_block",   True,      "Enable grounded to controller projection.")
flags.DEFINE_bool   ("detach_g_to_h",  False,     "Stop gradients from controller to grounded.")
flags.DEFINE_bool   ("sliced_grnn",    False,     "Sliced GRNN")
flags.DEFINE_integer("sliced_labels",  256,       "Number of sliced labels")
flags.DEFINE_bool   ("sample_uniform", False,     "Sample negative labels uniformly for "
                                                  "sliced GRNN")
flags.DEFINE_float  ("dropout",        0.0,       "GRNN dropout from concepts to control")
flags.DEFINE_string ("lstm_hidden",    "ch",      "c, h, ch")
flags.DEFINE_bool   ("normlstm_mem",   False,     "One dim per concept for normlstm")
flags.DEFINE_bool   ("diagonal_cell",  True,      "Diagonal weights in GRNN cells")
flags.DEFINE_integer("num_blocks",     8,         "Number of blocks for EntNet")
flags.DEFINE_integer("hidden_size",    128,       "Hidden size for RNN")
flags.DEFINE_integer("latent_size",    128,       "Latent label space size for grounded RNN")
flags.DEFINE_string ("grnn_summary",   "sigmoid", "sigmoid/cosine/softmax/scale/fixed")
flags.DEFINE_integer("grnn_fixedsize", 2,         "Number of dims to look at for each label")
flags.DEFINE_bool   ("train_embs",     True,      "Train word embeddings")
flags.DEFINE_bool   ("use_attention",  True,      "Use attention where optional")
flags.DEFINE_float  ("lm_weight",      0.0,       "Language modeling objective weight")
flags.DEFINE_integer("attn_window",    5,         "The span of words to determine score for "
                                                  "attention")
flags.DEFINE_bool   ("attn_on_dims",   True,      "Apply attention on each dimension individually")
flags.DEFINE_bool   ("sigmoid_attn",   False,     "Use sigmoid instead of softmax for attention")
flags.DEFINE_bool   ("curriculum",     False,     "Increase max note length as training progresses")
flags.DEFINE_bool   ("random_chop",    False,     "Randomly chop off notes during training")
flags.DEFINE_integer("len_start",      50,        "Starting note length for curriculum")
flags.DEFINE_float  ("len_multiply",   0.35,      "Fraction of note length to increase by on each "
                                                  "epoch for curriculum")
flags.DEFINE_integer("max_note_len",   4000,      "Maximum note length. -1 to disable")
flags.DEFINE_integer("max_dgn_labels", 500,       "Diagnoses vocabulary for labels. -1 for default")
flags.DEFINE_integer("max_pcd_labels", 0,         "Procedures vocabulary for labels. "
                                                  "-1 for default")
flags.DEFINE_integer("test_labels",    -1,        "If positive, compute stats on these many top "
                                                  "labels (for debugging)")
flags.DEFINE_string ("optimizer",      "adam",    "Optimizer to use (sgd, adam, adagrad, adadelta)")
flags.DEFINE_float  ("max_grad_norm",  5.0,       "Maximum gradient norm for clipping")
flags.DEFINE_float  ("learning_rate",  1e-3,      "Optimizer initial learning rate")
flags.DEFINE_integer("threads",        -1,        "Maximum number of threads/subprocesses. -1 to "
                                                  "automatically determine")
flags.DEFINE_integer("epochs",         -1,        "Number of training+val epochs. -1 for no limit, "
                                                  "0 to skip to testing.")
flags.DEFINE_integer("max_steps",      -1,        "Max steps per epoch (for debugging)")
flags.DEFINE_float  ("best_score",     0.0,       "Initial best score (for resuming from a "
                                                  "best_save_file)")
flags.DEFINE_integer("sanity_epoch",   -1,        "Epoch to sanity check loss at. -1 to disable.")
flags.DEFINE_float  ("sanity_min",     0.33,      "Minimum loss at sanity epoch to not quit")
flags.DEFINE_float  ("sanity_max",     1.0,       "Maximum loss at sanity epoch to not quit")
flags.DEFINE_bool   ("early_stop",     True,      "Stop early if validation loss stops improving")
flags.DEFINE_bool   ("macro_auc",      False,     "Compute macro-averaged AUCs (slow)")
flags.DEFINE_integer("min_epochs",     20,        "Minimum number of epochs before early stopping")
flags.DEFINE_float  ("stop_increment", 1.25,      "Increase early stop target by this when new "
                                                  "best validation")
flags.DEFINE_float  ("keep_vocab",     0.97,      "Fraction of data for vocab to cover")
flags.DEFINE_float  ("train_split",    0.9,       "Fraction of patients for training. "
                                                  "test = 1 - train - val")
flags.DEFINE_float  ("val_split",      0.033,     "Fraction of patients for validation. "
                                                  "test = 1 - train - val")
flags.DEFINE_float  ("train_fraction", 1.0,       "Fraction of training data to use for training "
                                                  "(for debugging)")
flags.DEFINE_integer("print_every",    50,        "Print every these many steps")
flags.DEFINE_integer("save_every",     500,       "Save every these many steps (0 to disable)")
flags.DEFINE_bool   ("save_overwrite", True,      "Overwrite the same save file each time")
flags.DEFINE_bool   ("visualize",      False,     "Run visualizations")
flags.DEFINE_string ("query",          "",        "Query for visualization")

flags.DEFINE_bool   ("bow_stopwords",  False,     "Allow stopwords in stat BOW model")
flags.DEFINE_bool   ("bow_log_tf",     True,      "Sublinear term frequencies for stat BOW model")
flags.DEFINE_string ("bow_norm",       "",        "Normalize BOW vectors, can be 'l1' or 'l2'")
flags.DEFINE_bool   ("bow_search",     False,     "Search for optimal BOW hyperparameters")
flags.DEFINE_string ("bow_hpfile",     "",        "File containing optimal BOW hyperparameters")


class Config(object):
    '''This class encapsulates all the configuration for the model.'''

    def __init__(self, from_cmd_line=True, verbose=True):
        self.dict = {}
        if from_cmd_line:
            if verbose:
                print('Config:')
            flags.FLAGS._parse_flags()
            if verbose:
                maxlen = max(len(k) for k in flags.FLAGS.__dict__['__flags'])

            # copy flag values to attributes of this Config object
            for k, v in sorted(flags.FLAGS.__dict__['__flags'].items(), key=lambda x: x[0]):
                self.dict[k] = v
                if verbose:
                    print(k.ljust(maxlen + 2), v)
            if verbose:
                print()
            self.pr_at_k = [int(k) for k in self.pr_at_k.split(',')]
            if self.threads == -1:
                self.threads = multiprocessing.cpu_count() - 1
                if self.threads < 1:
                    self.threads = 1
                if verbose:
                    print('Setting threads to', self.threads)
                    print()

    def __getattr__(self, name):
        try:
            return self.dict[name]
        except KeyError:
            raise AttributeError
