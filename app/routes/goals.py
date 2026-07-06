from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models.models import Goal

goals_bp = Blueprint("goals", __name__, template_folder="../templates")


@goals_bp.route("/", methods=["GET", "POST"])
@login_required
def goals_index():
    if request.method == "POST":
        goal_type = request.form.get("goal_type")
        target_value = request.form.get("target_value")
        description = request.form.get("description")

        try:
            target_value = int(target_value)
            if target_value <= 0:
                raise ValueError
        except (TypeError, ValueError):
            flash("Target value must be a positive integer.", "danger")
            return redirect(url_for("goals.goals_index"))

        goal = Goal(
            user_id=current_user.id,
            goal_type=goal_type,
            description=description,
            target_value=target_value,
            current_value=0,
            status="active",
        )
        db.session.add(goal)
        db.session.commit()
        flash("Goal created.", "success")
        return redirect(url_for("goals.goals_index"))

    goals = Goal.query.filter_by(user_id=current_user.id).order_by(
        Goal.created_at.desc()
    )
    return render_template("goals.html", goals=goals)


@goals_bp.route("/complete/<int:goal_id>", methods=["POST"])
@login_required
def complete_goal(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    goal.status = "completed"
    db.session.commit()
    flash("Goal marked as completed.", "success")
    return redirect(url_for("goals.goals_index"))
