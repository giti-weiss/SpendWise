# controllers/goals_controller.py
from flask import Blueprint, request, jsonify
from dto.Goals.GoalsDto import GoalCreateDTO, GoalDetailCreateDTO
from services.Goals.Goals import GoalsService
from repositories.Goals.Goals import GoalsRepository
from db_connection import SessionLocal

session = SessionLocal()
goals_repo = GoalsRepository(session)
details_repo = GoalsRepository(session)
service = GoalsService(goals_repo, details_repo)

goals_bp = Blueprint("goals", __name__)

# ---------- Goals ----------
@goals_bp.route('', methods=['POST'])
def create_goal():
    dto = GoalCreateDTO(**request.get_json())
    goal = service.create_goal(dto)
    return jsonify({"goal_id": goal.goal_id}), 201

@goals_bp.route('', methods=['GET'])
def get_goals():
    data = service.get_all_goals()
    return jsonify([{
        "goal_id": g.goal_id,
        "user_id": g.user_id,
        "goal_created_date": g.goal_created_date.isoformat()
    } for g in data])

@goals_bp.route('/<int:goal_id>', methods=['GET'])
def get_goal(goal_id):
    goal = service.get_goal_by_id(goal_id)
    if not goal:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "goal_id": goal.goal_id,
        "user_id": goal.user_id,
        "goal_created_date": goal.goal_created_date.isoformat()
    })

@goals_bp.route('/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    dto = GoalCreateDTO(**request.get_json())
    goal = service.update_goal(goal_id, dto)
    if not goal:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "updated"})

@goals_bp.route('/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    goal = service.delete_goal(goal_id)
    if not goal:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})


# ---------- GoalDetails ----------
@goals_bp.route('/details', methods=['POST'])
def create_goal_detail():
    dto = GoalDetailCreateDTO(**request.get_json())
    detail = service.create_goal_detail(dto)
    return jsonify({"detail_id": detail.detail_id}), 201

@goals_bp.route('/details/<int:goal_id>', methods=['GET'])
def get_goal_details(goal_id):
    details = service.get_goal_details(goal_id)
    return jsonify([{
        "detail_id": d.detail_id,
        "goal_id": d.goal_id,
        "goal_type_id": d.goal_type_id,
        "goal_description": d.goal_description,
        "goal_target_date": d.goal_target_date.isoformat(),
        "status_id": d.status_id
    } for d in details])

@goals_bp.route('/details/<int:detail_id>', methods=['PUT'])
def update_goal_detail(detail_id):
    dto = GoalDetailCreateDTO(**request.get_json())
    detail = service.update_goal_detail(detail_id, dto)
    if not detail:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "updated"})

@goals_bp.route('/details/<int:detail_id>', methods=['DELETE'])
def delete_goal_detail(detail_id):
    detail = service.delete_goal_detail(detail_id)
    if not detail:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"})