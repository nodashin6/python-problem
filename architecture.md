# アーキテクチャ図


## パッケージの分離
各packageは、/backend/packageに記載。

- core: 抽象的な設計、汎用的な関数の提供
- auth: user管理
- problem-system: 問題の提供、識別
- judge-system: 提出したコードの実行
- edutorial-system: 問題の解説を管理する
- seed: 指定のリポジトリをcloneすれば、問題集を自作・配布することができる。seedはそのimport処理を書く。


## ひとつのパッケージのアーキテクチャ

```mermaid

graph TD


subgraph QueueSystem

    subgraph QueueLayer
        QMessage -->|input| QService -->|output| QResponse
    end
    QController
    QConsumer
    QDispatcher
    QRuntime

end

subgraph DB
    Database
    MessageQueue
    QConsumer -->|access| MessageQueue
end

subgraph DDD

    subgraph ApplicationLayer

        subgraph APIRequest
            APIRequestModel
            APIResponseModel
        end

        subgraph API
            APIRouter
            APIController
        end

        App -->|depends| APIRouter
        APIRouter -->|depends| APIController
        API -->|depends| APIRequest

    end

    subgraph UseCaseLayer
        Command -->|input| UseCase -->|output| Result
    end

    subgraph Domain

        Helper

        subgraph DataModel
            Entity
            Model

            Model -->|depends| Entity
            Entity --> Enums
        end

        subgraph DomainLayer

            DomainService

            subgraph DomainSchema
                CreateSchema
                UpdateSchema
                ReadSchema
                ReadSchema -->|transform| Entity
            end

        end

    end

    subgraph InfrastructureLayer
        Table
        ConcreteSchema
        Repository
        AggregateRepository
        Repository -->|depends| ConcreteSchema
        ConcreteSchema -->|transform| ReadSchema
        Repository -->|depends| Table
        Database -->|depends| Table
    end

    DomainLayer -.->|If needed| Helper
    InfrastructureLayer -.->|If needed| Helper
    Helper -->|depends| DataModel

    UseCase -->|use| DomainService
    DomainService -->|use| Repository
    DomainService -->|use| AggregateRepository
    DomainService -->|depends| DataModel
    DomainService -->|depends| DomainSchema
    Repository -->|depends| DomainSchema
    Repository -->|access| Database
    AggregateRepository -->|depends| Model
    AggregateRepository -->|use| Repository


end

QueueLayer -.->|depends| UseCaseLayer

QConsumer -->|pop| QMessage

QDispatcher -->|use| QConsumer
QConsumer -->|return message| QDispatcher


QController -->|use| QDispatcher
QDispatcher -->|return message| QController

QDispatcher -->|use| QRuntime

QController -->|args=message| QService

QService -->|exec| UseCase

APIController -->|use| UseCase
App -->|background| QController

```