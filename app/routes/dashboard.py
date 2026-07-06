from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..extensions import db
from ..models.models import LeetCodeProfile, Goal, ContestHistory
from ..services.leetcode_service import LeetCodeService

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    lc_profile = current_user.leetcode_profile

    if lc_profile:
        stats = {
            "total_solved": lc_profile.total_solved,
            "easy_solved": lc_profile.easy_solved,
            "medium_solved": lc_profile.medium_solved,
            "hard_solved": lc_profile.hard_solved,
            "contest_rating": lc_profile.contest_rating,
            "contest_ranking": lc_profile.contest_ranking,
            "acceptance_rate": lc_profile.acceptance_rate,
        }
        recent_submissions = LeetCodeService.fetch_recent_submissions(
            lc_profile.leetcode_username, limit=5
        )
        monthly_activity = LeetCodeService.fetch_monthly_activity(
            lc_profile.leetcode_username
        )
    else:
        stats = None
        recent_submissions = []
        monthly_activity = {}

    active_goals = (
        Goal.query.filter_by(user_id=current_user.id, status="active")
        .order_by(Goal.created_at.desc())
        .all()
    )

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_submissions=recent_submissions,
        monthly_activity=monthly_activity,
        active_goals=active_goals,
        lc_profile=lc_profile,
    )


@dashboard_bp.route("/analytics")
@login_required
def analytics():
    lc_profile = current_user.leetcode_profile
    if not lc_profile:
        return render_template("analytics.html", lc_profile=None)

    # For charts
    

    monthly_activity = LeetCodeService.fetch_monthly_activity(
        lc_profile.leetcode_username
    )

    return render_template(
        "analytics.html",
        lc_profile=lc_profile,
        contest_history=contest_history,
        monthly_activity=monthly_activity,
    )
