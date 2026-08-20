from src.events import EventEnvelope
from src.models import Trade
from src.transport.contracts import EventProducer


class TradeEventPublisher:
    def __init__(self, producer: EventProducer, topic: str = "trades.executed.v1"):
        self._producer = producer
        self._topic = topic

    def publish(self, trade: Trade, correlation_id: str) -> EventEnvelope:
        event = EventEnvelope.trade_executed(trade, correlation_id)
        self._producer.publish(self._topic, event)
        return event
