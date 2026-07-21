from flask import Blueprint, jsonify
from db_connection import SessionLocal

from services.core.UserCategoryGoalService import UserCategoryGoalService
from repositories.core.UserCategoryGoalRepository import UserCategoryGoalRepository


user_goal_blueprint = Blueprint(
    "user_goal",
    __name__,
    url_prefix="/user_goal"
)


def get_service():
    session = SessionLocal()
    repo = UserCategoryGoalRepository(session)
    service = UserCategoryGoalService(repo)
    return session, service


@user_goal_blueprint.route("", methods=["GET"])
def get_all():
    session, service = get_service()
    try:
        results = service.get_all()
        return jsonify([r.model_dump() for r in results])
    finally:
        session.close()


@user_goal_blueprint.route("/<int:id>", methods=["GET"])
def get_by_id(id):
    session, service = get_service()
    try:
        result = service.get_by_id(id)
        if not result:
            return jsonify({"message": "Not found"}), 404
        return jsonify(result.model_dump())
    finally:
        session.close()


@user_goal_blueprint.route("/user/<int:user_id>", methods=["GET"])
def get_by_user(user_id):
    session, service = get_service()
    try:
        results = service.get_by_user(user_id)
        return jsonify([r.model_dump() for r in results])
    finally:
        session.close()


@user_goal_blueprint.route("/user/<int:user_id>/recalculate", methods=["POST"])
def recalculate(user_id):
    """
    מחשב מחדש את כל היעדים החודשיים לפי:
    target_amount = amount_per_person × family_size
    """
    session, service = get_service()
    try:
        results = service.recalculate_for_user(user_id)
        return jsonify({
            "message": f"Recalculated {len(results)} goals",
            "goals": [r.model_dump() for r in results]
        }), 201
    finally:
        session.close()


@user_goal_blueprint.route("/user/<int:user_id>/targets", methods=["GET"])
def get_targets_map(user_id):
    """מחזיר dict: {category_id: target_amount}"""
    session, service = get_service()
    try:
        targets = service.get_targets_map(user_id)
        return jsonify({"targets": targets})
    finally:
        session.close()
