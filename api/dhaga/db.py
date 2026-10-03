import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def utcnow():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Vendor(Base):
    __tablename__ = "vendors"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(80))


class Product(Base):
    __tablename__ = "products"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    sku: Mapped[str] = mapped_column(String(40), unique=True)
    vendor_id: Mapped[str] = mapped_column(ForeignKey("vendors.id"))
    name: Mapped[str] = mapped_column(String(150))
    category: Mapped[str] = mapped_column(String(60))
    colour: Mapped[str | None] = mapped_column(String(60))
    fabric: Mapped[str | None] = mapped_column(String(60))
    price: Mapped[float] = mapped_column(Float)
    inventory: Mapped[dict] = mapped_column(JSON)
    raw_attributes: Mapped[dict] = mapped_column(JSON)
    field_provenance: Mapped[dict] = mapped_column(JSON)
    images: Mapped[list] = mapped_column(JSON)
    workflow: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(40))
    target_drop: Mapped[str] = mapped_column(String(30))


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    demo_phone: Mapped[str] = mapped_column(String(30))
    language: Mapped[str] = mapped_column(String(30))
    city: Mapped[str] = mapped_column(String(80))


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payment_mode: Mapped[str] = mapped_column(String(20))
    payment_status: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30))
    status_history: Mapped[list] = mapped_column(JSON)
    line_items: Mapped[list] = mapped_column(JSON)
    total: Mapped[float] = mapped_column(Float)
    inspection_status: Mapped[str] = mapped_column(String(30))


class Shipment(Base):
    __tablename__ = "shipments"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"))
    carrier: Mapped[str] = mapped_column(String(30))
    tracking_id: Mapped[str] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(30))
    scan_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scan_city: Mapped[str] = mapped_column(String(80))
    eta: Mapped[str | None] = mapped_column(String(30))
    simulate_timeout: Mapped[bool] = mapped_column(Boolean, default=False)


class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(70), unique=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    order_id: Mapped[str | None] = mapped_column(String(40), ForeignKey("orders.id"))
    channel: Mapped[str] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(30))
    expected_intent: Mapped[str] = mapped_column(String(30))
    scenario: Mapped[str | None] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(30), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    messages: Mapped[list] = mapped_column(JSON)


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    rating: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(30))
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    analysis: Mapped[dict | None] = mapped_column(JSON)


class ReviewInvestigation(Base):
    __tablename__ = "review_investigations"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    issue_code: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30))
    owner: Mapped[str] = mapped_column(String(80))
    notes: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Run(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.id"))
    session_id: Mapped[str] = mapped_column(String(80))
    intent: Mapped[str] = mapped_column(String(30))
    decision: Mapped[str] = mapped_column(String(30))
    proposed_reply: Mapped[str] = mapped_column(Text)
    proposed_action: Mapped[str | None] = mapped_column(String(50))
    reason_codes: Mapped[list] = mapped_column(JSON)
    verified_facts: Mapped[dict] = mapped_column(JSON)
    policy_id: Mapped[str | None] = mapped_column(String(50))
    trace: Mapped[list] = mapped_column(JSON)
    cost_usd: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Audit(Base):
    __tablename__ = "audits"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"))
    action: Mapped[str] = mapped_column(String(30))
    actor: Mapped[str] = mapped_column(String(80))
    before: Mapped[str] = mapped_column(Text)
    after: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


load_dotenv(Path(__file__).parents[1] / ".env")
url = os.getenv("DATABASE_URL", "sqlite:///./dhaga-demo.db")
if url.startswith("postgres://"):
    url = "postgresql+psycopg://" + url[len("postgres://"):]
elif url.startswith("postgresql://") and "+psycopg" not in url:
    url = "postgresql+psycopg://" + url[len("postgresql://"):]
engine = create_engine(url, pool_pre_ping=True, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {})
if url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
