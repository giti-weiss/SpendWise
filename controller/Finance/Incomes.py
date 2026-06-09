from flask import Blueprint, request, jsonify

from dto.Finance.IncomesDto import (
    IncomeCreateDTO,
    IncomeResponseDTO
)
from services.Finance.Incomes import IncomeService
from repositories.Finance.Incomes import IncomesRepository
from db_connection import SessionLocal

session = SessionLocal()

repo = IncomesRepository(session)
service = IncomeService(repo)

income_blueprint = Blueprint(
    "income",
    __name__
)


@income_blueprint.route('', methods=['POST'])
def add_income():
    dto = IncomeCreateDTO(**request.get_json())

    income = service.add_income(dto)

    return jsonify({
        "transaction_id": income.transaction_id
    }), 201


@income_blueprint.route('', methods=['GET'])
def get_incomes():
    incomes = service.get_all_incomes()

    return jsonify([
        IncomeResponseDTO.model_validate(
            income
        ).model_dump(mode="json")
        for income in incomes
    ])


@income_blueprint.route('/<int:transaction_id>', methods=['GET'])
def get_income(transaction_id):
    income = service.get_income_by_id(transaction_id)

    if not income:
        return jsonify({
            "error": "Income not found"
        }), 404

    return jsonify(
        IncomeResponseDTO.model_validate(
            income
        ).model_dump(mode="json")
    )


@income_blueprint.route('/<int:transaction_id>', methods=['PUT'])
def update_income(transaction_id):
    dto = IncomeCreateDTO(**request.get_json())

    income = service.update_income(
        transaction_id,
        dto
    )

    if not income:
        return jsonify({
            "error": "Income not found"
        }), 404

    return jsonify({
        "message": "Income updated"
    })


@income_blueprint.route('/<int:transaction_id>', methods=['DELETE'])
def delete_income(transaction_id):
    income = service.delete_income(transaction_id)

    if not income:
        return jsonify({
            "error": "Income not found"
        }), 404

    return jsonify({
        "message": "Income deleted"
    })