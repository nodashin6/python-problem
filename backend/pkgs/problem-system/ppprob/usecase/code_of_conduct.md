# UseCase

命名は
xxxx_use_case.py
とする


xxxx_use_case.py: controllerが直接使うもの
_xxxx_use_case.py: controlelrが直接使わないもの（システムからの呼び出し）


## フォルダ分け
適宜フォルダを分けて実装してもよいが、`__init__.py`を作成して、浅く呼び出せるようにすること。