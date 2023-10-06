from flask import request, Blueprint
from flask_restful import Resource, fields, marshal_with, reqparse
from extensions import db
from database import Product, BusinessValidationError, NotFoundError, Category, Cart

api_blueprint = Blueprint('api', __name__, url_prefix='/api')

product_parser = reqparse.RequestParser()
product_parser.add_argument('name')
product_parser.add_argument('price', type=float)
product_parser.add_argument('stock', type=int)
product_parser.add_argument('description')
product_parser.add_argument('category_id', type=int)

product_response_fields = {
    "id": fields.Integer(attribute="id"),  
    "name": fields.String(attribute="name"),  
    "price": fields.Float(attribute="price"),  
    "stock": fields.Integer(attribute="stock"),  
    "description": fields.String(attribute="description"),  
    "category_id": fields.Integer(attribute="category_id")  
}


class ProductAPI(Resource):
    @marshal_with(product_response_fields)
    def get(self, product_id=None):
        if product_id is None:
            all_products = Product.query.all()
            return all_products
        else:
            product = Product.query.get(product_id)
            if product:
                return product
            else:
                raise NotFoundError(status_code=404)

    def delete(self, product_id):
        product_exist = db.session.query(
            Product).filter(Product.id == product_id).first()

        if product_exist:
            db.session.delete(product_exist)
            db.session.commit()
            return '', 200

        if product_exist is None:
            raise NotFoundError(status_code=404)
    @marshal_with(product_response_fields)
    def put(self, product_id):
        args = product_parser.parse_args()
        product_name = args.get('name', None)  
        product_price = args.get('price', None) 
        product_stock = args.get('stock', None) 
        product_description = args.get('description', None)
        product_category_id = args.get('category_id', None)


        if product_name is None:
            raise BusinessValidationError(
                status_code=400, error_code='MISSING_PRODUCT_NAME', error_message='Product name is required and should be a string')

        if product_price is None:
            raise BusinessValidationError(
                status_code=400, error_code='MISSING_PRODUCT_PRICE', error_message='Product price is required and should be a number')

        if product_stock is None:
            raise BusinessValidationError(
                status_code=400, error_code='MISSING_PRODUCT_STOCK', error_message='Product stock is required and should be an integer')

        if product_description is None:
            raise BusinessValidationError(
                status_code=400, error_code='MISSING_PRODUCT_DESCRIPTION', error_message='Product description is required and should be a string')

        if product_category_id is None:
            raise BusinessValidationError(
                status_code=400, error_code='MISSING_PRODUCT_CATEGORY', error_message='Product category ID is required and should be an integer')

        product = db.session.query(Product).filter(Product.id == product_id).first()

        if product is None:
            raise NotFoundError(status_code=404)

        product.name = product_name
        product.price = product_price
        product.stock = product_stock
        product.description = product_description
        product.category_id = product_category_id

        db.session.commit()

        return product


    @marshal_with(product_response_fields)
    def post(self):
        args = product_parser.parse_args()
        product_name = args.get('name', None)  
        product_price = args.get('price', None) 
        product_stock = args.get('stock', None) 
        product_description = args.get('description', None)
        product_category_id = args.get('category_id', None)

        if product_name is None:
            raise BusinessValidationError(
                status_code=400, error_code='MISSING_PRODUCT_NAME', error_message='Product name is required and should be a string')

        if product_price is None:
            raise BusinessValidationError(
                status_code=400, error_code='MISSING_PRODUCT_PRICE', error_message='Product price is required and should be a number')

        if product_stock is None:
            raise BusinessValidationError(
                status_code=400, error_code='MISSING_PRODUCT_STOCK', error_message='Product stock is required and should be an integer')

        if product_description is None:
            raise BusinessValidationError(
                status_code=400, error_code='MISSING_PRODUCT_DESCRIPTION', error_message='Product description is required and should be a string')

        if product_category_id is None:
            raise BusinessValidationError(
                status_code=400, error_code='MISSING_PRODUCT_CATEGORY', error_message='Product category ID is required and should be an integer')

        product = db.session.query(Product).filter(Product.name == product_name).first()

        if product:
            raise BusinessValidationError(status_code=409, error_code='PRODUCT_ALREADY_EXISTS', error_message='Product with this name already exists')

        new_product = Product(
            name=product_name,
            price=product_price,
            stock=product_stock,
            description=product_description,
            category_id=product_category_id
        )

        db.session.add(new_product)
        db.session.commit()

        return new_product, 201
    
