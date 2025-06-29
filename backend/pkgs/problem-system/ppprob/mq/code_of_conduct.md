# MessageQueue

QueueMessage --> QueueService --> QueueResponse
の構成で作成すること。


QueueServiceはUseCaseしか持ってはいけない。
Queueを読み込んでUseCaseを実行することがQueueServiceの役目である。



