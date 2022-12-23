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
from exceptions.exceptions import RedCalibrationError, KosakaQODMRcalibrationError
from KosakaQbackend import KosakaQbackend
from job.job_monitor import job_monitor

class ODMR_calibration():
    def __init__(self, backend: KosakaQbackend):
        self.backend = backend
        self.mode = None
        self.job_num = 0
        self.job = []
        self.mode = []
        self.calibration = []
        self.result = []
    
    
    def run(self, start, stop, HighPower = False):  # 大輔が作ります
        """
        mode: Ey or E1E2 or all
        どの周りのスペクトルを取るか選べる。
        """
        
        access_token = self.backend.provider.access_token
        self.result.append([])   # Rabi_project20_E6EL06_area06_NV04_PLE_all_0.txtの内容が入ったlistを返します。
        if HighPower == False:
            data = "ODMR " + str(start) + " " + str(stop) + " " + str(8947) + " " + str(0.001)
        elif HighPower == True:
            data = "ODMR " + str(start) + " " + str(stop) + " " + str(21) + " " + str(0.5)
        else:
            raise KosakaQODMRcalibrationError("argument HighPower must be bool")
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



    def draw(self, fitting=False, error=0, Ey=False, E1E2=False, save=False, job_num = 0):#書き換えが必要
        """
        This function draws photoluminescence excitation (PLE).
        
        fitting: True or false
           フィッティングするか選ぶ
        error: 0, 1, 2 or 3
           1.範囲をエラーバーとするグラフを表示
           2.標準偏差をエラーバーとするグラフを表示
           3.標準誤差をエラーバーとするグラフを表示
        Ey: True or false
           Eyの中心値を表示するか選ぶ
        E1E2: True or false
           E1E2の中心値を表示するか選ぶ
        save: True or false
           Ey, E1E2を保存するか選べる
        """
        if job_num > self.job_num or job_num < 0 or not( type(job_num) == int ):   #get resultにデータがあるか
            raise KosakaQRedcalibrationError
        
        if self.mode[job_num-1] == None:   # runをまだ実行してなかったら(self.mode == None)、エラーを返す。（これは最初でやるべき？）
            raise KosakaQRedcalibrationError("Run function is not done.")
        
        if fitting == True:   # optionでfittingするか選べる ← fitingのlistには_make_fittingメソッドを使って下さい。
            self._make_fitting(job_num)
            cou_y = self._make_fitting(job_num)   # 縦軸の値
        elif self.mode[job_num - 1] == "Ey":
            peak_x[0] = Ey
            peak_x[1]= Ey
        elif self.mode[job_num - 1] == "E1E2":
            peak_x[0] = E1E2
            peak_x[1] = E1E2
        elif self.mode[job_num - 1] == "all":
            peak_x[0] = E1E2
            peak_x[1] = Ey
        
        fre_x = copy.deepcopy[self.result[job_num - 1][1]]  # 横軸の値
        # optionでエラーバーいれるか選べる。
        # 参考文献: https://dreamer-uma.com/errorbar-python/
        
        if peak[0] == peak[1]:
            i = 1
        else:
            i =2
        for j in range(i):
            if error == 1:   # 範囲をエラーバーとしたグラフ
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
    
    
    # author: Mori Yugo
    # def laser_draw(self, fitting=False, Ey=False, E1E2=False, save=False, job_num = 0):
    #     # optionでfittingするか選べる ← fitingのlistはこちらは簡単だと思うので、自分で作って下さい。
    #     # optionで保存するか選べる。
    #     # その他、optionを入れる。optionは引数にするが、あくまでoptionなので、選ばなくても良いようにする。
    #     if self.mode == None:   # runをまだ実行してなかったら(self.mode == None)、エラーを返す。（これは最初でやるべき？）
    #         raise KosakaQRedcalibrationError("Run function is not done.")


    # author: Honda Yuma
    def calibration(self, job_num = 0):  # E1E2とEyのキャリブレーション結果を返す ← E1E2は二つの頂点のちょうど中心を取る。Eyは_make_fittingのself.x0を返す。
        # runをまだ実行してなかったら(self.mode == None)、エラーを返す。
        # 結果は　self.calibration[job_num-1]に辞書で入れる。例）[{E1E2:470.0678453678},{E1E2:470.0034567, Ey:470.145678}]
        pass

    

    def calibration(self, job_num = 0):
        """
        Parameters
        ----------
        job_num : TYPE, optional
            DESCRIPTION. The default is 0.

        Returns
        -------
        None.

        """
        list1 = copy.deepcopy(self.result[job_num-1][0])#周波数（横軸）
        list2 = copy.deepcopy(self.result[job_num-1][1])#光子数（縦軸）
        list3 = copy.deepcopy(self.result[job_num-1][2])#エラーバー
        list4 = list()#傾き代入用の空のリスト作成
        if self.mode[job_num-1] == "E1E2":#二つの頂点のちょうど中心を取る
            i = 0#whileのためのカウント用i
            while i<= 91:#101個なので91まで
                
                x = np.array(list1)#numpyのarrayにリストを入れる,arrayだとベクトルになる。
                y = np.array(list2)#xと同様

                def katamuki(x, y):#傾きを求める関数
                    n = 10#10こ区切り
                    a = ((np.dot(x[i:i+n-1], y[i:i+n-1])- y[i:i+n-1].sum() * x[i:i+n-1].sum()/n)/
                         ((x[i:i+n-1] ** 2).sum() - x[i:i+n-1].sum()**2 / n))#スライシングで10個分の最小二乗法による傾き
                    b = (y[i:i+n-1].sum() - a * x[i:i+n-1].sum())/n#切片（不要）
                    return a, b

                a, b = katamuki(x, y)#a,bに傾きと切片代入
                list4.append(a)#リストに傾き代入
                i = i+1#カウント＋１する
            for #list4回して、マイナスになったインデックスから極地のHzのためのインデックスを求める
                
        elif self.mode[job_num-1] == "all"
            i = 0#whileのためのカウント用i
            while i<= 491:#501個なので491まで
                
                x = np.array(list1)#numpyのarrayにリストを入れる
                y = np.array(list2)#xと同様

                def katamuki(x, y):#傾きを求める関数
                    n = 10#10こ区切り
                    a = ((np.dot(x[i:i+n-1], y[i:i+n-1])- y[i:i+n-1].sum() * x[i:i+n-1].sum()/n)/
                         ((x[i:i+n-1] ** 2).sum() - x[i:i+n-1].sum()**2 / n))#スライシングで10個分の最小二乗法による傾き
                    b = (y[i:i+n-1].sum() - a * x[i:i+n-1].sum())/n#切片（不要）
                    return a, b

                a, b = katamuki(x, y)#a,bに傾きと切片代入
                list4.append(a)#リストに傾き代入
                i = i+1#カウント＋１する
        elif self.mode[job_num-1] == "Ey":
            #Eyは_make_fittingのself.x0を返す。
        else:
            print("error")
        #list1,2,3で頂点の探し方を考える。範囲絞っての最大値or極値
        
        # runをまだ実行してなかったら(self.mode == None)、エラーを返す。
        
        pass
    
    

    def save(self, job_num = 0):  # jsonにE1とExEy保存する。
        if job_num > self.job_num or job_num < 0 or not( type(job_num) == int ):
            raise KosakaQRedcalibrationError
        if self.flag[job_num-1]["calibration"] == False:
            raise KosakaQRedcalibrationError
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
        #E1,E2はエラーを返す
        #Eyについてのfitingのlistを返す（ローレンチアン）、x0とγをself.x0とself.gammaに代入
        #runをまだ実行してなかったら(self.mode == None)、エラーを返す。
        
        if self.mode[job_num - 1] == None:  # runを実行してなかった場合
            raise KosakaQRedcalibrationError('runが実行されていません')
            
        elif self.mode[job_num - 1] == "E1E2":  # E1_E2の場合
            raise KosakaQRedcalibrationError('E1E2です')
            
        elif self.mode[job_num - 1] == "Ey":  # Eyの場合
            fre_y1 = copy.deepcopy[self.result[job_num - 1][0]]  # 横軸の値
            cou_x1 = copy.deepcopy[self.result[job_num - 1][1]]  # 縦軸の値
            
            #ローレンツ関数の初期値　beta = [バックグラウンドの強度, ローレンツ関数の強度, 線幅, ピーク位置]
            beta = np.array([300, 2700000, 300, 4.70479295e+08])
            tolerance =  1e-4
            epsilon = 1e-4
            
            delta = 2*tolerance
            alpha = 1
            while np.linalg.norm(delta) > tolerance:
                F = cou_x1-(beta[0]+beta[1]/(beta[2]+pow(fre_y1+beta[3],2)))
                J = np.zeros((len(F), len(beta)))  # 有限差分ヤコビアン
                for jj in range(0, len(beta)):
                    dBeta = np.zeros(beta.shape)
                    dBeta[jj] = epsilon
                    J[:, jj] = (cou_x1-((beta[0]+dBeta[0])+(beta[1]+dBeta[1])/((beta[2]+dBeta[2])+pow(fre_y1+(beta[3]+dBeta[3]),2)))-F)/epsilon
                delta = -np.linalg.pinv(J).dot(F)  # 探索方向
                beta = beta + alpha*delta
            
            # Ey1_countはフィッティング後の縦軸のリスト
            Ey1_count = beta[0]+beta[1]/(beta[2]+pow(fre_y1+beta[3],2))
            return Ey1_count
        
        
        elif self.mode[job_num - 1] == "all":  # 全体の場合
            fre_y2 = copy.deepcopy[self.result[job_num - 1][0]]  # 横軸全体の値
            cou_x2 = copy.deepcopy[self.result[job_num - 1][1]]  # 縦軸全体の値
            
            #Eyのみを切り取る
            fre_y2 = fre_y2[350:430]
            cou_x2 = cou_x2[350:430]
            
            #ローレンツ関数の初期値　beta = [バックグラウンドの強度, ローレンツ関数の強度, 線幅, ピーク位置]
            beta = np.array([300, 2700000, 300, 4.70479295e+08])
            tolerance =  1e-4
            epsilon = 1e-4
            
            delta = 2*tolerance
            alpha = 1
            while np.linalg.norm(delta) > tolerance:
                F = cou_x2-(beta[0]+beta[1]/(beta[2]+pow(fre_y2+beta[3],2)))
                J = np.zeros((len(F), len(beta)))  # 有限差分ヤコビアン
                for jj in range(0, len(beta)):
                    dBeta = np.zeros(beta.shape)
                    dBeta[jj] = epsilon
                    J[:, jj] = (cou_x2-((beta[0]+dBeta[0])+(beta[1]+dBeta[1])/((beta[2]+dBeta[2])+pow(fre_y2+(beta[3]+dBeta[3]),2)))-F)/epsilon
                delta = -np.linalg.pinv(J).dot(F)  # 探索方向
                beta = beta + alpha*delta
            
            # Ey2_countはフィッティング後の縦軸のリスト
            Ey2_count = beta[0]+beta[1]/(beta[2]+pow(fre_y2+beta[3],2))
            return Ey2_count

    