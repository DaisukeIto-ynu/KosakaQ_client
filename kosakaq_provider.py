# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 15:00:00 2022

@author: Yokohama National University, Kosaka Lab
"""

import requests
from qiskit.providers import ProviderV1 as Provider #抽象クラスのインポート
from qiskit.providers.exceptions import QiskitBackendNotFoundError #エラー用のクラスをインポート

class KosakaQProvider(Provider): #抽象クラスからの継承としてproviderクラスを作る

    def __init__(self, access_token=None):#引数はself(必須)とtoken(認証が必要な場合)、ユーザーに自分でコピペしてもらう
        super().__init__() #ソースコードは（）空なので真似した
        self.access_token = access_token #トークン定義
        self.name = 'kosakaq_provider' #nameという変数を右辺に初期化、このproviderクラスの名づけ
        self.url = 'https://192.168.11.156' #リンク変更可能
        self.wjson = '/api/backends.json' #jsonに何を入れてサーバーに送るか
    

  
    def get_backends(self, name=None, **kwargs): #ユーザーに"Rabi"などを引数として入れてもらう、もしbackendsメソッドのreturnにRabiがあればインスタンスを作れる
        
        backends = self.backends(name, **kwargs) #backendsという変数にbackendsメソッドのreturnのリストを代入
        if len(backends) > 1:
            raise QiskitBackendNotFoundError('More than one backend matches criteria')
        if not backends:
            raise QiskitBackendNotFoundError('No backend matches criteria.')

        return backends[0]
    
    def backends(self, name=None, **kwargs):#API(サーバー)に今使えるbackendを聞く(Rabiが使えるとかunicornが使えるとかをreturn[使えるもの]で教えてくれる)
        """指定したフィルタリングと合うバックエンドを一つだけ返すメソッド
        引数:
            name (str): バックエンドの名前(Rabiやunicorn).
            **kwargs: フィルタリングに使用される辞書型
        戻り値:
            list[Backend]:　フィルタリング基準に合うバックエンドたちのリスト
        """
        res = requests.get(self.url + self.wjson, headers={"Authorization": "access_token" + self.access_token})
        response = res.json()
    
    def __eq__(self, other): #等号の定義
        """Equality comparison.
        By default, it is assumed that two `Providers` from the same class are
        equal. Subclassed providers can override this behavior.
        """
        return type(self).__name__ == type(other).__name__
    

