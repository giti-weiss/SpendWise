from datetime import datetime
from sqlalchemy import func, extract
from models.Finance.Expenses import Expense
from models.core.Categories import Category
from models.system.MonthlyExpensesSummary import MonthlyExpensesSummary
from models.system.EarlyWarningAlert import EarlyWarningAlert

class EarlyWarningService:

    def __init__(self, session, alert_repo):
        self.session = session
        self.alert_repo = alert_repo

    # =========================
    def check_spending_vs_budget(self, user_id, year, month, budget_plan):

        now = datetime.now()
        is_current_month = (now.year == year and now.month == month)

        if month == 12:
            days_in_month = 31
        else:
            days_in_month = (datetime(year, month + 1, 1) - datetime(year, month, 1)).days

        if is_current_month:
            days_elapsed = now.day
        else:
            days_elapsed = days_in_month

        days_elapsed_pct = min((days_elapsed / days_in_month) * 100, 100)

        actual_rows = (
            self.session.query(
                Expense.category_id,
                Category.category_name,
                func.sum(Expense.amount).label("total")
            )
            .join(Category, Expense.category_id == Category.category_id)
            .filter(
                Expense.user_id == user_id,
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month
            )
            .group_by(Expense.category_id, Category.category_name)
            .all()
        )

        spent_map = {
            row.category_id: {
                "category_name": row.category_name,
                "total": float(row.total)
            }
            for row in actual_rows
        }

        total_spent = sum(v["total"] for v in spent_map.values())
        monthly_limit = budget_plan.get("monthly_limit", 0)
        budget_items = budget_plan.get("budget", [])
        budget_map = {}
        for b in budget_items:
            cid = b.get("category_id")
            planned = b.get("current_amount", 0) - b.get("cut_amount", 0)
            budget_map[cid] = {
                "category_name": b.get("category_name", ""),
                "planned": max(0, planned)
            }

        budget_used_pct = (total_spent / monthly_limit * 100) if monthly_limit > 0 else 0

        general_status = "OK"
        general_message = ""
        general_severity = "LOW"

        if budget_used_pct > 100:
            general_status = "DANGER"
            general_severity = "HIGH"
            general_message = (
                f"⚠️ חרגת מהתקציב החודשי! "
                f"נוצלו {total_spent:.0f} ש״ח — {budget_used_pct:.0f}% מהתקציב."
            )
        elif budget_used_pct > days_elapsed_pct * 1.3:
            general_status = "WARNING"
            general_severity = "MEDIUM"
            general_message = (
                f"⚡ קצב ההוצאות גבוה מהצפוי. "
                f"עברו {days_elapsed_pct:.0f}% מהחודש אבל נוצלו {budget_used_pct:.0f}% מהתקציב."
            )
        else:
            general_message = (
                f"✅ קצב הוצאות תקין — {budget_used_pct:.0f}% נוצל, "
                f"{days_elapsed_pct:.0f}% מהחודש עבר."
            )

        if general_status in ("WARNING", "DANGER"):
            self._upsert_general_alert(
                user_id, year, month,
                general_status, general_severity, general_message,
                monthly_limit, total_spent
            )
        else:
            self._resolve_general_if_ok(user_id, year, month)

        category_alerts = []
        for cid, budget_data in budget_map.items():
            planned = budget_data["planned"]
            if planned <= 0:
                continue

            spent = spent_map.get(cid, {}).get("total", 0)
            spent_pct = (spent / planned) * 100

            if spent > planned:
                category_alerts.append({
                    "category_id": cid,
                    "category_name": budget_data["category_name"],
                    "type": "OVERSPENT",
                    "severity": "HIGH",
                    "budget_amount": round(planned, 2),
                    "spent_so_far": round(spent, 2),
                    "remaining": 0,
                    "message": (
                        f"🔴 חרגת מתקציב {budget_data['category_name']}! "
                        f"הוצאת {spent:.0f} ש״ח מתוך תקציב של {planned:.0f} ש״ח."
                    )
                })
            elif spent_pct > days_elapsed_pct * 1.5:
                category_alerts.append({
                    "category_id": cid,
                    "category_name": budget_data["category_name"],
                    "type": "DANGEROUS_TREND",
                    "severity": "MEDIUM",
                    "budget_amount": round(planned, 2),
                    "spent_so_far": round(spent, 2),
                    "remaining": round(planned - spent, 2),
                    "message": (
                        f"🟠 קצב גבוה ב{budget_data['category_name']}: "
                        f"{spent_pct:.0f}% מהתקציב נוצל — {spent:.0f} מתוך {planned:.0f} ש״ח."
                    )
                })

        for alert_data in category_alerts:
            self._upsert_category_alert(user_id, year, month, alert_data)

        alerted_cids = {a["category_id"] for a in category_alerts}
        self._resolve_ok_categories(user_id, year, month, alerted_cids)

        return {
            "status": general_status,
            "general": {
                "days_elapsed_pct": round(days_elapsed_pct, 1),
                "budget_used_pct": round(budget_used_pct, 1),
                "total_spent": round(total_spent, 2),
                "monthly_limit": monthly_limit,
                "message": general_message
            },
            "alerts": category_alerts
        }

    # =========================
    def check_single_expense(self, user_id, year, month, amount, category_id, category_name=""):
        self.alert_repo.close_previous_alerts(
            user_id,
            year,
            month
        )
        avg_history = (
            self.session.query(
                func.avg(MonthlyExpensesSummary.total_amount)
            )
            .filter(
                MonthlyExpensesSummary.user_id == user_id,
                MonthlyExpensesSummary.category_id == category_id
            )
            .scalar()
        ) or 0

        if avg_history > 0 and amount > avg_history * 2:
            message = (
                f"📊 הוצאה חריגה ({amount:.0f} ש״ח) בקטגוריה {category_name} — "
                f"כמעט פי {amount / avg_history:.1f} מהממוצע החודשי ({avg_history:.0f} ש״ח)."
            )

            alert = EarlyWarningAlert(
                user_id=user_id,
                category_id=category_id,
                year=year,
                month=month,
                alert_type="SINGLE_SPIKE",
                severity="MEDIUM",
                title=f"הוצאה חריגה — {category_name}",
                message=message,
                budget_amount=avg_history,
                spent_so_far=amount,
                status="ACTIVE"
            )
            self.alert_repo.add(alert)

            return {
                "is_spike": True,
                "message": message
            }

        return None

    # =========================
    def check_before_expense(self, user_id, year, month, amount, category_id, category_name=""):
        """
        Smart alert BEFORE saving an expense.
        Checks three things:
        1. Will this expense push the category over its planned budget?
        2. Will this expense push total spending over the monthly limit?
        3. Is this expense unusually large compared to historical avg?

        Returns a dict with warnings the frontend can display immediately.
        """
        from models.Finance.BudgetPlan import BudgetPlan

        now = datetime.now()
        warnings = []
        is_over_category = False
        is_over_total = False
        is_spike = False

        # ── 1. Category-level check: spent_so_far + new_amount vs planned ──
        spent_this_month = (
            self.session.query(func.sum(Expense.amount))
            .filter(
                Expense.user_id == user_id,
                Expense.category_id == category_id,
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month,
            )
            .scalar()
        ) or 0

        planned_for_category = (
            self.session.query(BudgetPlan.planned_amount)
            .filter(
                BudgetPlan.user_id == user_id,
                BudgetPlan.category_id == category_id,
                BudgetPlan.year == year,
                BudgetPlan.month == month,
            )
            .scalar()
        )

        if planned_for_category and planned_for_category > 0:
            after_expense = spent_this_month + amount
            pct_after = (after_expense / planned_for_category) * 100
            pct_before = (spent_this_month / planned_for_category) * 100

            if after_expense > planned_for_category:
                is_over_category = True
                overshoot = after_expense - planned_for_category
                warnings.append({
                    "type": "OVER_BUDGET",
                    "severity": "HIGH",
                    "category_id": category_id,
                    "category_name": category_name,
                    "planned": round(planned_for_category, 2),
                    "spent_so_far": round(spent_this_month, 2),
                    "new_expense": amount,
                    "after_expense": round(after_expense, 2),
                    "overshoot": round(overshoot, 2),
                    "message": (
                        f"⚠️ שימו לב! הוצאה זו ({amount:,.0f}₪) תחרוג מתקציב "
                        f"{category_name} — {after_expense:,.0f}₪ מתוך {planned_for_category:,.0f}₪ "
                        f"(חריגה של {overshoot:,.0f}₪)"
                    ),
                })
            elif after_expense > planned_for_category * 0.85:
                # Warn when approaching the limit (over 85%)
                remaining = planned_for_category - after_expense
                warnings.append({
                    "type": "APPROACHING_LIMIT",
                    "severity": "MEDIUM",
                    "category_id": category_id,
                    "category_name": category_name,
                    "planned": round(planned_for_category, 2),
                    "spent_so_far": round(spent_this_month, 2),
                    "new_expense": amount,
                    "after_expense": round(after_expense, 2),
                    "remaining": round(remaining, 2),
                    "message": (
                        f"📊 אחרי הוצאה זו יישאר לך {remaining:,.0f}₪ בלבד "
                        f"בקטגוריית {category_name} ({pct_after:.0f}% מהתקציב)"
                    ),
                })

        # ── 2. Total budget check ──
        total_spent = (
            self.session.query(func.sum(Expense.amount))
            .filter(
                Expense.user_id == user_id,
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month,
            )
            .scalar()
        ) or 0

        total_planned = sum(
            p.planned_amount for p in (
                self.session.query(BudgetPlan)
                .filter(BudgetPlan.user_id == user_id, BudgetPlan.year == year, BudgetPlan.month == month)
                .all()
            )
        )

        if total_planned > 0:
            after_total = total_spent + amount
            if after_total > total_planned:
                is_over_total = True
                overshoot = after_total - total_planned
                warnings.append({
                    "type": "TOTAL_OVER_BUDGET",
                    "severity": "HIGH",
                    "category_id": None,
                    "category_name": "כללי",
                    "total_planned": round(total_planned, 2),
                    "total_spent": round(total_spent, 2),
                    "new_expense": amount,
                    "after_total": round(after_total, 2),
                    "overshoot": round(overshoot, 2),
                    "message": (
                        f"🔴 הוצאה זו תגרום לחריגה מהתקציב החודשי הכולל! "
                        f"{after_total:,.0f}₪ מתוך {total_planned:,.0f}₪"
                    ),
                })

        # ── 3. Spike detection ──
        avg_history = (
            self.session.query(func.avg(MonthlyExpensesSummary.total_amount))
            .filter(
                MonthlyExpensesSummary.user_id == user_id,
                MonthlyExpensesSummary.category_id == category_id,
            )
            .scalar()
        ) or 0

        if avg_history > 0 and amount > avg_history * 2:
            is_spike = True
            warnings.append({
                "type": "UNUSUAL_SPIKE",
                "severity": "MEDIUM",
                "category_id": category_id,
                "category_name": category_name,
                "amount": amount,
                "avg_history": round(avg_history, 2),
                "ratio": round(amount / avg_history, 1),
                "message": (
                    f"📊 הוצאה חריגה: {amount:,.0f}₪ — כמעט פי "
                    f"{amount / avg_history:.1f} מהממוצע החודשי ({avg_history:,.0f}₪)"
                ),
            })

            # Also save SINGLE_SPIKE alert to DB
            alert = EarlyWarningAlert(
                user_id=user_id,
                category_id=category_id,
                year=year,
                month=month,
                alert_type="SINGLE_SPIKE",
                severity="MEDIUM",
                title=f"הוצאה חריגה — {category_name}",
                message=warnings[-1]["message"],
                budget_amount=avg_history,
                spent_so_far=amount,
                status="ACTIVE",
            )
            self.alert_repo.add(alert)

        return {
            "has_warnings": len(warnings) > 0,
            "is_over_category": is_over_category,
            "is_over_total": is_over_total,
            "is_spike": is_spike,
            "warnings": warnings,
            "spent_so_far_in_category": round(spent_this_month, 2),
            "total_spent_so_far": round(total_spent, 2),
            "total_budget": round(total_planned, 2) if total_planned > 0 else None,
        }

    # =========================
    # suggest rebalance — הצעות לאיזון תקציב
    # =========================
    def suggest_rebalance(self, user_id, year, month, budget_plan):
        """
        מזהה קטגוריות שחרגו ומציע לכסות את הפער מקטגוריות
        גמישות שיש בהן עודף תקציב.
        """
        from sqlalchemy import extract

        # 1. map actual spending
        actual_rows = (
            self.session.query(
                Expense.category_id,
                func.sum(Expense.amount).label("total")
            )
            .filter(
                Expense.user_id == user_id,
                extract("year", Expense.date) == year,
                extract("month", Expense.date) == month
            )
            .group_by(Expense.category_id)
            .all()
        )
        spent_map = {row.category_id: float(row.total) for row in actual_rows}

        budget_items = budget_plan.get("budget", [])
        if not budget_items:
            return {"suggestions": [], "summary": "אין תוכנית תקציבית לחודש זה"}

        # 2. classify each category
        from repositories.core.CategoryStandard import CategoryStandardRepository
        standards = CategoryStandardRepository(self.session).get_all()
        std_map = {s.category_id: s for s in standards}

        overspent = []   # חרגו — צריכים כיסוי
        underspent = []  # נשאר כסף — יכולים לתרום

        for b in budget_items:
            cid = b.get("category_id")
            planned = b.get("planned_amount", 0)
            spent = spent_map.get(cid, 0)
            gap = spent - planned  # חיובי = חריגה, שלילי = עודף
            name = b.get("category_name", f"cat {cid}")

            std = std_map.get(cid)
            is_fixed = std.is_fixed_cost if std else False
            is_essential = std.is_essential if std else False

            if gap > 0:
                overspent.append({
                    "category_id": cid,
                    "category_name": name,
                    "planned": planned,
                    "spent": spent,
                    "gap": round(gap, 2),
                    "is_essential": is_essential,
                })
            elif gap < 0:
                room = abs(gap)
                # можем להציע להעביר מכאן רק אם הקטגוריה לא קבועה
                can_give = not is_fixed
                underspent.append({
                    "category_id": cid,
                    "category_name": name,
                    "planned": planned,
                    "spent": spent,
                    "room": round(room, 2),
                    "can_give": can_give,
                    "is_essential": is_essential,
                })

        # 3. for each overspent category, list ALL underspent categories as options
        # Sort: flexible first (can_give=True), then by room descending
        all_underspent = sorted(underspent, key=lambda x: (not x["can_give"], -x["room"]))

        total_gaps = sum(o["gap"] for o in overspent)

        # group suggestions by overspent category
        suggestions_by_gap = []
        for over in overspent:
            options = []
            for under in all_underspent:
                if under["room"] <= 0:
                    continue
                options.append({
                    "from_category": under["category_name"],
                    "from_category_id": under["category_id"],
                    "available_room": round(under["room"], 2),
                    "is_essential": under["is_essential"],
                    "can_give": under["can_give"],
                    "warning": "קטגוריה חיונית/קבועה — לא מומלץ" if not under["can_give"] else None,
                })
            suggestions_by_gap.append({
                "to_category": over["category_name"],
                "to_category_id": over["category_id"],
                "gap": over["gap"],
                "planned": over["planned"],
                "spent": over["spent"],
                "options": options,  # user chooses from these
            })

        has_any_options = any(s["options"] for s in suggestions_by_gap)

        if not has_any_options:
            summary = "אין קטגוריות עם עודף לכסות את החריגות."
        else:
            summary = (
                f"יש קטגוריות עם עודף שיכולות לכסות "
                f"חריגות של {total_gaps:.0f}₪."
            )

        return {
            "suggestions": suggestions_by_gap,
            "summary": summary,
            "total_gaps": round(total_gaps, 2),
        }

    def apply_rebalance(self, user_id, year, month, transfers, plan_repo):
        """
        מקבל רשימת העברות שהמשתמש אישר ומעדכן את Budget_Plans.
        transfers: [{from_category_id, to_category_id, amount}, ...]
        """
        plan_rows = plan_repo.get_plan_for_month(user_id, year, month)
        plan_map = {r.category_id: r for r in plan_rows}

        applied = []
        for t in transfers:
            from_cid = t.get("from_category_id")
            to_cid = t.get("to_category_id")
            amount = t.get("amount", 0)

            if from_cid in plan_map and to_cid in plan_map:
                from_row = plan_map[from_cid]
                to_row = plan_map[to_cid]

                from_row.planned_amount = round(from_row.planned_amount - amount, 2)
                to_row.planned_amount = round(to_row.planned_amount + amount, 2)

                applied.append({
                    "from_category_id": from_cid,
                    "to_category_id": to_cid,
                    "amount": amount,
                    "new_from_planned": from_row.planned_amount,
                    "new_to_planned": to_row.planned_amount,
                })

        self.session.commit()

        return {
            "applied": applied,
            "message": f"בוצעו {len(applied)} העברות",
        }

    # =========================
    # helpers — UPSERT
    # =========================
    def _upsert_general_alert(self, user_id, year, month, status, severity, message,
                               budget_amount, spent_so_far):
        alert_type = "OVERSPENT" if status == "DANGER" else "DANGEROUS_TREND"
        existing = self.alert_repo.get_existing_alert(
            user_id, year, month, None, alert_type
        )
        if existing:
            existing.spent_so_far = spent_so_far
            existing.budget_amount = budget_amount
            existing.message = message
            self.session.commit()
            return

        alert = EarlyWarningAlert(
            user_id=user_id,
            category_id=None,
            year=year,
            month=month,
            alert_type=alert_type,
            severity=severity,
            title="חריגה תקציבית כללית",
            message=message,
            budget_amount=budget_amount,
            spent_so_far=spent_so_far,
            status="ACTIVE"
        )
        self.alert_repo.add(alert)

    def _upsert_category_alert(self, user_id, year, month, alert_data):
        existing = self.alert_repo.get_existing_alert(
            user_id, year, month,
            alert_data["category_id"],
            alert_data["type"]
        )
        if existing:
            existing.spent_so_far = alert_data["spent_so_far"]
            existing.message = alert_data["message"]
            self.session.commit()
            return

        alert = EarlyWarningAlert(
            user_id=user_id,
            category_id=alert_data["category_id"],
            year=year,
            month=month,
            alert_type=alert_data["type"],
            severity=alert_data["severity"],
            title=f"חריגה — {alert_data['category_name']}",
            message=alert_data["message"],
            budget_amount=alert_data["budget_amount"],
            spent_so_far=alert_data["spent_so_far"],
            status="ACTIVE"
        )
        self.alert_repo.add(alert)

    def _resolve_general_if_ok(self, user_id, year, month):
        self.session.query(EarlyWarningAlert).filter(
            EarlyWarningAlert.user_id == user_id,
            EarlyWarningAlert.year == year,
            EarlyWarningAlert.month == month,
            EarlyWarningAlert.category_id.is_(None),
            EarlyWarningAlert.status == "ACTIVE"
        ).update({
            "status": "RESOLVED",
            "resolved_at": datetime.utcnow()
        })
        self.session.commit()

    def _resolve_ok_categories(self, user_id, year, month, active_alerted_cids):
        if not active_alerted_cids:
            self.session.query(EarlyWarningAlert).filter(
                EarlyWarningAlert.user_id == user_id,
                EarlyWarningAlert.year == year,
                EarlyWarningAlert.month == month,
                EarlyWarningAlert.category_id.isnot(None),
                EarlyWarningAlert.status == "ACTIVE"
            ).update({
                "status": "RESOLVED",
                "resolved_at": datetime.utcnow()
            })
        else:
            self.session.query(EarlyWarningAlert).filter(
                EarlyWarningAlert.user_id == user_id,
                EarlyWarningAlert.year == year,
                EarlyWarningAlert.month == month,
                EarlyWarningAlert.category_id.isnot(None),
                EarlyWarningAlert.category_id.notin_(active_alerted_cids),
                EarlyWarningAlert.status == "ACTIVE"
            ).update({
                "status": "RESOLVED",
                "resolved_at": datetime.utcnow()
            })
        self.session.commit()

    # =========================
    def get_active_alerts(self, user_id, year, month):
        return self.alert_repo.get_active_alerts(user_id, year, month)

    def get_all_alerts(self, user_id, year, month):
        return self.alert_repo.get_all_alerts_for_month(user_id, year, month)
