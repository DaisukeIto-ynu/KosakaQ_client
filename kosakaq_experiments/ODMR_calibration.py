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
from exceptions.exceptions import ODMRCalibrationError, KosakaQODMRcalibrationError
from KosakaQbackend import KosakaQbackend
from job.job_monitor import job_monitor
from scipy.optimize import curve_fit

class ODMR_calibration():
    def __init__(self, backend: KosakaQbackend):
        self.backend = backend
        self.mode = None
        self.job_num = 0
        self.job = []
        self.mode = []
        self.calibration = []
        self.result = []
    
    def run(self, mode):  # 大輔が作ります
        """
        mode: Ey or E1E2 or all
        どの周りのスペクトルを取るか選べる。
        """
        self.result.append([])   # Rabi_project20_E6EL06_area06_NV04_PLE_all_0.txtの内容が入ったlistを返します。
        # self.power = []  #周波数 vs.laser_power
        if not(mode == "Ey" or mode == "E1E2" or mode == "all"):
            raise KosakaQODMRcalibrationError('choose mode from "Ey" or "E1E2" or "all"')
        self.job.append(self.backend.run("red"+mode))
        self.job_num += 1  # 発行したjobの数
        self.mode.append(mode)
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
             

    def get_result(self, job_num = 0):  # job_num = 0にすることで、使うとき job_num-1 = -1 となり、最新のが使える。
        """
        This function gets results of Red-raser calibration.
        """
        if job_num > self.job_num or job_num < 0 or not( type(job_num) == int ):
            raise KosakaQODMRcalibrationError
        
        if self.flag[-1]["get_result"] == True:
            print("Already executed")
        
        # job_status確認して表示
        nowstatus = self.job[job_num-1].status()
        print(nowstatus.value)
        
        # status:queuedだったら、何番目か表示して、このまま待つか聞いて、待つようだったらjob monitor表示
        if nowstatus == JobStatus.QUEUED:
            print("You're job number is ",self.job[job_num-1].queue_position())
            ans = input("Do you wait? y/n:")
            if ans == "y" or "yes":
                job_monitor()
            else:
                raise KosakaQODMRcalibrationError
                
        while (not (self.job[job_num-1].status() == JobStatus.DONE)):
            if nowstatus == JobStatus.DONE: # status:doneだったら/なったら、result取ってくる。
                result = self.job[job_num-1].result() #resultはResultクラスのインスタンス
            time.sleep(random.randrange(8, 12, 1))
        
        self.flag[job_num-1]["get_result"] = True
        
        self.result[job_num-1].append(result._get_experiment())
        
        return result._get_experiment()
        
        # result[job_num-1][0]=frequencyのlist, result[job_num-1][1]=count（縦軸), result[job_num-1][2] = エラーバーのlist


    def draw(self, fitting=False, error=0, save=False, job_num = 0):#書き換えが必要
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
            raise KosakaQODMRcalibrationError
        
        if self.mode[job_num-1] == None:   # runをまだ実行してなかったら(self.mode == None)、エラーを返す。（これは最初でやるべき？）
            raise KosakaQODMRcalibrationError("Run function is not done.")
        
        if fitting == True:   # optionでfittingするか選べる ← fitingのlistには_make_fittingメソッドを使って下さい。
            self._make_fitting(job_num)
            cou_y = self._make_fitting(job_num)   # 縦軸の値
        
        fre_x = copy.deepcopy[self.result[job_num - 1][1]]  # 横軸の値
        # optionでエラーバーいれるか選べる。
        # 参考文献: https://dreamer-uma.com/errorbar-python/
        
            if error == 1:  # 範囲をエラーバーとしたグラフ
                cou_yerr_scope = np.array(cou_y.max() - cou_y.min())   #データの範囲
                fig, ax = plt.subplots()
                ax.plot(fre_x, cou_y, marker='o')
                ax.errorbar(peak_x[j], peak_y[j], cou_yerr=cou_yerr_scope)
                ax.set_title('PLE - error bar: scope')
            elif error == 2:   # 標準偏差をエラーバーとしたグラフ
                cou_yerr_sd = np.array(cou_y.std())   #標準偏差
                fig, ax = plt.subplots()
                ax.plot(fre_x, cou_y, marker='o')
                ax.errorbar(peak_x[j], peak_y[j], cou_yerr=cou_yerr_sd)
                ax.set_title('PLE - error bar: SD')
            elif error == 3:   # 標準誤差をエラーバーとしたグラフ
                cou_yerr_se = np.array(cou_y.std() / np.sqrt(len(cou_y)))   #標準偏差
                fig, ax = plt.subplots()
                ax.plot(fre_x, cou_y, marker='o')
                ax.errorbar(peak_x[j], peak_y[j], cou_yerr=cou_yerr_se)
                ax.set_title('PLE - error bar: SE')
        ax.set_xlabel('count')
        ax.set_xlabel('frequency')
        plt.show()
        
        if Ey == True:   # optionでE1E2,Eyの中心値を表示するか選べる。 ← 中心値にはcalibrationメソッドを使ってください。
            self.calibration(job_num)
        if E1E2 == True:
            self.calibration(job_num)
        
        if save == True:   # optionで保存するか選べる。(保存とは何の保存を意味しているのか？)
            self.save(job_num)
        
        # その他、optionを入れる。optionは引数にするが、あくまでoptionなので、選ばなくても良いようにする。
    
    
    def save(self, job_num = 0):  # jsonにE1とExEy保存する。
        if job_num > self.job_num or job_num < 0 or not( type(job_num) == int ):
            raise KosakaQODMRcalibrationError
        if self.flag[job_num-1]["calibration"] == False:
            raise KosakaQODMRcalibrationError
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
    def _make_fitting(self, job_num = 0):#書き換えが必要(ガウシアンでフィッティング)
        #fitingのlistを返す
        #runをまだ実行してなかったら(self.mode == None)、エラーを返す。
        
        if self.mode[job_num - 1] == None:  # runを実行してなかった場合
            raise KosakaQODMRcalibrationError('runが実行されていません')
            
        fre_x2 = copy.deepcopy[self.result[job_num - 1][0]]  # 横軸全体の値
        cou_y2 = copy.deepcopy[self.result[job_num - 1][1]]  # 縦軸全体の値
        
        def func2(x, *params):
            y = np.zeros_like(fre_x2)
            amp=params[0]
            ctr=params[1]
            wid=params[2]
            y = amp*np.exp(-((x - ctr)/wid)**2)
            y_sum = y + params[-1]
            return y_sum
        
        #初期値のリストを作成
        #[a,b,c]
        guess = []
        guess.append([-0.8,0.21,0.05]) #真値と少しずらす
        
        #バックグラウンドの初期値
        bias = np.mean(cou_y2) #データ平均値を使用
        
        #初期値リストの結合
        guess_total = []
        for i in guess:
            guess_total.extend(i)
        guess_total.append(bias) #初期値リスト名
        
        popt, pcov = curve_fit(func2, fre_x2, cou_y2, p0=guess_total)
        fit = func2(fre_x2, *popt)
        return fit

    