category_parser = reqparse.RequestParser()
category_parser.add_argument('name', required=True)

category_response_fields = {
    "id": fields.Integer(attribute="id"),
    "name": fields.String(attribute="name")
}

class CategoryAPI(Resource):
    @marshal_with(category_response_fields)
    def get(self, category_id=None):
        if category_id is None:
            all_categories = Category.query.all()
            return all_categories
        else:
            category = Category.query.get(category_id)
            if category:
                return category
            else:
                raise NotFoundError(status_code=404)

    def delete(self, category_id):
        category_exist = db.session.query(
            Category).filter(Category.id == category_id).first()

        if category_exist:
            db.session.delete(category_exist)
            db.session.commit()
            return '', 200

        if category_exist is None:
            raise NotFoundError(status_code=404)

    @marshal_with(category_response_fields)
    def put(self, category_id):
        args = category_parser.parse_args()
        category_name = args.get('name', None)

        if category_name is None:
            raise BusinessValidationError(
                status_code=400, error_code='MISSING_CATEGORY_NAME', error_message='Category name is required and should be a string')

        category = db.session.query(Category).filter(
            Category.id == category_id).first()

        if category is None:
            raise NotFoundError(status_code=404)

        category.name = category_name
        db.session.commit()

        return category

    @marshal_with(category_response_fields)
    def post(self):
        args = category_parser.parse_args()
        category_name = args.get('name', None)

        if category_name is None:
            raise BusinessValidationError(
                status_code=400, error_code='MISSING_CATEGORY_NAME', error_message='Category name is required and should be a string')

        category = db.session.query(Category).filter(
            Category.name == category_name).first()

        if category:
            raise BusinessValidationError(status_code=409, error_code='CATEGORY_ALREADY_EXISTS', error_message='Category with this name already exists')

        new_category = Category(name=category_name)

        db.session.add(new_category)
        db.session.commit()

        return new_category, 201
cart_parser = reqparse.RequestParser()
cart_parser.add_argument('user_id', type=int, required=True)
cart_parser.add_argument('product_id', type=int, required=True)
cart_parser.add_argument('quantity', type=int, required=True)

cart_response_fields = {
    "id": fields.Integer(attribute="id"),
    "user_id": fields.Integer(attribute="user_id"),
    "product_id": fields.Integer(attribute="product_id"),
    "quantity": fields.Integer(attribute="quantity")
}

class CartAPI(Resource):
    @marshal_with(cart_response_fields)
    def get(self, cart_id=None):
        if cart_id is None:
            all_cart_items = Cart.query.all()
            return all_cart_items
        else:
            cart_item = Cart.query.get(cart_id)
            if cart_item:
                return cart_item
            else:
                raise NotFoundError(status_code=404)

    def delete(self, cart_id):
        cart_item_exist = db.session.query(
            Cart).filter(Cart.id == cart_id).first()

        if cart_item_exist:
            db.session.delete(cart_item_exist)
            db.session.commit()
            return '', 200

        if cart_item_exist is None:
            raise NotFoundError(status_code=404)

    @marshal_with(cart_response_fields)
    def put(self, cart_id):
        args = cart_parser.parse_args()
        user_id = args.get('user_id')
        product_id = args.get('product_id')
        quantity = args.get('quantity')

        cart_item = db.session.query(Cart).filter(Cart.id == cart_id).first()

        if cart_item is None:
            raise NotFoundError(status_code=404)

        cart_item.user_id = user_id
        cart_item.product_id = product_id
        cart_item.quantity = quantity

        db.session.commit()

        return cart_item

    @marshal_with(cart_response_fields)
    def post(self):
        args = cart_parser.parse_args()
        user_id = args.get('user_id')
        product_id = args.get('product_id')
        quantity = args.get('quantity')

        new_cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)

        db.session.add(new_cart_item)
        db.session.commit()

        return new_cart_item, 201
    

from flask_restful import Api

api = Api(api_blueprint)
api.add_resource(ProductAPI, '/products', '/products/<int:product_id>')
api.add_resource(CategoryAPI, '/categories', '/categories/<int:category_id>')
api.add_resource(CartAPI, '/carts', '/carts/<int:cart_id>')
