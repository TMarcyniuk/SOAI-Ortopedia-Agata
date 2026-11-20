"""Modelos de la base de datos: Category y Product."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())

    products = db.relationship("Product", back_populates="category")


class Product(db.Model):
    __tablename__ = "products"
    # Los CHECK requieren MySQL 8.0.16 o superior (en versiones anteriores se ignoran)
    __table_args__ = (
        db.CheckConstraint("price >= 0", name="ck_products_price_nonneg"),
        db.CheckConstraint("stock >= 0", name="ck_products_stock_nonneg"),
        db.CheckConstraint("min_stock >= 0", name="ck_products_min_stock_nonneg"),
    )

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(12, 2), nullable=False)  # dinero: siempre Decimal, nunca float
    stock = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    min_stock = db.Column(db.Integer, nullable=True)  # opcional: si es None no se evalúa stock bajo
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime, nullable=False, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp()
    )

    category = db.relationship("Category", back_populates="products")
