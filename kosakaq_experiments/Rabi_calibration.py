import copy
import random
import time
import json
from qiskit.providers.jobstatus import JobStatus
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
 #グラフの描画のためのインポート
import sys
sys.path.append("..")
import matplotlib.pyplot as plt  #ここイランかも
import numpy as np
from exceptions import RabiCalibrationError, KosakaQRabicalibrationError
from kosakaq_backend import KosakaQBackend
from kosakaq_job import KosakaQExperimentJob

import requests



class Rabi_calibration():
    def __init__(self, backend: KosakaQBackend):
        self.backend = backend
        self.mode = None
        self.job_num = 0
        self.job = []
        self.mode = []
        self.calibration = []
        self.result = []


    
    def run(self, start, stop, Amp):  # 大輔が作ります
        """
        mode: Ey or E1E2 or all
        どの周りのスペクトルを取るか選べる。
        """
        
        access_token = self.backend.provider.access_token
        self.result.append([])   # Rabi_project20_E6EL06_area06_NV04_PLE_all_0.txtの内容が入ったlistを返します。
        data = "Rabi " + str(start) + " " + str(stop) + " " + str(Amp)
        kosakaq_json ={
                'experiment': 'experiment',
                'data': data,
                'access_token': access_token,
                'repetitions': 1,
                'backend': self.backend.name,
        }
        header = {
            "Authorization": "token " + access_token,
        }
        res = requests.post("http://192.168.11.85/job/", data=kosakaq_json, headers=header)
        response = res.json()
        print(response)
        res.raise_for_status()
        self.job.append(KosakaQExperimentJob(self.backend, response['id'], access_token=self.backend.provider.access_token, qobj=data))
        self.job_num += 1  # 発行したjobの数
        self.flag.append({})  # 各種Flag
        self.flag[-1]["get_result"] = False
        self.flag[-1]["calibration"] = False
        self.flag[-1]["fitting"] = False
        return self.job[-1]  # result[0]=frequencyのlist, result[1]=count（縦軸), result[2] = エラーバーのlist
    

    def jobs(self):
        if self.job_num == 0:
            print("There is no job.")
        else:
            for i in range(self.job_num):
                if self.flag[i]["get_result"] == False:
                    print("job",i+1,"... ","mode: ",self.mode[i], " get_result: not yet")
                else:
                    print("job",i+1,"... ","mode: ",self.mode[i], " get_result: done")
             

    # author: Goto Kyosuke and Daisuke Ito
    def get_result(self, job_num = 0):  # job_num = 0にすることで、使うとき job_num-1 = -1 となり、最新のが使える。
        """
        This function gets results of Red-raser calibration.
        """
        if job_num > self.job_num or job_num < 0 or not( type(job_num) == int ):
            raise KosakaQRabicalibrationError
        
        if self.flag[-1]["get_result"] == True:
            print("Already executed")
                        
        self.result[job_num-1] = self.job[job_num-1].result()
        
        self.flag[job_num-1]["get_result"] = True
        
        # result[job_num-1][0]=frequencyのlist, result[job_num-1][1]=count（縦軸), result[job_num-1][2] = エラーバーのlist
        return self.result[job_num-1]
        
        # result[job_num-1][0]=frequencyのlist, result[job_num-1][1]=count（縦軸), result[job_num-1][2] = エラーバーのlist



    # author: Mori Yugo　#rabi用に変更が必要
    def draw(self, fitting=False, error=0, save=False, job_num = 0):
        """
        This function draws photoluminescence excitation (PLE).
        
        fitting: True or false
            フィッティングするか選ぶ
        error: 0, 1, 2 or 3
            1.範囲をエラーバーとするグラフを表示
            2.標準偏差をエラーバーとするグラフを表示
            3.標準誤差をエラーバーとするグラフを表示
        save: True or false
            Ey, E1E2を保存するか選べる
        """
        if job_num > self.job_num or job_num < 0 or not( type(job_num) == int ):   #get resultにデータがあるか
            raise KosakaQRabicalibrationError
        
        if self.mode[job_num-1] == None:   # runをまだ実行してなかったら(self.mode == None)、エラーを返す。（これは最初でやるべき？）
            raise KosakaQRabicalibrationError("Run function is not done.")
        
        if fitting == True:   # optionでfittingするか選べる ← fitingのlistには_make_fittingメソッドを使って下さい。
            self._make_fitting(job_num)
            fre_y = self._make_fitting(job_num)   # 縦軸の値
        
        cou_x = copy.deepcopy[self.result[job_num - 1][1]]  # 横軸の値
        # optionでエラーバーいれるか選べる。
        # 参考文献: https://dreamer-uma.com/errorbar-python/
        fre_y_mean = np.array(fre_y.mean())   # 各点を平均値とする
        if error == 1:   # 範囲をエラーバーとしたグラフ
            fre_yerr_scope = np.array(fre_y.max() - fre_y.min())   #データの範囲
            fig, ax = plt.subplots()
            ax.plot(cou_x, fre_y, marker='o')
            ax.errorbar(cou_x, fre_y_mean, fre_yerr=fre_yerr_scope)
            ax.set_title('PLE - error bar: scope')
        elif error == 2:   # 標準偏差をエラーバーとしたグラフ
            fre_yerr_sd = np.array(fre_y.std())   #標準偏差
            fig, ax = plt.subplots()
            ax.plot(cou_x, fre_y, marker='o')
            ax.errorbar(cou_x, fre_y_mean, fre_yerr=fre_yerr_sd)
            ax.set_title('PLE - error bar: SD')
        elif error == 3:   # 標準誤差をエラーバーとしたグラフ
            fre_yerr_se = np.array(fre_y.std() / np.sqrt(len(fre_y)))   #標準偏差
            fig, ax = plt.subplots()
            ax.plot(cou_x, fre_y, marker='o')
            ax.errorbar(cou_x, fre_y_mean, fre_yerr=fre_yerr_se)
            ax.set_title('PLE - error bar: SE')
        ax.set_xlabel('count')
        ax.set_xlabel('frequency')
        plt.show()
        
        if save == True:   # optionで保存するか選べる。(保存とは何の保存を意味しているのか？)
            self.save(job_num)



    def save(self, job_num = 0):  # jsonにE1とExEy保存する。
        if job_num > self.job_num or job_num < 0 or not( type(job_num) == int ):
            raise KosakaQRabicalibrationError
        if self.flag[job_num-1]["calibration"] == False:
            raise KosakaQRabicalibrationError
        try:
            with open("calibration_data.json", "r") as json_file:
                json_data = json.load(json_file)
        except:
            json_data = {}
            json_data["red"] = {}
        if self.mode[job_num-1] == "Ey" or self.mode[job_num-1] == "all":
            json_data["red"]["Ey"] = self.calibration[job_num-1]["Ey"]
        if self.mode[job_num-1] == "E1E2" or self.mode[job_num-1] == "all":
            json_data["red"]["E1E2"] = self.calibration[job_num-1]["E1E2"]
        with open("calibration_data.json", "w") as json_file:
            json.dump(json_data,json_file)



    # author: Ebihara Syo
    def _make_fitting(self, job_num = 0):
        
        if self.mode[job_num - 1] == None:  # runを実行してなかった場合
            raise KosakaQRabicalibrationError('runが実行されていません')
            
        elif self.mode[job_num - 1] == "rabi":
            T = copy.deepcopy[self.result[job_num - 1][0]]  # 横軸の値
            Y = copy.deepcopy[self.result[job_num - 1][1]]  # 縦軸の値
            
            #フィッティング関数の初期値　beta
            beta = np.array([300, 300])
            tolerance =  1e-4
            epsilon = 1e-4
            
            delta = 2*tolerance
            alpha = 1
            while np.linalg.norm(delta) > tolerance:
                F = Y-beta[0]*(1-np.cos(beta[1]*T))
                J = np.zeros((len(F), len(beta)))  # 有限差分ヤコビアン
                for jj in range(0, len(beta)):
                    dBeta = np.zeros(beta.shape)
                    dBeta[jj] = epsilon
                    J[:, jj] = (Y-(beta[0]+dBeta[0])*(1-np.cos((beta[1]+dBeta[1])*T))-F)/epsilon
                delta = -np.linalg.pinv(J).dot(F)  # 探索方向
                beta = beta + alpha*delta
            
            # Y2はフィッティング後の縦軸のリスト
            Y2 = beta[0](1-np.cos(beta[1]*T))
            return Y2
        
        