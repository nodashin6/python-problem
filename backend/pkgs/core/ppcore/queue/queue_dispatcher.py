"""
Queue Dispatcher
キューディスパッチャー - メッセージルーティング

アーキテクチャ図のQDispatcherに対応
"""

from .queue_consumer import QConsumer
from .queue_runtime import QRuntime
from .services.queue_service import QMessage, QResponse, QueueService


class QDispatcher:
    """
    Queue Dispatcher
    キューディスパッチャー - メッセージを適切なサービスにルーティング
    """

    def __init__(self, consumer: QConsumer, runtime: QRuntime):
        self.consumer = consumer
        self.runtime = runtime
        self.services: dict[str, QueueService] = {}

    def register_service(self, message_type: str, service: QueueService) -> None:
        """Register queue service for specific message type"""
        self.services[message_type] = service

    async def get_next_message(self) -> QMessage | None:
        """Get next message from consumer"""
        return await self.consumer.pop_message()

    async def process_message(self, message: QMessage) -> QResponse:
        """Process message using appropriate service"""
        service = self.services.get(message.message_type)
        if service:
            return await self.runtime.execute_service(service, message)
        else:
            return QResponse(
                success=False, error=f"No service registered for message type: {message.message_type}"
            )

    async def handle_response(self, response: QResponse) -> None:
        """Handle service response (logging, metrics, etc.)"""
        # This can be extended by concrete implementations
        if not response.success:
            # Log error
            print(f"Queue service error: {response.error}")

    def return_message_to_consumer(self, message: QMessage) -> None:
        """Return message to consumer (for retry logic)"""
        # Implementation depends on queue system
        # Concrete implementations should override this
        return
