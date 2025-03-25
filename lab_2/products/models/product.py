import pydantic
import decimal


class ProductBase(pydantic.BaseModel):
    name: str
    description: str
    price: decimal.Decimal
    category: str
    in_stock: int


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
