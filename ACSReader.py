from glob import glob
import pandas as pd
from warnings import warn

import xml.etree.ElementTree as et
import os
import shutil
import requests
import zipfile


class Reader():
    def __init__(self, path=None, target=None):

        self.path = path
        self.file_paths = None

        # create the dataframe
        self.data_frame = None
        self.device_frame = None
        self.labels = []

        # set targets
        self._allowed_targets = ['freq',
                                 'phAngle',
                                 'power',
                                 'reacPower',
                                 'rmsCur',
                                 'rmsVolt']

        if target is not None:
            # allowed_targets target values
            if isinstance(target, str):
                self.targets = [target]
            else:
                self.targets = list(target)

            is_allowed = self._check_target_value()
            if not all(is_allowed):
                self.targets = self._allowed_targets
                warn(f"One of the targets given is not an allowed target.\n Setting the default: {self._allowed_targets}")
        else:
            self.targets = self._allowed_targets
            warn("No targets set. Creating pd.DataFrame for all possible variables.")

    @staticmethod
    def create_signature_dataset(data_frame):
        """

        Creating a dataframe with the shape (n_samples, n_features),
        where the index is the label and the column name the feature name

        :param data_frame: dataframe to convert (advised to create this input using this reader)
        :return: dataframe of signatures
        """
        if data_frame is None:
            raise ValueError("No Data found.")

        ids = set([int(i.split('_')[-1]) for i in data_frame.index])

        signature_df = pd.DataFrame()

        for id in ids:
            tmp = data_frame[data_frame.index.str.endswith(f'_{id}')]
            label = tmp['label'].values[0]
            tmp_T = tmp.transpose().dropna().drop(labels='label')
            tmp_T.columns = [i.split('_')[0] for i in tmp_T.columns]
            tmp_T.index = [label] * len(tmp_T.index)
            signature_df = signature_df.append(tmp_T)

        return signature_df

    @staticmethod
    def create_intersession_protocol(data_frame):
        """

        Creating the train and test dataframe according to the intersession protocol.

        :return: DataFrame Train, DataFrame Test
        """

        df_train = data_frame[data_frame.index.str.contains('_1_')]
        df_test = data_frame[data_frame.index.str.contains('_2_')]

        return df_train, df_test

    def download_data(self, version, save_dir='.', unzip=False, keep_zip=True):
        chunk_size = 128
        save_path = save_dir + "/ACS-F{}.zip".format(version)

        if os.path.exists(save_path):
            warn("The requested dataset exists already.")
        else:
            url = "https://icosys.ch/wp-content/uploads/datasets/ACS-F{}.zip".format(version)
            r = requests.get(url, stream=True)
            with open(save_path, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    fd.write(chunk)

            if unzip:
                with zipfile.ZipFile(save_path, 'r') as zip_ref:
                    zip_ref.extractall(save_dir)
                # I am super unhappy about this...but mac creates this folder, when unzipping and I can't suppress that
                if os.path.exists(save_dir + "/__MACOSX"):
                    shutil.rmtree(save_dir + "/__MACOSX")

            if not keep_zip and unzip:
                os.remove(save_path)

    def _check_target_value(self):
        return [x in self._allowed_targets for x in list(self.targets)]

    def set_file_paths(self, path):
        file_paths = glob(f'{path}/*/*/*.xml')
        if not file_paths:
            raise ValueError(
                "No .xml files found under this path. Please be sure to provide the correct path to the ACS-F2 files")
        self.file_paths = file_paths

    def set_targets(self, target):
        if isinstance(target, str):
            self.targets = [target]
        else:
            self.targets = list(target)

        is_allowed = self._check_target_value()
        if not all(is_allowed):
             raise ValueError(f"One of the targets given is not allowed. Please only use: {self._allowed_targets}")

    def to_csv(self, path, name):
        self.data_frame.to_csv(path + '/' + name)

    def create_label_dict(self):
        if self.data_frame is None:
            raise ValueError("No Data found.")

        label_dict = {}
        for i, k in enumerate(self.data_frame['label'].unique()):
            label_dict[k] = int(i)

        return label_dict

    def create_dataframe(self, path=None):
        device = []
        device_values = {}
        device_id = 0

        if path is None:
            warn(f"No path to dataset given.")
            if self.file_paths is None:
                raise ValueError("No .xml found")
        else:
            self.set_file_paths(path)

        for file in self.file_paths:
            tree = et.parse(file)

            for machine in tree.iter('targetDevice'):
                device.append(machine.attrib)

            label = machine.attrib['type']

            try:
                model = machine.attrib['model']
            except KeyError:
                model = "N/A"

            session = [r.attrib for r in tree.iter('acquisitionContext')][0]['session']

            for element in tree.iter('signalPoint'):
                element_item = element.attrib.items()
                for k, v in element_item:
                    if k in self.targets:
                        key = "{}_{}_{}_{}_{}".format(k, label, model, session, device_id)
                        try:
                            v = float(v)
                        except ValueError:
                            continue
                        if key in device_values:
                            device_values[key].append(v)
                        else:
                            self.labels.append(label)
                            device_values[key] = [v]

            device_id += 1

        data_frame = pd.DataFrame.from_dict(device_values, orient='index')
        data_frame['label'] = self.labels
        device_frame = pd.DataFrame(device)

        return data_frame, device_frame


if __name__ == '__main__':
    test1 = Reader(target=['phAngle', 'power', 'reacPower', 'rmsCur'])
    # test1.load_data(version=2, unzip=True, keep_zip=False)
    test1.create_dataframe(path='../../data/ACSF2/original/Dataset/*/*.xml')
    df_train, df_test = test1.create_intersession_protocol()
    df_train_sig = test1.create_signature_set(df_train)
    # test1.to_csv(path='.', name='ACSFReacPower.csv')
