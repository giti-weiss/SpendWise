from flask import Blueprint, request, jsonify

from dto.core.category_dto import CategoryCreateDTO
from services.core.Categories import CategoriesService
from repositories.core.Categories import CategoriesRepository
from db_connection import SessionLocal

categories_blueprint = Blueprint(
    "categories",
    __name__,
    url_prefix="/categories"
)


def get_service():
    db_session = SessionLocal()
    repo = CategoriesRepository(db_session)
    service = CategoriesService(repo)

    return db_session, service


# ==================== יצירת קטגוריה (POST) ====================
@categories_blueprint.route('', methods=['POST'])
def add_category():
    db_session, service = get_service()

    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        dto = CategoryCreateDTO(**data)

        service.add_category(dto)

        return jsonify({'message': 'Category added'}), 201

    finally:
        db_session.close()


# ==================== קבלת כל הקטגוריות (GET) ====================
@categories_blueprint.route('', methods=['GET'])
def get_all_categories():
    db_session, service = get_service()

    try:
        categories = service.get_all_categories()

        return jsonify([
            {
                'category_id': c.category_id,
                'category_name': c.category_name,
                'category_type_id': c.category_type_id,
                'category_description': c.category_description,
                'user_id': c.user_id,
                'created_at': c.created_at.isoformat() if c.created_at else None
            }
            for c in categories
        ])

    finally:
        db_session.close()


# ==================== קבלת קטגוריה לפי ID (GET) ====================
@categories_blueprint.route('/<int:category_id>', methods=['GET'])
def get_category_by_id(category_id):
    db_session, service = get_service()

    try:
        category = service.get_category_by_id(category_id)

        if category is None:
            return jsonify({'message': 'Category not found'}), 404

        return jsonify({
            'category_id': category.category_id,
            'category_name': category.category_name,
            'category_type_id': category.category_type_id,
            'category_description': category.category_description,
            'user_id': category.user_id,
            'created_at': category.created_at.isoformat() if category.created_at else None
        })

    finally:
        db_session.close()


# ==================== עדכון קטגוריה (PUT) ====================
@categories_blueprint.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    db_session, service = get_service()

    try:
        dto = CategoryCreateDTO(**request.get_json())

        updated = service.update_category(category_id, dto)

        if updated is None:
            return jsonify({'message': 'Category not found'}), 404

        return jsonify({'message': 'Category updated'})

    finally:
        db_session.close()


# ==================== מחיקת קטגוריה (DELETE) ====================
@categories_blueprint.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    db_session, service = get_service()

    try:
        deleted = service.delete_category(category_id)

        if not deleted:
            return jsonify({'message': 'Category not found'}), 404

        return jsonify({'message': 'Category deleted'})

    finally:
        db_session.close()