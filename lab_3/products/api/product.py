import typing as tp

from fastapi import APIRouter, HTTPException, Query

from models import product as product_models

router = APIRouter(prefix="/products", tags=["products"])


products_db: tp.List[product_models.Product] = []


# GET /products/list - Получить все продукты с возможностью фильтрации
@router.get("/list", response_model=tp.List[product_models.Product])
def get_products(
    name: tp.Optional[str] = Query(None, description="Фильтр по названию товара"),
    category: tp.Optional[str] = Query(None, description="Фильтр по категории"),
    min_price: tp.Optional[float] = Query(None, description="Минимальная цена"),
    max_price: tp.Optional[float] = Query(None, description="Максимальная цена"),
):
    filtered_products = products_db.copy()

    if name is not None:
        filtered_products = [
            p for p in filtered_products if name.lower() in p.name.lower()
        ]

    if category is not None:
        filtered_products = [
            p for p in filtered_products if category.lower() in p.category.lower()
        ]

    if min_price is not None:
        filtered_products = [p for p in filtered_products if p.price >= min_price]

    if max_price is not None:
        filtered_products = [p for p in filtered_products if p.price <= max_price]

    return filtered_products


@router.get("/details", response_model=product_models.Product)
def get_product(product_id: int):
    for product in products_db:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


# POST /products/create - Создать новый продукт
@router.post("/create", response_model=product_models.Product, status_code=201)
def create_product(product: product_models.ProductCreate):
    product_id = 1 if not products_db else max(p.id for p in products_db) + 1

    new_product = product_models.Product(
        id=product_id,
        name=product.name,
        description=product.description,
        price=product.price,
        category=product.category,
        in_stock=product.in_stock,
    )

    products_db.append(new_product)
    return new_product


# PUT /products/update - Обновить продукт по ID
@router.put("/update", response_model=product_models.Product)
def update_product(product_id: int, product_update: product_models.ProductBase):
    for index, product in enumerate(products_db):
        if product.id == product_id:
            updated_product = product_models.Product(
                id=product_id,
                name=product_update.name,
                description=product_update.description,
                price=product_update.price,
                category=product_update.category,
                in_stock=product_update.in_stock,
            )
            products_db[index] = updated_product
            return updated_product
    raise HTTPException(status_code=404, detail="Product not found")


# DELETE /products/delete - Удалить продукт по ID
@router.delete("/delete", response_model=product_models.Product)
def delete_product(product_id: int):
    for index, product in enumerate(products_db):
        if product.id == product_id:
            deleted_product = products_db.pop(index)
            return deleted_product
    raise HTTPException(status_code=404, detail="Product not found")


# /create/bulk - массовое добавление продуктов
@router.post("/create/bulk", response_model=tp.List[product_models.Product])
def create_products_bulk(products: tp.List[product_models.ProductCreate]):
    new_products = []
    for product in products:
        product_id = 1 if not products_db else max(p.id for p in products_db) + 1

        new_product = product_models.Product(
            id=product_id,
            name=product.name,
            description=product.description,
            price=product.price,
            category=product.category,
            in_stock=product.in_stock,
        )

        products_db.append(new_product)
        new_products.append(new_product)

    return new_products
