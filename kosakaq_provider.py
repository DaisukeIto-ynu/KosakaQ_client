# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 15:00:00 2022

@author: Yokohama National University, Kosaka Lab
"""

import requests
import warnings
from qiskit.providers import ProviderV1 as Provider #抽象クラスのインポート
from qiskit.providers.exceptions import QiskitBackendNotFoundError #エラー用のクラスをインポート
from qiskit.providers.jobstatus import JobStatus
from .exceptions import KosakaQTokenError, KosakaQBackendJobIdError #エラー用のクラス（自作）をインポート
from .kosakaq_backend import KosakaQBackend 
from typing import Optional, Union, List, Dict, Any
from datetime import datetime as python_datetime

class KosakaQProvider(Provider): #抽象クラスからの継承としてproviderクラスを作る

    def __init__(self, access_token=None):#引数はself(必須)とtoken(認証が必要な場合)、ユーザーに自分でコピペしてもらう
        super().__init__() #ソースコードは（）空なので真似した
        self.access_token = access_token #トークン定義  
        self.name = 'kosakaq_provider' #nameという変数を右辺に初期化、このproviderクラスの名づけ
        self.url = 'https://192.168.11.156' #リンク変更可能
        self.wjson = '/api/backends.json' #jsonに何を入れてサーバーに送るか
    

  
    def get_backend(self, name=None, **kwargs): #ユーザーに"Rabi"などを引数として入れてもらう、もしbackendsメソッドのreturnにRabiがあればインスタンスを作れる
        """指定されたフィルタリングに合うバックエンドを一つだけ返す(一つ下のメソッドbackendsの一つ目を取り出す)
       引数:
           name (str): バックエンドの名前
           **kwargs: フィルタリングに使用される辞書型
       戻り値:
           Backend: 指定されたフィルタリングに合うバックエンド
       Raises:
           QiskitBackendNotFoundError: バックエンドが見つからなかった場合、もしくは複数のバックエンドがフィルタリングに合う場合、もしくは一つもフィルタリング条件に合わない場合
       """
        backends = self.backends(name, **kwargs) #backendsという変数にbackendsメソッドのreturnのリストを代入
        if len(backends) > 1:
            raise QiskitBackendNotFoundError('More than one backend matches criteria')
        if not backends:
            raise QiskitBackendNotFoundError('No backend matches criteria.')

        return backends[0]
    
    def backends(self, name=None, **kwargs):#API(サーバー)に今使えるbackendを聞く(Rabiが使えるとかunicornが使えるとかをreturn[使えるもの]で教えてくれる)
        """指定したフィルタリングと合うバックエンドたちを返すメソッド
        引数:
            name (str): バックエンドの名前(Rabiやunicorn).
            **kwargs: フィルタリングに使用される辞書型
        戻り値:
            list[Backend]:　フィルタリング基準に合うバックエンドたちのリスト
        """
        self._backend=[] #availableなバックエンドクラスのbkednameを入れていくためのリスト
        res = requests.get(self.url + self.wjson, headers={"Authorization": "access_token" + self.access_token})
        response = res.json() #[{'id': 1, 'bkedid': 0, 'bkedname': 'Rabi', 'bkedstatus': 'unavailable','detail': 'Authentication credentials were not provided',...}, {'id': 2, 'bkedid': 1, 'bkedname': 'Unicorn', 'bkedstatus': 'available'}]
        if response[0]['detail'] == 'Authentication credentials were not provided': #トークンが違ったらdetailの辞書一つだけがresponseのリストに入っていることになる
            raise KosakaQTokenError('access_token was wrong') #トークン間違いを警告
        for i in range(len(response)):   
            if response[i]['bkedstatus'] =='available':
                self._backend.append(KosakaQBackend(self, response[i]['bkedname'], self.url, response[i]['bkedversion'], response[i]['bkednqubits'], 4096, 1))
        return self._backend#responseのstatusがavailableかつフィルタリングにあうバックエンドたちのバックエンドクラスのインスタンスリストを返す
    
    #過去に行ったjobをサーバーから条件指定して取り出す、jobのリストを返す
    def jobs(self,
            limit: int = 10,
            skip: int = 0,
            status: Optional[Union[JobStatus, str, List[Union[JobStatus, str]]]] = None,
            job_name: Optional[str] = None,
            start_datetime: Optional[python_datetime] = None,
            end_datetime: Optional[python_datetime] = None,
            job_tags: Optional[List[str]] = None,
            job_tags_operator: Optional[str] = "OR",
            experiment_id: Optional[str] = None,
            descending: bool = True,
            db_filter: Optional[Dict[str, Any]] = None
    ): #list[KosakaQJob]を返す
        """このバックエンドに送信されたjobのうち指定したフィルタに合うものを取得して、必要があればページ分割する。
        サーバーは一回のコールで返すjobの数に制限があるのでサーバーを何度も呼び出すかもしれない。ページ分割をより細かく制御するにはskipパラメータを参照。
        引数:
            limit: 取得するjobの数
            skip: job取得の検索を開始するインデックス.
            status: このステータスを持つjobのみを取得する。
                    指定方法の例 `status=JobStatus.RUNNING` or `status="RUNNING"`
                    or `status=["RUNNING", "ERROR"]`
            job_name: jobの名前でのフィルタリング用。 job名は部分的にマッチする、そして
                    `regular expressions(正規表現)
               <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions>`_
               が使われる。
            start_datetime: 指定された開始日（現地時間）でのフィルター用。これは作成日がこの指定した現地時間より後のjobを探すのに使われる。
            end_datetime: 指定された終了日（現地時間）でのフィルター用。 これは作成日がこの指定された現地時間よりも前に作られたjobを見つけるために使われる。
            job_tags: jobに割り当てられたタグでフィルターするための引数。
            job_tags_operator: job_tagsでフィルタリングする際に使用する論理演算子。"AND"か"OR"が有効な値。
                   *もしANDを指定した場合、jobにはjob_tagsで指定されたすべてのタグが必要。
                   *もしORを指定した場合、jobはjob_tagsで指定されたタグのいずれかを持っている必要がある。
            experiment_id: jobのexperimentIDでフィルタリング用。
            descending:もし"True"ならjobの作成日の降順で(新しいものから)jobを返す。
                      "False"なら昇順で（古いものから）jobを返す。
            db_filter: ループバックベースのフィルタ
               <https://loopback.io/doc/en/lb2/Querying-data.html>`_.
               これはデータベースの"where"フィルターへのインターフェースである。
               使用例
               エラーのある直近の5つのjobをフィルタリング::
                  job_list = backend.jobs(limit=5, status=JobStatus.ERROR)
               ハブ名"kosaka-q(ibm-q)"を持つ5つのjobをフィルタリング::
                 filter = {'hubInfo.hub.name': 'kosaka-q(ibm-q)'}
                 job_list = backend.jobs(limit=5, db_filter=filter)
        戻り値:
           条件に合うjobのリスト
        Raises:
           KosakaQBackendValueError: キーワード値が認識されない場合 (でも、メソッド内で使われてない)
        """
        return self.jobs( #このjobは違う
            limit=limit, skip=skip, backend_name=self.name(), status=status,
            job_name=job_name, start_datetime=start_datetime, end_datetime=end_datetime,
            job_tags=job_tags, job_tags_operator=job_tags_operator,
            experiment_id=experiment_id, descending=descending, db_filter=db_filter)
        
   
    def retrieve_job(self, job_id: str):#jobidを文字列として代入してもらう（指定してもらう）,対応するJobを返す
        """このバックエンドに投入されたjobを一つだけ返す
        引数:
            job_id: 取得したいjobのID
        戻り値:
            与えられたIDのjob
        Raises:
            KosakaQBackendJobIdError: もしjobの取得に失敗した場合
        """
        job = self.retrieve_job(job_id) #このメソッドたぶん違う
        job_backend = job.backend()

        if self.name() != job_backend.name():
            warnings.warn('Job {} belongs to another backend than the one queried. '
                          'The query was made on backend {}, '
                          'but the job actually belongs to backend {}.'
                          .format(job_id, self.name(), job_backend.name()))
            raise KosakaQBackendJobIdError('Failed to get job {}: '
                                   'job does not belong to backend {}.'
                                   .format(job_id, self.name()))

        return job

        
    def __eq__(self, other): #等号の定義
        """Equality comparison.
        By default, it is assumed that two `Providers` from the same class are
        equal. Subclassed providers can override this behavior.
        """
        return type(self).__name__ == type(other).__name__


