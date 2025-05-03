import decimal
import pydantic
import typing as tp

class ProductBase(pydantic.BaseModel):
    name: str
    description: tp.Optional[str]
    price: decimal.Decimal
    category: str
    in_stock: int
    
    class Config:
        json_encoders = {
            decimal.Decimal: lambda v: float(v)
        }

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: str
    
    class Config:
        json_encoders = {
            decimal.Decimal: lambda v: float(v)
        }
