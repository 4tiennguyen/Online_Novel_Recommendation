import os
import codecs
import json

import torch
from torch import optim
import numpy as np

from algorithms.models_for_fiction_rec.model import NovelNet
from algorithms.models_for_fiction_rec import cumulative_trainer
from algorithms.models_for_fiction_rec import dataset
from common import common_path


class BaseModelForFictionRec:
    """
    base class for fiction recommendation
    """

    def __init__(self, batch_size: int = 1024, epochs: int = 10, embedding_size: int = 128,
                 hidden_size: int = 128, max_session_len: int = 50, attribute_embedding_size: int = 32,
                 features: str = '', top: str = '1,3,5,10,15,20', debug: bool = False, mil: bool = False,
                 mode_loss: bool = False, remove_repeat_mode: bool = False, train: bool = True,
                 evaluation: bool = False, infer: bool = True, analysis: bool = False, analysis_best_epoch: bool = -1,
                 analysis_observe_model: bool = False, analysis_repeat_ratio: bool = False,
                 analysis_predict_best_epoch: bool = False, dot_product: bool = False, encoder_name: str = None,
                 my_method: str = None, remove_mode: bool = False, model_version: str = 'v1', other_args: dict = None):
        self.batch_size = batch_size
        self.epochs = epochs
        self.embedding_size = embedding_size
        self.attribute_embedding_size = attribute_embedding_size
        self.hidden_size = hidden_size
        self.max_session_len = max_session_len
        self.features = [] if features == '' else features.split(',')
        self.top = top
        self.debug = debug
        self.mil = mil
        self.mode_loss = mode_loss
        self.remove_repeat_mode = remove_repeat_mode
        self.train = train
        self.evaluation = evaluation
        self.infer = infer
        self.analysis = analysis
        self.analysis_best_epoch = analysis_best_epoch
        self.analysis_observe_model = analysis_observe_model
        self.analysis_repeat_ratio = analysis_repeat_ratio
        self.analysis_predict_best_epoch = analysis_predict_best_epoch
        self.dot_product = dot_product
        self.encoder_name = encoder_name
        self.my_method = my_method
        self.remove_mode = remove_mode
        self.model_version = model_version
        self.other_args = other_args
        self.load_external_data()

    def load_external_data(self):
        item_popularity_path = os.path.join(common_path.external_data_dir, 'item_popularity.json')
        with open(item_popularity_path) as input_file:
            temp = json.load(input_file)
            item_popularity = {}
            for item_id, popularity in temp.items():
                item_popularity[int(item_id)] = popularity
            self.other_args['item_popularity'] = item_popularity

    def save_meta_data(self):
        meta_data_path = os.path.join(common_path.repeat_aware_rec_base_dir, 'meta_data.json')
        meta_data = {
            'max_feature_index': self.max_feature_index,
            'item_vocab_size': self.item_vocab_size
        }
        with open(meta_data_path, mode='w') as output_file:
            json.dump(meta_data, output_file)

    def load_meta_data(self):
        meta_data_path = os.path.join(common_path.repeat_aware_rec_base_dir, 'meta_data.json')
        with open(meta_data_path) as input_file:
            meta_data = json.load(input_file)
            self.max_feature_index = meta_data['max_feature_index']
            self.item_vocab_size = meta_data['item_vocab_size']

    def fit(self, train, valid):
        """
        优化方向：
        1. 加特征
        2. 优化模型
        :param train:
        :param valid:
        :return:
        """
        print('fit in BasemodelFiction')
        print('--------------dataframe: ')
        print(train.shape)
        print(train)
        print('-------------------------')
        if self.train:
        
            train_dataset = dataset.NovelNetDataset(train, self.max_session_len, 2, debug=self.debug,
                                                     config=self.other_args)

            if self.debug:
                train_dataset.max_feature_index['item_ids'] = 50833

            self.max_feature_index = train_dataset.max_feature_index

            self.item_vocab_size = train_dataset.max_feature_index['item_ids'] + 1

            self.save_meta_data()

            model = NovelNet(self.embedding_size, self.hidden_size, self.item_vocab_size,
                              self.max_feature_index, self.features,
                              self.attribute_embedding_size, self.mil,
                              mode_loss=self.mode_loss, remove_repeat_mode=self.remove_repeat_mode,
                              dot_product=self.dot_product, encoder_name=self.encoder_name,
                              my_method=self.my_method, remove_mode=self.remove_mode,
                              model_version=self.model_version, other_args=self.other_args)
            cumulative_trainer.init_params(model)

            trainer = cumulative_trainer.CumulativeTrainer(model, None, None, None, 4)
            model_optimizer = optim.Adam(model.parameters())
            for i in range(self.epochs):
                trainer.train_epoch('train', train_dataset, dataset.collate_fn, self.batch_size, i, model_optimizer)
                trainer.serialize(i, output_path=common_path.repeat_aware_rec_base_dir)

    def predict_next(self, session_id, input_item_id, predict_for_item_ids, skip=False, mode_type='view', timestamp=0):
        """

        """
        pass

    def history_coverage(self, history_items: list, predicted_items: list):
        """

        :param history_items:
        :param predicted_items:
        :return:
        """
        valid_history_items = set([e for e in history_items if e != 0])
        history_items_in_predicted = [1 if e in predicted_items else 0 for e in valid_history_items]
        result = sum(history_items_in_predicted) / len(valid_history_items)
        return result


    def eval(self, valid, test):
        """

        @param valid:
        @param test:
        @return:
        """
        print('co vo day ko')
        if self.evaluation:
            print('self.eval in BasemodelFiction')

            self.load_meta_data()

            if self.infer:
                print('olala')
                valid_dataset = dataset.NovelNetDataset(valid, self.max_session_len, 3, debug=self.debug,
                                                         config=self.other_args)
                test_dataset = dataset.NovelNetDataset(test, self.max_session_len, 4, debug=self.debug,
                                                        config=self.other_args)

                # 预测
                for i in range(self.epochs):
                    print('epoch', i)
                    file = common_path.repeat_aware_rec_base_dir + 'model/' + str(i) + '.pkl'

                    if os.path.exists(file):
                        print('vo tiep day')
                        model = NovelNet(self.embedding_size, self.hidden_size, self.item_vocab_size,
                                          self.max_feature_index, self.features,
                                          self.attribute_embedding_size, self.mil,
                                          mode_loss=self.mode_loss, remove_repeat_mode=self.remove_repeat_mode,
                                          dot_product=self.dot_product, encoder_name=self.encoder_name,
                                          my_method=self.my_method, remove_mode=self.remove_mode,
                                          model_version=self.model_version, other_args=self.other_args)
                        model.load_state_dict(torch.load(file, map_location='cpu'))
                        trainer = cumulative_trainer.CumulativeTrainer(model, None, None, None, 4)

                        rs = trainer.predict('infer', valid_dataset, dataset.collate_fn, self.batch_size, None, None)
                        base_output_path = common_path.repeat_aware_rec_base_dir + 'result/'
                        if 'evaluation_mode' in self.other_args:
                            print('chac ko vo day')
                            if self.other_args['evaluation_mode'] == 'repeat':
                                base_output_path = base_output_path + 'repeat/'
                            elif self.other_args['evaluation_mode'] == 'new':
                                base_output_path = base_output_path + 'new/'
                            else:
                                raise NotImplementedError(self.other_args['evaluation_mode'])
                        if not os.path.exists(base_output_path):
                            os.makedirs(base_output_path)
                        file = codecs.open(base_output_path + str(i) + '.valid',
                                           mode='w', encoding='utf-8')
                        print("print rs nhaaaaaaaaaaaaaaaa",rs)
                        for data, output in rs:
                            
                            scores, index = output
                            
                            label = data['item_tgt']
                            
                            for j in range(label.size(0)):
                                file.write('[' + ','.join([str(id) for id in index[j, :70].tolist()]) + ']|['
                                           + ','.join([str(id) for id in label[j].tolist()]) + ']|['
                                           + ','.join([str(id) for id in data['mode_label'][j].tolist()]) + ']|['
                                           + ','.join([str(id) for id in data['item_seq'][j].tolist() if id not in (0, 50833)]) + ']'
                                           + os.linesep)
                        file.close()
                        print('toi day chua vai')
                        rs = trainer.predict('infer', test_dataset, dataset.collate_fn, self.batch_size, None, None)
                        file = codecs.open(common_path.repeat_aware_rec_base_dir + 'result/' + str(i) + '.test',
                                           mode='w', encoding='utf-8')
                        file_tien = codecs.open(common_path.repeat_aware_rec_base_dir + 'result/' + str(i) + '.tien',
                                           mode='w', encoding='utf-8')
                        print('rs in test a', rs)
                        for data, output in rs:
                            print('print rs trong for loop:')
                            scores, index = output
                            print('----output:', output)
                            print('----score: ', scores)
                            print('---- index', index)
                            print('-----data', data)
                            label = data['item_tgt']
                            for j in range(label.size(0)):
                                file.write('[' + ','.join([str(id) for id in index[j, :70].tolist()]) + ']|['
                                           + ','.join([str(id) for id in label[j].tolist()]) + ']|['
                                           + ','.join([str(id) for id in data['mode_label'][j].tolist()]) + ']|['
                                           + ','.join([str(id) for id in data['item_seq'][j].tolist() if id not in (0, 50833)]) + ']'
                                           + os.linesep)
                                file_tien.write('[' + ','.join([str(id) for id in index[j,:70].tolist()]) + ']|['
                                            + ','.join([str(id) for id in scores[j,:70].tolist()]) + ']|['        
                                            + ','.join([str(id) for id in label[j].tolist()]) + ']|['
                                            + ','.join([str(id) for id in data['mode_label'][j].tolist()]) + ']|['
                                            + ','.join([str(id) for id in data['item_seq'][j].tolist() if id not in (0, 50833)]) + ']'
                                            + os.linesep)  
                                print('--- tien')  
                        file_tien.close()
                        file.close()
                    ############### Tien 
                        
        
            

            # 评估
            evaluation_modes = ['all', 'repeat', 'new', 'known_repeat', 'known_new',
                                'repeat_contribution', 'new_contribution']
            evaluation_results = {evaluation_mode: {} for evaluation_mode in evaluation_modes}
            for evaluation_mode in evaluation_modes:
                for n in [int(e) for e in self.top.split(',')]:
                    base_output_path = common_path.repeat_aware_rec_base_dir + 'result/'
                    if 'evaluation_mode' in self.other_args:
                        if self.other_args['evaluation_mode'] == 'repeat':
                            print('chac ko vo day 1')
                            base_output_path = base_output_path + 'repeat/'
                        elif self.other_args['evaluation_mode'] == 'new':
                            print('chac ko vo day 2')
                            base_output_path = base_output_path + 'new/'
                        else:
                            raise NotImplementedError(self.other_args['evaluation_mode'])

                    mrr = []
                    recall = []
                    for i in range(self.epochs):
                        valid_scores = []
                        test_scores = []
                        valid_file = os.path.join(base_output_path, "%s.valid" % (str(i)))
                        test_file = os.path.join(base_output_path, "%s.test" % (str(i)))
                        if not os.path.exists(valid_file) or not os.path.exists(test_file):
                            break

                        if os.path.exists(test_file):
                            f = codecs.open(valid_file, mode='r', encoding='utf-8')
                            print('f la  gi :', f)
                            lines = f.readlines()
                            valid_instance_count = 0
                            print('hinh nhu day la valid')
                            for line in lines:
                                candidates, target, mode_label, historical_items = map(json.loads, line.split('|'))
                                historical_items = set(historical_items)
                                candidates_new = [e for e in candidates if e not in historical_items]
                                candidates_consumed = [e for e in candidates if e in historical_items]

                                if (evaluation_mode in ('repeat', 'known_repeat') and mode_label[0] != 1.0) \
                                        or (evaluation_mode in ('new', 'known_new') and mode_label[0] != 0.0):
                                    continue
                                if evaluation_mode == 'known_repeat':
                                    candidates = candidates_consumed
                                if evaluation_mode == 'known_new':
                                    candidates = candidates_new

                                valid_instance_count += 1
                                target = target[0]
                                id = None
                                for k in range(min(n, len(candidates))):
                                    if candidates[k] == target:
                                        id = k + 1
                                        break

                                if (evaluation_mode == 'repeat_contribution' and mode_label[0] != 1.0) \
                                        or (evaluation_mode == 'new_contribution' and mode_label[0] != 0.0):
                                    id = None

                                valid_scores.append(1.0 / id if id else 0)
                            f.close()
                            if i == 1 and n == 1:
                                print('valid_instance_count: %d' % valid_instance_count)

                            f = codecs.open(test_file, mode='r', encoding='utf-8')
                            lines = f.readlines()
                            test_instance_count = 0
                            print('Test neeeeeeeeeeeee')
                            print('Xem thu j trong day-------------------------------------')
                            print(lines)
                            for line in lines:
                                print('*********** xem tung line nha')
                                candidates, target, mode_label, historical_items = map(json.loads, line.split('|'))
                                print( candidates, target, mode_label, historical_items)
                                historical_items = set(historical_items)
                                print('trong historical co j ta',historical_items)
                                candidates_new = [e for e in candidates if e not in historical_items]
                                print('candidates_new', candidates_new)
                                candidates_consumed = [e for e in candidates if e in historical_items]
                                print('candidates_consumed', candidates_consumed)
                                if (evaluation_mode in ('repeat', 'known_repeat') and mode_label[0] != 1.0) \
                                        or (evaluation_mode in ('new', 'known_new') and mode_label[0] != 0.0):
                                    continue
                                if evaluation_mode == 'known_repeat':
                                    candidates = candidates_consumed
                                if evaluation_mode == 'known_new':
                                    candidates = candidates_new

                                test_instance_count += 1
                                target = target[0]
                                print('co gi trong targer[0]')
                                id = None
                                for k in range(min(n, len(candidates))):
                                    if candidates[k] == target:
                                        id = k + 1
                                        break

                                if (evaluation_mode == 'repeat_contribution' and mode_label[0] != 1.0) \
                                        or (evaluation_mode == 'new_contribution' and mode_label[0] != 0.0):
                                    id = None

                                test_scores.append(1.0 / id if id else 0)
                            f.close
                            if i == 1 and n == 1:
                                print('test_instance_count: %d' % test_instance_count)
                        valid_scores = np.array(valid_scores)
                        test_scores = np.array(test_scores)
                        mrr.append((i, sum(valid_scores) / len(valid_scores), sum(test_scores) / len(test_scores)))
                        recall.append((i, np.sum(valid_scores > 0) * 1.0 / len(valid_scores), np.sum(test_scores > 0) * 1.0 / len(test_scores)))
                    evaluation_results[evaluation_mode][n] = [mrr, recall]
            target_results = evaluation_results['all'][1][0]
            best_epoch = -1
            best_valid_score = -1
            for epoch_scores in target_results:
                if epoch_scores[0] == 0:
                    best_epoch = 0
                    best_valid_score = epoch_scores[1]
                else:
                    if epoch_scores[1] > best_valid_score:
                        best_epoch = epoch_scores[0]
                        best_valid_score = epoch_scores[1]
            print('best_epoch: %d' % best_epoch)
            for evaluation_mode in evaluation_modes:
                print('evaluation_mode: %s' % evaluation_mode)
                for n in [int(e) for e in self.top.split(',')]:
                    best_mrr = evaluation_results[evaluation_mode][n][0][best_epoch]
                    best_recall = evaluation_results[evaluation_mode][n][1][best_epoch]
                    print('@%d' % n)
                    print('epoch: %d valid (MRR %.4f, HR %.4f), test (MRR %.4f, HR %.4f)'
                          % (best_epoch, best_mrr[1], best_recall[1], best_mrr[2], best_recall[2]))

        

    def clear(self):
        pass
